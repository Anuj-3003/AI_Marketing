from datetime import datetime

from sqlmodel import Field, SQLModel


class CompanyLookup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query_name: str
    resolved_name: str
    created_at: datetime


class Competitor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_lookup_id: int = Field(foreign_key="companylookup.id")
    name: str
    domain: str | None = None
    logo_url: str | None = None
