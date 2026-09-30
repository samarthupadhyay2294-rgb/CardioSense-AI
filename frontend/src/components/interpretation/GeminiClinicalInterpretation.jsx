import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BrainCircuit,
  AlertTriangle,
  Loader2,
  RefreshCw,
  Info,
  Activity,
  ShieldCheck,
  X,
} from 'lucide-react'
import { Card, CardHeader } from '../Card'
import { api } from '../../services/api'

function GeminiClinicalInterpretation({ analysisId, isImage = false }) {
  const [interpretation, setInterpretation] = React.useState(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState(null)
  const [retryCount, setRetryCount] = React.useState(0)

  React.useEffect(() => {
    if (!analysisId) return
    fetchInterpretation()
  }, [analysisId, retryCount])

  const fetchInterpretation = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.getGeminiInterpretation(analysisId)
      if (result.success && result.interpretation) {
        setInterpretation(result.interpretation)
      } else {
        setError(result.error?.message || 'Interpretation unavailable')
      }
    } catch (e) {
      setError('Clinical interpretation is temporarily unavailable')
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount((prev) => prev + 1)
  }

  if (loading && !interpretation) {
    return (
      <Card>
        <CardHeader
          title="Clinical Interpretation"
          icon={BrainCircuit}
        />
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary-500 dark:text-aqua-400" />
          <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
            Generating clinical interpretation...
          </p>
        </div>
      </Card>
    )
  }

  if (error && !interpretation) {
    return (
      <Card>
        <CardHeader
          title="Clinical Interpretation"
          icon={BrainCircuit}
        />
        <div className="rounded-xl bg-amber-50 p-4 text-sm text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="flex-1">
              <p className="font-medium">Interpretation Unavailable</p>
              <p className="mt-1 text-xs">{error}</p>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                Your original CardioSense ECG prediction is still available above.
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleRetry}
          className="mt-4 btn-secondary w-full"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      </Card>
    )
  }

  if (!interpretation) {
    return null
  }

  return (
    <Card>
      <CardHeader
        title="Clinical Interpretation"
        icon={BrainCircuit}
      />
      <div className="space-y-6">
        {/* Summary */}
        {interpretation.summary && (
          <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/50">
            <p className="text-sm text-slate-700 dark:text-slate-300">
              {interpretation.summary}
            </p>
          </div>
        )}

        {/* Primary Finding */}
        {interpretation.primary_finding && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-100">
              <Activity className="h-4 w-4 text-primary-500 dark:text-aqua-400" />
              Detected Finding
            </h3>
            <div className="rounded-xl border-l-4 border-primary-500 bg-primary-50 p-4 dark:border-aqua-400 dark:bg-primary-500/10">
              <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                {interpretation.primary_finding}
              </p>
            </div>
          </div>
        )}

        {/* Interpretation Confidence */}
        {(interpretation.interpretation_confidence || interpretation.confidence_interpretation) && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-100">
              <Info className="h-4 w-4 text-blue-500" />
              Interpretation Confidence
            </h3>
            <div className="inline-flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 dark:bg-blue-500/10 dark:text-blue-400">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              {interpretation.interpretation_confidence || interpretation.confidence_interpretation}
            </div>
          </div>
        )}

        {/* Possible Clinical Associations */}
        {interpretation.possible_clinical_associations &&
          interpretation.possible_clinical_associations.length > 0 && (
            <div>
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-100">
                <ShieldCheck className="h-4 w-4 text-teal-500" />
                Possible Clinical Associations
              </h3>
              <div className="space-y-3">
                {interpretation.possible_clinical_associations.map((assoc, index) => {
                  const name = typeof assoc === 'string' ? assoc : (assoc.name || assoc.condition || assoc.title || 'Possible Association')
                  const explanation = typeof assoc === 'object' ? assoc.explanation : ''
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
                    >
                      <p className="font-display text-sm font-semibold text-slate-800 dark:text-slate-100">
                        {name}
                      </p>
                      {explanation && explanation !== name && (
                        <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">
                          {explanation}
                        </p>
                      )}
                      <div className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-700 dark:bg-teal-500/10 dark:text-teal-400">
                        <span className="h-1.5 w-1.5 rounded-full bg-teal-500" />
                        Possible Association
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          )}

        {/* Why Was This Flagged */}
        {interpretation.why_flagged && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-100">
              <Info className="h-4 w-4 text-blue-500" />
              Why Was This Flagged?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {interpretation.why_flagged}
            </p>
          </div>
        )}

        {/* What Does This Mean */}
        {interpretation.what_it_means && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-100">
              <Info className="h-4 w-4 text-blue-500" />
              What Does This Mean?
            </h3>
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/50">
              <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-line">
                {interpretation.what_it_means}
              </p>
            </div>
          </div>
        )}

        {/* Limitations and Disclaimer removed from display per user request */}
      </div>
    </Card>
  )
}

export default GeminiClinicalInterpretation
