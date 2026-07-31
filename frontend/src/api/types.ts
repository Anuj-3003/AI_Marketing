export interface Competitor {
  id: number
  name: string
  domain: string | null
  logo_url: string | null
}

export interface LookupResponse {
  resolved_name: string
  competitors: Competitor[]
}

export interface ScrapedAd {
  id: number
  source: string
  headline: string | null
  body_text: string | null
  image_url: string | null
  landing_url: string | null
  first_seen: string | null
  fetched_at: string
}

export interface CompetitorAdsResponse {
  competitor: { id: number; name: string; domain: string | null }
  ads: ScrapedAd[]
  status: 'fresh' | 'refreshing'
}

export interface GeneratedAdConcept {
  id: number
  headlines: string[]
  descriptions: string[]
  differentiation: string
  reasoning: string
  image_url: string | null
}

export interface GenerateAdsResponse {
  ads: GeneratedAdConcept[]
}

export interface PublishResponse {
  campaign_id: number
  status: string
}

export interface AnalyticsResponse {
  impressions: number
  clicks: number
  cost: number
  ctr: number
  date_range: string
}
