import React from 'react'

function ECGImagePreview({ file }) {
  const [preview, setPreview] = React.useState('')

  React.useEffect(() => {
    if (!file) {
      setPreview('')
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  if (!file) return null

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
      <p className="mb-3 label">Image preview (model resizes to 224×224)</p>
      <div className="relative flex justify-center">
        <img
          src={preview}
          alt="ECG preview"
          className="max-h-56 max-w-full rounded-lg border border-slate-200 object-contain dark:border-slate-600"
        />
      </div>
    </div>
  )
}

export default ECGImagePreview
