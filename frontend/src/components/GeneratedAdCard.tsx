import type { GeneratedAdConcept } from '../api/types'
import { PublishButton } from './PublishButton'

export function GeneratedAdCard({ ad }: { ad: GeneratedAdConcept }) {
  return (
    <div className="rounded-lg border border-gray-200 p-5 dark:border-gray-700">
      <div className="space-y-1">
        {ad.headlines.map((headline, i) => (
          <p key={i} className="font-medium text-gray-900 dark:text-gray-100">
            {headline}
          </p>
        ))}
      </div>

      <div className="mt-2 space-y-1">
        {ad.descriptions.map((description, i) => (
          <p key={i} className="text-sm text-gray-600 dark:text-gray-400">
            {description}
          </p>
        ))}
      </div>

      <div className="mt-4 rounded-md bg-gray-50 p-3 dark:bg-gray-800/50">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          What makes this stand out
        </p>
        <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{ad.differentiation}</p>
      </div>

      <div className="mt-3 rounded-md bg-gray-50 p-3 dark:bg-gray-800/50">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Why this should work
        </p>
        <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{ad.reasoning}</p>
      </div>

      <div className="mt-4">
        <PublishButton adId={ad.id} />
      </div>
    </div>
  )
}
