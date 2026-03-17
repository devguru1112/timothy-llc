import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { format } from 'date-fns'
import { ArrowPathIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'

const statusColors = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export default function Scraping() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [runLimit, setRunLimit] = useState(100)

  const { data, isLoading, error, refetch } = useQuery(
    'scraping-jobs',
    async () => {
      const res = await api.get('/scrapers/jobs/')
      return res.data
    },
    { enabled: !!user?.is_superuser }
  )

  const { data: schedule } = useQuery(
    'scraping-schedule',
    async () => {
      const res = await api.get('/scrapers/schedule/')
      return res.data
    },
    { enabled: !!user?.is_superuser }
  )

  useEffect(() => {
    if (schedule?.limit != null) setRunLimit(schedule.limit)
  }, [schedule])

  const scrapeNowMutation = useMutation(
    () => api.post('/scrapers/jobs/scrape_all/', { limit: runLimit }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('scraping-jobs')
      },
    }
  )

  const jobs = data?.results ?? (Array.isArray(data) ? data : [])
  const hasRunning = jobs.some((j) => j.status === 'running')

  // Auto-refresh while any job is running
  useEffect(() => {
    if (!hasRunning) return
    const interval = setInterval(() => refetch(), 3000)
    return () => clearInterval(interval)
  }, [hasRunning, refetch])

  if (!user?.is_superuser) {
    return (
      <div className="text-center py-12 text-gray-600">
        You need admin access to view the scraping process.
      </div>
    )
  }
  if (isLoading) return <div className="text-center py-12">Loading scraping jobs...</div>
  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        {error.response?.status === 403
          ? 'You need admin access to view scraping.'
          : 'Error loading scraping jobs.'}
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scraping</h1>
          <p className="mt-2 text-sm text-gray-600">
            View scraping job history and run scraping now. Jobs run in the background.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-700">
            Limit per platform:
            <input
              type="number"
              min={1}
              max={500}
              value={runLimit}
              onChange={(e) => setRunLimit(Number(e.target.value) || 50)}
              className="ml-2 w-20 rounded border border-gray-300 px-2 py-1 text-sm"
            />
          </label>
          <button
          type="button"
          onClick={() => scrapeNowMutation.mutate()}
          disabled={scrapeNowMutation.isLoading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <ArrowPathIcon
            className={`-ml-1 mr-2 h-5 w-5 ${scrapeNowMutation.isLoading ? 'animate-spin' : ''}`}
            aria-hidden="true"
          />
          {scrapeNowMutation.isLoading ? 'Starting…' : 'Run scraping now'}
        </button>
        </div>
      </div>

      <p className="mb-4 text-xs text-gray-500">
        &quot;Added&quot; can be lower than &quot;Found&quot;: duplicates are skipped, and if you use Scraping categories in Django Admin, only projects matching those categories are added. Increase the limit above to fetch more per platform (max 500).
      </p>

      {scrapeNowMutation.isSuccess && (
        <div className="mb-4 p-3 rounded-md bg-green-50 text-green-800 text-sm">
          Scraping started in the background. The list below will update as jobs run.
        </div>
      )}
      {scrapeNowMutation.isError && (
        <div className="mb-4 p-3 rounded-md bg-red-50 text-red-800 text-sm">
          {scrapeNowMutation.error?.response?.data?.error ||
            scrapeNowMutation.error?.response?.data?.detail ||
            'Failed to start scraping'}
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900">Recent scraping jobs</h2>
          <button
            type="button"
            onClick={() => refetch()}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Platform
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                  Found
                </th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                  Added
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Started
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Completed
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Error
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    No scraping jobs yet. Click &quot;Run scraping now&quot; to start.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {job.platform?.name ?? '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          statusColors[job.status] ?? 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">
                      {job.projects_found ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">
                      {job.projects_added ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {job.started_at
                        ? format(new Date(job.started_at), 'MMM d, HH:mm')
                        : '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {job.completed_at
                        ? format(new Date(job.completed_at), 'MMM d, HH:mm')
                        : '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-red-600 max-w-xs truncate" title={job.error_message}>
                      {job.error_message || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
