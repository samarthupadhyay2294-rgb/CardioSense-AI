import React from 'react'
import { Link } from 'react-router-dom'
import { HeartPulse, ShieldCheck } from 'lucide-react'

function Footer() {
  return (
    <footer className="border-t border-slate-200/70 bg-white/60 dark:border-slate-800 dark:bg-slate-900/60">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row">
          <div className="max-w-sm">
            <Link to="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-700 to-aqua-500 text-white">
                <HeartPulse className="h-4 w-4" />
              </span>
              <span className="font-display text-base font-bold text-slate-900 dark:text-white">
                CardioSense <span className="text-aqua-600 dark:text-aqua-400">AI</span>
              </span>
            </Link>
            <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
              Intelligent ECG Analysis. Clearer Cardiac Insights.
            </p>
          </div>
          <div className="flex flex-wrap gap-8">
            <div>
              <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Product</h4>
              <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
                <li><Link className="hover:text-primary-600" to="/dashboard">Dashboard</Link></li>
                <li><Link className="hover:text-primary-600" to="/analyze">Analyze ECG</Link></li>
                <li><Link className="hover:text-primary-600" to="/history">History</Link></li>
                <li><Link className="hover:text-primary-600" to="/model">Model</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Resources</h4>
              <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
                <li><Link className="hover:text-primary-600" to="/help">Documentation</Link></li>
                <li><Link className="hover:text-primary-600" to="/settings">Settings</Link></li>
                <li><Link className="hover:text-primary-600" to="/analytics">Analytics</Link></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8 flex items-start gap-2 rounded-xl bg-slate-50 p-4 text-xs leading-relaxed text-slate-500 dark:bg-slate-800/50 dark:text-slate-400">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal-500" />
          <p>
            CardioSense AI provides AI-generated ECG signal analysis for research and decision-support purposes.
            It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional.
          </p>
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-slate-200/70 pt-4 dark:border-slate-800">
          <p className="text-xs text-slate-400">© {new Date().getFullYear()} CardioSense AI. Research &amp; decision support only.</p>
          <p className="text-xs text-slate-400">Model v1.0 · ECGCNN · PTB-XL</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
