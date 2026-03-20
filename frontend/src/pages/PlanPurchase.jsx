import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from 'react-query'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'

const PLAN_NAMES = {
  pro: 'Pro',
  premium: 'Premium',
}

function formatUsd(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(amount || 0))
}

export default function PlanPurchase() {
  const { planId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, fetchUser } = useAuth()
  const [selectedMonths, setSelectedMonths] = useState(1)

  const { data, isLoading } = useQuery('plan-pricing', async () => {
    const res = await api.get('/payments/plans/')
    return res.data
  })

  const plan = data?.plans?.[planId]

  const selectedOption = useMemo(
    () => plan?.options?.find((o) => Number(o.months) === Number(selectedMonths)),
    [plan, selectedMonths]
  )

  const purchaseMutation = useMutation(
    async () => {
      const res = await api.post('/payments/plans/purchase/', {
        plan: planId,
        months: Number(selectedMonths),
      })
      return res.data
    },
    {
      onSuccess: async () => {
        queryClient.invalidateQueries('profile')
        queryClient.invalidateQueries('plan-pricing')
        await fetchUser?.()
        navigate('/dashboard/settings')
      },
    }
  )

  if (!PLAN_NAMES[planId]) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
        Unknown plan.
      </div>
    )
  }

  if (isLoading) return <div className="text-center py-12">Loading purchase details...</div>

  if (!plan) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
        Could not load plan pricing.
      </div>
    )
  }

  const currentBalance = Number(user?.balance || 0)
  const total = Number(selectedOption?.total || 0)
  const insufficient = currentBalance < total

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <Link to="/dashboard/plans" className="text-sm font-medium text-blue-600 hover:text-blue-800">
          ← Back to plans
        </Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
          Purchase {PLAN_NAMES[planId]}
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Choose billing duration. Discounts apply automatically based on duration.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Current balance</p>
            <p className="text-xl font-semibold text-slate-900">{formatUsd(currentBalance)}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Base monthly price</p>
            <p className="text-xl font-semibold text-slate-900">{formatUsd(plan.monthly_price)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(plan.options || []).map((option) => {
            const active = Number(option.months) === Number(selectedMonths)
            return (
              <button
                key={option.months}
                type="button"
                onClick={() => setSelectedMonths(Number(option.months))}
                className={`rounded-xl border p-4 text-left transition ${
                  active ? 'border-blue-300 bg-blue-50 ring-1 ring-blue-200' : 'border-slate-200 hover:bg-slate-50'
                }`}
              >
                <p className="text-sm font-semibold text-slate-900">
                  {option.months} month{Number(option.months) > 1 ? 's' : ''}
                </p>
                <p className="mt-1 text-xs text-slate-500">Discount: {option.discount_pct}%</p>
                <p className="mt-2 text-sm text-slate-600">Subtotal: {formatUsd(option.subtotal)}</p>
                <p className="text-base font-semibold text-slate-900">Total: {formatUsd(option.total)}</p>
              </button>
            )
          })}
        </div>

        <div className="mt-6 rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-700">
          <p>
            Pricing logic:
            {' '}
            <strong>1 month</strong> = base price,
            {' '}
            <strong>3 months</strong> = 10% off,
            {' '}
            <strong>6 months</strong> = 15% off,
            {' '}
            <strong>1 year</strong> = 25% off.
          </p>
        </div>

        {insufficient && (
          <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Insufficient balance for this purchase. Please top up first.
          </div>
        )}
        {purchaseMutation.isError && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {purchaseMutation.error?.response?.data?.detail || 'Purchase failed.'}
          </div>
        )}

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-600">
            You will be charged <span className="font-semibold text-slate-900">{formatUsd(total)}</span>.
          </p>
          <button
            type="button"
            onClick={() => purchaseMutation.mutate()}
            disabled={insufficient || purchaseMutation.isLoading}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {purchaseMutation.isLoading ? 'Processing...' : `Confirm purchase (${PLAN_NAMES[planId]})`}
          </button>
        </div>
      </div>
    </div>
  )
}
