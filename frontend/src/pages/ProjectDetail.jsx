import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

/** Split description into paragraphs and list-like blocks for readable display */
function formatDescription(text) {
  if (!text || typeof text !== 'string') return null
  const trimmed = text.trim()
  if (!trimmed) return null

  const paragraphs = trimmed.split(/\n\n+/)
  const bulletRegex = /^[\s]*[•\-*]\s+/
  const numberRegex = /^[\s]*\d+[.)]\s+/

  return paragraphs.map((block, i) => {
    const lines = block.split(/\n/).map((l) => l.trim()).filter(Boolean)
    if (lines.length === 0) return null

    const looksLikeList =
      lines.length > 1 &&
      lines.every(
        (line) => bulletRegex.test(line) || numberRegex.test(line)
      )
    if (looksLikeList) {
      return (
        <ul key={i} className="list-disc list-outside pl-5 space-y-1.5 my-3">
          {lines.map((line, j) => (
            <li key={j} className="text-slate-700 leading-relaxed">
              {line.replace(/^[\s]*[•\-*]\s+/, '').replace(/^[\s]*\d+[.)]\s+/, '')}
            </li>
          ))}
        </ul>
      )
    }
    return (
      <p key={i} className="text-slate-700 leading-relaxed mb-4 last:mb-0">
        {block}
      </p>
    )
  })
}

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: project, isLoading } = useQuery(
    ['project', id],
    async () => {
      const response = await api.get(`/projects/leads/${id}/`)
      return response.data
    }
  )

  const matchMutation = useMutation(
    () => api.post(`/projects/leads/${id}/match/`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['project', id])
        queryClient.invalidateQueries('projects')
        queryClient.invalidateQueries('projects-available')
      },
    }
  )

  if (isLoading) return <div className="text-center py-12">Loading...</div>
  if (!project) return <div className="text-center py-12">Project not found</div>

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <button
          onClick={() => navigate('/dashboard/projects')}
          className="text-slate-600 hover:text-slate-900 font-medium mb-4 inline-flex items-center gap-1 transition-colors"
        >
          ← Back to Projects
        </button>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
          {project.title}
        </h1>
      </div>

      <div className="bg-white shadow-sm ring-1 ring-slate-200/60 rounded-xl overflow-hidden">
        {/* Meta / Project details */}
        <div className="px-6 py-5 bg-slate-50/80 border-b border-slate-200/80">
          <div className="flex flex-wrap justify-between items-start gap-4">
            <div>
              <h2 className="text-base font-semibold text-slate-800">
                Project Details
              </h2>
              <p className="mt-0.5 text-sm text-slate-500">
                Source: {project.source_platform_name}
              </p>
            </div>
            <button
              onClick={() => matchMutation.mutate()}
              disabled={matchMutation.isLoading}
              className="px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 transition-colors"
            >
              {matchMutation.isLoading ? 'Finding…' : 'Find Matches'}
            </button>
          </div>
          <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-4 mt-6">
            <div>
              <dt className="text-xs font-medium text-slate-500 uppercase tracking-wider">Status</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900 capitalize">{project.status}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{project.status}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500 uppercase tracking-wider">Company</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">
                {project.company_name || '—'}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500 uppercase tracking-wider">Relevance Score</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">
                {(project.relevance_score * 100).toFixed(1)}%
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500 uppercase tracking-wider">Budget</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">
                {project.budget_min
                  ? `$${project.budget_min} – $${project.budget_max || 'N/A'}`
                  : 'Not specified'}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500 uppercase tracking-wider">Contact</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">
                {project.contact_name || '—'}
                {project.contact_email && (
                  <a
                    href={`mailto:${project.contact_email}`}
                    className="ml-1.5 text-blue-600 hover:text-blue-700"
                  >
                    {project.contact_email}
                  </a>
                )}
              </dd>
            </div>
          </dl>
        </div>

        {/* Description — full-width, readable typography */}
        <div className="px-6 py-6 sm:px-8 sm:py-8">
          <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wider mb-4">
            Description
          </h3>
          <div className="max-w-3xl text-base leading-relaxed text-slate-800">
            {formatDescription(project.description) ?? (
              <p className="text-slate-500 italic">No description provided.</p>
            )}
          </div>
        </div>

        {/* Skills */}
        <div className="border-t border-slate-200 px-6 py-5 sm:px-8">
          <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wider mb-3">
            Skills Required
          </h3>
          {project.skills_required?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {project.skills_required.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-50 text-blue-800 ring-1 ring-blue-200/60"
                >
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 italic">No skills specified.</p>
          )}
        </div>

        {/* Footer CTA */}
        <div className="border-t border-slate-200 px-6 py-4 sm:px-8 bg-slate-50/50">
          <a
            href={project.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
          >
            View Original Posting
            <span aria-hidden>→</span>
          </a>
        </div>
      </div>
    </div>
  )
}
