import React from 'react'
import { getClassColor, formatConfidence } from '../../utils/helpers'

function ProbabilityBar({ label, value, highlight }) {
  const color = getClassColor(label)
  const pct = value * 100
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className={`text-sm font-medium ${highlight ? 'font-bold' : ''} text-slate-700 dark:text-slate-200`}>
          {label}
        </span>
        <span className={`text-sm font-semibold ${color.text}`}>{formatConfidence(value)}</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${highlight ? 'bg-gradient-to-r from-teal-500 to-aqua-500' : 'bg-slate-300 dark:bg-slate-600'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function ProbabilityChart({ probabilities, prediction }) {
  if (!probabilities) return null
  const entries = Object.entries(probabilities).sort((a, b) => b[1] - a[1])
  return (
    <div className="space-y-4">
      {entries.map(([label, value]) => (
        <ProbabilityBar key={label} label={label} value={value} highlight={label === prediction} />
      ))}
    </div>
  )
}

export default ProbabilityChart
