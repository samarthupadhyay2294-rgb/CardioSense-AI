import React from 'react'

export function Card({ children, className = '', ...props }) {
  return (
    <div className={`card p-6 ${className}`} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="mb-5 flex items-start justify-between">
      <div className="flex items-start gap-3">
        {Icon && (
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-aqua-400">
            <Icon className="h-5 w-5" />
          </span>
        )}
        <div>
          <h3 className="font-display text-base font-semibold text-slate-900 dark:text-white">{title}</h3>
          {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

export function Spinner({ className = 'h-6 w-6' }) {
  return (
    <div
      className={`animate-spin rounded-full border-2 border-primary-600 border-t-transparent ${className}`}
      role="status"
      aria-label="Loading"
    />
  )
}

export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20">
      <Spinner className="h-8 w-8" />
      <p className="text-sm text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-500 dark:bg-red-500/10">
        <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path strokeLinecap="round" d="M12 8v4m0 4h.01" />
        </svg>
      </div>
      <div className="text-center">
        <p className="font-semibold text-slate-900 dark:text-white">Something went wrong</p>
        <p className="mt-1 max-w-md text-sm text-slate-500 dark:text-slate-400">{message}</p>
      </div>
      {onRetry && (
        <button className="btn-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

export function EmptyState({ icon: Icon, title, message, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      {Icon && <Icon className="h-10 w-10 text-slate-300 dark:text-slate-600" />}
      <div>
        <p className="font-semibold text-slate-700 dark:text-slate-200">{title}</p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{message}</p>
      </div>
      {action}
    </div>
  )
}
