"""LinkedIn Ad Library scraper — commented out for this demo (Meta-only scope, see
PROJECT_PLAN.md section 4). No official API for competitor ad transparency; this would
use Playwright, same approach and layout-drift risk as the Google Transparency scraper.
Key for B2B competitor coverage, so a strong candidate for the next source to enable.

To enable later:
1. Add `playwright` to backend/requirements.txt and run `playwright install chromium`.
2. Implement fetch_ads() below, following the same normalized-schema contract as
   meta_ad_library.fetch_ads() (source="linkedin", capped at settings.max_ads_per_source).
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
#         await page.goto(f"https://www.linkedin.com/ad-library/search?companyName={advertiser_name}")
#         # ... scrape rendered ad cards, normalize into the shared ScrapedAd schema ...
#         await browser.close()
#     return results[:effective_limit]


async def fetch_ads(advertiser_name: str, limit: int | None = None) -> list[dict]:
    raise NotImplementedError(
        "LinkedIn Ad Library scraping is disabled for this demo (Meta-only scope)."
    )
