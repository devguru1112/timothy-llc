import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { format } from 'date-fns'

export default function Projects() {
  const { data, isLoading, error } = useQuery('projects', async () => {
    const response = await api.get('/api/projects/leads/')
    return response.data
  })

  if (isLoading) return <div className="text-center py-12">Loading projects...</div>
  if (error) return <div className="text-center py-12 text-red-600">Error loading projects</div>

  const projects = data?.results || []

  const getStatusColor = (status) => {
    const colors = {
      new: 'bg-gray-100 text-gray-800',
      qualified: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      matched: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="mt-2 text-sm text-gray-600">
            Browse and manage project opportunities
          </p>
        </div>
        <Link
          to="/projects/available"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          View Available
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {projects.map((project) => (
            <li key={project.id}>
              <Link
                to={`/projects/${project.id}`}
                className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-blue-600 truncate">
                        {project.title}
                      </p>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          project.status
                        )}`}
                      >
                        {project.status}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <p className="truncate">{project.description?.substring(0, 150)}...</p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span>{project.source_platform_name}</span>
                      {project.budget_min && (
                        <span className="ml-4">
                          ${project.budget_min} - ${project.budget_max || 'N/A'}
                        </span>
                      )}
                      <span className="ml-4">
                        {format(new Date(project.scraped_at), 'MMM d, yyyy')}
                      </span>
                    </div>
                  </div>
                  <div className="ml-5 flex-shrink-0">
                    <div className="text-sm text-gray-500">
                      Score: {(project.relevance_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
