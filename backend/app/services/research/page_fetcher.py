from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

_FETCH_TIMEOUT = 5
_MAX_CHARS = 3000
_USER_AGENT = "Mozilla/5.0 (CreatorOS ResearchAgent; +full-page-fetch)"

_STRIP_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg", "iframe"]

_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANKLINES_RE = re.compile(r"\n{3,}")


def fetch_page_text(url: str) -> str | None:
    """
    Downloads a URL and extracts clean, readable body text (boilerplate
    like nav/scripts/footers stripped). Returns None on any failure so
    callers can gracefully fall back to the search-snippet only.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": _USER_AGENT},
            timeout=_FETCH_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "html" not in content_type.lower():
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag_name in _STRIP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        text = soup.get_text(separator="\n")
        text = _WHITESPACE_RE.sub(" ", text)
        text = _BLANKLINES_RE.sub("\n\n", text)
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

        if not text:
            return None

        return text[:_MAX_CHARS]

    except Exception:
        return None


def fetch_pages_parallel(urls: list[str], *, max_fetch: int = 3) -> dict[str, str]:
    """
    Fetches full-page text for up to `max_fetch` URLs in parallel.
    Returns {url: text} only for URLs that succeeded - failures are
    silently omitted so callers can fall back to the snippet.
    """
    targets = [u for u in urls if u][:max_fetch]
    if not targets:
        return {}

    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(targets)) as executor:
        future_to_url = {executor.submit(fetch_page_text, url): url for url in targets}
        for future in as_completed(future_to_url, timeout=_FETCH_TIMEOUT + 3):
            url = future_to_url[future]
            try:
                text = future.result()
            except Exception:
                text = None
            if text:
                results[url] = text

    return results