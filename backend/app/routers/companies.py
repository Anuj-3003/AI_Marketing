from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.models import CompanyLookup, Competitor
from app.services import openrouter

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.post("/lookup")
async def lookup_company(payload: dict, session: Session = Depends(get_session)):
    company_name = payload["company_name"]

    result = await openrouter.get_competitors(company_name)

    lookup = CompanyLookup(
        query_name=company_name,
        resolved_name=result["resolved_name"],
        created_at=datetime.utcnow(),
    )
    session.add(lookup)
    session.commit()
    session.refresh(lookup)

    competitors: list[Competitor] = []
    for c in result["competitors"]:
        competitor = Competitor(
            company_lookup_id=lookup.id,
            name=c["name"],
            domain=c.get("domain"),
            logo_url=c.get("logo_url"),
        )
        session.add(competitor)
        competitors.append(competitor)
    session.commit()
    for competitor in competitors:
        session.refresh(competitor)

    return {
        "resolved_name": lookup.resolved_name,
        "competitors": [
            {
                "id": c.id,
                "name": c.name,
                "domain": c.domain,
                "logo_url": c.logo_url,
            }
            for c in competitors
        ],
    }
