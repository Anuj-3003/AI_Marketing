# Competitor Ad Intelligence — Project Plan

## 1. Overview

A single-user demo web app with three core flows:
1. Enter a company name → get 3 competitors.
2. Click a competitor → see all ads they're running (Meta only for this demo — Google/TikTok/LinkedIn scoped but disabled, see section 4).
3. Generate 3 original ad concepts → publish to Google Ads → view analytics.

**Scope**: single-user demo, local-only (docker-compose), monorepo.

---

## 2. Tech Stack (finalized)

| Layer | Choice | Notes |
|---|---|---|
| Backend framework | FastAPI | async, auto OpenAPI schema |
| ORM | SQLModel | Pydantic + SQLAlchemy in one; models double as API schemas |
| Database | SQLite | zero-setup; swappable to Postgres later via connection string only |
| Background jobs | FastAPI `BackgroundTasks` | no Celery/Redis needed at this scale |
| Scraping | Playwright | needed for Google Transparency Center (JS-rendered SPA) |
| Frontend | React + Vite | plain SPA, no SSR needed |
| Styling | Tailwind CSS | |
| Data fetching | TanStack Query | handles cache/poll/refresh pattern naturally |
| LLM/image access | OpenRouter (single API key) | see model matrix below |
| Repo structure | Monorepo | `backend/` + `frontend/` in one repo |
| Deployment | Local only | docker-compose, run on your machine |
| Google Ads credentials | `.env` only | single refresh token, no DB row (single-user) |

---

## 3. Model Matrix (OpenRouter)

| Task | Model | Why |
|---|---|---|
| Competitor discovery | `perplexity/sonar-pro` | built-in web search + citations, cheaper than reasoning-tier Sonar |
| Ad copy generation | `openai/gpt-5` | swapped from Claude Sonnet — this OpenRouter account's allowed-providers setting rejects every Claude-serving provider (Anthropic, Vertex, Bedrock, Azure); OpenAI is allowed and is the next-best default for creative/marketing copy. Swap back to Claude by changing `OPENROUTER_COPY_MODEL` once the account's provider allowlist is updated at openrouter.ai/settings/preferences |
| Ad image generation | `google/gemini-2.5-flash-image` (Nano Banana) | fast, cheap, via OpenRouter's unified Image API |

All three go through the same OpenRouter key — one client wrapper (`app/services/openrouter.py`) with per-task model config, so swapping any model later is a one-line change (`config.py` / `.env`).

**Structured output**: use `response_format: {"type": "json_schema", "json_schema": {...}}`, not `json_object` — Perplexity's OpenRouter route rejects `json_object` outright, and `json_schema` is honored by both Perplexity and OpenAI here.

**Ad copy generation prompt** is given the scraped competitor ads (headlines/body text) as context and, for each of the 3 concepts, must return alongside the copy:
- `differentiation`: what makes this company better/stand out vs. the competitor ads it was shown (concrete, not generic — grounded in the actual competitor copy pulled in step 2/3)
- `reasoning`: why this specific angle/hook should work (the persuasion logic — pain point targeted, positioning gap it exploits, etc.)

---

## 4. Ad Data Sources

| Source | Access | Notes | Status (this demo) |
|---|---|---|---|
| Meta Ad Library | Adyntel API (paid, third-party) | proxies Meta's ad archive — sidesteps needing Meta's own Ad Library API access (identity verification at facebook.com/ads/library/api), which a normal dev token can't get past (error_subcode 2332002) | **Active** — `ADYNTEL_API_KEY` + `ADYNTEL_EMAIL` in `.env`; domain-based lookup preferred (richer creative data), falls back to keyword search on company name |
| Google Ads Transparency Center | No official API — Playwright scrape | isolate as its own module; page layout may change over time | Commented out — future work |
| TikTok Commercial Content Library | Official API (free) | included as third source | Commented out — future work |
| LinkedIn Ad Library | No official API — Playwright scrape | key for B2B competitors; isolate as its own module like the Google scraper, same layout-drift risk | Commented out — future work |

Only Meta is wired up for this demo — the other three services are scaffolded as stub modules with their logic commented out, so enabling them later is a matter of uncommenting + adding credentials, not rewriting.

**Scrape/fetch limit**: each source fetch is capped at `MAX_ADS_PER_SOURCE` (env var, default `25`) most-recent ads per competitor. Bounds scrape/API time, DB size, and the LLM context window when these ads are later fed into ad generation. Applied at the service layer before rows are written to `ScrapedAd`.

**Normalized schema** (all sources map to this before hitting the frontend):
```
{
  source: "meta" | "google_transparency" | "tiktok" | "linkedin",
  advertiser: str,
  headline: str | null,
  body_text: str | null,
  image_url: str | null,
  landing_url: str | null,
  first_seen: date | null,
  fetched_at: datetime
}
```

Caching: store scraped ads with a `fetched_at` timestamp; serve cache if <24h old, otherwise kick off a background refresh (`BackgroundTasks`) and serve stale data immediately (stale-while-revalidate), never block the request on a live scrape.

---

## 5. Data Model (SQLModel)

```python
class CompanyLookup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query_name: str
    resolved_name: str
    created_at: datetime

class Competitor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_lookup_id: int = Field(foreign_key="companylookup.id")
    name: str
    domain: str | None
    logo_url: str | None

class ScrapedAd(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    competitor_id: int = Field(foreign_key="competitor.id")
    source: str  # meta | google_transparency | tiktok | linkedin
    headline: str | None
    body_text: str | None
    image_url: str | None
    landing_url: str | None
    first_seen: date | None
    fetched_at: datetime

class GeneratedAd(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    company_name: str
    headline_variants: str  # JSON-encoded list
    description_variants: str  # JSON-encoded list
    differentiation: str  # what makes this company stand out vs. competitor ads shown to the model
    reasoning: str  # why this ad angle should work
    image_url: str | None
    status: str  # draft | published

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
```

### 5a. Postgres DDL (reference — for the eventual SQLite → Postgres swap)

Types are chosen to match what SQLAlchemy already emits for the SQLModel classes above (e.g. `headline_variants`/`description_variants` stay `TEXT` holding JSON-encoded strings, not `JSONB`), so the swap really is connection-string-only — no model or app-layer code changes.

```sql
CREATE TABLE companylookup (
    id              BIGSERIAL PRIMARY KEY,
    query_name      TEXT NOT NULL,
    resolved_name   TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
);

CREATE TABLE competitor (
    id                  BIGSERIAL PRIMARY KEY,
    company_lookup_id   BIGINT NOT NULL REFERENCES companylookup(id),
    name                TEXT NOT NULL,
    domain              TEXT,
    logo_url            TEXT
);

CREATE TABLE scrapedad (
    id              BIGSERIAL PRIMARY KEY,
    competitor_id   BIGINT NOT NULL REFERENCES competitor(id),
    source          TEXT NOT NULL CHECK (source IN ('meta', 'google_transparency', 'tiktok', 'linkedin')),
    headline        TEXT,
    body_text       TEXT,
    image_url       TEXT,
    landing_url     TEXT,
    first_seen      DATE,
    fetched_at      TIMESTAMPTZ NOT NULL
);

CREATE TABLE generatedad (
    id                      BIGSERIAL PRIMARY KEY,
    created_at              TIMESTAMPTZ NOT NULL,
    company_name            TEXT NOT NULL,
    headline_variants       TEXT NOT NULL,   -- JSON-encoded list
    description_variants    TEXT NOT NULL,   -- JSON-encoded list
    differentiation         TEXT NOT NULL,
    reasoning               TEXT NOT NULL,
    image_url               TEXT,
    status                  TEXT NOT NULL CHECK (status IN ('draft', 'published'))
);

CREATE TABLE campaign (
    id                  BIGSERIAL PRIMARY KEY,
    generated_ad_id     BIGINT NOT NULL REFERENCES generatedad(id),
    google_campaign_id  TEXT NOT NULL,
    google_ad_group_id  TEXT NOT NULL,
    google_ad_id        TEXT NOT NULL,
    budget_amount       NUMERIC(10, 2) NOT NULL,
    status              TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL
);

CREATE TABLE analyticssnapshot (
    id              BIGSERIAL PRIMARY KEY,
    campaign_id     BIGINT NOT NULL REFERENCES campaign(id),
    date            DATE NOT NULL,
    impressions     BIGINT NOT NULL,
    clicks          BIGINT NOT NULL,
    cost_micros     BIGINT NOT NULL,
    ctr             DOUBLE PRECISION NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_competitor_company_lookup_id ON competitor(company_lookup_id);
CREATE INDEX idx_scrapedad_competitor_id ON scrapedad(competitor_id);
CREATE INDEX idx_campaign_generated_ad_id ON campaign(generated_ad_id);
CREATE INDEX idx_analyticssnapshot_campaign_id ON analyticssnapshot(campaign_id);
```

---

## 6. API Contracts

```
POST /api/companies/lookup
  body: { company_name: str }
  → { resolved_name: str, competitors: [{ id, name, domain, logo_url }] }

GET  /api/competitors/{id}/ads
  → { ads: [...], status: "fresh" | "refreshing" }

GET  /api/competitors/{id}/ads/status
  → { status: "fresh" | "refreshing" | "done" }

POST /api/ads/generate
  body: { company_name: str, context?: str }
  → { ads: [ { id, headlines: [str], descriptions: [str], differentiation: str, reasoning: str, image_url? } x3 ] }

POST /api/ads/{id}/publish
  → { campaign_id: int, status: str }

GET  /api/campaigns/{id}/analytics
  → { impressions, clicks, cost, ctr, date_range }
```

---

## 7. Folder Structure (monorepo)

```
/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/            # SQLModel tables
│   │   ├── routers/           # companies, ads, campaigns
│   │   ├── services/
│   │   │   ├── openrouter.py       # unified LLM/image client
│   │   │   ├── meta_ad_library.py                  # active for this demo
│   │   │   ├── google_transparency_scraper.py      # Playwright — commented out, future work
│   │   │   ├── tiktok_ad_library.py                # commented out, future work
│   │   │   ├── linkedin_ad_library_scraper.py      # Playwright — commented out, future work
│   │   │   └── google_ads_client.py            # OAuth, publish, GAQL
│   │   ├── db.py
│   │   └── config.py          # Pydantic BaseSettings, reads .env
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/              # Home, CompetitorAds, GeneratedAds, Analytics
│   │   ├── components/         # AdCard, CompetitorCard, PublishButton, AnalyticsPanel
│   │   ├── api/                 # TanStack Query hooks
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── PROJECT_PLAN.md
```

---

## 8. Google Ads Integration

- OAuth done once (single-user), refresh token stored in `.env`.
- Publish flow creates: Campaign Budget → Campaign → Ad Group → Responsive Search Ad.
- Analytics pulled via GAQL queries.
- **Test vs. real ad account**: deferred — will decide when we reach this step. Leaning real (per earlier discussion) since test accounts never produce real analytics data.

---

## 9. Build Order

1. Competitor lookup (Sonar Pro) — read-only, validates the LLM integration first
2. Meta Ad Library + TikTok integration (official APIs, easiest wins)
3. Google Transparency + LinkedIn Ad Library Playwright scrapers (isolated modules, riskiest part — no official APIs, layout drift risk)
4. Ad copy generation (Claude) + optional image gen (Nano Banana)
5. Google Ads OAuth + publish flow
6. Analytics dashboard (GAQL)
7. Polish: caching, error/edge-case handling, empty states
