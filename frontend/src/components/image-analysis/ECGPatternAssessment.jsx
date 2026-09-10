import React from 'react'
import {
  Layers,
  ListOrdered,
  FileText,
  Stethoscope,
  CircleAlert,
  Activity,
  ListChecks,
} from 'lucide-react'
import { Card, CardHeader, EmptyState } from '../Card'
import { formatConfidence, humanReadableLabel, GROUP_ORDER } from '../../utils/helpers'

const GROUP_COLORS = {
  Normal: { text: 'text-emerald-600', bar: 'from-emerald-400 to-teal-500' },
  Supraventricular: { text: 'text-blue-600', bar: 'from-blue-400 to-cyan-500' },
  Ventricular: { text: 'text-red-600', bar: 'from-red-400 to-rose-500' },
  Fusion: { text: 'text-purple-600', bar: 'from-purple-400 to-fuchsia-500' },
  'Other/Unclassifiable': { text: 'text-slate-600', bar: 'from-slate-400 to-slate-500' },
}

function groupColor(group) {
  return GROUP_COLORS[group] || GROUP_COLORS['Other/Unclassifiable']
}

function GroupBar({ group, value, dominant }) {
  const color = groupColor(group)
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className={`text-sm font-medium ${dominant ? 'font-bold' : ''} text-slate-700 dark:text-slate-200`}>
          {group}
          {dominant && (
            <span className="ml-2 rounded-full bg-primary-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-primary-700 dark:bg-primary-500/15 dark:text-aqua-400">
              dominant
            </span>
          )}
        </span>
        <span className={`text-sm font-semibold ${color.text}`}>{formatConfidence(value)}</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color.bar} transition-all duration-700`}
          style={{ width: `${Math.min(value * 100, 100)}%` }}
        />
      </div>
    </div>
  )
}

function SubclassBar({ item, primary }) {
  const pct = item.probability * 100
  return (
    <div className="rounded-xl border border-slate-100 p-3 dark:border-slate-800">
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <p className={`truncate text-sm ${primary ? 'font-bold text-primary-700 dark:text-aqua-400' : 'font-medium text-slate-700 dark:text-slate-200'}`}>
            {item.human_readable_label}
          </p>
          <p className="text-xs text-slate-400">{item.group}</p>
        </div>
        <span className="shrink-0 text-sm font-semibold text-slate-800 dark:text-slate-100">
          {formatConfidence(item.probability)}
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${primary ? 'bg-gradient-to-r from-primary-500 to-aqua-500' : 'bg-slate-300 dark:bg-slate-600'}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  )
}

function NumberedItem({ index, children }) {
  return (
    <li className="flex items-start gap-3">
      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-500/15 dark:text-aqua-400">
        {index}
      </span>
      <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">{children}</p>
    </li>
  )
}

export default function ECGPatternAssessment({ analysis, showDisclaimer = true }) {
  const groupProbs = analysis.group_probabilities || {}
  const subclassResults = analysis.subclass_results || []
  const dominantGroup = analysis.dominant_group
  const patternSummary = analysis.pattern_summary
  const nextSteps = analysis.recommended_next_steps || analysis.next_steps || []
  const medicalDisclaimer = showDisclaimer ? analysis.medical_disclaimer : ''
  const primaryLabel = analysis.primary_label || humanReadableLabel(analysis.primary_prediction)

  if (subclassResults.length === 0) {
    return (
      <Card>
        <CardHeader
          title="ECG Pattern Assessment"
          subtitle="Subclass probabilities are unavailable"
          icon={Layers}
        />
        <EmptyState
          icon={Layers}
          title="No probability data"
          message="This analysis has no stored model probabilities."
        />
      </Card>
    )
  }

  const sortedGroups = GROUP_ORDER.filter((g) => groupProbs[g] !== undefined)
    .map((g) => ({ group: g, value: groupProbs[g] }))
    .sort((a, b) => b.value - a.value)

  return (
    <>
      <Card>
        <CardHeader
          title="Predicted ECG Pattern"
          subtitle="Highest-probability ECG subclass from the model output"
          icon={Activity}
        />
        <div className="rounded-2xl border border-primary-200 bg-primary-50/60 p-5 dark:border-primary-500/30 dark:bg-primary-500/10">
          <p className="text-3xl font-bold text-primary-700 dark:text-aqua-300">
            {primaryLabel || 'N/A'}
          </p>
          {dominantGroup && (
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
              Dominant ECG group: <span className="font-semibold">{dominantGroup}</span>
            </p>
          )}
        </div>
      </Card>

      <Card>
        <CardHeader
          title="ECG Pattern Groups"
          subtitle="Aggregated from the model's 15 subclass probabilities"
          icon={Layers}
          action={
            analysis.distribution_verified === false ? (
              <span className="badge border border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400">
                Distribution not verified
              </span>
            ) : (
              <span className="badge border border-slate-200 text-slate-600 dark:border-slate-600 dark:text-slate-300">
                {Object.keys(groupProbs).length} groups
              </span>
            )
          }
        />
        <div className="space-y-4">
          {sortedGroups.map(({ group, value }) => (
            <GroupBar
              key={group}
              group={group}
              value={value}
              dominant={group === dominantGroup}
            />
          ))}
        </div>
        <p className="mt-4 flex items-start gap-1.5 text-xs leading-relaxed text-slate-400 dark:text-slate-500">
          <CircleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          These values are aggregated model pattern probabilities, not disease risk or
          diagnostic likelihood.
        </p>
      </Card>

      <Card>
        <CardHeader
          title="ECG Subclass Probabilities"
          subtitle="All 15 ECG subclasses, sorted from highest to lowest probability"
          icon={ListOrdered}
        />
        <div className="grid gap-3 md:grid-cols-2">
          {subclassResults.map((item) => (
            <SubclassBar
              key={item.raw_class}
              item={item}
              primary={item.raw_class === analysis.primary_prediction}
            />
          ))}
        </div>
        <p className="mt-4 flex items-start gap-1.5 text-xs leading-relaxed text-slate-400 dark:text-slate-500">
          <CircleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          These are the model's classification probabilities for the ECG subclasses.
          They are not disease probabilities and should not be interpreted as a clinical
          diagnosis.
        </p>
      </Card>

      <Card>
        <CardHeader
          title="ECG Pattern Summary"
          subtitle="User-friendly interpretation of the complete probability distribution"
          icon={FileText}
        />
        {patternSummary ? (
          <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-200">
            {patternSummary}
          </p>
        ) : (
          <p className="text-sm text-slate-400">
            A pattern summary is not available for this analysis.
          </p>
        )}
      </Card>

      <Card>
        <CardHeader
          title="Recommended Next Steps"
          subtitle="Guidance based on the predicted ECG pattern and the full probability distribution"
          icon={ListChecks}
        />
        {nextSteps.length === 0 ? (
          <p className="text-sm text-slate-400">No next-step guidance is available.</p>
        ) : (
          <ol className="space-y-3">
            {nextSteps.map((step, i) => (
              <NumberedItem key={i} index={i + 1}>
                {step}
              </NumberedItem>
            ))}
          </ol>
        )}
        <div className="mt-5 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400">
          <Stethoscope className="mt-0.5 h-4 w-4 shrink-0" />
          <p>
            These recommendations are informational and do not prescribe medication, dosage,
            or treatment. Any medical decision must be made by a qualified healthcare
            professional.
          </p>
        </div>
      </Card>

      {medicalDisclaimer && (
        <Card>
          <CardHeader
            title="Medical Disclaimer"
            subtitle="Important information about this AI-based assessment"
            icon={CircleAlert}
          />
          <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            {medicalDisclaimer}
          </p>
        </Card>
      )}
    </>
  )
}
