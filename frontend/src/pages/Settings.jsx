import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { useState } from 'react'

export default function Settings() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [skills, setSkills] = useState(user?.skills || [])
  const [newSkill, setNewSkill] = useState('')

  const { data: profile } = useQuery('profile', async () => {
    const response = await api.get('/api/auth/profile/')
    return response.data
  })

  const updateMutation = useMutation(
    (data) => api.patch('/api/auth/profile/', data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('profile')
      },
    }
  )

  const handleAddSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      const updated = [...skills, newSkill.trim()]
      setSkills(updated)
      updateMutation.mutate({ skills: updated })
      setNewSkill('')
    }
  }

  const handleRemoveSkill = (skill) => {
    const updated = skills.filter((s) => s !== skill)
    setSkills(updated)
    updateMutation.mutate({ skills: updated })
  }

  if (!profile) return <div className="text-center py-12">Loading...</div>

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-600">Manage your profile and preferences</p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Profile</h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Username</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.username}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Priority Level</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.priority_level}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Portfolio</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.portfolio_url ? (
                  <a
                    href={profile.portfolio_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {profile.portfolio_url}
                  </a>
                ) : (
                  'Not set'
                )}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Bio</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {profile.bio || 'Not set'}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500 mb-2">Skills</dt>
              <dd className="mt-1">
                <div className="flex flex-wrap gap-2 mb-4">
                  {skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                    >
                      {skill}
                      <button
                        onClick={() => handleRemoveSkill(skill)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                    placeholder="Add skill"
                    className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <button
                    onClick={handleAddSkill}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
