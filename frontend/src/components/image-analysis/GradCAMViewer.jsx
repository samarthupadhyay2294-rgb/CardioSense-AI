import React from 'react'
import { ImageIcon, Eye } from 'lucide-react'

function GradCAMViewer({ imageUrl, gradcamUrl, prediction }) {
  const [tab, setTab] = React.useState('overlay')
  const [imgError, setImgError] = React.useState(false)

  if (!gradcamUrl) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Eye className="h-4 w-4 text-slate-500 dark:text-slate-400" />
        <p className="font-medium text-slate-800 dark:text-slate-100">Grad-CAM Explanation</p>
        <span className="text-xs text-slate-400 dark:text-slate-400">
          Target class: {prediction}
        </span>
      </div>

      <div className="flex gap-2" role="tablist">
        <button
          role="tab"
          onClick={() => setTab('overlay')}
          className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
            tab === 'overlay'
              ? 'border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-aqua-300'
              : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800'
          }`}
        >
          Overlay
        </button>
        <button
          role="tab"
          onClick={() => setTab('heatmap')}
          className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
            tab === 'heatmap'
              ? 'border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-aqua-300'
              : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800'
          }`}
        >
          Heatmap
        </button>
        <button
          role="tab"
          onClick={() => setTab('original')}
          className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
            tab === 'original'
              ? 'border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-aqua-300'
              : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800'
          }`}
        >
          Original
        </button>
      </div>

      <div className="relative flex justify-center rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
        {!imgError ? (
          <img
            src={tab === 'overlay' ? gradcamUrl : tab === 'original' ? imageUrl : gradcamUrl}
            alt={tab === 'overlay' ? 'Grad-CAM overlay' : tab === 'heatmap' ? 'Grad-CAM heatmap' : 'ECG image'}
            className="max-h-80 max-w-full rounded-lg object-contain"
            onError={(e) => {
              e.target.onerror = null
              setImgError(true)
            }}
          />
        ) : (
          <div className="flex flex-col items-center gap-2 py-8 text-slate-400">
            <ImageIcon className="h-10 w-10" />
            <span className="text-sm">Image not available</span>
          </div>
        )}
      </div>

      <p className="text-xs italic text-slate-400 dark:text-slate-500">
        Highlight intensity reflects how strongly each image region contributed to the model's
        prediction. Grad-CAM visualizations are not clinical findings.
      </p>
    </div>
  )
}

export default GradCAMViewer
