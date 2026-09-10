import React from 'react'

function StatCard({ label, value, sub, icon: Icon, color = 'primary' }) {
  const colorMap = {
    primary: 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-aqua-400',
    teal: 'bg-teal-50 text-teal-600 dark:bg-teal-500/10 dark:text-teal-400',
    success: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400',
    warning: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400',
    danger: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-500/10 dark:text-purple-400',
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400',
  }

  return (
    <div className="card card-hover flex items-start gap-4 p-5">
      {Icon && (
        <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${colorMap[color] || colorMap.primary}`}>
          <Icon className="h-5 w-5" />
        </span>
      )}
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</p>
        <p className="mt-1 truncate font-display text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
        {sub && <p className="mt-0.5 text-xs text-slate-400 dark:text-slate-500">{sub}</p>}
      </div>
    </div>
  )
}

export default StatCard
