# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

# backend/app/ingestion/news_fetcher.py
import argparse
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from urllib.parse import urlparse, quote_plus

import feedparser
from curl_cffi import requests as cffi_requests
from dateutil import parser as date_parser
from bs4 import BeautifulSoup
import trafilatura

# Optional extraction libraries
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

try:
    from fundus import NewsMap
    FUNDUS_AVAILABLE = True
except ImportError:
    FUNDUS_AVAILABLE = False

# Decoder – optional
try:
    from googlenewsdecoder import gnewsdecoder
except ImportError:
    gnewsdecoder = None

from app.config import get_settings
from app.ingestion.cleaner import clean_news_content
from app.ingestion.prefilter import validate_article_prefilter

logger = logging.getLogger(__name__)
settings = get_settings()

# Set log level
try:
    log_level_name = settings.ingestion_log_level.upper()
    logger.setLevel(getattr(logging, log_level_name))
except (AttributeError, TypeError):
    logger.setLevel(logging.INFO)

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
GOOGLE_OWNED_DOMAINS = (
    "google.com", "googleusercontent.com", "gstatic.com",
    "googleapis.com", "googletagmanager.com", "googlesyndication.com",
    "doubleclick.net", "schema.org", "w3.org"
)
NON_ARTICLE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".css", ".js")

# Blacklist from config
PAYWALL_BLACKLIST = set(settings.blacklist_domains)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _is_real_publisher_url(url: Optional[str]) -> bool:
    if not url or not url.startswith("http"):
        return False
    domain = urlparse(url).netloc.lower()
    if any(domain == d or domain.endswith("." + d) for d in GOOGLE_OWNED_DOMAINS):
        return False
    if url.lower().split("?")[0].endswith(NON_ARTICLE_EXTENSIONS):
        return False
    return True

def parse_to_iso_utc(date_str: str) -> str:
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = date_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()

# ------------------------------------------------------------------
# Stealth Fetch with WAF detection
# ------------------------------------------------------------------
def _is_cloudflare_challenge(status_code: int, html: str, headers: dict) -> bool:
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

def safe_fetch_html(url: str, max_retries: int = 3) -> Tuple[str, int]:
    """Fetch HTML with Chrome impersonation, WAF detection, exponential backoff."""
    domain = urlparse(url).netloc
    if any(bp in domain for bp in PAYWALL_BLACKLIST):
        return "", 403

    for attempt in range(1, max_retries + 1):
        try:
            res = cffi_requests.get(
                url,
                impersonate="chrome",
                timeout=15,
                headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            # WAF/Cloudflare check
            if _is_cloudflare_challenge(res.status_code, res.text, res.headers):
                logger.warning(f"Cloudflare challenge on {domain}")
                return "", 403

            if res.status_code == 200:
                return res.text, 200
            elif res.status_code == 429:
                wait = 2 ** attempt
                logger.warning(f"Rate limited (429) on {url}. Waiting {wait}s...")
                time.sleep(wait)
                continue
            elif res.status_code in (401, 403, 404, 410):
                return "", res.status_code
            else:
                wait = attempt * 1.5
                logger.warning(f"Got {res.status_code} on {url}. Retrying in {wait}s")
                time.sleep(wait)
                continue
        except Exception as e:
            logger.error(f"Fetch attempt {attempt} failed for {url}: {e}")
            if attempt < max_retries:
                time.sleep(attempt * 2)
            else:
                return "", -1
    return "", -1

# ------------------------------------------------------------------
# Multi‑tier Google URL Decoding (3‑tier)
# ------------------------------------------------------------------
def decode_google_url_multitier(google_url: str) -> Optional[str]:
    """
    3‑tier: gnewsdecoder → BeautifulSoup HTML parsing → HTTP redirect.
    Returns real publisher URL or None.
    """
    if "news.google.com" not in google_url:
        return google_url

    logger.info(f"Decoding Google URL: {google_url[:80]}...")

    # Tier 1: gnewsdecoder (with retries)
    if gnewsdecoder:
        for attempt in range(1, 4):
            try:
                decoded = gnewsdecoder(google_url)
                candidate = None
                if isinstance(decoded, dict):
                    if decoded.get("status") and decoded.get("decoded_url"):
                        candidate = decoded["decoded_url"]
                    elif decoded.get("url"):
                        candidate = decoded["url"]
                elif isinstance(decoded, str) and decoded.startswith("http"):
                    candidate = decoded

                if _is_real_publisher_url(candidate):
                    logger.info(f"✓ Tier 1 success: {candidate}")
                    return candidate
            except Exception as e:
                logger.warning(f"Tier 1 attempt {attempt} failed: {e}")
            time.sleep(2 * attempt)  # backoff

    # Tier 2: BeautifulSoup parse
    try:
        html, status = safe_fetch_html(google_url, max_retries=2)
        if html and status == 200:
            soup = BeautifulSoup(html, 'html.parser')
            # data-n-au
            for a in soup.find_all('a', attrs={'data-n-au': True}):
                href = a.get('data-n-au')
                if _is_real_publisher_url(href):
                    logger.info(f"✓ Tier 2 success (data-n-au): {href}")
                    return href
            # any href
            for a in soup.find_all('a', href=True):
                href = a['href']
                if _is_real_publisher_url(href):
                    logger.info(f"✓ Tier 2 success (href): {href}")
                    return href
            # window.location.replace
            for script in soup.find_all('script'):
                if script.string:
                    match = re.search(r'window\.location\.replace\(["\'](https?://[^"\']+)["\']\)', script.string)
                    if match and _is_real_publisher_url(match.group(1)):
                        logger.info(f"✓ Tier 2 success (window.location): {match.group(1)}")
                        return match.group(1)
    except Exception as e:
        logger.error(f"Tier 2 failed: {e}")

    # Tier 3: HTTP redirect
    try:
        res = cffi_requests.get(google_url, impersonate="chrome", timeout=10, allow_redirects=True)
        final_url = str(res.url)
        if _is_real_publisher_url(final_url):
            logger.info(f"✓ Tier 3 success: {final_url}")
            return final_url
    except Exception as e:
        logger.error(f"Tier 3 failed: {e}")

    logger.error(f"✗ All decoding tiers failed for {google_url[:60]}...")
    return None

# ------------------------------------------------------------------
# Extraction Cascade (Fundus → Trafilatura → Newspaper → Readability)
# ------------------------------------------------------------------
def extract_article_content(url: str, html: str) -> Tuple[str, str]:
    """Extract text using multiple extractors. Returns (text, extractor_used)."""
    # Tier 1: Fundus
    if FUNDUS_AVAILABLE:
        try:
            publisher = NewsMap().get_publisher(url)
            if publisher:
                parsed = publisher.parser.parse(html, url)
                if parsed and parsed.body:
                    return parsed.body, "fundus"
        except Exception:
            pass

    # Tier 2: Trafilatura
    if trafilatura:
        try:
            text = trafilatura.extract(html, include_links=False, include_images=False, output_format="markdown")
            if text and len(text.strip()) > 100:
                return text.strip(), "trafilatura"
        except Exception:
            pass

    # Tier 3: Newspaper4k
    if NEWSPAPER_AVAILABLE:
        try:
            article = Article(url=url)
            article.download(raw_html=html)
            article.parse()
            if article.text and len(article.text.strip()) > 100:
                return article.text.strip(), "newspaper4k"
        except Exception:
            pass

    # Tier 4: Readability
    if READABILITY_AVAILABLE:
        try:
            doc = Document(html)
            text = doc.summary()
            if text and len(text.strip()) > 100:
                return text.strip(), "readability"
        except Exception:
            pass

    return "", "none"

# ------------------------------------------------------------------
# Main Pipeline Function
# ------------------------------------------------------------------
def fetch_competitive_news_articles(
    sources: Optional[Dict[str, str]] = None,
    max_articles: Optional[int] = None,
) -> List[Dict]:
    """
    Orchestrates the entire competitive news ingestion.
    Returns list of dicts with keys: title, content, url, source_name, published_at,
    matched_competitors, matched_contexts.
    """
    if sources is None:
        sources = settings.competitive_news_rss_urls

    processed = []
    mode = settings.validation_mode
    min_words = settings.min_word_count

    for source_name, feed_url in sources.items():
        if max_articles and len(processed) >= max_articles:
            break

        logger.info(f"Fetching RSS from: {source_name}")
        raw_rss, status = safe_fetch_html(feed_url)
        if not raw_rss or status != 200:
            logger.error(f"Failed to fetch RSS {source_name} (status {status})")
            continue

        feed = feedparser.parse(raw_rss)
        logger.info(f"Parsed {len(feed.entries)} entries from {source_name}")

        for entry in feed.entries:
            if max_articles and len(processed) >= max_articles:
                break

            title = clean_news_content(getattr(entry, "title", ""))
            summary = clean_news_content(getattr(entry, "summary", getattr(entry, "description", "")))
            article_url = getattr(entry, "link", "")
            published_raw = getattr(entry, "published", getattr(entry, "updated", ""))

            # 1. Prefilter (two‑factor validation)
            is_valid, comps, ctx = validate_article_prefilter(
                title, summary, mode=mode, min_word_count=min_words
            )
            if not is_valid:
                logger.debug(f"Skipped (prefilter): {title[:60]}...")
                continue

            # 2. Decode URL
            real_url = decode_google_url_multitier(article_url)
            if not _is_real_publisher_url(real_url):
                # If decoding fails, we can still use the original (may be Google) but will fail extraction.
                # Instead, try RSS summary fallback.
                if settings.extractor_fallback_to_summary and len(summary.split()) >= 30:
                    logger.info(f"Using RSS summary for: {title[:60]}")
                    content = summary
                    real_url = article_url
                else:
                    logger.warning(f"No real URL and summary too short: {title[:60]}")
                    continue
            else:
                # 3. Fetch publisher HTML
                html, status = safe_fetch_html(real_url)
                if not html or status != 200:
                    if settings.extractor_fallback_to_summary and len(summary.split()) >= 30:
                        logger.info(f"Fetch failed, using RSS summary for: {title[:60]}")
                        content = summary
                    else:
                        logger.warning(f"Fetch failed and no summary: {title[:60]}")
                        continue
                else:
                    # 4. Extract content using cascade
                    content, extractor = extract_article_content(real_url, html)
                    if not content or len(content.split()) < min_words:
                        # Fallback to summary
                        if settings.extractor_fallback_to_summary and len(summary.split()) >= 30:
                            logger.info(f"Extraction short, using RSS summary for: {title[:60]}")
                            content = summary
                        else:
                            logger.warning(f"Extraction insufficient and no summary: {title[:60]}")
                            continue
                    # optional: log extractor used
                    logger.debug(f"Extractor used: {extractor}")

            # 5. Build final dict
            published_at = parse_to_iso_utc(published_raw)
            processed.append({
                "title": title,
                "content": content.strip(),
                "url": real_url,
                "source_name": source_name,
                "published_at": published_at,
                "matched_competitors": comps,
                "matched_contexts": ctx,
            })

            # Delay to avoid rate limits
            time.sleep(settings.decode_interval)

    logger.info(f"Total articles processed: {len(processed)}")
    return processed

# ------------------------------------------------------------------
# Utility to run and save JSON (for testing)
# ------------------------------------------------------------------
def run_and_save_ingestion_pipeline(
    output_path: str = "output_articles.json",
    max_articles: Optional[int] = None
) -> List[Dict]:
    logger.info("Starting competitive ingestion pipeline...")
    articles = fetch_competitive_news_articles(max_articles=max_articles)

    contract = [
        {
            "title": a["title"],
            "content": a["content"],
            "url": a["url"],
            "source_name": a["source_name"],
            "published_at": a["published_at"],
        }
        for a in articles
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=4, ensure_ascii=False)

    logger.info(f"Saved {len(contract)} articles to {output_path}")
    return contract

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Run Competitive Ingestion Pipeline.")
    parser.add_argument("--output", type=str, default="output_articles.json")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    run_and_save_ingestion_pipeline(args.output, max_articles=args.limit)