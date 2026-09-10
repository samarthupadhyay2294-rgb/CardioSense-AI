import React from 'react'
import { Link } from 'react-router-dom'
import {
  Upload,
  FileText,
  BrainCircuit,
  HelpCircle,
  ShieldCheck,
  BookOpen,
  Terminal,
  Cpu,
  MessageSquareText,
  BarChart3,
} from 'lucide-react'
import { Card, CardHeader } from '../components/Card'

function Help() {
  const faqs = [
    {
      q: 'What file formats are supported?',
      a: 'You can upload WFDB recordings (.hea + .dat together), or single files in .mat, .csv, .npy, or .txt format. Files are validated for type, size (max 20 MB), number of leads (12), sampling rate (100 Hz), and signal length (1000 samples).',
    },
    {
      q: 'What happens to my uploaded ECG?',
      a: 'The signal is read, validated, then processed with the exact preprocessing pipeline used during training (bandpass filter 0.5–40 Hz and per-record z-score normalization). It is passed through the real trained model — predictions are never fabricated.',
    },
    {
      q: 'What do the predictions mean?',
      a: 'The model outputs probabilities for five PTB-XL diagnostic superclasses: Normal (NORM), Myocardial Infarction (MI), ST/T Changes (STTC), Conduction Disturbance (CD), and Hypertrophy (HYP). A per-class threshold (tuned on validation data) converts probabilities into detected labels.',
    },
    {
      q: 'Is this a medical diagnosis?',
      a: 'No. CardioSense AI provides AI-generated ECG signal analysis for research and decision-support purposes. It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional.',
    },
    {
      q: 'How is the "confidence" computed?',
      a: 'The confidence is the model probability for the primary (highest-probability detected) class. The full probability distribution across all classes is shown in the results view.',
    },
    {
      q: 'Can I export a report?',
      a: 'Yes. Every analysis can be exported as a branded PDF report containing the prediction, probability distribution, signal statistics, and explainability (when available).',
    },
  ]

  const topics = [
    { icon: Upload, title: 'Uploading ECGs', desc: 'Supported formats and validation rules.', to: '/analyze' },
    { icon: FileText, title: 'PDF Reports', desc: 'Export branded analysis reports.', to: '/results' },
    { icon: BrainCircuit, title: 'Model Details', desc: 'Architecture, configuration, and test metrics.', to: '/model' },
    { icon: BarChart3, title: 'Analytics', desc: 'Statistics from your analysis history.', to: '/analytics' },
    { icon: MessageSquareText, title: 'Assistant', desc: 'Ask questions about your analysis.', to: '/help' },
  ]

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="section-title">Help &amp; Documentation</h1>
        <p className="section-subtitle mt-1">Everything you need to understand CardioSense AI.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {topics.map((t) => (
          <Link key={t.title} to={t.to} className="card card-hover flex flex-col items-center gap-3 p-5 text-center">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-aqua-400">
              <t.icon className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{t.title}</p>
              <p className="mt-1 text-xs text-slate-400">{t.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader title="Frequently Asked Questions" subtitle="Common questions" icon={HelpCircle} />
        <div className="space-y-4">
          {faqs.map((f) => (
            <details key={f.q} className="group rounded-xl border border-slate-200 p-4 dark:border-slate-700">
              <summary className="flex cursor-pointer items-center justify-between text-sm font-semibold text-slate-800 dark:text-slate-100">
                {f.q}
                <span className="text-slate-400 transition-transform group-open:rotate-45">+</span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-slate-500 dark:text-slate-400">{f.a}</p>
            </details>
          ))}
        </div>
      </Card>

      <Card>
        <CardHeader title="Quick Start" subtitle="Analyze your first ECG in three steps" icon={BookOpen} />
        <div className="space-y-4">
          {[
            ['1', 'Open the Analyze page', 'Navigate to /analyze and drag & drop a 12-lead ECG file (or the .hea/.dat pair).'],
            ['2', 'Run the analysis', 'The backend validates, preprocesses, and runs the real model. Results appear in a few seconds.'],
            ['3', 'Explore & export', 'Inspect the waveform, probabilities, explainability, and statistics. Download the PDF report or revisit it from History.'],
          ].map(([n, title, desc]) => (
            <div key={n} className="flex gap-4">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-aqua-500 text-sm font-bold text-white">
                {n}
              </span>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</p>
                <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <CardHeader title="API Access" subtitle="FastAPI endpoints" icon={Terminal} />
        <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">
          The backend exposes a REST API with interactive Swagger documentation at{' '}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs dark:bg-slate-800">/docs</code>.
        </p>
        <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500 dark:bg-slate-800/50 dark:text-slate-400">
              <tr>
                <th className="px-4 py-2">Method</th>
                <th className="px-4 py-2">Endpoint</th>
                <th className="px-4 py-2">Purpose</th>
              </tr>
            </thead>
            <tbody className="font-mono text-xs">
              {[
                ['GET', '/api/health', 'Health & model status'],
                ['POST', '/api/ecg/analyze', 'Upload and analyze ECG'],
                ['GET', '/api/ecg/{id}', 'Fetch analysis'],
                ['GET', '/api/ecg/history', 'List analyses'],
                ['DELETE', '/api/ecg/{id}', 'Delete analysis'],
                ['GET', '/api/statistics', 'Aggregate statistics'],
                ['GET', '/api/model/info', 'Model information'],
                ['GET', '/api/model/status', 'Model runtime status'],
                ['GET', '/api/ecg/report/{id}', 'PDF report'],
                ['POST', '/api/ecg/{id}/summary', 'AI summary'],
                ['POST', '/api/ecg/{id}/assistant', 'Assistant Q&A'],
              ].map(([m, ep, p]) => (
                <tr key={ep} className="border-t border-slate-100 dark:border-slate-800">
                  <td className={`px-4 py-2 font-semibold ${m === 'POST' || m === 'DELETE' ? 'text-amber-600' : 'text-emerald-600'}`}>{m}</td>
                  <td className="px-4 py-2 text-slate-600 dark:text-slate-300">{ep}</td>
                  <td className="px-4 py-2 text-slate-400">{p}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-700 dark:bg-slate-900">
        <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-teal-500" />
        <div>
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">Medical disclaimer</p>
          <p className="mt-1 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
            CardioSense AI provides AI-generated ECG signal analysis for research and decision-support purposes.
            It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Help
