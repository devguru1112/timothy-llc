import { useMutation, useQueryClient } from 'react-query'
import { CheckIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

const PLAN_DEFS = [
  {
    id: 'starter',
    name: 'Starter',
    priority: 1,
    price: '$0',
    description: 'Good for getting started with project matching.',
    features: ['Standard priority in matching', 'Dashboard and outreach access', 'Manual top-up available'],
  },
  {
    id: 'pro',
    name: 'Pro',
    priority: 3,
    price: '$29/mo',
    description: 'Faster visibility and stronger matching outcomes.',
    features: ['Higher priority in matching queue', 'Better chance to appear early', 'Ideal for active freelancers'],
  },
  {
    id: 'premium',
    name: 'Premium',
    priority: 5,
    price: '$79/mo',
    description: 'Maximum matching priority for power users.',
    features: ['Top-tier matching priority', 'Best visibility across incoming leads', 'Built for high-volume users'],
  },
]

export default function Plans() {
  const { user, fetchUser } = useAuth()
  const queryClient = useQueryClient()

  const unlockMutation = useMutation(
    async (priorityLevel) => {
      const res = await api.patch('/auth/profile/', { priority_level: priorityLevel })
      return res.data
    },
    {
      onSuccess: async () => {
        queryClient.invalidateQueries('profile')
        await fetchUser?.()
      },
    }
  )

  const currentPriority = Number(user?.priority_level || 1)

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

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        {PLAN_DEFS.map((plan) => {
          const isCurrent = currentPriority === plan.priority
          const isHigher = currentPriority > plan.priority
          const isFeatured = plan.id === 'premium'
          const disabled = isCurrent || unlockMutation.isLoading

          return (
            <div
              key={plan.id}
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
                  <span className="text-sm font-semibold text-slate-700">{plan.price}</span>
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
                  <button
                    type="button"
                    onClick={() => unlockMutation.mutate(plan.priority)}
                    disabled={disabled}
                    className={`w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition ${
                      isCurrent
                        ? 'cursor-default bg-slate-100 text-slate-500'
                        : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60'
                    }`}
                  >
                    {isCurrent ? 'Current plan' : `Unlock ${plan.name}`}
                  </button>

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

      {unlockMutation.isError && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {unlockMutation.error?.response?.data?.detail || 'Failed to unlock plan. Please try again.'}
        </div>
      )}
      {unlockMutation.isSuccess && (
        <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          Plan unlocked successfully.
        </div>
      )}
    </div>
  )
}
