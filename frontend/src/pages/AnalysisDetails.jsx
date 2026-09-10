import React from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  Activity,
  Trash2,
  ChevronLeft,
  Download,
  Radio,
  Waves,
  BrainCircuit,
  Gauge,
  FileText,
  AlertTriangle,
} from 'lucide-react'
import { api } from '../services/api'
import { Card, CardHeader, LoadingState, ErrorState } from '../components/Card'
import ECGChart from '../components/ecg/ECGChart'
import ProbabilityChart from '../components/results/ProbabilityChart'
import {
  formatDate,
  formatDuration,
  formatConfidence,
  getClassColor,
  signalQualityBadge,
} from '../utils/helpers'

const LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

function AnalysisDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)
  const [deleting, setDeleting] = React.useState(false)

  React.useEffect(() => {
    api.getAnalysis(id).then(setAnalysis).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!window.confirm('Delete this analysis?')) return
    setDeleting(true)
    try {
      await api.deleteAnalysis(id)
      navigate('/history')
    } catch (e) {
      setError(e.message)
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <LoadingState message="Loading analysis details..." />
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!analysis) return null

  const color = getClassColor(analysis.prediction)
  const quality = signalQualityBadge(analysis.signal_quality)
  const signal = analysis.signal_data || []
  const leadStats = analysis.ecg_statistics || {}

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link to="/history" className="btn-ghost !px-3 !py-2">
            <ChevronLeft className="h-4 w-4" />
            History
          </Link>
          <h1 className="section-title">Analysis Details</h1>
        </div>
        <div className="flex items-center gap-2">
          <a href={api.getReportUrl(analysis.id)} target="_blank" rel="noreferrer" className="btn-secondary">
            <Download className="h-4 w-4" />
            PDF
          </a>
          <Link to={`/results/${analysis.id}`} className="btn-secondary">
            <Activity className="h-4 w-4" />
            Results view
          </Link>
          <button className="btn-secondary !text-red-600" onClick={handleDelete} disabled={deleting}>
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className={`card border-l-4 p-6 ${color.border}`}>
        <div className="flex flex-wrap items-center gap-4">
          <span className={`flex h-14 w-14 items-center justify-center rounded-2xl ${color.bg} ${color.text} ${color.darkBg}`}>
            <Activity className="h-7 w-7" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Analysis #{analysis.id}</p>
            <p className="font-display text-xl font-bold text-slate-900 dark:text-white">{analysis.prediction}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {analysis.file_name} · {formatDate(analysis.created_at)}
            </p>
          </div>
          <div className="text-right">
            <p className={`font-display text-2xl font-extrabold ${color.text}`}>
              {formatConfidence(analysis.confidence)}
            </p>
            <span className={`badge mt-1 ${quality.cls}`}>{quality.label}</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="ECG Waveform" subtitle="12-lead recording" icon={Waves} />
          <ECGChart signal={signal} leadNames={LEAD_NAMES.slice(0, signal.length)} height={380} />
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Probabilities" icon={Gauge} />
            <ProbabilityChart probabilities={analysis.probabilities} prediction={analysis.prediction} />
          </Card>

          <Card>
            <CardHeader title="Record Information" icon={Radio} />
            <div className="space-y-2.5">
              {[
                ['Model version', analysis.model_version],
                ['Sampling rate', `${analysis.sampling_rate} Hz`],
                ['Duration', formatDuration(analysis.duration)],
                ['Leads', String(analysis.num_leads)],
                ['Signal quality', quality.label],
                ['Processing time', `${(analysis.processing_time || 0).toFixed(3)} s`],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between border-b border-slate-100 pb-2 last:border-0 dark:border-slate-800">
                  <span className="text-sm text-slate-500 dark:text-slate-400">{k}</span>
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{v}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {analysis.explainability && !analysis.explainability.error && (
        <Card>
          <CardHeader title="Explainability" subtitle="Lead importance from Integrated Gradients" icon={BrainCircuit} />
          <div className="grid grid-cols-2 gap-x-8 gap-y-2.5 sm:grid-cols-3 md:grid-cols-4">
            {Object.entries(analysis.explainability.lead_importance || {})
              .sort((a, b) => b[1] - a[1])
              .map(([lead, imp]) => (
                <div key={lead} className="flex items-center gap-2">
                  <span className="w-9 text-xs font-semibold text-slate-500 dark:text-slate-400">{lead}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                    <div className="h-full rounded-full bg-gradient-to-r from-aqua-500 to-teal-500" style={{ width: `${imp * 100}%` }} />
                  </div>
                  <span className="w-11 text-right text-xs text-slate-400">{(imp * 100).toFixed(1)}%</span>
                </div>
              ))}
          </div>
          <p className="mt-4 text-xs italic text-slate-400">
            Highlighted regions represent signal areas that contributed to the model prediction. They should not be
            interpreted as a clinical diagnosis.
          </p>
        </Card>
      )}

      <Card>
        <CardHeader title="Per-lead Statistics" subtitle="Mean, standard deviation, min, and max per lead" icon={FileText} />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-400">
                <th className="px-4 py-2.5">Lead</th>
                <th className="px-4 py-2.5">Mean</th>
                <th className="px-4 py-2.5">Std</th>
                <th className="px-4 py-2.5">Min</th>
                <th className="px-4 py-2.5">Max</th>
                <th className="px-4 py-2.5">RMS</th>
              </tr>
            </thead>
            <tbody>
              {LEAD_NAMES.slice(0, signal.length).map((lead) => {
                const s = leadStats[lead]
                if (!s) return null
                return (
                  <tr key={lead} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                    <td className="px-4 py-2.5 font-semibold text-slate-700 dark:text-slate-200">{lead}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{s.mean.toFixed(4)}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{s.std.toFixed(4)}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{s.min.toFixed(4)}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{s.max.toFixed(4)}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{s.rms.toFixed(4)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="flex items-start gap-2 rounded-xl bg-amber-50 p-4 text-xs leading-relaxed text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
        CardioSense AI provides AI-generated ECG signal analysis for research and decision-support purposes. It is not a
        medical diagnosis and does not replace evaluation by a qualified healthcare professional.
      </div>
    </div>
  )
}

export default AnalysisDetails
