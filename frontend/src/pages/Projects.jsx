import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { format } from 'date-fns'
import { useState } from 'react'

const SORT_OPTIONS = [
  { value: '-created_at', label: 'Newest first' },
  { value: 'created_at', label: 'Oldest first' },
  { value: 'company_name', label: 'Company (A–Z)' },
  { value: '-company_name', label: 'Company (Z–A)' },
  { value: '-scraped_at', label: 'Data added (newest)' },
  { value: 'scraped_at', label: 'Data added (oldest)' },
  { value: '-relevance_score', label: 'Relevance (high first)' },
  { value: 'relevance_score', label: 'Relevance (low first)' },
]

export default function Projects() {
  const [searchKeyword, setSearchKeyword] = useState('')
  const [sortBy, setSortBy] = useState('-created_at')

  const { data, isLoading, error } = useQuery(
    ['projects', searchKeyword, sortBy],
    async () => {
      const params = { ordering: sortBy }
      if (searchKeyword.trim()) params.search = searchKeyword.trim()
      const response = await api.get('/projects/leads/', { params })
      return response.data
    }
  )

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
          to="/dashboard/projects/available"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          View Available
        </Link>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          type="search"
          placeholder="Search by keyword (title, company, description...)"
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          className="flex-1 min-w-[200px] rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        <label className="flex items-center gap-2 text-sm text-gray-700">
          Sort by
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {projects.length === 0 ? (
            <li className="px-4 py-12 text-center text-gray-500">
              {searchKeyword.trim()
                ? 'No projects match your search.'
                : 'No projects yet. Run scraping to add project leads.'}
            </li>
          ) : (
            projects.map((project) => (
            <li key={project.id}>
              <Link
                to={`/dashboard/projects/${project.id}`}
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
                        {format(new Date(project.scraped_at || project.created_at), 'MMM d, yyyy')}
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
          )))}
        </ul>
      </div>
    </div>
  )
}
