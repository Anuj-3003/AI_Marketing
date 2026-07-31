import { usePublishAd } from '../api/hooks'
import { ApiError } from '../api/client'

export function PublishButton({ adId }: { adId: number }) {
  const publish = usePublishAd()

  return (
    <div>
      <button
        type="button"
        onClick={() => publish.mutate(adId)}
        disabled={publish.isPending}
        className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700 disabled:opacity-50"
      >
        {publish.isPending ? 'Publishing…' : 'Publish to Google Ads'}
      </button>
      {publish.isError && (
        <p className="mt-2 text-sm text-amber-600 dark:text-amber-400">
          {publish.error instanceof ApiError && publish.error.status === 501
            ? 'Publishing isn’t wired up yet — Google Ads OAuth is a later build step.'
            : 'Publish failed. Please try again.'}
        </p>
      )}
      {publish.isSuccess && (
        <p className="mt-2 text-sm text-green-600 dark:text-green-400">
          Published — campaign #{publish.data.campaign_id}
        </p>
      )}
    </div>
  )
}
