# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

import html
import re


def clean_html(raw_html: str) -> str:
    """Strips HTML tags and unescapes entities safely."""
    if not raw_html:
        return ""

    clean_re = re.compile(r"<[^>]+>")
    text = re.sub(clean_re, "", raw_html)
    text = html.unescape(text)

    return text.strip()


def clean_text(text: str) -> str:
    """
    Cleans raw post text for AI processing:
    - Removes HTML tags & unescapes entities
    - Strips Reddit RSS footer boilerplate ('submitted by ... [link] [comments]')
    - Converts markdown links [text](url) -> text
    - Strips raw URLs
    - Normalizes Reddit user/subreddit tags (/u/user, /r/subreddit)
    - Normalizes whitespace
    """
    if not text:
        return ""

    text = clean_html(text)

    text = re.sub(
        r"\s*submitted by\s+.*?(\[link\]|\[comments\])*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"/u/\w+", "", text)
    text = re.sub(r"/r/\w+", "", text)
    text = re.sub(r"\[link\]|\[comments\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def prepare_text_for_ai(title: str, content: str) -> str:
    """
    Combines and cleans title and content into a single string for AI inference.
    """
    clean_title = clean_text(title)
    clean_content = clean_text(content)

    if clean_title and clean_content:
        if clean_content.startswith(clean_title):
            return clean_content
        return f"{clean_title}. {clean_content}"

    return clean_title or clean_content


def clean_news_content(raw_content: str) -> str:
    """
    Sprint 2: Sanitizes full news article bodies extracted via Trafilatura or RSS.
    Removes boilerplate tags, leftover inline scripts, and excessive whitespace while
    preserving punctuation critical for downstream SLM copywriters.
    """
    if not raw_content:
        return ""

    text = clean_html(raw_content)
    # Remove URL strings left in article text
    text = re.sub(r"http[s]?://\S+", "", text)
    # Normalize excessive newlines and double spaces
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()