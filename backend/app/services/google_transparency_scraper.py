"""Google Ads Transparency Center scraper — commented out for this demo (Meta-only scope,
see PROJECT_PLAN.md section 4). No official API; this would use Playwright to scrape the
JS-rendered Transparency Center SPA. Layout may drift over time, so keep this isolated here.

To enable later:
1. Add `playwright` to backend/requirements.txt and run `playwright install chromium`.
2. Implement fetch_ads() below, following the same normalized-schema contract as
   meta_ad_library.fetch_ads() (source="google_transparency", capped at settings.max_ads_per_source).
3. Uncomment the aggregation call in app/routers/ads.py.
"""

# from datetime import datetime, timezone
# from playwright.async_api import async_playwright
# from app.config import settings
#
# async def fetch_ads(advertiser_name: str, limit: int | None = None) -> list[dict]:
#     effective_limit = limit or settings.max_ads_per_source
#     results: list[dict] = []
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto(f"https://adstransparency.google.com/?query={advertiser_name}")
#         # ... scrape rendered ad cards, normalize into the shared ScrapedAd schema ...
#         await browser.close()
#     return results[:effective_limit]


async def fetch_ads(advertiser_name: str, limit: int | None = None) -> list[dict]:
    raise NotImplementedError(
        "Google Transparency Center scraping is disabled for this demo (Meta-only scope)."
    )
