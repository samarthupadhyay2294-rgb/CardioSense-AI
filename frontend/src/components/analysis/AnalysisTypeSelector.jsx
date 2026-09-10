import React from 'react'
import { Activity, Image as ImageIcon } from 'lucide-react'

function AnalysisTypeSelector({ value, onChange }) {
  const options = [
    { value: 'signal', label: 'ECG Signal', icon: Activity, desc: '12-lead WFDB, .mat, .csv, .npy' },
    { value: 'image', label: 'ECG Image', icon: ImageIcon, desc: 'PNG, JPG, JPEG ECG scans' },
  ]

  return (
    <div className="mb-2 flex flex-wrap gap-3">
      {options.map((opt) => {
        const selected = value === opt.value
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={`flex items-center gap-3 rounded-xl border-2 px-5 py-3 text-left transition-all ${
              selected
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
                : 'border-slate-200 bg-white hover:border-primary-300 dark:border-slate-700 dark:bg-slate-800'
            }`}
          >
            <span
              className={`flex h-9 w-9 items-center justify-center rounded-xl ${
                selected
                  ? 'bg-gradient-to-br from-primary-600 to-aqua-500 text-white'
                  : 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
              }`}
            >
              <opt.icon className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className={`font-display font-semibold ${selected ? 'text-primary-700 dark:text-aqua-300' : 'text-slate-800 dark:text-slate-100'}`}>
                {opt.label}
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-400">{opt.desc}</p>
            </div>
            {selected && (
              <span className="ml-auto rounded-full bg-primary-600 px-2.5 py-0.5 text-[10px] font-bold text-white">
                Active
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

export default AnalysisTypeSelector
