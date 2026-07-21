import html
import re

def clean_html(raw_html: str) -> str:
    """Strips HTML tags and unescapes entities safely."""
    if not raw_html:
        return ""
    
    # Step 1: Remove actual HTML tags first (<p>, <a href="...">, <b>)
    clean_re = re.compile(r"<[^>]+>")
    text = re.sub(clean_re, "", raw_html)
    
    # Step 2: Unescape HTML entities (&amp; -> &, &lt; -> <)
    text = html.unescape(text)
    
    return text.strip()


def clean_text(text: str) -> str:
    """
    Cleans raw post text for AI processing:
    - Removes HTML tags & unescapes entities
    - Strips URLs
    - Normalizes Reddit-style markup (/u/user, /r/subreddit)
    - Normalizes whitespace
    """
    if not text:
        return ""

    # Step 1: Remove HTML tags & unescape entities
    text = clean_html(text)

    # Step 2: Remove HTTP/HTTPS URLs
    text = re.sub(r"http[s]?://\S+", "", text)

    # Step 3: Normalize Reddit user/subreddit tags
    text = re.sub(r"/u/\w+", "", text)
    text = re.sub(r"/r/\w+", "", text)

    # Step 4: Remove extra spaces, tabs, and newlines
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