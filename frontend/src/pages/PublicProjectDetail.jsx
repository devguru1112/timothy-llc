import { useQuery, useMutation } from 'react-query'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'
import api from '../services/api'
import { format } from 'date-fns'
import ApplicationForm from '../components/ApplicationForm'

export default function PublicProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [showApplicationForm, setShowApplicationForm] = useState(false)

  const { data: project, isLoading, error } = useQuery(
    ['public-project', id],
    async () => {
      const response = await api.get(`/projects/leads/${id}/`)
      return response.data
    },
    { retry: false }
  )

  const applicationMutation = useMutation(
    (formData) => api.post('/projects/applications/', formData),
    {
      onSuccess: (data) => {
        setShowApplicationForm(false)
        const remaining = data.data?.applications_remaining
        const limit = data.data?.applications_limit
        
        if (remaining !== undefined) {
          alert(`Application submitted successfully! ${remaining} applications remaining.`)
          if (remaining === 0) {
            setTimeout(() => {
              if (window.confirm('You have reached the application limit. Would you like to register to continue?')) {
                navigate('/register')
              }
            }, 1000)
          }
        } else {
          alert('Application submitted successfully! We will contact you soon.')
        }
      },
      onError: (error) => {
        const errorData = error.response?.data
        if (errorData?.requires_registration) {
          if (window.confirm(`${errorData.error}\n\nWould you like to register to continue?`)) {
            navigate('/register')
          }
        } else {
          alert(errorData?.error || 'Failed to submit application. Please try again.')
        }
      },
    }
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const errorData = error?.response?.data
  const blockedViewStats = errorData?.view_stats

  if (errorData?.requires_upgrade) {
    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/public" className="text-blue-600 hover:text-blue-800 mr-4">
                  ← Back
                </Link>
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

        <div className="max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="bg-white shadow-sm rounded-lg border border-amber-200">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900">Unlock Pro Plan</h2>
              <p className="mt-2 text-sm text-gray-600">
                {errorData?.message || 'You have reached your free project limit.'}
              </p>
              {blockedViewStats && (
                <p className="mt-2 text-sm text-gray-600">
                  You have viewed {blockedViewStats.count} of {blockedViewStats.limit} free projects.
                </p>
              )}
              <div className="mt-5 flex flex-wrap gap-3">
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Unlock Pro Plan
                </Link>
                <Link
                  to="/public"
                  className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Back to Projects
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Project not found.</p>
          <Link to="/public" className="text-blue-600 mt-4 inline-block">
            ← Back to Projects
          </Link>
        </div>
      </div>
    )
  }

  const handleApply = () => {
    setShowApplicationForm(true)
  }

  const viewStats = project?.view_stats

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/public" className="text-blue-600 hover:text-blue-800 mr-4">
                ← Back
              </Link>
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
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {viewStats && (
          <div
            className={`mb-6 rounded-lg border px-4 py-4 ${
              viewStats.reached ? 'border-amber-200 bg-amber-50' : 'border-gray-200 bg-white'
            }`}
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-gray-900">
                  {viewStats.reached
                    ? 'You have reached your free project limit.'
                    : `You have viewed ${viewStats.count} of ${viewStats.limit} free projects.`}
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  {viewStats.reached
                    ? 'Unlock Pro Plan to keep browsing new project opportunities.'
                    : `${viewStats.remaining} free project views remaining.`}
                </p>
              </div>
              {viewStats.reached && (
                <button
                  onClick={() => navigate('/register')}
                  className="inline-flex items-center justify-center rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Unlock Pro Plan
                </button>
              )}
            </div>
          </div>
        )}

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl leading-6 font-medium text-gray-900">
                  {project.title}
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  {project.source_platform_name}
                </p>
              </div>
              <button
                onClick={handleApply}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
              >
                Apply Now
              </button>
            </div>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              {project.company_name && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company</dt>
                  <dd className="mt-1 text-sm text-gray-900">{project.company_name}</dd>
                </div>
              )}
              {project.budget_min && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Budget</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    ${project.budget_min} - ${project.budget_max || 'N/A'} {project.budget_currency}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-sm font-medium text-gray-500">Posted</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(project.created_at), 'MMMM d, yyyy')}
                </dd>
              </div>
              {project.project_type && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Project Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{project.project_type}</dd>
                </div>
              )}
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                  {project.description}
                </dd>
              </div>
              {project.skills_required && project.skills_required.length > 0 && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500 mb-2">Skills Required</dt>
                  <dd className="mt-1">
                    <div className="flex flex-wrap gap-2">
                      {project.skills_required.map((skill, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </dd>
                </div>
              )}
            </dl>
          </div>
          <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
            <button
              onClick={handleApply}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-lg"
            >
              Apply for This Project
            </button>
          </div>
        </div>

        {/* Application Form Modal */}
        {showApplicationForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Apply for Project</h3>
                  <button
                    onClick={() => setShowApplicationForm(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                <ApplicationForm
                  projectId={project.id}
                  onSubmit={(formData) => applicationMutation.mutate(formData)}
                  onCancel={() => setShowApplicationForm(false)}
                  isLoading={applicationMutation.isLoading}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
