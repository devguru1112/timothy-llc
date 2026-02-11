import { useQuery } from 'react-query'
import api from '../services/api'
import { Link } from 'react-router-dom'
import { BriefcaseIcon, EnvelopeIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery('dashboard-stats', async () => {
    const [projects, outreach] = await Promise.all([
      api.get('/projects/leads/'),
      api.get('/outreach/messages/'),
    ])
    
    const availableProjects = projects.data.results?.filter(
      (p) => p.status === 'qualified' && !p.matched_user_username
    ) || []
    
    const myProjects = projects.data.results?.filter(
      (p) => p.matched_user_username
    ) || []
    
    const sentMessages = outreach.data.results?.filter(
      (m) => m.status === 'sent'
    ) || []

    return {
      available: availableProjects.length,
      matched: myProjects.length,
      contacted: sentMessages.length,
    }
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
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
                to="/projects"
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
                to="/projects"
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
    </div>
  )
}
