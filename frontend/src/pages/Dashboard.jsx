import { useQuery } from 'react-query'
import api from '../services/api'
import { Link } from 'react-router-dom'
import { BriefcaseIcon, EnvelopeIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { format } from 'date-fns'

export default function Dashboard() {
  const { data: stats, isLoading, isError } = useQuery('dashboard-stats', async () => {
    const [statsRes, availableRes, outreachRes] = await Promise.all([
      api.get('/projects/leads/dashboard-stats/'),
      api.get('/projects/leads/available/', {
        params: { ordering: '-created_at' },
      }),
      api.get('/outreach/messages/'),
    ])
    const scrapedProjects = Array.isArray(availableRes.data)
      ? availableRes.data
      : (availableRes.data?.results || [])
    const outreachList = Array.isArray(outreachRes.data)
      ? outreachRes.data
      : (outreachRes.data?.results || [])

    const { available = 0, matched = 0 } = statsRes.data || {}
    const sentMessages = outreachList.filter((m) => m.status === 'sent')

    return {
      available,
      matched,
      contacted: sentMessages.length,
      scrapedProjects,
    }
  })

  const recentScraped = (stats?.scrapedProjects || []).slice(0, 10)

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (isError) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-red-600">Unable to load dashboard data. You may need to log in again.</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Overview of your project matching activity
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BriefcaseIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Available Projects
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats?.available || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link
                to="/dashboard/projects"
                className="font-medium text-blue-700 hover:text-blue-900"
              >
                View all projects
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Matched Projects
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats?.matched || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link
                to="/dashboard/projects"
                className="font-medium text-blue-700 hover:text-blue-900"
              >
                View my projects
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <EnvelopeIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Outreach Sent
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats?.contacted || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link
                to="/outreach"
                className="font-medium text-blue-700 hover:text-blue-900"
              >
                View outreach
              </Link>
            </div>
          </div>
        </div>
      </div>

      {recentScraped.length > 0 && (
        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Scraped projects</h2>
            <Link
              to="/dashboard/projects/available"
              className="text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              View all
            </Link>
          </div>
          <ul className="divide-y divide-gray-200">
            {recentScraped.map((project) => (
              <li key={project.id}>
                <Link
                  to={`/dashboard/projects/${project.id}`}
                  className="block hover:bg-gray-50 px-4 py-3 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-blue-600 truncate">{project.title}</p>
                      <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                        {project.company_name && <span>{project.company_name}</span>}
                        <span>{project.source_platform_name}</span>
                        <span>{project.created_at ? format(new Date(project.created_at), 'MMM d, yyyy') : '—'}</span>
                      </div>
                    </div>
                    <span className="ml-2 inline-flex px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {project.status}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
      {recentScraped.length === 0 && (
        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Scraped projects</h2>
          </div>
          <div className="px-4 py-8 text-center text-gray-500 text-sm">
            No scraped projects yet. Run scraping from Dashboard → Scraping (or Settings) to add project leads.
          </div>
        </div>
      )}
    </div>
  )
}
