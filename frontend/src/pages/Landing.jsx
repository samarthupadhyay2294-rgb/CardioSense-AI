import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  HeartPulse,
  Activity,
  Upload,
  BrainCircuit,
  Sparkles,
  LineChart,
  BarChart3,
  ShieldCheck,
  FileText,
  MessageSquareText,
  ArrowRight,
  Cpu,
  Database,
  Layers,
  Eye,
  Wifi,
} from 'lucide-react'
import ECGWaveform from '../components/ecg/ECGWaveform'
import { api } from '../services/api'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: 'easeOut' },
  }),
}

function Feature({ icon: Icon, title, desc, color = 'primary' }) {
  const colorMap = {
    primary: 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-aqua-400',
    teal: 'bg-teal-50 text-teal-600 dark:bg-teal-500/10 dark:text-teal-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-500/10 dark:text-purple-400',
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400',
  }
  return (
    <motion.div variants={fadeUp} custom={0} className="card card-hover p-6">
      <span className={`mb-4 flex h-12 w-12 items-center justify-center rounded-2xl ${colorMap[color]}`}>
        <Icon className="h-6 w-6" />
      </span>
      <h3 className="mb-2 font-display text-base font-semibold text-slate-900 dark:text-white">{title}</h3>
      <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400">{desc}</p>
    </motion.div>
  )
}

function Landing() {
  const [modelStatus, setModelStatus] = React.useState(null)
  const [stats, setStats] = React.useState(null)

  React.useEffect(() => {
    api.getHealth().then((h) => setModelStatus(h)).catch(() => setModelStatus({ model_loaded: false }))
    api.getStatistics().then((s) => setStats(s)).catch(() => {})
  }, [])

  const steps = [
    { icon: Upload, title: 'Upload', desc: 'Upload a 12-lead ECG recording (WFDB .hea/.dat, or .mat, .csv, .npy).' },
    { icon: BrainCircuit, title: 'Analyze', desc: 'A real trained deep learning model processes the signal with the original preprocessing pipeline.' },
    { icon: Eye, title: 'Explain', desc: 'View predictions, probabilities, and signal attribution — with clear caveats.' },
    { icon: FileText, title: 'Review', desc: 'Save analyses to history, generate PDF reports, and explore analytics.' },
  ]

  return (
    <div className="min-h-screen">
      <nav className="glass fixed top-0 z-50 w-full border-b border-slate-200/60 dark:border-slate-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-700 to-aqua-500 text-white shadow-glow">
              <HeartPulse className="h-5 w-5" />
            </span>
            <span className="font-display text-lg font-bold text-slate-900 dark:text-white">
              CardioSense <span className="text-aqua-600 dark:text-aqua-400">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="btn-ghost hidden sm:inline-flex">Dashboard</Link>
            <Link to="/model" className="btn-ghost hidden sm:inline-flex">Model</Link>
            <Link to="/analyze" className="btn-primary">
              <Activity className="h-4 w-4" />
              Analyze ECG
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-950 via-primary-900 to-slate-900 pb-20 pt-32">
        <div className="ecg-grid-bg pointer-events-none absolute inset-0 opacity-30" />
        <div className="pointer-events-none absolute -right-32 top-20 h-96 w-96 rounded-full bg-aqua-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -left-32 bottom-10 h-80 w-80 rounded-full bg-primary-500/20 blur-3xl" />

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <div className="mx-auto max-w-3xl text-center">
            <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}>
              <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-aqua-400/30 bg-aqua-500/10 px-4 py-1.5 text-xs font-medium text-aqua-400">
                <Sparkles className="h-3.5 w-3.5" />
                Deep Learning Powered ECG Analysis
              </span>
            </motion.div>
            <motion.h1
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              custom={1}
              className="font-display text-4xl font-extrabold leading-tight text-white sm:text-5xl md:text-6xl"
            >
              Intelligent ECG Analysis.
              <br />
              <span className="bg-gradient-to-r from-teal-400 to-aqua-400 bg-clip-text text-transparent">
                Clearer Cardiac Insights.
              </span>
            </motion.h1>
            <motion.p
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              custom={2}
              className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg"
            >
              Upload a 12-lead ECG and get predictions from a real, trained convolutional neural network —
              with probabilities, signal statistics, explainability, PDF reports, and full history.
            </motion.p>
            <motion.div
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              custom={3}
              className="mt-8 flex flex-wrap items-center justify-center gap-3"
            >
              <Link to="/analyze" className="btn-primary !px-6 !py-3 !text-base">
                Start Analysis
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link to="/model" className="btn-secondary !px-6 !py-3 !text-base">
                View Model Info
              </Link>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.7 }}
            className="mx-auto mt-16 max-w-4xl"
          >
            <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
              <div className="mb-3 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                  Live 12-lead preview
                </span>
                <span>10 s · 100 Hz</span>
              </div>
              <ECGWaveform />
            </div>
          </motion.div>

          {modelStatus && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mx-auto mt-8 flex max-w-4xl items-center justify-center gap-4 rounded-2xl border border-white/10 bg-white/5 px-6 py-3 text-sm text-slate-300"
            >
              <span className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-aqua-400" />
                Device: {modelStatus.device || 'cpu'}
              </span>
              <span className="h-3 w-px bg-white/20" />
              <span className="flex items-center gap-2">
                <Database className="h-4 w-4 text-teal-400" />
                Model v{modelStatus.version || '1.0'}
              </span>
              <span className="h-3 w-px bg-white/20" />
              <span
                className={`flex items-center gap-2 ${
                  modelStatus.model_loaded ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                <Wifi className="h-4 w-4" />
                {modelStatus.model_loaded ? 'Model loaded' : 'Model offline'}
              </span>
            </motion.div>
          )}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="mb-12 text-center">
            <h2 className="section-title">How it works</h2>
            <p className="section-subtitle mx-auto mt-2 max-w-xl">
              From raw ECG to clear, explainable insights in four steps.
            </p>
          </motion.div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((s, i) => (
              <motion.div key={s.title} variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={i}>
                <div className="card card-hover relative p-6">
                  <span className="absolute right-5 top-4 font-display text-4xl font-extrabold text-slate-100 dark:text-slate-800">
                    {i + 1}
                  </span>
                  <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-aqua-500 text-white">
                    <s.icon className="h-6 w-6" />
                  </span>
                  <h3 className="mb-2 font-display text-base font-semibold text-slate-900 dark:text-white">{s.title}</h3>
                  <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400">{s.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gradient-to-b from-slate-50 to-white py-20 dark:from-slate-900 dark:to-slate-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="mb-12 text-center">
            <h2 className="section-title">AI Workflow &amp; Features</h2>
            <p className="section-subtitle mx-auto mt-2 max-w-xl">
              A complete toolkit built around a real deep learning ECG model.
            </p>
          </motion.div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Feature icon={BrainCircuit} color="primary" title="Real Trained Model" desc="A 1D CNN (ECGCNN) trained on PTB-XL with 5 diagnostic superclasses. No fake predictions, ever." />
            <Feature icon={LineChart} color="teal" title="Interactive ECG Charts" desc="Zoom, pan, and inspect 12-lead waveforms with a grid, time axis, and lead selector." />
            <Feature icon={Eye} color="purple" title="Explainable AI" desc="Integrated Gradients attribution showing which leads and signal regions drove the prediction." />
            <Feature icon={FileText} color="blue" title="PDF Reports" desc="Branded reports with prediction, probabilities, statistics, and explainability." />
            <Feature icon={BarChart3} color="amber" title="Analytics Dashboard" desc="Real statistics computed live from your analysis history — nothing hardcoded." />
            <Feature icon={MessageSquareText} color="red" title="CardioSense Assistant" desc="Ask questions about the result, confidence, leads, and statistics. Answers from in-app data only." />
          </div>
        </div>
      </section>

      {/* Model info strip */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="card overflow-hidden">
            <div className="grid gap-0 md:grid-cols-2">
              <div className="flex flex-col justify-center p-8 md:p-12">
                <span className="mb-4 inline-flex w-fit items-center gap-1.5 rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-600 dark:bg-teal-500/10 dark:text-teal-400">
                  <Layers className="h-3.5 w-3.5" />
                  ECGCNN · v1.0
                </span>
                <h2 className="mb-3 font-display text-2xl font-bold text-slate-900 dark:text-white">
                  A 1D CNN trained on PTB-XL
                </h2>
                <p className="mb-6 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                  12 leads × 1,000 samples (10 seconds at 100 Hz). Four convolutional blocks with batch
                  normalization and adaptive average pooling, followed by a small fully-connected head.
                  338,725 parameters. Trained with BCE-with-logits loss; per-class thresholds tuned on the
                  validation split.
                </p>
                <div className="mb-8 flex flex-wrap gap-2 text-xs">
                  {['12 leads', '100 Hz', '10 s', '5 classes', 'CPU/GPU', '338K params'].map((t) => (
                    <span key={t} className="rounded-full border border-slate-200 px-3 py-1 text-slate-500 dark:border-slate-700 dark:text-slate-400">
                      {t}
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link to="/model" className="btn-secondary">Model details</Link>
                  <Link to="/analyze" className="btn-primary">Try it now</Link>
                </div>
              </div>
              <div className="border-t border-slate-100 bg-slate-50 p-8 md:border-l md:border-t-0 dark:border-slate-800 dark:bg-slate-900 md:p-12">
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">Real test metrics</h3>
                <div className="space-y-4">
                  {[
                    ['Normal', 0.9413, '#16a34a'],
                    ['Myocardial Infarction', 0.9252, '#dc2626'],
                    ['ST/T Changes', 0.9350, '#d97706'],
                    ['Conduction Disturbance', 0.9230, '#2563eb'],
                    ['Hypertrophy', 0.8395, '#9333ea'],
                    ['Mean AUC', 0.9128, '#0891b2'],
                  ].map(([label, auc, color]) => (
                    <div key={label}>
                      <div className="mb-1 flex items-center justify-between text-sm">
                        <span className="text-slate-600 dark:text-slate-300">{label}</span>
                        <span className="font-semibold" style={{ color }}>{auc.toFixed(4)}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                        <div className="h-full rounded-full" style={{ width: `${auc * 100}%`, backgroundColor: color }} />
                      </div>
                    </div>
                  ))}
                </div>
                <p className="mt-6 text-xs text-slate-400">
                  AUC values reported from the notebook's held-out test split. Mean test AUC: 0.9128.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="pb-20">
        <div className="mx-auto max-w-3xl px-4 sm:px-6">
          <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-700 dark:bg-slate-900">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-teal-500" />
            <div>
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">Medical disclaimer</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                CardioSense AI provides AI-generated ECG signal analysis for research and decision-support purposes.
                It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Landing
