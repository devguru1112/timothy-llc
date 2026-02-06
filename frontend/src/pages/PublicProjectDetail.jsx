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

  const { data: project, isLoading } = useQuery(
    ['public-project', id],
    async () => {
      const response = await api.get(`/api/projects/leads/${id}/`)
      return response.data
    }
  )

  const applicationMutation = useMutation(
    (formData) => api.post('/api/projects/applications/', formData),
    {
      onSuccess: () => {
        setShowApplicationForm(false)
        alert('Application submitted successfully! We will contact you soon.')
      },
      onError: (error) => {
        alert(error.response?.data?.error || 'Failed to submit application. Please try again.')
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
