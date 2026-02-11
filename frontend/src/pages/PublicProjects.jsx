import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { format } from 'date-fns'

export default function PublicProjects() {
  const { data, isLoading, error } = useQuery('public-projects', async () => {
    const response = await api.get('/projects/leads/public/')
    return response.data
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading projects...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <p>Error loading projects. Please try again later.</p>
        </div>
      </div>
    )
  }

  const projects = data?.results || []
  const limit = data?.limit || 10

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Project Matcher</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Browse Projects</h2>
          <p className="mt-2 text-sm text-gray-600">
            Explore {limit} free project opportunities. Sign up to see more!
          </p>
        </div>

        {projects.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">No projects available at the moment.</p>
            <p className="text-sm text-gray-400 mt-2">Check back later for new opportunities.</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {projects.map((project) => (
                <li key={project.id}>
                  <Link
                    to={`/public/projects/${project.id}`}
                    className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center">
                          <p className="text-sm font-medium text-blue-600 truncate">
                            {project.title}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <p className="truncate">{project.description?.substring(0, 150)}...</p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          {project.company_name && (
                            <span className="mr-4">{project.company_name}</span>
                          )}
                          {project.budget_min && (
                            <span className="mr-4">
                              ${project.budget_min} - ${project.budget_max || 'N/A'}
                            </span>
                          )}
                          <span>{format(new Date(project.created_at), 'MMM d, yyyy')}</span>
                        </div>
                        {project.skills_required && project.skills_required.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {project.skills_required.slice(0, 5).map((skill, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="ml-5 flex-shrink-0">
                        <span className="text-blue-600 text-sm font-medium">View Details →</span>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        {projects.length > 0 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Want to see more projects?
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Sign up for free to access unlimited project opportunities and get matched with the perfect projects for your skills.
            </p>
            <Link
              to="/register"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
            >
              Sign Up Free
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
