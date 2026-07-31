import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useGenerateAds } from '../api/hooks'
import { GeneratedAdCard } from '../components/GeneratedAdCard'
import { ApiError } from '../api/client'

export function GeneratedAds() {
  const location = useLocation()
  const initialCompanyName = (location.state as { companyName?: string } | null)?.companyName ?? ''

  const [companyName, setCompanyName] = useState(initialCompanyName)
  const [context, setContext] = useState('')
  const generate = useGenerateAds()

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <Link to="/" className="text-sm text-purple-600 hover:underline dark:text-purple-400">
        ← Back
      </Link>

      <h1 className="mt-2 text-xl font-semibold text-gray-900 dark:text-gray-100">
        Generate ad concepts
      </h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Grounded in the competitor ads already scraped for this company.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (companyName.trim()) {
            generate.mutate({ companyName: companyName.trim(), context: context.trim() || undefined })
          }
        }}
        className="mt-6 space-y-3"
      >
        <input
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="Company name"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900"
        />
        <textarea
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Optional extra context (positioning, target audience, offer, etc.)"
          rows={3}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900"
        />
        <button
          type="submit"
          disabled={generate.isPending || !companyName.trim()}
          className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700 disabled:opacity-50"
        >
          {generate.isPending ? 'Generating…' : 'Generate 3 ad concepts'}
        </button>
      </form>

      {generate.isError && (
        <p className="mt-4 text-sm text-red-600">
          {generate.error instanceof ApiError ? generate.error.message : 'Generation failed.'}
        </p>
      )}

      {generate.isSuccess && (
        <div className="mt-8 space-y-4">
          {generate.data.ads.map((ad) => (
            <GeneratedAdCard key={ad.id} ad={ad} />
          ))}
        </div>
      )}
    </div>
  )
}
