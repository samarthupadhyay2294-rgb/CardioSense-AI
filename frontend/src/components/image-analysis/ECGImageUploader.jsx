import React from 'react'
import { UploadCloud, FileCheck, X, Image as ImageIcon, FileWarning } from 'lucide-react'

const ACCEPTED = 'image/png,image/jpeg,image/jpg'
const MAX_SIZE = 20 * 1024 * 1024

function ECGImageUploader({ onFileSelect, selected }) {
  const [error, setError] = React.useState(null)

  const validate = (file) => {
    const ext = ('.' + (file.name.split('.').pop() || '').toLowerCase()).replace('..', '.')
    if (!['.png', '.jpg', '.jpeg'].includes(ext)) {
      setError(`Unsupported file type: ${ext}. Expected PNG, JPG, or JPEG.`)
      return null
    }
    if (!file.type.startsWith('image/')) {
      setError(`File is not a recognized image (${file.type}).`)
      return null
    }
    if (file.size === 0) {
      setError('The selected image is empty.')
      return null
    }
    if (file.size > MAX_SIZE) {
      setError(`Image exceeds the maximum allowed size of 20 MB.`)
      return null
    }
    return file
  }

  const handleFiles = (list) => {
    setError(null)
    const file = list[0]
    const valid = validate(file)
    if (!valid) return
    onFileSelect(valid)
  }

  const onDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }

  const removeFile = () => onFileSelect(null)

  return (
    <div>
      {!selected ? (
        <div
          onDragOver={(e) => {
            e.preventDefault()
            e.dataTransfer.dropEffect = 'copy'
          }}
          onDragLeave={() => {}}
          onDrop={onDrop}
          className="flex min-h-[240px] flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center transition-colors hover:border-primary-300 hover:bg-primary-50 dark:border-slate-600 dark:bg-slate-800/50"
        >
          <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-aqua-500 text-white shadow-glow">
            <ImageIcon className="h-7 w-7" />
          </span>
          <div>
            <p className="font-display text-lg font-semibold text-slate-800 dark:text-white">
              Drag &amp; drop an ECG image here
            </p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              PNG, JPG, or JPEG · up to 20 MB
            </p>
          </div>
          <label className="btn-primary">
            <UploadCloud className="h-4 w-4" />
            Browse files
            <input
              type="file"
              accept={ACCEPTED}
              className="hidden"
              onChange={(e) => {
                if (e.target.files.length > 0) handleFiles(Array.from(e.target.files))
                e.target.value = ''
              }}
            />
          </label>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-600 dark:bg-teal-500/10 dark:text-teal-400">
              <FileCheck className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">{selected.name}</p>
              <p className="text-xs text-slate-400">
                {(selected.size / 1024).toFixed(1)} KB · {selected.type || 'image/*'}
              </p>
            </div>
            <button
              onClick={removeFile}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-red-500 dark:hover:bg-slate-700"
              aria-label={`Remove ${selected.name}`}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <label className="btn-secondary !py-1.5 !text-xs">
            <UploadCloud className="h-4 w-4" />
            Change image
            <input
              type="file"
              accept={ACCEPTED}
              className="hidden"
              onChange={(e) => {
                if (e.target.files.length > 0) handleFiles(Array.from(e.target.files))
                e.target.value = ''
              }}
            />
          </label>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-start gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
          <FileWarning className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}

export default ECGImageUploader
