"""TikTok Commercial Content Library integration — commented out for this demo (Meta-only
scope, see PROJECT_PLAN.md section 4). Official free API, so this is an easy win to enable
later, but not needed for the current demo.

To enable later:
1. Register a TikTok for Business developer app and get Commercial Content Library API access.
2. Implement fetch_ads() below, following the same normalized-schema contract as
   meta_ad_library.fetch_ads() (source="tiktok", capped at settings.max_ads_per_source).
3. Uncomment the aggregation call in app/routers/ads.py.
"""

# import httpx
# from datetime import datetime, timezone
# from app.config import settings
#
# _BASE_URL = "https://ads.tiktok.com/creative_radar_api/v1/commercial_content/ad/list"
#
# async def fetch_ads(advertiser_name: str, limit: int | None = None) -> list[dict]:
#     effective_limit = limit or settings.max_ads_per_source
#     # ... call the Commercial Content Library API, paginate up to effective_limit,
#     # normalize into the shared ScrapedAd schema (source="tiktok") ...
#     return []


async def fetch_ads(advertiser_name: str, limit: int | None = None) -> list[dict]:
    raise NotImplementedError(
        "TikTok Commercial Content Library integration is disabled for this demo (Meta-only scope)."
    )
