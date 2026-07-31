import { Link } from 'react-router-dom'
import type { Competitor } from '../api/types'

export function CompetitorCard({
  competitor,
  companyName,
}: {
  competitor: Competitor
  companyName?: string
}) {
  return (
    <Link
      to={`/competitors/${competitor.id}/ads`}
      state={companyName ? { companyName } : undefined}
      className="flex items-center gap-3 rounded-lg border border-gray-200 p-4 transition hover:border-purple-400 hover:shadow-sm dark:border-gray-700 dark:hover:border-purple-500"
    >
      {competitor.logo_url ? (
        <img src={competitor.logo_url} alt="" className="h-10 w-10 rounded object-contain" />
      ) : (
        <div className="flex h-10 w-10 items-center justify-center rounded bg-gray-100 text-sm font-medium text-gray-500 dark:bg-gray-800">
          {competitor.name.slice(0, 1).toUpperCase()}
        </div>
      )}
      <div className="text-left">
        <p className="font-medium text-gray-900 dark:text-gray-100">{competitor.name}</p>
        {competitor.domain && (
          <p className="text-sm text-gray-500 dark:text-gray-400">{competitor.domain}</p>
        )}
      </div>
    </Link>
  )
}
