import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { useState, useEffect } from 'react'
import { ArrowPathIcon, ClockIcon } from '@heroicons/react/24/outline'

export default function Settings() {
  const { user, fetchUser } = useAuth()
  const queryClient = useQueryClient()
  const [skills, setSkills] = useState(user?.skills || [])
  const [newSkill, setNewSkill] = useState('')
  const [scheduleTime, setScheduleTime] = useState('02:00')
  const [scheduleEnabled, setScheduleEnabled] = useState(true)
  const [scheduleLimit, setScheduleLimit] = useState(50)
  const [bio, setBio] = useState('')
  const [summary, setSummary] = useState('')
  const [portfolioUrl, setPortfolioUrl] = useState('')
  const [education, setEducation] = useState([])
  const [workHistory, setWorkHistory] = useState([])
  const [newEdu, setNewEdu] = useState({ school: '', degree: '', field: '', startDate: '', endDate: '', description: '' })
  const [newWork, setNewWork] = useState({
    company: '',
    title: '',
    startDate: '',
    endDate: '',
    location: '',
    description: '',
  })

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

  useEffect(() => {
    if (!profile) return
    setSkills(profile.skills || [])
    setBio(profile.bio || '')
    setSummary(profile.summary || '')
    setPortfolioUrl(profile.portfolio_url || '')
    setEducation(Array.isArray(profile.education) ? profile.education : [])
    setWorkHistory(Array.isArray(profile.work_history) ? profile.work_history : [])
  }, [profile])

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
      onSuccess: async () => {
        queryClient.invalidateQueries('profile')
        await fetchUser?.()
      },
    }
  )

  const updatePhotoMutation = useMutation(
    async (file) => {
      const form = new FormData()
      form.append('photo', file)
      const res = await api.post('/auth/profile/photo/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    {
      onSuccess: async () => {
        queryClient.invalidateQueries('profile')
        await fetchUser?.()
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

  const handleSaveBasics = () => {
    updateMutation.mutate({
      bio,
      summary,
      portfolio_url: portfolioUrl,
    })
  }

  const handleAddEducation = () => {
    const item = {
      school: newEdu.school.trim(),
      degree: newEdu.degree.trim(),
      field: newEdu.field.trim(),
      startDate: newEdu.startDate || null,
      endDate: newEdu.endDate || null,
      description: newEdu.description.trim(),
    }
    if (!item.school) return
    const updated = [...education, item]
    setEducation(updated)
    updateMutation.mutate({ education: updated })
    setNewEdu({ school: '', degree: '', field: '', startDate: '', endDate: '', description: '' })
  }

  const handleRemoveEducation = (idx) => {
    const updated = education.filter((_, i) => i !== idx)
    setEducation(updated)
    updateMutation.mutate({ education: updated })
  }

  const handleAddWork = () => {
    const item = {
      company: newWork.company.trim(),
      title: newWork.title.trim(),
      startDate: newWork.startDate || null,
      endDate: newWork.endDate || null,
      location: newWork.location.trim(),
      description: newWork.description.trim(),
    }
    if (!item.company || !item.title) return
    const updated = [...workHistory, item]
    setWorkHistory(updated)
    updateMutation.mutate({ work_history: updated })
    setNewWork({ company: '', title: '', startDate: '', endDate: '', location: '', description: '' })
  }

  const handleRemoveWork = (idx) => {
    const updated = workHistory.filter((_, i) => i !== idx)
    setWorkHistory(updated)
    updateMutation.mutate({ work_history: updated })
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
              <dd className="mt-1">
                <input
                  type="url"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  placeholder="https://…"
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Balance</dt>
              <dd className="mt-1 text-sm text-gray-900">
                ${Number(profile.balance ?? 0).toFixed(2)}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Photo</dt>
              <dd className="mt-2 flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center">
                  {profile.photo_url ? (
                    <img src={profile.photo_url} alt="Profile" className="h-16 w-16 object-cover" />
                  ) : (
                    <span className="text-xs text-gray-500">No photo</span>
                  )}
                </div>
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) updatePhotoMutation.mutate(file)
                      e.target.value = ''
                    }}
                    className="block text-sm text-gray-700"
                  />
                  {updatePhotoMutation.isError && (
                    <div className="mt-1 text-sm text-red-600">
                      {updatePhotoMutation.error?.response?.data?.detail || 'Failed to upload photo'}
                    </div>
                  )}
                </div>
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Summary</dt>
              <dd className="mt-1">
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={4}
                  placeholder="A short professional summary…"
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Bio</dt>
              <dd className="mt-1">
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={4}
                  placeholder="More detail about you…"
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
                <div className="mt-3 flex items-center justify-end gap-3">
                  {updateMutation.isError && (
                    <span className="text-sm text-red-600">
                      {updateMutation.error?.response?.data?.detail || 'Failed to save'}
                    </span>
                  )}
                  {updateMutation.isSuccess && (
                    <span className="text-sm text-green-600">Saved</span>
                  )}
                  <button
                    type="button"
                    onClick={handleSaveBasics}
                    disabled={updateMutation.isLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {updateMutation.isLoading ? 'Saving…' : 'Save'}
                  </button>
                </div>
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

      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Top up balance</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add funds to your account using card (Stripe), PayPal, Payoneer, or crypto.
          </p>
        </div>
        <TopUpSection />
      </div>

      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Education</h3>
          <p className="mt-1 text-sm text-gray-500">Add schools, degrees, and relevant notes.</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6 space-y-4">
          {education.length === 0 ? (
            <div className="text-sm text-gray-500">No education added yet.</div>
          ) : (
            <ul className="space-y-3">
              {education.map((e, idx) => (
                <li key={idx} className="flex items-start justify-between gap-4 rounded-md border border-gray-200 p-3">
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-gray-900">
                      {e.school || 'School'}{e.degree ? ` • ${e.degree}` : ''}{e.field ? `, ${e.field}` : ''}
                    </div>
                    <div className="text-xs text-gray-500">
                      {(e.startDate || '—')} – {(e.endDate || '—')}
                    </div>
                    {e.description ? <div className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{e.description}</div> : null}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveEducation(idx)}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="pt-4 border-t border-gray-100">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="text"
                value={newEdu.school}
                onChange={(e) => setNewEdu((p) => ({ ...p, school: e.target.value }))}
                placeholder="School"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <input
                type="text"
                value={newEdu.degree}
                onChange={(e) => setNewEdu((p) => ({ ...p, degree: e.target.value }))}
                placeholder="Degree"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <input
                type="text"
                value={newEdu.field}
                onChange={(e) => setNewEdu((p) => ({ ...p, field: e.target.value }))}
                placeholder="Field (optional)"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="month"
                  value={newEdu.startDate}
                  onChange={(e) => setNewEdu((p) => ({ ...p, startDate: e.target.value }))}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
                <input
                  type="month"
                  value={newEdu.endDate}
                  onChange={(e) => setNewEdu((p) => ({ ...p, endDate: e.target.value }))}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <textarea
                value={newEdu.description}
                onChange={(e) => setNewEdu((p) => ({ ...p, description: e.target.value }))}
                rows={3}
                placeholder="Description (optional)"
                className="sm:col-span-2 shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                onClick={handleAddEducation}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add education
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Work history</h3>
          <p className="mt-1 text-sm text-gray-500">Add roles you want to highlight.</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6 space-y-4">
          {workHistory.length === 0 ? (
            <div className="text-sm text-gray-500">No work history added yet.</div>
          ) : (
            <ul className="space-y-3">
              {workHistory.map((w, idx) => (
                <li key={idx} className="flex items-start justify-between gap-4 rounded-md border border-gray-200 p-3">
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-gray-900">
                      {w.title || 'Title'}{w.company ? ` • ${w.company}` : ''}
                    </div>
                    <div className="text-xs text-gray-500">
                      {(w.startDate || '—')} – {(w.endDate || '—')}{w.location ? ` • ${w.location}` : ''}
                    </div>
                    {w.description ? <div className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{w.description}</div> : null}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveWork(idx)}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="pt-4 border-t border-gray-100">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="text"
                value={newWork.title}
                onChange={(e) => setNewWork((p) => ({ ...p, title: e.target.value }))}
                placeholder="Title"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <input
                type="text"
                value={newWork.company}
                onChange={(e) => setNewWork((p) => ({ ...p, company: e.target.value }))}
                placeholder="Company"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="month"
                  value={newWork.startDate}
                  onChange={(e) => setNewWork((p) => ({ ...p, startDate: e.target.value }))}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
                <input
                  type="month"
                  value={newWork.endDate}
                  onChange={(e) => setNewWork((p) => ({ ...p, endDate: e.target.value }))}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              <input
                type="text"
                value={newWork.location}
                onChange={(e) => setNewWork((p) => ({ ...p, location: e.target.value }))}
                placeholder="Location (optional)"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
              <textarea
                value={newWork.description}
                onChange={(e) => setNewWork((p) => ({ ...p, description: e.target.value }))}
                rows={3}
                placeholder="Description (optional)"
                className="sm:col-span-2 shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                onClick={handleAddWork}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add work history
              </button>
            </div>
          </div>
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

function TopUpSection() {
  const [amount, setAmount] = useState('')
  const [provider, setProvider] = useState('stripe')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const handleTopUp = async () => {
    setError('')
    setMessage('')
    const value = parseFloat(amount)
    if (!value || value <= 0) {
      setError('Enter a valid amount greater than 0.')
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/payments/topups/create/', {
        provider,
        amount: value.toFixed(2),
      })
      const data = res.data
      if (data.kind === 'redirect' && data.redirect_url) {
        window.location.href = data.redirect_url
      } else if (data.kind === 'manual') {
        setMessage(
          data.message ||
            'Payoneer top-up created. Please contact support or follow the provided Payoneer instructions.'
        )
      } else {
        setMessage('Top-up created. Follow the payment instructions.')
      }
    } catch (e) {
      const detail = e?.response?.data?.detail || 'Failed to create top-up.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-gray-700">Amount (USD)</label>
          <input
            type="number"
            min="1"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="50.00"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Payment method</label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
          >
            <option value="stripe">Card (Stripe)</option>
            <option value="paypal">PayPal</option>
            <option value="payoneer">Payoneer (manual)</option>
            <option value="crypto">Crypto (Coinbase)</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            type="button"
            onClick={handleTopUp}
            disabled={loading}
            className="inline-flex w-full justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Processing…' : 'Top up'}
          </button>
        </div>
      </div>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      {message && <p className="mt-3 text-sm text-green-600">{message}</p>}
      <p className="mt-3 text-xs text-gray-500">
        Stripe is used for card payments. Payoneer is handled manually; you will receive instructions from support.
      </p>
    </div>
  )
}
