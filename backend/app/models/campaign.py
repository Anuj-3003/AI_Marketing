from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Campaign(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    generated_ad_id: int = Field(foreign_key="generatedad.id")
    google_campaign_id: str
    google_ad_group_id: str
    google_ad_id: str
    budget_amount: float
    status: str
    created_at: datetime


class AnalyticsSnapshot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    date: date
    impressions: int
    clicks: int
    cost_micros: int
    ctr: float
    fetched_at: datetime
