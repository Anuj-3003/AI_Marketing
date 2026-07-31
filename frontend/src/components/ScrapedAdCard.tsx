import type { ScrapedAd } from '../api/types'

export function ScrapedAdCard({ ad }: { ad: ScrapedAd }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <span className="inline-block rounded bg-purple-100 px-2 py-0.5 text-xs font-medium uppercase tracking-wide text-purple-700 dark:bg-purple-900/40 dark:text-purple-300">
        {ad.source}
      </span>
      {ad.headline && (
        <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">{ad.headline}</p>
      )}
      {ad.body_text && (
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{ad.body_text}</p>
      )}
      {ad.landing_url && (
        <a
          href={ad.landing_url}
          target="_blank"
          rel="noreferrer"
          className="mt-2 inline-block text-sm text-purple-600 hover:underline dark:text-purple-400"
        >
          View ad ↗
        </a>
      )}
      {ad.first_seen && (
        <p className="mt-2 text-xs text-gray-400">First seen {ad.first_seen}</p>
      )}
    </div>
  )
}
