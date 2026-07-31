import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCompanyLookup } from '../api/hooks'
import { CompetitorCard } from '../components/CompetitorCard'
import { ApiError } from '../api/client'

export function Home() {
  const [companyName, setCompanyName] = useState('')
  const lookup = useCompanyLookup()

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
        Competitor Ad Intelligence
      </h1>
      <p className="mt-1 text-gray-500 dark:text-gray-400">
        Enter a company name to find its competitors and see what ads they're running.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (companyName.trim()) lookup.mutate(companyName.trim())
        }}
        className="mt-6 flex gap-2"
      >
        <input
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g. Notion"
          className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900"
        />
        <button
          type="submit"
          disabled={lookup.isPending || !companyName.trim()}
          className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700 disabled:opacity-50"
        >
          {lookup.isPending ? 'Searching…' : 'Find competitors'}
        </button>
      </form>

      {lookup.isError && (
        <p className="mt-4 text-sm text-red-600">
          {lookup.error instanceof ApiError ? lookup.error.message : 'Lookup failed.'}
        </p>
      )}

      {lookup.isSuccess && (
        <div className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Competitors of {lookup.data.resolved_name}
            </h2>
            <Link
              to="/ads/generate"
              state={{ companyName: lookup.data.resolved_name }}
              className="text-sm text-purple-600 hover:underline dark:text-purple-400"
            >
              Generate ads for {lookup.data.resolved_name} →
            </Link>
          </div>
          <div className="mt-4 space-y-3">
            {lookup.data.competitors.map((competitor) => (
              <CompetitorCard
                key={competitor.id}
                competitor={competitor}
                companyName={lookup.data.resolved_name}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
