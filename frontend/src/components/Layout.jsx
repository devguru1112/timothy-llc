import { useEffect, useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  HomeIcon,
  BriefcaseIcon,
  EnvelopeIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ArrowRightOnRectangleIcon,
  ArrowPathIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

function formatUsd(n) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(n ?? 0))
}

function navItemActive(pathname, href) {
  if (href === '/dashboard') {
    return pathname === '/dashboard'
  }
  return pathname === href || pathname.startsWith(`${href}/`)
}

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Projects', href: '/dashboard/projects', icon: BriefcaseIcon },
    { name: 'Outreach', href: '/dashboard/outreach', icon: EnvelopeIcon },
    { name: 'Plans', href: '/dashboard/plans', icon: SparklesIcon },
    ...(user?.is_superuser ? [{ name: 'Scraping', href: '/dashboard/scraping', icon: ArrowPathIcon }] : []),
    { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
  ]

  const linkBase =
    'inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors'
  const linkIdle = 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
  const linkActive = 'bg-white text-slate-900 shadow-sm ring-1 ring-slate-200/80'

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 shadow-sm shadow-slate-900/5 backdrop-blur-md">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Main">
          <div className="flex h-16 items-center justify-between gap-4">
            <div className="flex min-w-0 flex-1 items-center gap-3 sm:gap-8">
              <Link
                to="/dashboard"
                className="group flex shrink-0 items-center gap-2.5 rounded-xl py-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              >
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 text-sm font-bold text-white shadow-md shadow-blue-600/25 ring-2 ring-white">
                  PM
                </span>
                <span className="hidden truncate text-base font-bold tracking-tight text-slate-900 group-hover:text-slate-800 sm:block">
                  Project Matcher
                </span>
              </Link>

              <div className="hidden min-w-0 flex-1 items-center justify-center lg:flex">
                <div className="flex rounded-xl bg-slate-100/90 p-1 ring-1 ring-slate-200/60">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    const active = navItemActive(location.pathname, item.href)
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${linkBase} ${active ? linkActive : linkIdle}`}
                      >
                        <Icon className="h-5 w-5 shrink-0 opacity-80" aria-hidden />
                        {item.name}
                      </Link>
                    )
                  })}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                to="/dashboard/settings"
                className="hidden rounded-xl bg-slate-50 px-3 py-2 text-left ring-1 ring-slate-200/80 transition hover:bg-slate-100/90 sm:block"
              >
                <span className="block text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  Balance
                </span>
                <span className="block text-sm font-semibold tabular-nums text-slate-900">
                  {formatUsd(user?.balance)}
                </span>
              </Link>

              <div className="hidden h-8 w-px bg-slate-200 sm:block" aria-hidden />

              <div className="hidden items-center gap-2 sm:flex">
                <div className="flex items-center gap-2 rounded-xl py-1 pl-1 pr-2">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-slate-200 ring-2 ring-white">
                    {user?.photo_url ? (
                      <img src={user.photo_url} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <span className="text-xs font-bold text-slate-600">
                        {(user?.username || '?').slice(0, 1).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <span className="max-w-[8rem] truncate text-sm font-medium text-slate-800">
                    {user?.username}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={logout}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5 text-slate-500" aria-hidden />
                  <span className="hidden md:inline">Log out</span>
                </button>
              </div>

              <button
                type="button"
                className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white p-2.5 text-slate-700 shadow-sm transition hover:bg-slate-50 lg:hidden"
                onClick={() => setMobileOpen((o) => !o)}
                aria-expanded={mobileOpen}
                aria-controls="mobile-nav"
              >
                {mobileOpen ? (
                  <XMarkIcon className="h-6 w-6" aria-hidden />
                ) : (
                  <Bars3Icon className="h-6 w-6" aria-hidden />
                )}
                <span className="sr-only">{mobileOpen ? 'Close menu' : 'Open menu'}</span>
              </button>
            </div>
          </div>

          <div
            id="mobile-nav"
            className={`border-t border-slate-100 lg:hidden ${mobileOpen ? 'block' : 'hidden'}`}
          >
            <div className="flex flex-col gap-1 py-3">
              <Link
                to="/dashboard/settings"
                className="mx-1 flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 ring-1 ring-slate-200/80"
              >
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Balance</span>
                <span className="text-sm font-semibold tabular-nums text-slate-900">{formatUsd(user?.balance)}</span>
              </Link>
              {navigation.map((item) => {
                const Icon = item.icon
                const active = navItemActive(location.pathname, item.href)
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${linkBase} mx-1 ${active ? linkActive : linkIdle}`}
                  >
                    <Icon className="h-5 w-5 shrink-0" aria-hidden />
                    {item.name}
                  </Link>
                )
              })}
              <div className="mx-1 mt-2 flex items-center gap-2 border-t border-slate-100 pt-3">
                <div className="flex min-w-0 flex-1 items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-slate-200">
                    {user?.photo_url ? (
                      <img src={user.photo_url} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <span className="text-xs font-bold text-slate-600">
                        {(user?.username || '?').slice(0, 1).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <span className="truncate text-sm font-medium text-slate-800">{user?.username}</span>
                </div>
                <button
                  type="button"
                  onClick={logout}
                  className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" aria-hidden />
                  Log out
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}
