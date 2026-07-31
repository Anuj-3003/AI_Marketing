import { Link, useLocation, useParams } from 'react-router-dom'
import { useCompetitorAds } from '../api/hooks'
import { ScrapedAdCard } from '../components/ScrapedAdCard'

export function CompetitorAds() {
  const { id } = useParams<{ id: string }>()
  const competitorId = id ? Number(id) : undefined
  const location = useLocation()
  const companyName = (location.state as { companyName?: string } | null)?.companyName

  const { data, isLoading, isError } = useCompetitorAds(competitorId)

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <Link to="/" className="text-sm text-purple-600 hover:underline dark:text-purple-400">
        ← Back
      </Link>

      <div className="mt-2 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {data ? `${data.competitor.name} — ads (Meta)` : 'Competitor ads (Meta)'}
          </h1>
          {data?.competitor.domain && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{data.competitor.domain}</p>
          )}
        </div>
        {companyName && (
          <Link
            to="/ads/generate"
            state={{ companyName }}
            className="text-sm text-purple-600 hover:underline dark:text-purple-400"
          >
            Generate ads for {companyName} →
          </Link>
        )}
      </div>

      {data?.status === 'refreshing' && (
        <p className="mt-2 text-sm text-gray-500">Refreshing latest ads…</p>
      )}

      {isLoading && <p className="mt-4 text-sm text-gray-500">Loading ads…</p>}
      {isError && <p className="mt-4 text-sm text-red-600">Failed to load ads.</p>}

      {data && data.ads.length === 0 && data.status !== 'refreshing' && (
        <p className="mt-4 text-sm text-gray-500">No ads found for this competitor yet.</p>
      )}

      <div className="mt-4 space-y-3">
        {data?.ads.map((ad) => <ScrapedAdCard key={ad.id} ad={ad} />)}
      </div>
    </div>
  )
}
