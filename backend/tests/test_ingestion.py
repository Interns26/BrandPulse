import re
import socket
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from curl_cffi import requests as cffi_requests
from fundus import PublisherCollection, Crawler
from googlenewsdecoder import gnewsdecoder
import trafilatura

# Domains with hard paywalls to skip
PAYWALL_BLACKLIST = {"wsj.com", "bloomberg.com", "ft.com", "barrons.com", "seekingalpha.com"}

# Factor A: Competitor Entity Patterns (Enforces Word Boundaries)
COMPETITOR_PATTERNS = [
    r"\btoast\b", r"\bsquare\b", r"\bclover\b", r"\bshift4\b", 
    r"\blightspeed\b", r"\bstripe\b", r"\btouchbistro\b", r"\bspoton\b"
]

# Factor B: Domain Context Patterns (Prevents 'position' or 'post' matching 'pos')
DOMAIN_PATTERNS = [
    r"\bpos\b", r"\bpoint of sale\b", r"\bmerchant services\b", 
    r"\bpayment processing\b", r"\bcheckout terminal\b", r"\bcard reader\b",
    r"\brestaurant tech\b", r"\bmerchant acquiring\b", r"\bfintech\b"
]

# Disambiguation Negative Exclusions
NEGATIVE_PATTERNS = [
    r"\bairport\b", r"\bterminal velocity\b", r"\bbus terminal\b", 
    r"\balbum\b", r"\btribute\b", r"\belection\b", r"\bvacuum\b", 
    r"\btiger\b", r"\bdiplomacy\b", r"\bmilitary\b", r"\bdiscount\b"
]

def safe_fetch_html(url: str, max_retries: int = 3) -> str:
    """Pre-resolves DNS via OS socket and fetches URL using Chrome impersonation."""
    domain = urlparse(url).netloc

    if any(bp in domain for bp in PAYWALL_BLACKLIST):
        return ""

    try:
        socket.gethostbyname(domain)
    except Exception:
        pass

    for attempt in range(1, max_retries + 1):
        try:
            res = cffi_requests.get(
                url, 
                impersonate="chrome", 
                timeout=15,
                headers={"Accept-Language": "en-US,en;q=0.9"}
            )
            if res.status_code == 200:
                return res.text
            elif res.status_code in (401, 403, 404):
                return ""
        except Exception:
            if attempt < max_retries:
                time.sleep(1.5)
            else:
                return ""
    return ""

def validate_and_diagnose(title: str, text: str):
    """
    Strict Two-Factor Validation Logic:
    1. Length Gate: Rejects articles < 300 words.
    2. Exclusion Check: Drops false positives (airports, music, elections).
    3. Factor A: Must match a Target Competitor Entity via regex boundary.
    4. Factor B: Must match a POS Domain Context Anchor via regex boundary.
    
    Returns: (is_valid: bool, matched_entity: str, matched_context: str)
    """
    combined = f"{title} {text}".lower()
    words = len(text.split())

    # 1. Quality & Length Gate
    if words < 300:
        return False, None, None

    # 2. Hard Exclusion Check
    for neg in NEGATIVE_PATTERNS:
        if re.search(neg, combined):
            return False, None, None

    # 3. Factor A: Competitor Match
    matched_entity = None
    for pattern in COMPETITOR_PATTERNS:
        match = re.search(pattern, combined)
        if match:
            matched_entity = match.group(0)
            break

    if not matched_entity:
        return False, None, None

    # 4. Factor B: Domain Context Match
    matched_context = None
    for pattern in DOMAIN_PATTERNS:
        match = re.search(pattern, combined)
        if match:
            matched_context = match.group(0)
            break

    if not matched_context:
        return False, None, None

    return True, matched_entity, matched_context

def run_strict_pos_batch():
    successful_articles = []
    print("=================== BRANDPULSE: STRICT TWO-FACTOR POS INTELLIGENCE ===================\n")

    # ---------------------------------------------------------
    # PART 1: Fundus Stream with Two-Factor Regex Filtering
    # ---------------------------------------------------------
    print("--- Phase 1: Fundus Stream (Regex & Two-Factor Filter) ---")
    try:
        crawler = Crawler(PublisherCollection.us)
        fundus_count = 0
        
        # Fundus scans live feeds and discards unrelated consumer articles
        for article in crawler.crawl(max_articles=200):
            if fundus_count >= 5:
                break

            title = article.title or ""
            text = article.plaintext or ""
            
            is_valid, entity, context = validate_and_diagnose(title, text)
            
            if is_valid:
                fundus_count += 1
                art_id = len(successful_articles) + 1
                words = len(text.split())
                
                successful_articles.append({
                    "source": "Fundus",
                    "title": title,
                    "words": words,
                    "entity": entity,
                    "context": context
                })
                print(f"[{art_id}/10] [Fundus] VERIFIED MATCH: {title}")
                print(f"       Diagnostic Trigger: Entity ['{entity}'] | Context ['{context}']")
                print(f"       Word Count: {words} words")
                print(f"       Preview: \"{text[:220].strip()}...\"\n")

    except Exception as e:
        print(f"Fundus Execution Exception: {e}\n")

    # ---------------------------------------------------------
    # PART 2: Trafilatura + Context-Anchored Google News Query
    # ---------------------------------------------------------
    print("--- Phase 2: Trafilatura + Google News (Anchored Query & Disambiguation) ---")
    
    query = '("Toast POS" OR "Square POS" OR "Clover POS" OR "Shift4 Payments" OR "Lightspeed POS" OR "Stripe payments") AND ("point of sale" OR "merchant" OR "restaurant software") -airport -vacuum -tribute -election'
    rss_endpoint = f"https://news.google.com/rss/search?q={query}+when:2d&hl=en-US&gl=US&ceid=US:en"

    try:
        raw_rss = safe_fetch_html(rss_endpoint)
        if raw_rss:
            root = ET.fromstring(raw_rss)
            items = root.findall("./channel/item")

            trafilatura_count = 0
            for item in items:
                if trafilatura_count >= 5 or len(successful_articles) >= 10:
                    break

                title = item.find("title").text
                encoded_link = item.find("link").text

                try:
                    decoded = gnewsdecoder(encoded_link)
                    if not decoded.get("status"):
                        continue
                    target_url = decoded.get("decoded_url")
                except Exception:
                    continue

                html = safe_fetch_html(target_url)
                if not html:
                    continue

                body = trafilatura.extract(html)
                if not body:
                    continue

                is_valid, entity, context = validate_and_diagnose(title, body)
                
                if is_valid:
                    trafilatura_count += 1
                    art_id = len(successful_articles) + 1
                    words = len(body.split())

                    successful_articles.append({
                        "source": "Trafilatura",
                        "title": title,
                        "words": words,
                        "entity": entity,
                        "context": context
                    })
                    print(f"[{art_id}/10] [Trafilatura] VERIFIED MATCH: {title}")
                    print(f"       URL: {target_url}")
                    print(f"       Diagnostic Trigger: Entity ['{entity}'] | Context ['{context}']")
                    print(f"       Word Count: {words} words")
                    print(f"       Preview: \"{' '.join(body.split()[:35])}...\"\n")

    except Exception as e:
        print(f"Trafilatura Execution Exception: {e}\n")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("=================== BATCH INGESTION SUMMARY ===================")
    print(f"Total Verified Relevant POS Articles: {len(successful_articles)} / 10\n")

if __name__ == "__main__":
    run_strict_pos_batch()