import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { CheckIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

const PLAN_UI = {
  starter: {
    name: 'Starter',
    priority: 1,
    description: 'Good for getting started with project matching.',
    features: ['Standard priority in matching', 'Dashboard and outreach access', 'Manual top-up available'],
  },
  pro: {
    name: 'Pro',
    priority: 3,
    description: 'Faster visibility and stronger matching outcomes.',
    features: ['Higher priority in matching queue', 'Better chance to appear early', 'Ideal for active freelancers'],
  },
  premium: {
    name: 'Premium',
    priority: 5,
    description: 'Maximum matching priority for power users.',
    features: ['Top-tier matching priority', 'Best visibility across incoming leads', 'Built for high-volume users'],
  },
}

function formatUsd(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(amount || 0))
}

export default function Plans() {
  const { user } = useAuth()

  const { data, isLoading } = useQuery('plan-pricing', async () => {
    const res = await api.get('/payments/plans/')
    return res.data
  })

  const plansData = data?.plans || {}
  const currentPriority = Number(user?.priority_level || 1)

  if (isLoading) return <div className="text-center py-12">Loading plans...</div>

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Plans</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          Unlock a higher plan to increase your matching priority and get surfaced earlier.
        </p>
      </div>

      <div className="mb-6 rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Current plan level</p>
        <p className="mt-1 text-lg font-semibold text-slate-900">Priority {currentPriority}</p>
      </div>

      {user?.is_superuser && (
        <div className="mb-6 rounded-xl border border-indigo-200 bg-indigo-50/60 px-5 py-4 text-sm text-indigo-900">
          Plan base prices are controlled in Django Admin:
          {' '}
          <span className="font-semibold">System Settings</span>
          {' '}
          keys
          {' '}
          <span className="font-semibold">plan_pro_monthly_price</span>
          {' '}
          and
          {' '}
          <span className="font-semibold">plan_premium_monthly_price</span>.
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        {['starter', 'pro', 'premium'].map((planId) => {
          const plan = PLAN_UI[planId]
          const isCurrent = currentPriority === plan.priority
          const isHigher = currentPriority > plan.priority
          const isFeatured = planId === 'premium'
          const monthlyPrice = planId === 'starter'
            ? '0.00'
            : plansData?.[planId]?.monthly_price || (planId === 'pro' ? '29.00' : '79.00')

          return (
            <div
              key={planId}
              className={`overflow-hidden rounded-xl border bg-white shadow-sm ring-1 ${
                isFeatured
                  ? 'border-blue-200 ring-blue-200/80'
                  : 'border-slate-200 ring-slate-900/[0.03]'
              }`}
            >
              <div className={`px-5 py-5 ${isFeatured ? 'bg-blue-50/70' : 'bg-slate-50/70'}`}>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">{plan.name}</h2>
                    <p className="text-xs font-medium text-slate-500">Priority {plan.priority}</p>
                  </div>
                  <span className="text-sm font-semibold text-slate-700">
                    {planId === 'starter' ? '$0' : `${formatUsd(monthlyPrice)}/mo`}
                  </span>
                </div>
                <p className="mt-3 text-sm text-slate-600">{plan.description}</p>
              </div>

              <div className="px-5 py-5">
                <ul className="space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckIcon className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" aria-hidden />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-5">
                  {planId === 'starter' ? (
                    <button
                      type="button"
                      disabled
                      className="w-full cursor-default rounded-lg bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-500"
                    >
                      Default plan
                    </button>
                  ) : (
                    <Link
                      to={`/dashboard/plans/purchase/${planId}`}
                    className={`w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition ${
                        isCurrent
                          ? 'pointer-events-none block cursor-default bg-slate-100 text-center text-slate-500'
                          : 'block bg-blue-600 text-center text-white hover:bg-blue-700'
                      }`}
                    >
                      {isCurrent ? 'Current plan' : `Unlock ${plan.name}`}
                    </Link>
                  )}

                  {isHigher && !isCurrent && (
                    <p className="mt-2 text-xs text-slate-500">
                      You are currently on a higher priority than this plan.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
