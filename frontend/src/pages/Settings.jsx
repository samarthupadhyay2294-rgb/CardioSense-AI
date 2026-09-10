import React from 'react'
import {
  Sun,
  Moon,
  Monitor,
  Bell,
  BellRing,
  Cpu,
  Database,
  HardDrive,
  Info,
  CheckCircle2,
} from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { api } from '../services/api'
import { Card, CardHeader, LoadingState } from '../components/Card'

function Settings() {
  const { theme, setTheme } = useTheme()
  const [modelStatus, setModelStatus] = React.useState(null)
  const [stats, setStats] = React.useState(null)
  const [notifications, setNotifications] = React.useState(true)
  const [saved, setSaved] = React.useState(false)

  React.useEffect(() => {
    api.getModelStatus().then(setModelStatus).catch(() => {})
    api.getStatistics().then(setStats).catch(() => {})
  }, [])

  const save = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const themeOptions = [
    { key: 'light', label: 'Light', icon: Sun },
    { key: 'dark', label: 'Dark', icon: Moon },
  ]

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-subtitle mt-1">Preferences and system status.</p>
      </div>

      <Card>
        <CardHeader title="Appearance" subtitle="Theme preference" icon={Sun} />
        <div className="flex gap-3">
          {themeOptions.map((opt) => (
            <button
              key={opt.key}
              onClick={() => setTheme(opt.key)}
              className={`flex flex-1 flex-col items-center gap-2 rounded-xl border-2 p-4 transition-colors ${
                theme === opt.key
                  ? 'border-primary-500 bg-primary-50 dark:border-aqua-400 dark:bg-primary-500/10'
                  : 'border-slate-200 hover:border-slate-300 dark:border-slate-700'
              }`}
            >
              <opt.icon className={`h-5 w-5 ${theme === opt.key ? 'text-primary-600 dark:text-aqua-400' : 'text-slate-400'}`} />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{opt.label}</span>
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <CardHeader title="Notifications" subtitle="Application notifications" icon={Bell} />
        <label className="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 p-4 dark:border-slate-700">
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">Analysis completion alerts</p>
            <p className="text-xs text-slate-400">Receive a notification when an ECG analysis completes.</p>
          </div>
          <button
            onClick={() => setNotifications((n) => !n)}
            className={`relative h-6 w-11 rounded-full transition-colors ${notifications ? 'bg-primary-600' : 'bg-slate-300 dark:bg-slate-600'}`}
            role="switch"
            aria-checked={notifications}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${
                notifications ? 'left-[22px]' : 'left-0.5'
              }`}
            />
          </button>
        </label>
      </Card>

      {modelStatus && (
        <Card>
          <CardHeader title="Model &amp; API Status" subtitle="Backend model state" icon={Cpu} />
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <Cpu className="h-4 w-4" />
                Model
              </span>
              <span className="flex items-center gap-1.5 text-sm font-medium text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                {modelStatus.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <Database className="h-4 w-4" />
                Device
              </span>
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{modelStatus.device}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <HardDrive className="h-4 w-4" />
                Version
              </span>
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{modelStatus.model_version}</span>
            </div>
            {stats && (
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                  <Info className="h-4 w-4" />
                  Stored analyses
                </span>
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{stats.total_analyses}</span>
              </div>
            )}
          </div>
        </Card>
      )}

      <Card>
        <CardHeader title="Storage" subtitle="Upload limits" icon={HardDrive} />
        <div className="flex items-center justify-between rounded-xl border border-slate-200 p-4 dark:border-slate-700">
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">Maximum upload size</p>
            <p className="text-xs text-slate-400">Single file upload limit enforced by the backend.</p>
          </div>
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">20 MB</span>
        </div>
      </Card>

      <Card>
        <CardHeader title="App Information" icon={Info} />
        <div className="space-y-2.5">
          <div className="flex justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">Product</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">CardioSense AI</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">Version</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">Purpose</span>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">Research &amp; decision support</span>
          </div>
        </div>
      </Card>

      <div className="flex justify-end">
        <button className="btn-primary" onClick={save}>
          {saved ? (
            <>
              <CheckCircle2 className="h-4 w-4" />
              Saved
            </>
          ) : (
            'Save preferences'
          )}
        </button>
      </div>
    </div>
  )
}

export default Settings
