import { useCampaignAnalytics } from '../api/hooks'
import { ApiError } from '../api/client'

export function AnalyticsPanel({ campaignId }: { campaignId: number }) {
  const { data, isLoading, isError, error } = useCampaignAnalytics(campaignId)

  if (isLoading) return <p className="text-sm text-gray-500">Loading analytics…</p>

  if (isError) {
    const notImplemented = error instanceof ApiError && error.status === 501
    return (
      <p className="text-sm text-amber-600 dark:text-amber-400">
        {notImplemented
          ? 'Analytics aren’t wired up yet — the GAQL dashboard is a later build step.'
          : 'Failed to load analytics.'}
      </p>
    )
  }

  if (!data) return null

  const stats = [
    { label: 'Impressions', value: data.impressions.toLocaleString() },
    { label: 'Clicks', value: data.clicks.toLocaleString() },
    { label: 'Cost', value: `$${data.cost.toFixed(2)}` },
    { label: 'CTR', value: `${(data.ctr * 100).toFixed(2)}%` },
  ]

  return (
    <div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg border border-gray-200 p-4 text-left dark:border-gray-700">
            <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              {stat.label}
            </p>
            <p className="mt-1 text-xl font-semibold text-gray-900 dark:text-gray-100">
              {stat.value}
            </p>
          </div>
        ))}
      </div>
      <p className="mt-2 text-xs text-gray-400">{data.date_range}</p>
    </div>
  )
}
