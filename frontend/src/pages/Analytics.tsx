import { Link, useParams } from 'react-router-dom'
import { AnalyticsPanel } from '../components/AnalyticsPanel'

export function Analytics() {
  const { id } = useParams<{ id: string }>()
  const campaignId = id ? Number(id) : undefined

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <Link to="/" className="text-sm text-purple-600 hover:underline dark:text-purple-400">
        ← Back
      </Link>
      <h1 className="mt-2 text-xl font-semibold text-gray-900 dark:text-gray-100">
        Campaign analytics
      </h1>
      <div className="mt-6">{campaignId && <AnalyticsPanel campaignId={campaignId} />}</div>
    </div>
  )
}
