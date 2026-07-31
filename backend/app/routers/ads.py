import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.config import settings
from app.db import engine, get_session
from app.models import Competitor, GeneratedAd, ScrapedAd
from app.services import meta_ad_library, openrouter

router = APIRouter(prefix="/api", tags=["ads"])

_CACHE_TTL = timedelta(hours=24)
_refresh_in_progress: set[int] = set()


def _is_fresh(ads: list[ScrapedAd]) -> bool:
    if not ads:
        return False
    newest = max(ad.fetched_at for ad in ads)
    return datetime.utcnow() - newest < _CACHE_TTL


async def _refresh_ads_for_competitor(competitor_id: int) -> None:
    try:
        with Session(engine) as session:
            competitor = session.get(Competitor, competitor_id)
            if competitor is None:
                return

            # Only Meta is active for this demo (see PROJECT_PLAN.md section 4).
            # Google Transparency / TikTok / LinkedIn are scaffolded but disabled:
            # fresh_ads = [
            #     *await meta_ad_library.fetch_ads(competitor.name),
            #     *await google_transparency_scraper.fetch_ads(competitor.name),
            #     *await tiktok_ad_library.fetch_ads(competitor.name),
            #     *await linkedin_ad_library_scraper.fetch_ads(competitor.name),
            # ]
            fresh_ads = await meta_ad_library.fetch_ads(competitor.name, competitor.domain)

            # replace stale rows for this competitor rather than accumulating duplicates
            existing = session.exec(
                select(ScrapedAd).where(ScrapedAd.competitor_id == competitor_id)
            ).all()
            for row in existing:
                session.delete(row)

            for ad in fresh_ads:
                session.add(ScrapedAd(competitor_id=competitor_id, **ad))
            session.commit()
    finally:
        _refresh_in_progress.discard(competitor_id)


@router.get("/competitors/{competitor_id}/ads")
def get_competitor_ads(
    competitor_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    competitor = session.get(Competitor, competitor_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail="Competitor not found")

    ads = session.exec(select(ScrapedAd).where(ScrapedAd.competitor_id == competitor_id)).all()

    if _is_fresh(ads):
        status = "fresh"
    else:
        status = "refreshing"
        if competitor_id not in _refresh_in_progress:
            _refresh_in_progress.add(competitor_id)
            background_tasks.add_task(_refresh_ads_for_competitor, competitor_id)

    return {
        "competitor": {
            "id": competitor.id,
            "name": competitor.name,
            "domain": competitor.domain,
        },
        "ads": [
            {
                "id": ad.id,
                "source": ad.source,
                "headline": ad.headline,
                "body_text": ad.body_text,
                "image_url": ad.image_url,
                "landing_url": ad.landing_url,
                "first_seen": ad.first_seen,
                "fetched_at": ad.fetched_at,
            }
            for ad in ads
        ],
        "status": status,
    }


@router.get("/competitors/{competitor_id}/ads/status")
def get_competitor_ads_status(competitor_id: int, session: Session = Depends(get_session)):
    if competitor_id in _refresh_in_progress:
        return {"status": "refreshing"}
    ads = session.exec(select(ScrapedAd).where(ScrapedAd.competitor_id == competitor_id)).all()
    return {"status": "fresh" if _is_fresh(ads) else "done"}


@router.post("/ads/generate")
async def generate_ads(payload: dict, session: Session = Depends(get_session)):
    company_name = payload["company_name"]
    context = payload.get("context")

    # ground generation in the most recently scraped competitor ads on hand
    competitor_ads = session.exec(
        select(ScrapedAd).order_by(ScrapedAd.fetched_at.desc()).limit(settings.max_ads_per_source)
    ).all()
    competitor_ad_dicts = [
        {"source": ad.source, "headline": ad.headline, "body_text": ad.body_text}
        for ad in competitor_ads
    ]

    concepts = await openrouter.generate_ads(company_name, competitor_ad_dicts, context)

    generated: list[GeneratedAd] = []
    for concept in concepts:
        row = GeneratedAd(
            created_at=datetime.utcnow(),
            company_name=company_name,
            headline_variants=json.dumps(concept["headlines"]),
            description_variants=json.dumps(concept["descriptions"]),
            differentiation=concept["differentiation"],
            reasoning=concept["reasoning"],
            image_url=None,
            status="draft",
        )
        session.add(row)
        generated.append(row)
    session.commit()
    for row in generated:
        session.refresh(row)

    return {
        "ads": [
            {
                "id": row.id,
                "headlines": json.loads(row.headline_variants),
                "descriptions": json.loads(row.description_variants),
                "differentiation": row.differentiation,
                "reasoning": row.reasoning,
                "image_url": row.image_url,
            }
            for row in generated
        ]
    }


@router.post("/ads/{ad_id}/publish")
def publish_ad(ad_id: int):
    # Google Ads OAuth + publish flow is build order step 5 — not implemented yet.
    raise HTTPException(status_code=501, detail="Publish flow not implemented yet (build order step 5).")
