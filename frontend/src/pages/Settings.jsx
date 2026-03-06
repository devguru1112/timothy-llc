import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { useState, useEffect } from 'react'
import { ArrowPathIcon, ClockIcon } from '@heroicons/react/24/outline'

export default function Settings() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [skills, setSkills] = useState(user?.skills || [])
  const [newSkill, setNewSkill] = useState('')
  const [scheduleTime, setScheduleTime] = useState('02:00')
  const [scheduleEnabled, setScheduleEnabled] = useState(true)
  const [scheduleLimit, setScheduleLimit] = useState(50)

  const { data: profile } = useQuery('profile', async () => {
    const response = await api.get('/auth/profile/')
    return response.data
  })

  const { data: schedule, refetch: refetchSchedule } = useQuery(
    'scraping-schedule',
    async () => {
      const res = await api.get('/scrapers/schedule/')
      return res.data
    },
    { enabled: !!profile?.is_superuser }
  )

  useEffect(() => {
    if (schedule) {
      setScheduleTime(schedule.time || '02:00')
      setScheduleEnabled(schedule.enabled !== false)
      setScheduleLimit(schedule.limit ?? 50)
    }
  }, [schedule])

  const scrapeNowMutation = useMutation(
    () => api.post('/scrapers/jobs/scrape_all/', { limit: scheduleLimit }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('scraping-schedule')
        queryClient.invalidateQueries('scraping-jobs')
      },
    }
  )

  const updateScheduleMutation = useMutation(
    (data) => api.patch('/scrapers/schedule/', data),
    {
      onSuccess: () => {
        refetchSchedule()
      },
    }
  )

  const updateMutation = useMutation(
    (data) => api.patch('/auth/profile/', data),
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

      {profile?.is_superuser && (
        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Scraping</h3>
            <p className="mt-1 text-sm text-gray-500">
              Run job scraping now or set the automatic scraping time.
            </p>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6 space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => scrapeNowMutation.mutate()}
                disabled={scrapeNowMutation.isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <ArrowPathIcon
                  className={`-ml-1 mr-2 h-5 w-5 ${scrapeNowMutation.isLoading ? 'animate-spin' : ''}`}
                  aria-hidden="true"
                />
                {scrapeNowMutation.isLoading ? 'Starting…' : 'Run scraping now'}
              </button>
              {scrapeNowMutation.isSuccess && (
                <span className="text-sm text-green-600">Scraping started in background.</span>
              )}
              {scrapeNowMutation.isError && (
                <span className="text-sm text-red-600">
                  {scrapeNowMutation.error?.response?.data?.error ||
                    scrapeNowMutation.error?.response?.data?.detail ||
                    'Failed to start'}
                </span>
              )}
            </div>

            <div className="pt-4 border-t border-gray-100">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Automatic scraping schedule</h4>
              <div className="flex flex-wrap items-center gap-4">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={scheduleEnabled}
                    onChange={(e) => {
                      setScheduleEnabled(e.target.checked)
                      updateScheduleMutation.mutate({ enabled: e.target.checked })
                    }}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enabled</span>
                </label>
                <div className="flex items-center gap-2">
                  <ClockIcon className="h-5 w-5 text-gray-400" />
                  <input
                    type="time"
                    value={scheduleTime}
                    onChange={(e) => setScheduleTime(e.target.value)}
                    onBlur={() => updateScheduleMutation.mutate({ time: scheduleTime })}
                    className="rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  <span className="text-sm text-gray-500">(24h)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-700">Limit per platform:</span>
                  <input
                    type="number"
                    min={1}
                    max={500}
                    value={scheduleLimit}
                    onChange={(e) => setScheduleLimit(Number(e.target.value) || 50)}
                    onBlur={() => updateScheduleMutation.mutate({ limit: scheduleLimit })}
                    className="w-20 rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Scraping runs once per day at the set time when enabled. You can also change this in Django Admin → System Settings (scraping_schedule_time, scraping_schedule_enabled).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
