import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud,
  FileCheck,
  Activity,
  ShieldCheck,
  FileWarning,
  Loader2,
  X,
  Info,
  FileText,
  Database,
  Image as ImageIcon,
  BrainCircuit,
} from 'lucide-react'
import { api } from '../services/api'
import { Card } from '../components/Card'
import AnalysisTypeSelector from '../components/analysis/AnalysisTypeSelector'
import ECGImageUploader from '../components/image-analysis/ECGImageUploader'
import ECGImagePreview from '../components/image-analysis/ECGImagePreview'

const ACCEPTED = '.hea,.dat,.mat,.csv,.npy,.txt'
const IMAGE_ACCEPTED = 'image/png,image/jpeg,image/jpg'
const MAX_SIZE = 20 * 1024 * 1024

const formatLabels = {
  hea: 'WFDB header',
  dat: 'WFDB data',
  mat: 'MATLAB',
  csv: 'CSV',
  npy: 'NumPy',
  txt: 'Text',
}

function SignalPanel({ files, setFiles, dragOver, setDragOver, onDrop, addFiles, removeFile, error, setError, uploading, analyze }) {
  return (
    <>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          onDrop(e)
          setDragOver(false)
        }}
        className={`flex min-h-[220px] flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
          dragOver
            ? 'border-primary-500 bg-primary-50 dark:border-aqua-400 dark:bg-primary-500/10'
            : 'border-slate-300 bg-slate-50 dark:border-slate-600 dark:bg-slate-800/50'
        }`}
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-aqua-500 text-white shadow-glow">
          <UploadCloud className="h-7 w-7" />
        </span>
        <div>
          <p className="font-display text-lg font-semibold text-slate-800 dark:text-white">
            Drag &amp; drop ECG files here
          </p>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            WFDB <code className="rounded bg-slate-200 px-1 py-0.5 text-xs dark:bg-slate-700">.hea + .dat</code>,{' '}
            <code className="rounded bg-slate-200 px-1 py-0.5 text-xs dark:bg-slate-700">.mat</code>,{' '}
            <code className="rounded bg-slate-200 px-1 py-0.5 text-xs dark:bg-slate-700">.csv</code>,{' '}
            <code className="rounded bg-slate-200 px-1 py-0.5 text-xs dark:bg-slate-700">.npy</code>,{' '}
            <code className="rounded bg-slate-200 px-1 py-0.5 text-xs dark:bg-slate-700">.txt</code>
          </p>
          <p className="mt-2 text-xs text-slate-400">12 leads · 1000 samples · up to 20 MB per file</p>
        </div>
        <label className="btn-primary">
          <FileText className="h-4 w-4" />
          Browse files
          <input
            type="file"
            multiple
            accept={ACCEPTED}
            className="hidden"
            onChange={(e) => {
              addFiles(e.target.files)
              e.target.value = ''
            }}
          />
        </label>
      </div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 space-y-2"
          >
            <p className="label">Selected files ({files.length})</p>
            {files.map((f, i) => {
              const ext = (f.name.split('.').pop() || '').toLowerCase()
              return (
                <div key={`${f.name}-${i}`} className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-600 dark:bg-teal-500/10 dark:text-teal-400">
                    <FileCheck className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">{f.name}</p>
                    <p className="text-xs text-slate-400">
                      {formatLabels[ext] || ext.toUpperCase()} · {(f.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => removeFile(i)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-red-500 dark:hover:bg-slate-700"
                    aria-label={`Remove ${f.name}`}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

function AnalyzeECG() {
  const navigate = useNavigate()
  const [analysisType, setAnalysisType] = React.useState('signal')
  const [files, setFiles] = React.useState([])
  const [imageFile, setImageFile] = React.useState(null)
  const [dragOver, setDragOver] = React.useState(false)
  const [uploading, setUploading] = React.useState(false)
  const [error, setError] = React.useState(null)

  const validateFiles = (list) => {
    const arr = Array.from(list)
    const invalid = arr.filter((f) => !ACCEPTED.includes('.' + (f.name.split('.').pop() || '').toLowerCase()))
    if (invalid.length > 0) {
      setError(`Unsupported file type: ${invalid.map((f) => f.name).join(', ')}`)
      return null
    }
    const tooBig = arr.filter((f) => f.size > MAX_SIZE)
    if (tooBig.length > 0) {
      setError(`File(s) exceed 20 MB: ${tooBig.map((f) => f.name).join(', ')}`)
      return null
    }
    const empty = arr.filter((f) => f.size === 0)
    if (empty.length > 0) {
      setError(`Empty file(s): ${empty.map((f) => f.name).join(', ')}`)
      return null
    }
    return arr
  }

  const addFiles = (list) => {
    setError(null)
    const valid = validateFiles(list)
    if (!valid) return
    const combined = [...files]
    valid.forEach((f) => {
      if (!combined.some((existing) => existing.name === f.name && existing.size === f.size)) {
        combined.push(f)
      }
    })
    setFiles(combined)
  }

  const removeSignalFile = (index) => {
    setFiles((f) => f.filter((_, i) => i !== index))
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }

  const analyze = async () => {
    if (analysisType === 'image') {
      if (!imageFile) {
        setError('Please select an ECG image to analyze.')
        return
      }
      setUploading(true)
      setError(null)
      try {
        const result = await api.analyzeECGImage(imageFile)
        if (result.success && result.analysis_id) {
          navigate(`/results/${result.analysis_id}`)
        } else {
          setError(result.message || 'Image analysis failed')
        }
      } catch (e) {
        setError(e.message)
      } finally {
        setUploading(false)
      }
      return
    }

    if (files.length === 0) {
      setError('Please add at least one file.')
      return
    }
    const hasHea = files.some((f) => f.name.endsWith('.hea'))
    const hasDat = files.some((f) => f.name.endsWith('.dat'))
    if (hasHea || hasDat) {
      if (!(hasHea && hasDat)) {
        setError('WFDB recordings need both the .hea and .dat files.')
        return
      }
    }

    setUploading(true)
    setError(null)
    try {
      const result = await api.analyzeECG(files)
      if (result.success && result.analysis_id) {
        navigate(`/results/${result.analysis_id}`)
      } else {
        setError(result.message || 'Analysis failed')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="text-center">
        <h1 className="section-title">Analyze ECG</h1>
        <p className="section-subtitle mt-2">
          Choose an analysis mode. Signal analysis and image analysis use independent models —
          they never combine or average predictions.
        </p>
      </div>

      <Card className="p-6">
        <AnalysisTypeSelector value={analysisType} onChange={setAnalysisType} />

        {analysisType === 'signal' ? (
          <SignalPanel
            files={files}
            setFiles={setFiles}
            dragOver={dragOver}
            setDragOver={setDragOver}
            onDrop={onDrop}
            addFiles={addFiles}
            removeFile={removeSignalFile}
            error={error}
            setError={setError}
            uploading={uploading}
            analyze={analyze}
          />
        ) : (
          <div className="space-y-4">
            <ECGImageUploader onFileSelect={setImageFile} selected={imageFile} accept={IMAGE_ACCEPTED} />
            {imageFile && <ECGImagePreview file={imageFile} />}
          </div>
        )}
      </Card>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-4 flex items-start gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400"
          >
            <FileWarning className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <Card className="p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck className="h-4 w-4 text-teal-500" />
            Files are validated for type, size, and format. Image analyses include real
            Grad-CAM when supported.
          </div>
          <button className="btn-primary" onClick={analyze} disabled={uploading}>
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing…
              </>
            ) : (
              <>
                <BrainCircuit className="h-4 w-4" />
                {analysisType === 'image' ? 'Analyze ECG Image' : 'Analyze ECG'}
              </>
            )}
          </button>
        </div>
      </Card>
    </div>
  )
}

export default AnalyzeECG
