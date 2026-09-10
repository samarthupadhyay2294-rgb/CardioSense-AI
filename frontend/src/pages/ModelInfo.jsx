import React from 'react'
import {
  BrainCircuit,
  Layers,
  Cpu,
  Gauge,
  Database,
  Clock,
  Waves,
  Activity,
  CheckCircle2,
  ImageIcon,
  Eye,
} from 'lucide-react'
import { api } from '../services/api'
import { Card, CardHeader, LoadingState, ErrorState } from '../components/Card'

const METRIC_COLORS = {
  'NORM AUC': '#16a34a',
  'MI AUC': '#dc2626',
  'STTC AUC': '#d97706',
  'CD AUC': '#2563eb',
  'HYP AUC': '#9333ea',
  'Mean Test AUC': '#0891b2',
}

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-2.5 last:border-0 dark:border-slate-800">
      <span className="text-sm text-slate-500 dark:text-slate-400">{label}</span>
      <span className="text-right text-sm font-semibold text-slate-800 dark:text-slate-100">{value}</span>
    </div>
  )
}

function ModelInfo() {
  const [info, setInfo] = React.useState(null)
  const [imageInfo, setImageInfo] = React.useState(null)
  const [status, setStatus] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [i, s] = await Promise.all([api.getModelInfo(), api.getModelStatus()])
      setInfo(i)
      setStatus(s)
      try {
        const img = await api.getImageModelInfo()
        setImageInfo(img)
      } catch (e) {
        setImageInfo(null)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    load()
  }, [])

  if (loading) return <LoadingState message="Loading model information..." />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!info) return null

  const architectureLayers = [
    ['Conv1d (7×32) + BatchNorm + ReLU', '32 × 500'],
    ['Conv1d (7×64) + BatchNorm + ReLU', '64 × 250'],
    ['Conv1d (7×128) + BatchNorm + ReLU', '128 × 125'],
    ['Conv1d (7×256) + BatchNorm + ReLU', '256 × 62'],
    ['AdaptiveAvgPool1d', '256 × 1'],
    ['Linear 256 → 128 → 5', '5'],
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="section-title">Model Information</h1>
          <p className="section-subtitle mt-1">Real architecture, configuration, and test metrics — nothing invented.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-400">
          <CheckCircle2 className="h-4 w-4" />
          {status && status.loaded ? 'Model loaded' : 'Model not loaded'} · {status?.device || 'cpu'}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Overview" icon={BrainCircuit} />
          <InfoRow label="Name" value={info.model_name} />
          <InfoRow label="Version" value={info.model_version} />
          <InfoRow label="Framework" value="PyTorch" />
          <InfoRow label="Architecture" value="1D CNN" />
          <InfoRow label="Parameters" value="338,725" />
          <InfoRow label="Loss function" value={info.training_config?.loss_function || 'BCEWithLogitsLoss'} />
          <InfoRow label="Optimizer" value={info.training_config?.optimizer || 'Adam'} />
          <InfoRow label="Epochs" value={info.training_config?.epochs || 30} />
          <InfoRow label="Learning rate" value={info.training_config?.learning_rate || 0.001} />
        </Card>

        <Card>
          <CardHeader title="Input Configuration" icon={Cpu} />
          <InfoRow label="Input shape" value={`${info.input_shape.join(' × ')}`} />
          <InfoRow label="Leads" value={`${info.num_leads} (standard 12-lead)`} />
          <InfoRow label="Sampling rate" value={`${info.sampling_rate} Hz`} />
          <InfoRow label="Signal length" value={`${info.signal_length} samples`} />
          <InfoRow label="Duration" value={`${info.signal_length / info.sampling_rate} seconds`} />
          <InfoRow label="Preprocessing" value="Bandpass 0.5–40 Hz + per-record z-score" />
          <InfoRow label="Bandpass order" value={info.preprocessing?.bandpass_order || 4} />
          <InfoRow label="Normalization" value={info.preprocessing?.normalization || 'per_record_zscore'} />
        </Card>

        <Card>
          <CardHeader title="Model Parameters" icon={Layers} />
          <InfoRow label="In channels" value={info.model_parameters?.in_channels || 12} />
          <InfoRow label="N classes" value={info.model_parameters?.n_classes || 5} />
          <InfoRow label="Conv kernel" value={info.model_parameters?.conv_kernel_size || 7} />
          <InfoRow label="Conv padding" value={info.model_parameters?.conv_padding || 3} />
          <InfoRow label="Pool size" value={info.model_parameters?.pool_size || 2} />
          <InfoRow label="Dropout" value={info.model_parameters?.dropout || 0.4} />
          <InfoRow label="FC units" value={info.model_parameters?.fc_units?.join(' → ') || '256 → 128 → 5'} />
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Diagnostic Classes" subtitle="PTB-XL superclasses" icon={Activity} />
          <div className="space-y-3">
            {info.classes.map((code) => (
              <div key={code} className="rounded-xl border border-slate-200 p-3 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm font-bold text-primary-600 dark:text-aqua-400">{code}</span>
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{info.class_names[code]}</span>
                </div>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{info.class_descriptions[code]}</p>
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-[11px] text-slate-400">Threshold</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-aqua-500 to-teal-500"
                      style={{ width: `${(info.thresholds[code] || 0.5) * 100}%` }}
                    />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                    {(info.thresholds[code] || 0.5).toFixed(3)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Architecture" subtitle="Layer-by-layer (from model_architecture.txt)" icon={Layers} />
            <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs text-slate-500 dark:bg-slate-800/50 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-2">Layer</th>
                    <th className="px-4 py-2 text-right">Output</th>
                  </tr>
                </thead>
                <tbody>
                  {architectureLayers.map(([layer, shape]) => (
                    <tr key={layer} className="border-t border-slate-100 dark:border-slate-800">
                      <td className="px-4 py-2 font-mono text-xs text-slate-600 dark:text-slate-300">{layer}</td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-slate-500 dark:text-slate-400">{shape}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <Card>
            <CardHeader title="Test Metrics" subtitle="AUC on held-out test split" icon={Gauge} />
            <div className="space-y-4">
              {Object.entries(info.test_metrics || {}).map(([label, value]) => {
                const isMean = label.startsWith('Mean')
                return (
                  <div key={label}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span className={isMean ? 'font-semibold text-slate-800 dark:text-slate-100' : 'text-slate-600 dark:text-slate-300'}>
                        {label.replace(' AUC', '')}
                      </span>
                      <span className="font-semibold" style={{ color: METRIC_COLORS[label] }}>
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${(value || 0) * 100}%`, backgroundColor: METRIC_COLORS[label] }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
            <p className="mt-4 flex items-center gap-1.5 text-xs text-slate-400">
              <Database className="h-3.5 w-3.5" />
              Trained on PTB-XL (18,885 records · 12-lead ECG). Metrics are from the original training notebook.
            </p>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader title="Preprocessing Pipeline" subtitle="The exact steps from preprocessing.py" icon={Waves} />
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            ['1 · Bandpass filter', `Butterworth order ${info.preprocessing?.bandpass_order || 4}, 0.5–40 Hz at 100 Hz`],
            ['2 · Normalize', 'Per-record z-score: (x − mean) / (std + 1e-8), computed per lead'],
            ['3 · Format', 'Transposed to (12, 1000) float32 tensor for the CNN'],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60">
              <p className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">{title}</p>
              <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">{desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {imageInfo && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-aqua-400">
              <ImageIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Image Analysis Model</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">EfficientNet-B0 — 15-class ECG image classifier</p>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <Card>
              <CardHeader title="Overview" icon={BrainCircuit} />
              <InfoRow label="Name" value={imageInfo.model_name} />
              <InfoRow label="Version" value={imageInfo.model_version} />
              <InfoRow label="Framework" value={imageInfo.framework} />
              <InfoRow label="Architecture" value={imageInfo.architecture} />
              <InfoRow label="Input size" value={`${imageInfo.input_size?.join(' × ')}`} />
              <InfoRow label="Channels" value="3 (RGB)" />
              <InfoRow label="Num classes" value={imageInfo.classes?.length} />
              <InfoRow label="Explainability" value={imageInfo.gradcam_supported ? 'Grad-CAM supported' : 'Not available'} />
            </Card>

            <Card>
              <CardHeader title="Classes" subtitle="15 diagnostic classes (AHA/PTB-XL single-letter codes)" icon={Activity} />
              <div className="grid grid-cols-3 gap-2">
                {imageInfo.classes.map((c) => (
                  <span key={c} className="rounded-lg bg-slate-100 px-2.5 py-1.5 text-center text-xs font-mono font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                    {c}
                  </span>
                ))}
              </div>
              <InfoRow label="Normalization" value="ImageNet mean/std" />
              <InfoRow label="Class mapping" value={JSON.stringify(imageInfo.class_mapping)} />
            </Card>

            <Card>
              <CardHeader title="Image Preprocessing" subtitle="Training-compatible transforms" icon={Cpu} />
              {[
                ['1 · Convert to RGB', 'PIL Image.convert("RGB")'],
                ['2 · Resize', `${imageInfo.input_size[0] + 20} × ${imageInfo.input_size[1] + 20}`],
                ['3 · CenterCrop', `${imageInfo.input_size.join(' × ')}`],
                ['4 · ToTensor', 'HWC → CHW, scale to [0, 1]'],
                ['5 · Normalize', 'ImageNet mean [0.485, 0.456, 0.406], std [0.229, 0.224, 0.225]'],
              ].map(([title, desc]) => (
                <div key={title} className="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/60">
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">{title}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
                </div>
              ))}
            </Card>
          </div>

          <Card>
            <CardHeader title="Model Card Metrics" subtitle="From model card / training (NOT calibrated clinical probabilities)" icon={Gauge} />
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Trained on a user-provided ECG image dataset (54,613 images). Validation Macro F1 = 0.7019.
              Metrics are limited to those recorded during original training.
            </p>
          </Card>
        </div>
      )}

      {!imageInfo && (
        <Card>
          <CardHeader title="Image Analysis Model" icon={ImageIcon} />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            The ECG image model is not loaded. Signal analysis remains fully available.
          </p>
        </Card>
      )}

      <div className="flex items-start gap-2 rounded-xl bg-amber-50 p-4 text-xs leading-relaxed text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
        <Clock className="mt-0.5 h-4 w-4 shrink-0" />
        This page displays only information verified against the actual model checkpoints, configurations, and training
        notebooks. Accuracy claims are limited to metrics recorded during original training. Neither model replaces
        evaluation by a qualified healthcare professional.
      </div>
    </div>
  )
}

export default ModelInfo
