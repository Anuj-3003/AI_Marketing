import { useMutation, useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type {
  AnalyticsResponse,
  CompetitorAdsResponse,
  GenerateAdsResponse,
  LookupResponse,
  PublishResponse,
} from './types'

export function useCompanyLookup() {
  return useMutation({
    mutationFn: (companyName: string) =>
      apiFetch<LookupResponse>('/api/companies/lookup', {
        method: 'POST',
        body: JSON.stringify({ company_name: companyName }),
      }),
  })
}

export function useCompetitorAds(competitorId: number | undefined) {
  return useQuery({
    queryKey: ['competitor-ads', competitorId],
    queryFn: () => apiFetch<CompetitorAdsResponse>(`/api/competitors/${competitorId}/ads`),
    enabled: competitorId !== undefined,
    refetchInterval: (query) => (query.state.data?.status === 'refreshing' ? 2000 : false),
  })
}

export function useGenerateAds() {
  return useMutation({
    mutationFn: ({ companyName, context }: { companyName: string; context?: string }) =>
      apiFetch<GenerateAdsResponse>('/api/ads/generate', {
        method: 'POST',
        body: JSON.stringify({ company_name: companyName, context }),
      }),
  })
}

export function usePublishAd() {
  return useMutation({
    mutationFn: (adId: number) =>
      apiFetch<PublishResponse>(`/api/ads/${adId}/publish`, { method: 'POST' }),
  })
}

export function useCampaignAnalytics(campaignId: number | undefined) {
  return useQuery({
    queryKey: ['campaign-analytics', campaignId],
    queryFn: () => apiFetch<AnalyticsResponse>(`/api/campaigns/${campaignId}/analytics`),
    enabled: campaignId !== undefined,
    retry: false,
  })
}
