import React from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  Download,
  Trash2,
  ChevronLeft,
  BrainCircuit,
  AlertTriangle,
  ImageIcon,
} from 'lucide-react'
import { api } from '../services/api'
import { Card, CardHeader, LoadingState, ErrorState } from '../components/Card'
import ECGChart from '../components/ecg/ECGChart'
import Assistant from '../components/assistant/Assistant'
import GradCAMViewer from '../components/image-analysis/GradCAMViewer'
import ECGPatternAssessment from '../components/image-analysis/ECGPatternAssessment'
import {
  formatDate,
  formatDuration,
  formatConfidence,
  getClassColor,
  signalQualityBadge,
  humanReadableLabel,
} from '../utils/helpers'

const LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

function Results() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = React.useState(null)
  const [summary, setSummary] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)
  const [deleting, setDeleting] = React.useState(false)

  React.useEffect(() => {
    const load = async () => {
      try {
        // Try image endpoint first - it enriches image analyses with interpretation fields
        let a = null
        let isImg = false
        try {
          a = await api.getImageAnalysis(id)
          isImg = true
        } catch (_) {
          // If image endpoint fails (404), try signal endpoint
          a = await api.getAnalysis(id)
          isImg = false
        }
        setAnalysis(a)
        if (isImg) {
          api.getImageSummary(id).then((s) => setSummary(s.summary)).catch(() => {})
        } else {
          api.getSummary(id).then((s) => setSummary(s.summary)).catch(() => {})
        }
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
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

  if (loading) return <LoadingState message="Loading analysis..." />
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!analysis) return null

  const isImage = analysis.analysis_type === 'image'
  const reportUrl = isImage ? api.getImageReportUrl(analysis.id) : api.getReportUrl(analysis.id)

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link to="/history" className="btn-ghost !px-3 !py-2">
            <ChevronLeft className="h-4 w-4" />
            History
          </Link>
          <h1 className="section-title">Analysis #{analysis.id}</h1>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={reportUrl}
            target="_blank"
            rel="noreferrer"
            className="btn-secondary"
          >
            <Download className="h-4 w-4" />
            PDF Report
          </a>
          <button className="btn-secondary !text-red-600" onClick={handleDelete} disabled={deleting}>
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      </div>

      {isImage ? (
        <ImageResults analysis={analysis} />
      ) : (
        <SignalResults analysis={analysis} />
      )}

      <Assistant analysisId={analysis.id} isImage={isImage} />
    </div>
  )
}

function ImageResults({ analysis }) {
  return (
    <div className="space-y-6">
      {/* 1. ECG Image */}
      {analysis.image_path && (
        <Card>
          <CardHeader
            title="ECG Image"
            subtitle="The uploaded image analyzed by the AI"
            icon={ImageIcon}
          />
          <img
            src={api.getImageUrl(analysis.id)}
            alt="ECG uploaded"
            className="max-h-96 w-full rounded-xl border border-slate-200 object-contain dark:border-slate-600"
            onError={(e) => { e.target.onerror = null; e.target.src = '' }}
          />
        </Card>
      )}

      {/* Predicted pattern, groups, subclass probabilities, summary, and next steps */}
      <ECGPatternAssessment analysis={analysis} showDisclaimer={false} />

      {/* Grad-CAM */}
      {analysis.gradcam_available && (
        <Card>
          <CardHeader
            title="Grad-CAM"
            subtitle="Image regions the AI considered most influential for the prediction"
            icon={BrainCircuit}
          />
          <GradCAMViewer
            imageUrl={api.getImageUrl(analysis.id)}
            gradcamUrl={api.getGradcamUrl(analysis.id)}
            prediction={analysis.primary_label || humanReadableLabel(analysis.primary_prediction)}
          />
        </Card>
      )}

      {/* Medical Disclaimer */}
      {analysis.medical_disclaimer && (
        <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-relaxed text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <p>{analysis.medical_disclaimer}</p>
        </div>
      )}
    </div>
  )
}

function SignalResults({ analysis }) {
  const color = getClassColor(analysis.prediction)
  const quality = signalQualityBadge(analysis.signal_quality)
  const isNormal = analysis.prediction_code === 'NORM'
  const signal = analysis.signal_data || []
  const highlight =
    analysis.explainability && !analysis.explainability.error
      ? analysis.explainability.time_importance
      : null
  const [showExplain, setShowExplain] = React.useState(false)

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className={`card overflow-hidden border-l-4 p-6 ${color.border}`}>
          <div className="flex flex-wrap items-center gap-4">
            <span
              className={`flex h-16 w-16 items-center justify-center rounded-2xl ${color.bg} ${color.text} ${color.darkBg}`}
            >
              <Activity className="h-8 w-8" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Prediction
              </p>
              <p className="font-display text-2xl font-bold text-slate-900 dark:text-white">
                {analysis.prediction}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">{analysis.file_name}</p>
            </div>
            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Confidence
              </p>
              <p className={`font-display text-3xl font-extrabold ${color.text}`}>
                {formatConfidence(analysis.confidence)}
              </p>
              <span className={`badge mt-1 ${quality.cls}`}>{quality.label} signal</span>
            </div>
          </div>

          {isNormal ? (
            <div className="mt-4 flex items-center gap-2 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400">
              <AlertTriangle className="h-4 w-4" />
              No significant abnormalities detected by the model.
            </div>
          ) : (
            <div className="mt-4 flex items-start gap-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <p>
                The model detected {analysis.prediction.toLowerCase()}. This is an
                AI-generated finding for decision support — seek professional medical
                evaluation for any concerns.
              </p>
            </div>
          )}
        </div>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="ECG Waveform"
            subtitle="12-lead recording with zoom, pan, and lead inspection"
            icon={Activity}
            action={
              highlight ? (
                <button
                  className="btn-secondary !py-1.5 !text-xs"
                  onClick={() => setShowExplain((s) => !s)}
                >
                  <BrainCircuit className="h-3.5 w-3.5" />
                  {showExplain ? 'Hide' : 'Show'} importance
                </button>
              ) : null
            }
          />
          <ECGChart signal={signal} leadNames={LEAD_NAMES.slice(0, signal.length)} highlight={showExplain ? highlight : null} height={460} />
        </Card>

        <Card>
          <CardHeader title="Signal Statistics" subtitle="Technical ECG data" icon={Activity} />
          <div className="space-y-3">
            {[
              ['Sampling rate', `${analysis.sampling_rate} Hz`],
              ['Duration', formatDuration(analysis.duration)],
              ['Leads', String(analysis.num_leads)],
              ['Signal quality', quality.label],
              ['Processing time', `${(analysis.processing_time || 0).toFixed(3)} s`],
              ['Analyzed', formatDate(analysis.created_at)],
            ].map(([k, v]) => (
              <div
                key={k}
                className="flex items-center justify-between border-b border-slate-100 pb-2 last:border-0 dark:border-slate-800"
              >
                <span className="text-sm text-slate-500 dark:text-slate-400">{k}</span>
                <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{v}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {analysis.warning && (
        <Card>
          <CardHeader title="Note" icon={AlertTriangle} />
          <p className="text-sm text-amber-700 dark:text-amber-400">{analysis.warning}</p>
        </Card>
      )}

      <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-relaxed text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
        <p>
          CardioSense AI provides AI-generated ECG signal analysis for research and
          decision-support purposes. It is not a medical diagnosis and does not replace
          evaluation by a qualified healthcare professional.
        </p>
      </div>
    </>
  )
}

export default Results
