export const CLASS_COLORS = {
  Normal: { text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', hex: '#16a34a', darkBg: 'dark:bg-emerald-500/10' },
  'Myocardial Infarction': { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', hex: '#dc2626', darkBg: 'dark:bg-red-500/10' },
  'ST/T Changes': { text: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', hex: '#d97706', darkBg: 'dark:bg-amber-500/10' },
  'Conduction Disturbance': { text: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', hex: '#2563eb', darkBg: 'dark:bg-blue-500/10' },
  Hypertrophy: { text: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200', hex: '#9333ea', darkBg: 'dark:bg-purple-500/10' },
}

export const PREDICTION_CODE_MAP = {
  NORM: 'Normal',
  MI: 'Myocardial Infarction',
  STTC: 'ST/T Changes',
  CD: 'Conduction Disturbance',
  HYP: 'Hypertrophy',
}

export const SUBCLASS_LABEL_MAP = {
  N: 'Normal Beat',
  L: 'Left Bundle Branch Block Beat',
  R: 'Right Bundle Branch Block Beat',
  e: 'Atrial Escape Beat',
  j: 'Junctional Escape Beat',
  A: 'Atrial Premature Beat',
  J: 'Junctional Premature Beat',
  S: 'Supraventricular Premature Beat',
  aa: 'Aberrated Atrial Premature Beat',
  V: 'Ventricular Premature Beat (PVC)',
  E: 'Ventricular Escape Beat',
  F: 'Fusion Beat',
  Q: 'Unclassifiable Beat',
  p: 'Paced Beat',
  f: 'Fusion/Paced Beat',
}

export const SUBCLASS_ORDER = ['N', 'L', 'R', 'e', 'j', 'A', 'J', 'S', 'aa', 'V', 'E', 'F', 'Q', 'p', 'f']

export const GROUP_DEFINITIONS = {
  Normal: ['N', 'L', 'R', 'e', 'j'],
  Supraventricular: ['A', 'J', 'S', 'aa'],
  Ventricular: ['V', 'E'],
  Fusion: ['F'],
  'Other/Unclassifiable': ['Q', 'p', 'f'],
}

export const GROUP_ORDER = ['Normal', 'Supraventricular', 'Ventricular', 'Fusion', 'Other/Unclassifiable']

export function humanReadableLabel(code) {
  if (!code) return ''
  return SUBCLASS_LABEL_MAP[code] || code
}

export function getClassColor(prediction) {
  return CLASS_COLORS[prediction] || {
    text: 'text-slate-600',
    bg: 'bg-slate-100',
    border: 'border-slate-200',
    hex: '#64748b',
    darkBg: 'dark:bg-slate-500/10',
  }
}

export function formatConfidence(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
  return `${(value * 100).toFixed(1)}%`
}

export function formatDate(iso) {
  if (!iso) return 'N/A'
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(seconds) {
  if (seconds === undefined || seconds === null) return 'N/A'
  return `${seconds.toFixed(1)} s`
}

export function signalQualityBadge(quality) {
  const map = {
    excellent: { label: 'Excellent', cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400' },
    good: { label: 'Good', cls: 'bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-400' },
    fair: { label: 'Fair', cls: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400' },
    poor: { label: 'Poor', cls: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400' },
  }
  return map[quality] || { label: quality, cls: 'bg-slate-100 text-slate-700 dark:bg-slate-500/15 dark:text-slate-400' }
}
