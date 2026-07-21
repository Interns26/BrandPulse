import sys
from pathlib import Path

# Resolve app directory dynamically
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from app.ingestion.cleaner import clean_html, clean_text, prepare_text_for_ai


def test_clean_html_removes_tags():
    raw_html = "<p>This is a <b>test</b> post from <a href='https://example.com'>Reddit</a>.</p>"
    expected = "This is a test post from Reddit."
    assert clean_html(raw_html) == expected


def test_clean_html_unescapes_entities():
    raw_html = "BrandPulse &amp; Sentiment Analysis"
    expected = "BrandPulse & Sentiment Analysis"
    assert clean_html(raw_html) == expected


def test_clean_text_removes_urls_and_reddit_usernames():
    raw_text = "Check /r/Python or contact /u/developer at https://reddit.com/r/Python"
    expected = "Check or contact at"
    assert clean_text(raw_text) == expected


def test_prepare_text_for_ai_combines_title_and_content():
    title = "New Model Release"
    content = "<p>The team released a new model version today.</p>"
    expected = "New Model Release. The team released a new model version today."
    assert prepare_text_for_ai(title, content) == expected


def test_prepare_text_for_ai_prevents_duplicate_title():
    title = "Model release notes"
    content = "Model release notes show major performance gains."
    expected = "Model release notes show major performance gains."
    assert prepare_text_for_ai(title, content) == expected