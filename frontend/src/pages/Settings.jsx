import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { useState, useEffect } from 'react'
import {
  AcademicCapIcon,
  ArrowPathIcon,
  BanknotesIcon,
  BriefcaseIcon,
  ClockIcon,
  CreditCardIcon,
  CurrencyDollarIcon,
  GlobeAltIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'

function formatUsd(n) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n)
}

const inputShell =
  'rounded-xl border-0 bg-white py-2.5 px-3 text-sm text-slate-900 shadow-sm ring-1 ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500'

const inputClass = `block w-full ${inputShell}`

const inputClassCompact = `block w-auto min-w-[6.5rem] ${inputShell}`

const textareaClass = `block w-full min-h-[100px] ${inputShell}`

const btnPrimary =
  'inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'

const btnPrimarySm =
  'inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'

const btnRemove =
  'shrink-0 rounded-lg px-2.5 py-1 text-sm font-medium text-red-600 transition hover:bg-red-50'

function SettingsSectionHeader({ eyebrow, title, description, icon: Icon }) {
  return (
    <div className="border-b border-slate-100 bg-gradient-to-r from-slate-50/90 to-white px-6 py-5 sm:px-8">
      <div className="flex items-start gap-4">
        {Icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600/10 text-blue-600">
            <Icon className="h-5 w-5" aria-hidden />
          </div>
        )}
        <div className="min-w-0 flex-1">
          {eyebrow && (
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{eyebrow}</p>
          )}
          <h3 className="mt-0.5 text-lg font-semibold tracking-tight text-slate-900">{title}</h3>
          {description && (
            <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{description}</p>
          )}
        </div>
      </div>
    </div>
  )
}

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

  if (!profile) {
    return (
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-center py-24">
        <div
          className="h-10 w-10 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600"
          aria-hidden
        />
        <p className="mt-4 text-sm font-medium text-slate-600">Loading settings…</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl pb-12">
      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Settings</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">
          Manage your profile, wallet, and preferences. Changes to bio and summary are saved when you click Save.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm ring-1 ring-slate-900/5">
        <SettingsSectionHeader
          eyebrow="Account"
          title="Profile"
          description="Your public details, portfolio link, and skills used for matching."
          icon={UserCircleIcon}
        />
        <div className="px-6 py-6 sm:px-8">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl bg-slate-50/80 p-4 ring-1 ring-slate-100">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Username</p>
              <p className="mt-1 truncate text-sm font-semibold text-slate-900">{profile.username}</p>
            </div>
            <div className="rounded-xl bg-slate-50/80 p-4 ring-1 ring-slate-100">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Email</p>
              <p className="mt-1 truncate text-sm font-semibold text-slate-900">{profile.email}</p>
            </div>
            <div className="rounded-xl bg-slate-50/80 p-4 ring-1 ring-slate-100">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Priority</p>
              <p className="mt-1 text-sm font-semibold text-slate-900">{profile.priority_level}</p>
            </div>
            <div className="rounded-xl bg-slate-50/80 p-4 ring-1 ring-slate-100">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Balance</p>
              <p className="mt-1 text-sm font-semibold tabular-nums text-slate-900">
                {formatUsd(Number(profile.balance ?? 0))}
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[auto_1fr] lg:items-start">
            <div>
              <p className="text-sm font-medium text-slate-800">Photo</p>
              <p className="mt-0.5 text-xs text-slate-500">JPG or PNG</p>
              <div className="mt-3 flex flex-col items-start gap-4 sm:flex-row sm:items-center">
                <div className="h-20 w-20 overflow-hidden rounded-2xl bg-slate-100 ring-2 ring-white shadow-md ring-slate-200">
                  {profile.photo_url ? (
                    <img src={profile.photo_url} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
                      No photo
                    </div>
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
                    className="block w-full max-w-xs text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {updatePhotoMutation.isError && (
                    <div className="mt-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
                      {updatePhotoMutation.error?.response?.data?.detail || 'Failed to upload photo'}
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="min-w-0 space-y-6">
              <div>
                <label className="text-sm font-medium text-slate-800">Portfolio URL</label>
                <input
                  type="url"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  placeholder="https://…"
                  className={`${inputClass} mt-2`}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-800">Summary</label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={4}
                  placeholder="A short professional summary…"
                  className={`${textareaClass} mt-2`}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-800">Bio</label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={4}
                  placeholder="More detail about you…"
                  className={`${textareaClass} mt-2`}
                />
                <div className="mt-3 flex flex-wrap items-center justify-end gap-3">
                  {updateMutation.isError && (
                    <span className="text-sm text-red-600">
                      {updateMutation.error?.response?.data?.detail || 'Failed to save'}
                    </span>
                  )}
                  {updateMutation.isSuccess && !updateMutation.isLoading && (
                    <span className="text-sm font-medium text-emerald-600">Saved</span>
                  )}
                  <button
                    type="button"
                    onClick={handleSaveBasics}
                    disabled={updateMutation.isLoading}
                    className={btnPrimary}
                  >
                    {updateMutation.isLoading ? 'Saving…' : 'Save profile'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-10 border-t border-slate-100 pt-8">
            <label className="text-sm font-medium text-slate-800">Skills</label>
            <p className="mt-0.5 text-xs text-slate-500">Press Enter or click Add — saved immediately</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 rounded-full bg-blue-50 py-1 pl-3 pr-1 text-sm font-medium text-blue-900 ring-1 ring-blue-100"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="rounded-full p-0.5 text-blue-600 transition hover:bg-blue-100 hover:text-blue-800"
                    aria-label={`Remove ${skill}`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="mt-4 flex flex-col gap-2 sm:flex-row">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                placeholder="e.g. React, Python, AWS"
                className={inputClass}
              />
              <button type="button" onClick={handleAddSkill} className={`${btnPrimarySm} shrink-0 sm:w-auto`}>
                Add skill
              </button>
            </div>
          </div>
        </div>
      </div>

      <TopUpSection balance={Number(profile.balance ?? 0)} />

      <div className="mt-8 overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm ring-1 ring-slate-900/5">
        <SettingsSectionHeader
          eyebrow="Background"
          title="Education"
          description="Schools, degrees, and notes that strengthen your profile."
          icon={AcademicCapIcon}
        />
        <div className="space-y-6 px-6 py-6 sm:px-8">
          {education.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 px-4 py-8 text-center text-sm text-slate-500">
              No education yet. Add your first entry below.
            </div>
          ) : (
            <ul className="space-y-3">
              {education.map((e, idx) => (
                <li
                  key={idx}
                  className="flex items-start justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm ring-1 ring-slate-900/[0.02]"
                >
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-slate-900">
                      {e.school || 'School'}
                      {e.degree ? ` · ${e.degree}` : ''}
                      {e.field ? `, ${e.field}` : ''}
                    </div>
                    <div className="mt-1 text-xs font-medium text-slate-500">
                      {(e.startDate || '—')} – {(e.endDate || '—')}
                    </div>
                    {e.description ? (
                      <div className="mt-3 text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
                        {e.description}
                      </div>
                    ) : null}
                  </div>
                  <button type="button" onClick={() => handleRemoveEducation(idx)} className={btnRemove}>
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="rounded-xl bg-slate-50/80 p-5 ring-1 ring-slate-100">
            <p className="text-sm font-semibold text-slate-900">Add education</p>
            <p className="mt-0.5 text-xs text-slate-500">School is required; other fields are optional.</p>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <input
                type="text"
                value={newEdu.school}
                onChange={(e) => setNewEdu((p) => ({ ...p, school: e.target.value }))}
                placeholder="School"
                className={inputClass}
              />
              <input
                type="text"
                value={newEdu.degree}
                onChange={(e) => setNewEdu((p) => ({ ...p, degree: e.target.value }))}
                placeholder="Degree"
                className={inputClass}
              />
              <input
                type="text"
                value={newEdu.field}
                onChange={(e) => setNewEdu((p) => ({ ...p, field: e.target.value }))}
                placeholder="Field (optional)"
                className={inputClass}
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="month"
                  value={newEdu.startDate}
                  onChange={(e) => setNewEdu((p) => ({ ...p, startDate: e.target.value }))}
                  className={inputClass}
                />
                <input
                  type="month"
                  value={newEdu.endDate}
                  onChange={(e) => setNewEdu((p) => ({ ...p, endDate: e.target.value }))}
                  className={inputClass}
                />
              </div>
              <textarea
                value={newEdu.description}
                onChange={(e) => setNewEdu((p) => ({ ...p, description: e.target.value }))}
                rows={3}
                placeholder="Description (optional)"
                className={`${textareaClass} sm:col-span-2`}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <button type="button" onClick={handleAddEducation} className={btnPrimary}>
                Add education
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm ring-1 ring-slate-900/5">
        <SettingsSectionHeader
          eyebrow="Experience"
          title="Work history"
          description="Roles and companies you want clients to see first."
          icon={BriefcaseIcon}
        />
        <div className="space-y-6 px-6 py-6 sm:px-8">
          {workHistory.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 px-4 py-8 text-center text-sm text-slate-500">
              No work history yet. Add a role below.
            </div>
          ) : (
            <ul className="space-y-3">
              {workHistory.map((w, idx) => (
                <li
                  key={idx}
                  className="flex items-start justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm ring-1 ring-slate-900/[0.02]"
                >
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-slate-900">
                      {w.title || 'Title'}
                      {w.company ? ` · ${w.company}` : ''}
                    </div>
                    <div className="mt-1 text-xs font-medium text-slate-500">
                      {(w.startDate || '—')} – {(w.endDate || '—')}
                      {w.location ? ` · ${w.location}` : ''}
                    </div>
                    {w.description ? (
                      <div className="mt-3 text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
                        {w.description}
                      </div>
                    ) : null}
                  </div>
                  <button type="button" onClick={() => handleRemoveWork(idx)} className={btnRemove}>
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="rounded-xl bg-slate-50/80 p-5 ring-1 ring-slate-100">
            <p className="text-sm font-semibold text-slate-900">Add position</p>
            <p className="mt-0.5 text-xs text-slate-500">Title and company are required.</p>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <input
                type="text"
                value={newWork.title}
                onChange={(e) => setNewWork((p) => ({ ...p, title: e.target.value }))}
                placeholder="Job title"
                className={inputClass}
              />
              <input
                type="text"
                value={newWork.company}
                onChange={(e) => setNewWork((p) => ({ ...p, company: e.target.value }))}
                placeholder="Company"
                className={inputClass}
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="month"
                  value={newWork.startDate}
                  onChange={(e) => setNewWork((p) => ({ ...p, startDate: e.target.value }))}
                  className={inputClass}
                />
                <input
                  type="month"
                  value={newWork.endDate}
                  onChange={(e) => setNewWork((p) => ({ ...p, endDate: e.target.value }))}
                  className={inputClass}
                />
              </div>
              <input
                type="text"
                value={newWork.location}
                onChange={(e) => setNewWork((p) => ({ ...p, location: e.target.value }))}
                placeholder="Location (optional)"
                className={inputClass}
              />
              <textarea
                value={newWork.description}
                onChange={(e) => setNewWork((p) => ({ ...p, description: e.target.value }))}
                rows={3}
                placeholder="Description (optional)"
                className={`${textareaClass} sm:col-span-2`}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <button type="button" onClick={handleAddWork} className={btnPrimary}>
                Add work history
              </button>
            </div>
          </div>
        </div>
      </div>

      {profile?.is_superuser && (
        <div className="mt-8 overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm ring-1 ring-slate-900/5">
          <SettingsSectionHeader
            eyebrow="Admin"
            title="Job scraping"
            description="Trigger a scrape immediately or configure the daily schedule and per-platform limit."
            icon={ArrowPathIcon}
          />
          <div className="space-y-6 px-6 py-6 sm:px-8">
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-5">
              <p className="text-sm font-medium text-slate-800">Manual run</p>
              <p className="mt-1 text-xs text-slate-500">
                Uses the limit below for each platform. Runs in the background.
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => scrapeNowMutation.mutate()}
                  disabled={scrapeNowMutation.isLoading}
                  className={`${btnPrimary} inline-flex items-center gap-2`}
                >
                  <ArrowPathIcon
                    className={`h-5 w-5 ${scrapeNowMutation.isLoading ? 'animate-spin' : ''}`}
                    aria-hidden
                  />
                  {scrapeNowMutation.isLoading ? 'Starting…' : 'Run scraping now'}
                </button>
                {scrapeNowMutation.isSuccess && (
                  <span className="text-sm font-medium text-emerald-600">Scraping started in background.</span>
                )}
                {scrapeNowMutation.isError && (
                  <span className="text-sm text-red-600">
                    {scrapeNowMutation.error?.response?.data?.error ||
                      scrapeNowMutation.error?.response?.data?.detail ||
                      'Failed to start'}
                  </span>
                )}
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm ring-1 ring-slate-900/[0.02]">
              <div className="flex items-center gap-2">
                <ClockIcon className="h-5 w-5 text-slate-400" aria-hidden />
                <h4 className="text-sm font-semibold text-slate-900">Automatic schedule</h4>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Once per day at the chosen time (24h). Also configurable in Django Admin → System Settings.
              </p>
              <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
                <label className="inline-flex cursor-pointer items-center rounded-lg bg-slate-50 px-3 py-2 ring-1 ring-slate-200">
                  <input
                    type="checkbox"
                    checked={scheduleEnabled}
                    onChange={(e) => {
                      setScheduleEnabled(e.target.checked)
                      updateScheduleMutation.mutate({ enabled: e.target.checked })
                    }}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-slate-700">Schedule enabled</span>
                </label>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-600">Run at</span>
                  <input
                    type="time"
                    value={scheduleTime}
                    onChange={(e) => setScheduleTime(e.target.value)}
                    onBlur={() => updateScheduleMutation.mutate({ time: scheduleTime })}
                    className={inputClassCompact}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-600">Limit / platform</span>
                  <input
                    type="number"
                    min={1}
                    max={500}
                    value={scheduleLimit}
                    onChange={(e) => setScheduleLimit(Number(e.target.value) || 50)}
                    onBlur={() => updateScheduleMutation.mutate({ limit: scheduleLimit })}
                    className={`${inputClassCompact} min-w-[5rem]`}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const TOPUP_PRESETS = [25, 50, 100, 250]

const TOPUP_PROVIDERS = [
  { id: 'stripe', title: 'Card', hint: 'Stripe Checkout', Icon: CreditCardIcon },
  { id: 'paypal', title: 'PayPal', hint: 'Pay with account', Icon: GlobeAltIcon },
  { id: 'payoneer', title: 'Payoneer', hint: 'Manual transfer', Icon: BanknotesIcon },
  { id: 'crypto', title: 'Crypto', hint: 'Coinbase Commerce', Icon: CurrencyDollarIcon },
]

function TopUpSection({ balance }) {
  const [amount, setAmount] = useState('')
  const [provider, setProvider] = useState('stripe')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const parsedAmount = parseFloat(amount)
  const projected =
    !Number.isNaN(parsedAmount) && parsedAmount > 0 ? balance + parsedAmount : null

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
        const parts = []
        if (data.message) parts.push(data.message)
        if (data.payoneer_receive_email) {
          parts.push(`Payoneer receive email: ${data.payoneer_receive_email}`)
        }
        if (data.reference) {
          parts.push(`Reference: ${data.reference}`)
        }
        if (data.instructions) parts.push(data.instructions)
        setMessage(parts.join(' '))
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
    <div className="mt-8 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-lg shadow-slate-200/50 ring-1 ring-slate-900/5">
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-6 py-8 sm:px-8">
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-blue-500/20 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-20 -left-10 h-40 w-40 rounded-full bg-emerald-500/15 blur-3xl"
          aria-hidden
        />
        <div className="relative flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-xl">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Wallet</p>
            <h3 className="mt-1 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Top up your balance
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">
              Add funds with card, PayPal, Payoneer, or crypto. Credits apply after payment completes (instant for
              most card and PayPal flows).
            </p>
          </div>
          <div className="shrink-0 rounded-2xl border border-white/10 bg-white/[0.07] px-6 py-5 shadow-xl backdrop-blur-md sm:min-w-[220px]">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Current balance</p>
            <p className="mt-1 text-3xl font-semibold tabular-nums tracking-tight text-white sm:text-4xl">
              {formatUsd(balance)}
            </p>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-100 bg-slate-50/50 px-6 py-7 sm:px-8">
        <div className="mx-auto max-w-3xl space-y-8">
          <div>
            <label className="text-sm font-medium text-slate-800">Amount</label>
            <p className="mt-0.5 text-xs text-slate-500">USD — choose a preset or enter any amount</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {TOPUP_PRESETS.map((preset) => {
                const active = amount === String(preset)
                return (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => setAmount(String(preset))}
                    className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
                      active
                        ? 'bg-slate-900 text-white shadow-md shadow-slate-900/20 ring-2 ring-slate-900 ring-offset-2'
                        : 'bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50 hover:ring-slate-300'
                    }`}
                  >
                    {formatUsd(preset)}
                  </button>
                )
              })}
            </div>
            <div className="relative mt-4">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
              <input
                type="number"
                min="1"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="block w-full rounded-xl border-0 bg-white py-3 pl-8 pr-4 text-slate-900 shadow-sm ring-1 ring-slate-200 transition placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 sm:text-base"
                placeholder="50.00"
              />
            </div>
            {projected != null && (
              <p className="mt-2 text-xs text-slate-500">
                After this top-up completes: <span className="font-medium text-slate-700">{formatUsd(projected)}</span>
              </p>
            )}
          </div>

          <div>
            <label className="text-sm font-medium text-slate-800">Payment method</label>
            <p className="mt-0.5 text-xs text-slate-500">Select how you want to pay</p>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {TOPUP_PROVIDERS.map(({ id, title, hint, Icon }) => {
                const selected = provider === id
                return (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setProvider(id)}
                    className={`flex flex-col items-start rounded-xl p-4 text-left transition-all ${
                      selected
                        ? 'bg-blue-50 ring-2 ring-blue-500 ring-offset-2'
                        : 'bg-white ring-1 ring-slate-200 hover:bg-slate-50 hover:ring-slate-300'
                    }`}
                  >
                    <Icon
                      className={`h-6 w-6 ${selected ? 'text-blue-600' : 'text-slate-500'}`}
                      aria-hidden
                    />
                    <span className="mt-3 text-sm font-semibold text-slate-900">{title}</span>
                    <span className="mt-0.5 text-xs text-slate-500">{hint}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-slate-500 sm:max-w-md">
              Card payments use Stripe. Payoneer is manual — we show the receiving email and reference when
              configured.
            </p>
            <button
              type="button"
              onClick={handleTopUp}
              disabled={loading}
              className="inline-flex w-full shrink-0 items-center justify-center rounded-xl bg-blue-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
            >
              {loading ? 'Processing…' : 'Continue to payment'}
            </button>
          </div>

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
          )}
          {message && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
