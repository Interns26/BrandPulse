import html
import re


def clean_html(raw_html: str) -> str:
    """Strips HTML tags and unescapes entities safely."""
    if not raw_html:
        return ""

    # Remove actual HTML tags (<p>, <a href="...">, <b>)
    clean_re = re.compile(r"<[^>]+>")
    text = re.sub(clean_re, "", raw_html)

    # Unescape HTML entities (&amp; -> &, &lt; -> <)
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

    # Step 1: Remove HTML tags & unescape entities
    text = clean_html(text)

    # Step 2: Remove Reddit RSS footer metadata (e.g., "submitted by /u/name [link] [comments]")
    text = re.sub(
        r"\s*submitted by\s+.*?(\[link\]|\[comments\])*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Step 3: Convert Markdown links [Link Text](http://...) to plain 'Link Text'
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Step 4: Remove HTTP/HTTPS URLs
    text = re.sub(r"http[s]?://\S+", "", text)

    # Step 5: Normalize Reddit user/subreddit tags
    text = re.sub(r"/u/\w+", "", text)
    text = re.sub(r"/r/\w+", "", text)

    # Step 6: Remove leftover bracket tags like [link] or [comments]
    text = re.sub(r"\[link\]|\[comments\]", "", text, flags=re.IGNORECASE)

    # Step 7: Normalize extra whitespace
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