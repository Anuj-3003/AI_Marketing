from datetime import date, datetime

from sqlmodel import Field, SQLModel


class ScrapedAd(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    competitor_id: int = Field(foreign_key="competitor.id")
    source: str  # meta | google_transparency | tiktok | linkedin
    headline: str | None = None
    body_text: str | None = None
    image_url: str | None = None
    landing_url: str | None = None
    first_seen: date | None = None
    fetched_at: datetime


class GeneratedAd(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    company_name: str
    headline_variants: str  # JSON-encoded list
    description_variants: str  # JSON-encoded list
    differentiation: str  # what makes this company stand out vs. competitor ads shown to the model
    reasoning: str  # why this ad angle should work
    image_url: str | None = None
    status: str = "draft"  # draft | published
