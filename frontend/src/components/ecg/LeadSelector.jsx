import React from 'react'

function LeadSelector({ leads, selected, onSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {leads.map((lead) => (
        <button
          key={lead}
          onClick={() => onSelect(lead)}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
            selected === lead
              ? 'bg-primary-600 text-white shadow-soft'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
          }`}
        >
          {lead}
        </button>
      ))}
    </div>
  )
}

export default LeadSelector
