#!/usr/bin/env python3
"""
Final Google News Pipeline
- Adaptive RPC decoding (supports gnewsdecoder / new_decoderv1)
- WAF/Cloudflare detection
- Two‑Factor Validation (competitor, context, negatives)
- Multi‑tier extraction (Fundus → Trafilatura → Newspaper4k → Readability)
- Hard paywall blacklist, TLS impersonation, proxy support
"""

import re
import time
import logging
import json
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urlparse
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GoogleNewsPipeline")

# ------------------------------------------------------------------
# Optional Dependencies
# ------------------------------------------------------------------
gnewsdecoder = None
new_decoderv1 = None
try:
    from googlenewsdecoder import gnewsdecoder
except ImportError:
    pass
try:
    from googlenewsdecoder import new_decoderv1
except ImportError:
    pass

try:
    from curl_cffi import requests as crequests
except ImportError:
    crequests = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

try:
    from newspaper import Article
except ImportError:
    Article = None

# Optional: Fundus
try:
    from fundus import NewsMap
    FUNDUS_AVAILABLE = True
except ImportError:
    FUNDUS_AVAILABLE = False

# ------------------------------------------------------------------
# Phase 5: Hard Paywall Blacklist
# ------------------------------------------------------------------
PAYWALL_BLACKLIST = {
    "wsj.com", "bloomberg.com", "ft.com", "economist.com",
    "nytimes.com", "barrons.com", "seekingalpha.com",
    "theatlantic.com", "newyorker.com", "businessinsider.com",
}

# ------------------------------------------------------------------
# Two‑Factor Validation Patterns
# ------------------------------------------------------------------
COMPETITOR_PATTERNS = [
    r"\btoast\b", r"\bsquare\b", r"\bclover\b", r"\bshift4\b",
    r"\blightspeed\b", r"\bstripe\b", r"\btouchbistro\b", r"\bspoton\b"
]
DOMAIN_PATTERNS = [
    r"\bpos\b", r"\bpoint of sale\b", r"\bmerchant services\b",
    r"\bpayment processing\b", r"\bcheckout terminal\b", r"\bcard reader\b",
    r"\brestaurant tech\b", r"\bmerchant acquiring\b", r"\bfintech\b"
]
NEGATIVE_PATTERNS = [
    r"\bairport\b", r"\bterminal velocity\b", r"\bbus terminal\b",
    r"\balbum\b", r"\btribute\b", r"\belection\b", r"\bvacuum\b",
    r"\btiger\b", r"\bdiplomacy\b", r"\bmilitary\b", r"\bdiscount\b"
]

def validate_article(title: str, text: str) -> tuple:
    """
    Two‑Factor Validation:
    1. Length ≥ 300 words
    2. No negative patterns
    3. At least one competitor entity
    4. At least one domain context term
    Returns (is_valid, matched_entity, matched_context)
    """
    combined = f"{title} {text}".lower()
    words = len(text.split())
    if words < 300:
        return False, None, None

    for neg in NEGATIVE_PATTERNS:
        if re.search(neg, combined):
            return False, None, None

    entity = None
    for pat in COMPETITOR_PATTERNS:
        m = re.search(pat, combined)
        if m:
            entity = m.group(0)
            break
    if not entity:
        return False, None, None

    context = None
    for pat in DOMAIN_PATTERNS:
        m = re.search(pat, combined)
        if m:
            context = m.group(0)
            break
    if not context:
        return False, None, None

    return True, entity, context

def build_competitor_query(
    competitors: List[str] = None,
    domains: List[str] = None,
    negatives: List[str] = None,
) -> str:
    """Build Google News query from patterns."""
    if competitors is None:
        competitors = [re.sub(r'^\\b|\\b$', '', p) for p in COMPETITOR_PATTERNS]
    if domains is None:
        domains = [re.sub(r'^\\b|\\b$', '', p) for p in DOMAIN_PATTERNS]
    if negatives is None:
        negatives = [re.sub(r'^\\b|\\b$', '', p) for p in NEGATIVE_PATTERNS]

    def fmt(terms):
        out = []
        for t in terms:
            clean = re.sub(r'^\\b|\\b$', '', t).strip()
            out.append(f'"{clean}"' if ' ' in clean else clean)
        return out

    comp = ' OR '.join(fmt(competitors))
    dom  = ' OR '.join(fmt(domains))
    neg  = ' ' + ' '.join(f'-{t}' for t in fmt(negatives)) if negatives else ''
    return f"({comp}) AND ({dom}){neg}"

# ------------------------------------------------------------------
# Main Pipeline
# ------------------------------------------------------------------
class GoogleNewsPipeline:
    def __init__(
        self,
        proxy: Optional[str] = None,
        decode_interval: int = 3,
        impersonate_target: str = "chrome",
    ):
        self.proxy = proxy
        self.decode_interval = decode_interval
        self.impersonate_target = impersonate_target

    # ---------- RSS ----------
    def fetch_rss_feed(self, query: str, hl: str = "en-US", gl: str = "US", ceid: str = "US:en") -> List[Dict[str, str]]:
        encoded_query = quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}&ceid={ceid}"
        logger.info(f"[RSS] Querying: {rss_url}")

        try:
            if crequests:
                response = crequests.get(
                    rss_url,
                    impersonate=self.impersonate_target,
                    proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                    timeout=15,
                )
                xml_content = response.text
            else:
                import requests
                response = requests.get(rss_url, timeout=15)
                xml_content = response.text

            root = ET.fromstring(xml_content)
            items = root.findall("./channel/item") or root.findall(".//item")
            articles = []
            for item in items:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                source = item.findtext("source", "")
                if link:
                    articles.append({
                        "title": title,
                        "obfuscated_url": link,
                        "pub_date": pub_date,
                        "source": source
                    })
            logger.info(f"[RSS] Found {len(articles)} articles.")
            return articles
        except Exception as e:
            logger.error(f"[RSS] Failed: {e}")
            return []

    # ---------- Decoding (Adaptive) ----------
    def decode_google_url(self, obfuscated_url: str) -> Optional[str]:
        decoder_func = gnewsdecoder if gnewsdecoder else new_decoderv1
        if not decoder_func:
            logger.error("googlenewsdecoder missing.")
            return None

        try:
            kwargs = {"interval": self.decode_interval}
            if self.proxy:
                kwargs["proxy"] = self.proxy

            try:
                decoded_res = decoder_func(obfuscated_url, **kwargs)
            except TypeError:
                # Some versions don't accept proxy; retry without it
                decoded_res = decoder_func(obfuscated_url, interval=self.decode_interval)

            if isinstance(decoded_res, dict):
                if decoded_res.get("status") and "decoded_url" in decoded_res:
                    return decoded_res["decoded_url"]
                elif "decoded_url" in decoded_res:
                    return decoded_res["decoded_url"]
            elif isinstance(decoded_res, str):
                return decoded_res
            return None
        except Exception as e:
            logger.error(f"[Decode] Error: {e}")
            return None

    # ---------- Blacklist ----------
    def is_blacklisted(self, target_url: str) -> bool:
        try:
            netloc = urlparse(target_url).netloc.lower()
            return any(domain in netloc for domain in PAYWALL_BLACKLIST)
        except Exception:
            return False

    # ---------- Cloudflare/WAF Detection ----------
    def is_cloudflare_challenge(self, status_code: int, html: str, headers: dict) -> bool:
        if status_code in (403, 503, 429):
            server = headers.get("server", "").lower()
            if "cloudflare" in server or "cf-ray" in headers:
                return True
        cf_signatures = [
            "just a moment...", "cf-mitigated", "enable javascript and cookies to continue",
            "attention required! | cloudflare", "please complete the security check",
            "ddos protection by cloudflare"
        ]
        lower_html = html.lower()[:2000]
        return any(sig in lower_html for sig in cf_signatures)

    # ---------- Stealth Fetch ----------
    def fetch_html_stealth(self, target_url: str) -> Optional[str]:
        if not crequests:
            logger.error("curl_cffi required.")
            return None

        try:
            proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            response = crequests.get(
                target_url,
                impersonate=self.impersonate_target,
                proxies=proxies,
                timeout=15,
                headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                }
            )

            if self.is_cloudflare_challenge(response.status_code, response.text, response.headers):
                logger.warning(f"[WAF] Cloudflare on {urlparse(target_url).netloc}")
                return None

            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"[Fetch] HTTP {response.status_code} on {target_url}")
                return None
        except Exception as e:
            logger.error(f"[Fetch] Error: {e}")
            return None

    # ---------- Extraction Cascade ----------
    def extract_content(self, target_url: str, html: str) -> Dict[str, Any]:
        extracted = {"text": None, "extractor_used": None}

        # Tier 1: Fundus (if available)
        if FUNDUS_AVAILABLE:
            try:
                publisher = NewsMap().get_publisher(target_url)
                if publisher:
                    parsed = publisher.parser.parse(html, target_url)
                    if parsed and parsed.body:
                        extracted["text"] = parsed.body
                        extracted["extractor_used"] = "fundus"
                        return extracted
            except Exception:
                pass

        # Tier 2: Trafilatura
        if trafilatura:
            try:
                text = trafilatura.extract(html, include_links=False, include_images=False, output_format="markdown")
                if text and len(text.strip()) > 150:
                    extracted["text"] = text.strip()
                    extracted["extractor_used"] = "trafilatura"
                    return extracted
            except Exception:
                pass

        # Tier 3: Newspaper4k
        if Article:
            try:
                article = Article(url=target_url)
                article.download(raw_html=html)
                article.parse()
                if article.text and len(article.text.strip()) > 150:
                    extracted["text"] = article.text.strip()
                    extracted["extractor_used"] = "newspaper4k"
                    return extracted
            except Exception:
                pass

        # Tier 4: Readability (fallback)
        try:
            from readability import Document
            doc = Document(html)
            text = doc.summary()
            if text and len(text.strip()) > 150:
                extracted["text"] = text.strip()
                extracted["extractor_used"] = "readability"
        except Exception:
            pass

        return extracted

    # ---------- Main Pipeline ----------
    def run(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results = []
        feed_items = self.fetch_rss_feed(query)
        if limit:
            feed_items = feed_items[:limit]

        for idx, item in enumerate(feed_items, 1):
            logger.info(f"\n--- [{idx}/{len(feed_items)}] {item['title'][:60]} ---")

            # Step 1: Decode
            decoded_url = self.decode_google_url(item["obfuscated_url"])
            if not decoded_url:
                logger.warning("Decode failed.")
                continue
            logger.info(f"Decoded: {decoded_url[:80]}...")

            # Step 2: Blacklist
            if self.is_blacklisted(decoded_url):
                logger.warning(f"Blacklisted: {urlparse(decoded_url).netloc}")
                continue

            # Step 3: Fetch
            html = self.fetch_html_stealth(decoded_url)
            if not html:
                continue

            # Step 4: Extract
            extraction = self.extract_content(decoded_url, html)
            if not extraction["text"]:
                logger.warning("Extraction empty.")
                continue

            # Step 5: Two‑Factor Validation
            title = item["title"]
            text = extraction["text"]
            valid, entity, context = validate_article(title, text)
            if not valid:
                logger.info(f"Validation failed (entity='{entity}', context='{context}')")
                continue

            # Save
            result = {
                "title": title,
                "source": item["source"],
                "pub_date": item["pub_date"],
                "url": decoded_url,
                "content": text,
                "matched_entity": entity,
                "matched_context": context,
                "extractor_used": extraction["extractor_used"]
            }
            results.append(result)
            logger.info(f"✅ Valid article #{len(results)}: {title[:60]}...")

            time.sleep(self.decode_interval)

        return results

    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(results)} articles to {output_file}")

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Google News POS Scraper")
    parser.add_argument("--query", type=str, help="Custom query (overrides auto‑build)")
    parser.add_argument("--hl", default="en-US")
    parser.add_argument("--gl", default="US")
    parser.add_argument("--ceid", default="US:en")
    parser.add_argument("--time", default="1d", help="Time filter: 1h, 1d, 7d")
    parser.add_argument("--proxy", help="Proxy URL (socks5://user:pass@host:port)")
    parser.add_argument("--impersonate", default="chrome")
    parser.add_argument("--interval", type=int, default=3, help="Delay between articles (seconds)")
    parser.add_argument("--max", type=int, default=15, help="Max articles to process")
    parser.add_argument("-o", "--output", default="competitor_news.json")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.query:
        query = args.query
    else:
        query = build_competitor_query()
        logger.info(f"Auto‑built query: {query}")

    # Append time filter if not already present
    if args.time and 'when:' not in query:
        query += f" when:{args.time}"

    pipeline = GoogleNewsPipeline(
        proxy=args.proxy,
        decode_interval=args.interval,
        impersonate_target=args.impersonate
    )

    articles = pipeline.run(query, limit=args.max)
    pipeline.save_results(articles, args.output)