from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("/{campaign_id}/analytics")
def get_campaign_analytics(campaign_id: int):
    # GAQL-backed analytics dashboard is build order step 6 — not implemented yet.
    raise HTTPException(status_code=501, detail="Analytics not implemented yet (build order step 6).")
