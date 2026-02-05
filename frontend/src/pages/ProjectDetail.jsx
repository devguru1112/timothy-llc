import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { format } from 'date-fns'

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: project, isLoading } = useQuery(
    ['project', id],
    async () => {
      const response = await api.get(`/api/projects/leads/${id}/`)
      return response.data
    }
  )

  const matchMutation = useMutation(
    () => api.post(`/api/projects/leads/${id}/match/`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['project', id])
        queryClient.invalidateQueries('projects')
      },
    }
  )

  if (isLoading) return <div className="text-center py-12">Loading...</div>
  if (!project) return <div className="text-center py-12">Project not found</div>

  return (
    <div>
      <div className="mb-8">
        <button
          onClick={() => navigate('/projects')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Projects
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Project Details
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Source: {project.source_platform_name}
              </p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => matchMutation.mutate()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Find Matches
              </button>
            </div>
          </div>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{project.status}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Relevance Score</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {(project.relevance_score * 100).toFixed(1)}%
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Quality Score</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {(project.quality_score * 100).toFixed(1)}%
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Budget</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {project.budget_min
                  ? `$${project.budget_min} - $${project.budget_max || 'N/A'}`
                  : 'Not specified'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Company</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {project.company_name || 'Not specified'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Contact</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {project.contact_name || 'Not specified'}
                {project.contact_email && (
                  <span className="ml-2 text-blue-600">{project.contact_email}</span>
                )}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Description</dt>
              <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                {project.description}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Skills Required</dt>
              <dd className="mt-1">
                <div className="flex flex-wrap gap-2">
                  {project.skills_required?.map((skill, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </dd>
            </div>
          </dl>
        </div>
        <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
          <a
            href={project.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800"
          >
            View Original Posting →
          </a>
        </div>
      </div>
    </div>
  )
}
