from __future__ import annotations

import html
import logging
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from app.core.config.settings import settings
from app.services.research.page_fetcher import fetch_pages_parallel

logger = logging.getLogger(__name__)

_TIMEOUT = 6

_RESULT_PATTERN = re.compile(
    r'<a rel="nofollow" class="result__a" href="(?P<url>[^"]+)">(?P<title>.*?)</a>.*?'
    r'<a class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
    re.DOTALL,
)
_TAG_PATTERN = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    text = _TAG_PATTERN.sub("", text)
    return html.unescape(text).strip()


# ------------------------------------------------------------
# Domain trust signal - structural source verification, not just
# a prompt instruction. Used to tag sources so the model (and the
# user, via the Sources list) can weigh reliability.
# ------------------------------------------------------------
_TRUSTED_DOMAIN_PATTERNS = (
    "wikipedia.org", ".gov", ".gov.pk", ".edu",
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "theguardian.com", "who.int", "un.org",
    "nature.com", "sciencedirect.com",
)


def _domain_of(url: str) -> str:
    match = re.search(r"^https?://(?:www\.)?([^/]+)", url or "", re.IGNORECASE)
    return match.group(1).lower() if match else ""


def _is_trusted(url: str) -> bool:
    domain = _domain_of(url)
    if not domain:
        return False
    return any(domain == p or domain.endswith(p) for p in _TRUSTED_DOMAIN_PATTERNS)


def _search_tavily(query: str, max_results: int) -> list[dict]:
    if not settings.TAVILY_API_KEY:
        return []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": False,
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", [])[:max_results]:
            results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", ""),
                }
            )
        return results
    except Exception:
        return []


def _search_serper(query: str, max_results: int) -> list[dict]:
    if not settings.SERPER_API_KEY:
        return []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": max_results},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("organic", [])[:max_results]:
            results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                }
            )
        return results
    except Exception:
        return []


def _search_exa(query: str, max_results: int) -> list[dict]:
    if not settings.EXA_API_KEY:
        return []
    try:
        resp = requests.post(
            "https://api.exa.ai/search",
            headers={
                "x-api-key": settings.EXA_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "numResults": max_results,
                "contents": {"text": {"maxCharacters": 500}},
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", [])[:max_results]:
            text = r.get("text", "") or ""
            results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": text[:400],
                }
            )
        return results
    except Exception:
        return []


_PLACE_TRAILING_FILLERS = re.compile(
    r"\s+(ka|ki|ke|ke\s+bare\s+mein|ke\s+baray\s+mein|kya\s+hai|kya\s+hy|"
    r"kya\s+h|kahan\s+hai|kahan\s+hy|address|rating|location|"
    r"phone\s+number|number|timing|hours)\b.*$",
    re.IGNORECASE,
)
_PLACE_LEADING_FILLERS = re.compile(
    r"^(what\s+is\s+the|tell\s+me|batao|bataye|bataen|mujhe)\s+",
    re.IGNORECASE,
)


_MAX_WORDS_FOR_AGGRESSIVE_CLEAN = 12


def _clean_place_query(query: str) -> str:
    match = re.search(r"\b(?:of|for|about)\s+(.+)$", query, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip().rstrip("?.! ")
        if 1 <= len(candidate.split()) <= 10:
            return candidate

    # BUG FIX: _PLACE_TRAILING_FILLERS strips from the FIRST "ka/ki/ke..."
    # match to the END of the string - correct for a short query like
    # "Jay Dee Pan Shop ka address batao" (-> "Jay Dee Pan Shop"), but for
    # longer, multi-clause sentences "ka/ki/ke" are ordinary grammar words
    # that show up mid-sentence too. E.g. "Jay Dee Pan Shop jo ke Bahria
    # Town mein hai us ki location batao..." was getting chopped down to
    # just "Jay Dee Pan Shop jo" - destroying the actual query. For longer
    # queries, skip the aggressive stripping and only trim an obvious
    # leading filler word (e.g. "Mujhe ...") instead, leaving the rest of
    # the sentence intact for the search provider to work with.
    if len(query.split()) > _MAX_WORDS_FOR_AGGRESSIVE_CLEAN:
        trimmed = _PLACE_LEADING_FILLERS.sub("", query.strip()).strip().rstrip("?.! ")
        return trimmed or query

    candidate = query.strip()
    prev = None
    while prev != candidate:
        prev = candidate
        candidate = _PLACE_TRAILING_FILLERS.sub("", candidate).strip()
        candidate = _PLACE_LEADING_FILLERS.sub("", candidate).strip()

    candidate = candidate.rstrip("?.! ")
    if candidate and 1 <= len(candidate.split()) <= 10:
        return candidate
    return query


def _search_places(query: str, max_results: int, lat: float | None = None, lng: float | None = None) -> list[dict]:
    """
    Serper's "ll" coordinate-bias parameter does not reliably work for
    the /places endpoint (tested: it returns results from an unrelated
    part of the world regardless of the value passed). Instead, when
    lat/lng are given, we reverse-geocode them to a place name (city/
    town/village, falling back to broader region names as needed - this
    works for any country, not just one) and add that name directly to
    the search query text, which Google actually respects.

    If Serper is unavailable for any reason (no key, quota exhausted,
    request failure, or a valid-but-empty response), this falls back to
    a free OpenStreetMap search (_search_nominatim_places) instead of
    silently returning nothing - so location-aware results keep working,
    just with less detail (no ratings/phone/menu) until Serper is usable
    again.
    """
    query = _clean_place_query(query)

    location_name = None
    if lat is not None and lng is not None:
        location_name = _reverse_geocode(lat, lng)
        if location_name is None:
            logger.warning("web_search: reverse geocode returned no place name for lat=%s lng=%s", lat, lng)

    if not settings.SERPER_API_KEY:
        logger.warning("web_search: places provider skipped - SERPER_API_KEY is not set, using free OpenStreetMap fallback")
        return _search_nominatim_places(query, max_results, lat, lng, location_name)

    search_query = f"{query} in {location_name}" if location_name else query

    try:
        resp = requests.post(
            "https://google.serper.dev/places",
            headers={"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": search_query, "num": max_results},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for p in data.get("places", [])[:max_results]:
            parts = []
            if p.get("category"):
                parts.append("Category: " + str(p["category"]))
            if p.get("rating"):
                parts.append("Rating: " + str(p["rating"]) + " (" + str(p.get("ratingCount", 0)) + " reviews)")
            if p.get("latitude"):
                parts.append("Coordinates: " + str(p["latitude"]) + ", " + str(p["longitude"]))
            snippet = " | ".join(parts) if parts else "(no additional details)"
            maps_url = ""
            if p.get("cid"):
                maps_url = "https://www.google.com/maps/place/?q=place_id:" + str(p["cid"])
            results.append({"title": "[Verified Google Maps listing] " + p.get("title", ""), "url": maps_url, "snippet": snippet})
        if not results:
            logger.warning("web_search: places API returned zero results for query=%r, using free OpenStreetMap fallback", search_query)
            return _search_nominatim_places(query, max_results, lat, lng, location_name)
        return results
    except Exception as exc:
        # Covers quota/credit exhaustion (Serper returns a non-2xx status,
        # which raise_for_status() turns into an exception here) as well
        # as any other network/API failure.
        logger.warning("web_search: places provider request failed: %s - using free OpenStreetMap fallback", exc)
        return _search_nominatim_places(query, max_results, lat, lng, location_name)


def _search_nominatim_places(
    query: str,
    max_results: int,
    lat: float | None,
    lng: float | None,
    location_name: str | None,
) -> list[dict]:
    """
    Free fallback for location-aware business/place search, used only when
    Serper's Places API is unavailable (no key, quota exhausted, or a
    request failure). Uses the same free OpenStreetMap Nominatim service
    already used for reverse geocoding in this file - no API key, no cost.
    Results are less rich than Google Maps (name/address/category only -
    no ratings, phone numbers, or menus), which is labeled explicitly in
    the title so this is never mistaken for verified Maps data.
    """
    search_text = f"{query} in {location_name}" if location_name else query

    params: dict = {
        "q": search_text,
        "format": "json",
        "limit": max_results,
        "addressdetails": 1,
    }
    if lat is not None and lng is not None:
        # Soft bounding-box bias (~0.2 degrees, roughly 20km) toward the
        # user's area. bounded=0 makes this a *preference*, not a hard
        # cutoff, so results still come back even in sparser areas.
        delta = 0.2
        params["viewbox"] = f"{lng - delta},{lat + delta},{lng + delta},{lat - delta}"
        params["bounded"] = 0

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers={"User-Agent": "CreatorOS-LocationSearch/1.0"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("web_search: free OpenStreetMap places fallback also failed: %s", exc)
        return []

    results = []
    for p in data[:max_results]:
        display_name = p.get("display_name", "")
        name = display_name.split(",")[0].strip() if display_name else "Unknown place"
        category = p.get("type") or p.get("class") or ""
        parts = []
        if category:
            parts.append("Category: " + str(category))
        if display_name:
            parts.append("Address: " + display_name)
        snippet = " | ".join(parts) if parts else "(no additional details)"
        maps_url = ""
        if p.get("lat") and p.get("lon"):
            maps_url = f"https://www.openstreetmap.org/?mlat={p['lat']}&mlon={p['lon']}#map=18/{p['lat']}/{p['lon']}"
        results.append(
            {
                "title": "[OpenStreetMap listing - no rating/phone/menu available] " + name,
                "url": maps_url,
                "snippet": snippet,
            }
        )
    return results


_geocode_cache: dict[tuple[float, float], str | None] = {}


def _reverse_geocode(lat: float, lng: float) -> str | None:
    """
    Turns coordinates into a human-readable place name (e.g. "Lahore,
    Pakistan"), using OpenStreetMap's free Nominatim service - no API
    key needed. Works worldwide: falls back through city -> town ->
    village -> county -> state if a given level isn't available for
    that location (rural areas, small towns, etc. don't always have
    a "city" field). Coordinates are rounded before caching so nearby
    requests within the same session reuse one lookup instead of
    hitting the geocoder repeatedly. Returns None (never raises) on
    any failure - callers simply skip the location-text enrichment.
    """
    cache_key = (round(lat, 3), round(lng, 3))
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    location_name = None
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "json",
                "lat": lat,
                "lon": lng,
                "zoom": 14,
                "accept-language": "en",
            },
            headers={"User-Agent": "CreatorOS-LocationSearch/1.0"},
            timeout=5,
        )
        resp.raise_for_status()
        address = resp.json().get("address", {})

        place = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("suburb")
            or address.get("county")
            or address.get("state")
        )
        country = address.get("country")

        parts = [p for p in (place, country) if p]
        location_name = ", ".join(parts) if parts else None
    except Exception as exc:
        logger.warning("web_search: reverse geocode request failed for lat=%s lng=%s: %s", lat, lng, exc)
        location_name = None

    _geocode_cache[cache_key] = location_name
    return location_name

def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    try:
        response = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (CreatorOS ResearchAgent)"},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        return []

    results: list[dict] = []
    for match in _RESULT_PATTERN.finditer(response.text):
        if len(results) >= max_results:
            break
        results.append(
            {
                "title": _clean(match.group("title")),
                "url": match.group("url"),
                "snippet": _clean(match.group("snippet")),
            }
        )
    return results


_PROVIDERS = [
    ("tavily", _search_tavily),
    ("places", _search_places),
    ("serper", _search_serper),
    ("exa", _search_exa),
    ("duckduckgo", _search_duckduckgo),
]

# ------------------------------------------------------------
# Places (Google Maps listings) should only fire when the query is
# actually about a physical business/location - otherwise it returns
# random unrelated listings for topics like "cooking recipe" or
# "inflation rate". Non-place queries skip the places provider.
# ------------------------------------------------------------
_PLACE_INTENT_PATTERN = re.compile(
    r"\b(near me|nearby|aas\s?pas|aas\s?paas|qareeb|address|location|"
    r"kahan hai|kahan hy|phone number|contact number|timing|hours|"
    r"restaurant|shops?|stores?|clinic|hospital|branch|office|"
    r"showroom|dukan|rating|reviews|open now|khula|band|delivery)\b",
    re.IGNORECASE,
)


def _looks_like_place_query(query: str) -> bool:
    return bool(_PLACE_INTENT_PATTERN.search(query))


def _active_providers(query: str) -> list:
    """Same provider list as _PROVIDERS, but drops 'places' unless the
    query actually looks like a business/location search. When it does,
    'places' is moved to the front so fast-mode (which returns the
    first provider with results) actually tries it first instead of
    a generic web provider winning the race and places never running."""
    if _looks_like_place_query(query):
        places_entry = [(name, fn) for name, fn in _PROVIDERS if name == "places"]
        other_entries = [(name, fn) for name, fn in _PROVIDERS if name != "places"]
        return places_entry + other_entries
    return [(name, fn) for name, fn in _PROVIDERS if name != "places"]


_search_cache: dict[str, tuple[float, list[dict]]] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_key(query: str, max_results: int, deep: bool, lat: float | None = None, lng: float | None = None) -> str:
    return f"{query.strip().lower()}|{max_results}|{deep}|{lat}|{lng}"


def web_search(query: str, max_results: int = 5, deep: bool = False, lat: float | None = None, lng: float | None = None) -> list[dict]:
    """
    Cached wrapper around _web_search_impl(). Identical queries within
    the TTL window are served from memory instead of hitting search
    providers again - pure speed win, no behavior change.
    """
    cache_key = _cache_key(query, max_results, deep, lat, lng)
    cached = _search_cache.get(cache_key)
    if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    results = _web_search_impl(query, max_results, deep, lat, lng)
    _search_cache[cache_key] = (time.time(), results)
    return results


def _web_search_impl(query: str, max_results: int = 5, deep: bool = False, lat: float | None = None, lng: float | None = None) -> list[dict]:
    """
    Tries each configured search provider in order (fast mode), or
    queries every provider in parallel and merges results (deep mode).

    Deep mode additionally fetches full-page text (Web Scraper) for
    the top 3 results, attaching it as `full_text` on each result dict
    so downstream context is grounded in real page content, not just
    a one-line snippet. Fast mode skips this to stay snappy.

    Never raises - returns an empty list if every provider fails.
    """
    active_providers = _active_providers(query)

    if not deep:
        for _name, fn in active_providers:
            if _name == "places" and lat is not None and lng is not None:
                results = fn(query, max_results, lat=lat, lng=lng)
            else:
                results = fn(query, max_results)
            if results:
                if _name != "places" and _looks_like_place_query(query) and lat is not None:
                    logger.warning(
                        "web_search: location-aware 'places' provider returned nothing, "
                        "falling back to location-blind provider '%s' for query=%r",
                        _name, query,
                    )
                return results
        return []

    combined: list[dict] = []
    seen_urls: set[str] = set()

    with ThreadPoolExecutor(max_workers=len(active_providers)) as executor:
        future_to_name = {}
        for _pname, _pfn in active_providers:
            if _pname == "places" and lat is not None and lng is not None:
                future_to_name[executor.submit(_pfn, query, max_results, lat=lat, lng=lng)] = _pname
            else:
                future_to_name[executor.submit(_pfn, query, max_results)] = _pname
        try:
            iterator = as_completed(future_to_name, timeout=_TIMEOUT + 2)
            for future in iterator:
                try:
                    results = future.result()
                except Exception:
                    continue
                for r in results:
                    url = r.get("url", "")
                    if url and url in seen_urls:
                        continue
                    if url:
                        seen_urls.add(url)
                    combined.append(r)
        except Exception:
            for future in future_to_name:
                if future.done() and not future.cancelled():
                    try:
                        results = future.result()
                    except Exception:
                        continue
                    for r in results:
                        url = r.get("url", "")
                        if url and url in seen_urls:
                            continue
                        if url:
                            seen_urls.add(url)
                        combined.append(r)

    combined = combined[: max_results * 2]

    # Web Scraper: enrich top 3 sources with full page text (parallel,
    # tight timeout) - only in deep mode, to keep fast mode fast.
    if combined:
        top_urls = [r["url"] for r in combined if r.get("url")][:6]
        fetched = fetch_pages_parallel(top_urls, max_fetch=6)
        for r in combined:
            url = r.get("url")
            if url and url in fetched:
                r["full_text"] = fetched[url]

    return combined


def _format_context_from_results(results: list[dict]) -> str:
    if not results:
        return "(No live web search results available for this query.)"

    domains = {_domain_of(r.get("url", "")) for r in results if r.get("url")}
    domains.discard("")

    lines = [
        f"Live web search results ({len(results)} result(s) across "
        f"{len(domains)} distinct domain(s)):"
    ]
    for i, r in enumerate(results, start=1):
        url = r.get("url", "")
        trust_tag = "[Trusted source] " if _is_trusted(url) else ""
        body = r.get("full_text") or r.get("snippet", "")
        body = body[:3000]
        lines.append(f"{i}. {trust_tag}{r.get('title', '')}\n   {body}\n   Source: {url}")

    return "\n".join(lines)


def format_search_context(query: str, max_results: int = 5, deep: bool = False) -> str:
    """Back-compat wrapper: search + format in one call (context string only)."""
    results = web_search(query, max_results=max_results, deep=deep)
    return _format_context_from_results(results)


def extract_sources(results: list[dict], *, max_sources: int = 8) -> list[dict]:
    """Deduped, ordered {title, url} list for UI display (the 'Sources' button)."""
    sources: list[dict] = []
    seen: set[str] = set()
    for r in results:
        url = r.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        sources.append({"title": r.get("title", "") or url, "url": url})
        if len(sources) >= max_sources:
            break
    return sources


def web_search_with_sources(query: str, max_results: int = 5, deep: bool = False, lat: float | None = None, lng: float | None = None) -> tuple[str, list[dict]]:
    """
    Searches once, returns (context_string_for_prompt, sources_list_for_ui).
    Preferred over calling web_search()+format separately when both are
    needed, since it avoids a duplicate network round of searching.
    """
    results = web_search(query, max_results=max_results, deep=deep, lat=lat, lng=lng)
    context = _format_context_from_results(results)
    sources = extract_sources(results)
    return context, sources
