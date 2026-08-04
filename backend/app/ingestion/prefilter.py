# backend/app/ingestion/prefilter.py
import re
from typing import List, Tuple, Optional
from app.config import get_settings

settings = get_settings()

# Compile patterns once for performance
def _compile_patterns(keywords):
    return [re.compile(r"\b" + re.escape(kw.lower()) + r"\b") for kw in keywords]

_COMPETITOR_PATTERNS = _compile_patterns(settings.competitor_keywords)
_CONTEXT_PATTERNS = _compile_patterns(settings.pos_context_keywords)
_EXCLUSION_PATTERNS = _compile_patterns(settings.exclusion_keywords)

def validate_article_prefilter(
    title: str,
    content: str,
    competitor_keywords: Optional[List[str]] = None,
    context_keywords: Optional[List[str]] = None,
    exclusion_keywords: Optional[List[str]] = None,
    mode: str = "lenient",          # 'lenient' or 'strict'
    min_word_count: int = 200,
) -> Tuple[bool, List[str], List[str]]:
    """
    Two‑factor validation with optional strict mode.
    - lenient: requires at least one competitor AND one context (original behaviour)
    - strict: additionally checks exclusion, word count ≥ min_word_count, and no negative patterns.
    Returns (is_valid, matched_competitors, matched_contexts).
    """
    combined_text = f"{title} {content}".lower()

    # Step 0: Exclusion (always applied if strict, optional in lenient)
    if mode == "strict":
        for ex_pattern in _EXCLUSION_PATTERNS:
            if ex_pattern.search(combined_text):
                return False, [], []

    # Step 1: Match competitors
    matched_competitors = []
    patterns = _COMPETITOR_PATTERNS
    for idx, pat in enumerate(patterns):
        if pat.search(combined_text):
            matched_competitors.append(settings.competitor_keywords[idx])

    # Step 2: Match context
    matched_contexts = []
    for idx, pat in enumerate(_CONTEXT_PATTERNS):
        if pat.search(combined_text):
            matched_contexts.append(settings.pos_context_keywords[idx])

    # Step 3: Decide based on mode
    if mode == "lenient":
        # At least one competitor and one context
        if matched_competitors and matched_contexts:
            return True, list(set(matched_competitors)), list(set(matched_contexts))
        else:
            return False, [], []

    elif mode == "strict":
        # Must have both, plus word count
        if not matched_competitors or not matched_contexts:
            return False, [], []
        word_count = len(content.split())
        if word_count < min_word_count:
            return False, [], []
        return True, list(set(matched_competitors)), list(set(matched_contexts))

    # fallback
    return False, [], []