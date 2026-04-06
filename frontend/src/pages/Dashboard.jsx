import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  BriefcaseIcon,
  EnvelopeIcon,
  CheckCircleIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'

function userHasSkills(user) {
  if (!user?.skills || !Array.isArray(user.skills)) return false
  return user.skills.some((s) => s && String(s).trim().length > 0)
}

function userHasProfileIntro(user) {
  const bio = user?.bio != null ? String(user.bio).trim() : ''
  const summary = user?.summary != null ? String(user.summary).trim() : ''
  return Boolean(bio || summary)
}

/** Logged-in users see this until skills and at least a short bio or summary are filled in. */
function profileNeedsAttention(user) {
  if (!user) return false
  return !userHasSkills(user) || !userHasProfileIntro(user)
}

export default function Dashboard() {
  const { user } = useAuth()
  const [showBestMatches, setShowBestMatches] = useState(false)
  const showProfileReminder = profileNeedsAttention(user)

  useEffect(() => {
    if (!user) setShowBestMatches(false)
  }, [user])

  const { data: stats, isLoading: statsLoading, isError } = useQuery('dashboard-stats', async () => {
    const [statsRes, outreachRes] = await Promise.all([
      api.get('/projects/leads/dashboard-stats/'),
      api.get('/outreach/messages/'),
    ])
    const outreachList = Array.isArray(outreachRes.data)
      ? outreachRes.data
      : (outreachRes.data?.results || [])

    const { available = 0, matched = 0 } = statsRes.data || {}
    const sentMessages = outreachList.filter((m) => m.status === 'sent')

    return {
      available,
      matched,
      contacted: sentMessages.length,
    }
  })

  const {
    data: recentProjectsRaw,
    isLoading: projectsLoading,
    isError: projectsError,
    isFetching: projectsFetching,
  } = useQuery(
    ['dashboard-recent-projects', user?.id, showBestMatches],
    async () => {
      if (showBestMatches) {
        if (!user) return []
        const res = await api.get('/projects/leads/best-matches/', {
          params: { limit: 10 },
        })
        return Array.isArray(res.data) ? res.data : []
      }
      const res = await api.get('/projects/leads/available/', {
        params: { ordering: '-created_at' },
      })
      const list = Array.isArray(res.data) ? res.data : (res.data?.results || [])
      return list.slice(0, 10)
    },
    { enabled: Boolean(!showBestMatches || user), keepPreviousData: true }
  )

  const recentProjects = recentProjectsRaw ?? []
  const initialLoad =
    (statsLoading && stats === undefined) || (projectsLoading && recentProjectsRaw === undefined)

  if (initialLoad) {
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

      {user && showProfileReminder && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 shadow-sm">
          <div className="flex gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 shrink-0 text-amber-600" aria-hidden />
            <div className="min-w-0">
              <p className="text-sm font-medium text-amber-900">Complete your profile for better matches</p>
              <p className="mt-1 text-sm text-amber-800">
                {!userHasSkills(user) && (
                  <>
                    Add skills so we can rank projects against your experience.{' '}
                  </>
                )}
                {!userHasProfileIntro(user) && (
                  <>
                    Add a short bio or professional summary so your profile reflects how you work.{' '}
                  </>
                )}
                You can update everything in settings.
              </p>
              <Link
                to="/dashboard/settings"
                className="mt-2 inline-flex text-sm font-semibold text-amber-900 underline decoration-amber-600/60 hover:text-amber-950"
              >
                Open settings
              </Link>
            </div>
          </div>
        </div>
      )}

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

      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-4 border-b border-gray-200 flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center">
          <div>
            <h2 className="text-lg font-medium text-gray-900">
              {showBestMatches && user ? 'Best matches for you' : 'Scraped projects'}
            </h2>
            {showBestMatches && user && (
              <p className="mt-0.5 text-xs text-gray-500">
                Ranked by skills overlap with each listing (including related job categories), your plan priority, and
                project quality scores.
              </p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {user ? (
              <button
                type="button"
                role="switch"
                aria-checked={showBestMatches}
                onClick={() => setShowBestMatches((v) => !v)}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <span
                  className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
                    showBestMatches ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 translate-y-0.5 rounded-full bg-white shadow transition ${
                      showBestMatches ? 'translate-x-4' : 'translate-x-0.5'
                    }`}
                  />
                </span>
                Best matches
              </button>
            ) : null}
            <div className="flex items-center gap-2">
              {projectsFetching && !initialLoad && (
                <span className="text-xs text-gray-400 tabular-nums">Updating…</span>
              )}
              <Link
                to="/dashboard/projects/available"
                className="text-sm font-medium text-blue-600 hover:text-blue-800"
              >
                View all
              </Link>
            </div>
          </div>
        </div>
        {projectsError && (
          <div className="px-4 py-6 text-center text-sm text-red-600">
            Could not load projects. Try again or refresh the page.
          </div>
        )}
        {!projectsError && recentProjects.length > 0 && (
          <ul className="divide-y divide-gray-200">
            {recentProjects.map((project) => (
              <li key={project.id}>
                <Link
                  to={`/dashboard/projects/${project.id}`}
                  className="block hover:bg-gray-50 px-4 py-3 sm:px-6"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-blue-600 truncate">{project.title}</p>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                        {project.company_name && <span>{project.company_name}</span>}
                        <span>{project.source_platform_name}</span>
                        <span>{project.created_at ? format(new Date(project.created_at), 'MMM d, yyyy') : '—'}</span>
                        {typeof project.match_score === 'number' && (
                          <span className="inline-flex items-center rounded-full bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-800">
                            {Math.round(project.match_score * 100)}% match
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="ml-2 inline-flex shrink-0 px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {project.status}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
        {!projectsError && recentProjects.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-500 text-sm">
            No scraped projects yet. Run scraping from Dashboard → Scraping (or Settings) to add project leads.
          </div>
        )}
      </div>

      <div className="mt-8 overflow-hidden rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-sm">
        <div className="px-5 py-5 sm:px-6 sm:py-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <div className="inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-700 ring-1 ring-blue-100">
                <SparklesIcon className="h-4 w-4" aria-hidden />
                Unlock premium
              </div>
              <h2 className="mt-3 text-xl font-semibold tracking-tight text-slate-900">
                Want better priority in matching?
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Upgrade your plan to boost visibility and get surfaced earlier for incoming projects.
              </p>
            </div>
            <Link
              to="/dashboard/plans"
              className="inline-flex shrink-0 items-center justify-center rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              View plans
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
