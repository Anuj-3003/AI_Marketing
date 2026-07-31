"""Meta Ad Library integration — the only ad source wired up for this demo.

Sourced via Adyntel's Ad Intelligence API (https://docs.adyntel.com/), which proxies
Meta's ad archive. This avoids needing Meta's own Ad Library API access (identity
verification at facebook.com/ads/library/api), which blocked the direct Graph API
integration this replaces (see PROJECT_PLAN.md section 4).

Google Transparency Center, TikTok Commercial Content Library, and LinkedIn Ad Library
are scoped in PROJECT_PLAN.md section 4 but intentionally not implemented yet; see the
sibling `*_scraper.py` / `*_ad_library.py` stub modules in this package.
"""

from datetime import date, datetime

import httpx

from app.config import settings

_DOMAIN_URL = "https://api.adyntel.com/facebook"
_SEARCH_URL = "https://api.adyntel.com/facebook_ad_search"


def _auth() -> dict:
    return {"api_key": settings.adyntel_api_key, "email": settings.adyntel_email}


def _get(raw: dict, *keys: str):
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return None


def _parse_epoch_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.utcfromtimestamp(int(value)).date()
    except (TypeError, ValueError):
        return None


def _first_image_url(snapshot: dict) -> str | None:
    for image in snapshot.get("images") or []:
        url = _get(image, "original_image_url", "resized_image_url", "url")
        if url:
            return url
    return None


def _body_text(snapshot: dict) -> str | None:
    body = snapshot.get("body")
    return body.get("text") if isinstance(body, dict) else body


def _flatten(results) -> list[dict]:
    # the domain endpoint nests result pages as a list of lists; the keyword endpoint doesn't.
    flat: list[dict] = []
    for item in results or []:
        flat.extend(item) if isinstance(item, list) else flat.append(item)
    return flat


def _normalize(raw_ad: dict) -> dict:
    snapshot = raw_ad.get("snapshot") or {}
    return {
        "source": "meta",
        "headline": _get(snapshot, "title") or _get(raw_ad, "title"),
        "body_text": _body_text(snapshot),
        "image_url": _first_image_url(snapshot),
        "landing_url": _get(snapshot, "link_url", "linkUrl"),
        "first_seen": _parse_epoch_date(_get(raw_ad, "start_date", "startDate")),
        "fetched_at": datetime.utcnow(),
    }


async def _paginate(url: str, payload: dict, effective_limit: int) -> list[dict]:
    results: list[dict] = []
    async with httpx.AsyncClient(timeout=30) as client:
        while len(results) < effective_limit:
            response = await client.post(url, json=payload)
            if response.status_code == 204:
                break
            if response.is_error:
                raise RuntimeError(f"Adyntel API {response.status_code} error: {response.text}")
            data = response.json()

            for raw_ad in _flatten(data.get("results")):
                results.append(_normalize(raw_ad))
                if len(results) >= effective_limit:
                    break

            token = data.get("continuation_token")
            if not token or len(results) >= effective_limit:
                break
            payload = {**_auth(), "continuation_token": token}

    return results


async def fetch_ads(advertiser_name: str, domain: str | None = None, limit: int | None = None) -> list[dict]:
    """Fetch up to `limit` (default settings.max_ads_per_source) recent Meta ads for an
    advertiser via Adyntel, normalized to the shared ScrapedAd schema.

    Prefers a domain-based lookup (richer creative data — images/videos) when the
    competitor has a known domain, falling back to a keyword search on the company name
    otherwise (or if the domain lookup comes back empty).
    """
    effective_limit = limit or settings.max_ads_per_source

    if domain:
        domain_payload = {**_auth(), "company_domain": domain, "country_code": settings.adyntel_country_code}
        results = await _paginate(_DOMAIN_URL, domain_payload, effective_limit)
        if results:
            return results[:effective_limit]

    search_payload = {**_auth(), "keyword": advertiser_name, "country_code": settings.adyntel_country_code}
    return (await _paginate(_SEARCH_URL, search_payload, effective_limit))[:effective_limit]
