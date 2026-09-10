import React from 'react'
import { Link } from 'react-router-dom'
import {
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  Gauge,
  Timer,
  Trophy,
  RefreshCw,
  ImageIcon,
} from 'lucide-react'
import { api } from '../services/api'
import { Card, CardHeader, LoadingState, ErrorState, EmptyState } from '../components/Card'
import StatCard from '../components/dashboard/StatCard'
import { formatConfidence } from '../utils/helpers'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
} from 'recharts'

const CHART_COLORS = ['#16a34a', '#dc2626', '#d97706', '#2563eb', '#9333ea']

function Analytics() {
  const [stats, setStats] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setStats(await api.getStatistics())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    load()
  }, [])

  if (loading) return <LoadingState message="Loading analytics..." />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!stats) return null

  const pieData = Object.entries(stats.prediction_distribution || {}).map(([name, value]) => ({ name, value }))
  const imagePieData = Object.entries(stats.image_prediction_distribution || {}).map(([name, value]) => ({
    name,
    value,
  }))
  const confData = Object.entries(stats.confidence_distribution || {}).map(([name, value]) => ({
    name: name.replace('%', ''),
    count: value,
  }))
  const trendData = (stats.trend_data || []).map((t) => ({
    date: t.date,
    count: t.count,
  }))

  const normalPct = stats.total_analyses > 0 ? (stats.normal_count / stats.total_analyses) * 100 : 0
  const abnormalPct = stats.total_analyses > 0 ? (stats.abnormal_count / stats.total_analyses) * 100 : 0

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="section-title">Analytics</h1>
          <p className="section-subtitle mt-1">Real statistics computed from your analysis history.</p>
        </div>
        <button className="btn-secondary" onClick={load}>
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Analyses" value={stats.total_analyses} icon={FileSearch} color="primary" />
        <StatCard label="Signal Analyses" value={stats.signal_count} icon={Activity} color="teal" />
        <StatCard label="Image Analyses" value={stats.image_count} icon={ImageIcon} color="purple" />
        <StatCard label="Average Confidence" value={formatConfidence(stats.average_confidence)} icon={Gauge} color="teal" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Signal Prediction Distribution" subtitle="Count per diagnostic class (signal model)" icon={Activity} />
          {pieData.length === 0 ? (
            <EmptyState icon={Activity} title="No data" message="Analyze ECG signals to populate." />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={3} label>
                  {pieData.map((entry, i) => (
                    <Cell key={entry.name} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        {imagePieData.length > 0 ? (
          <Card>
            <CardHeader title="Image Prediction Distribution" subtitle="Count per class (image model)" icon={ImageIcon} />
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie data={imagePieData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={3} label>
                  {imagePieData.map((entry, i) => (
                    <Cell key={entry.name} fill={CHART_COLORS[(i + 2) % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        ) : (
          <Card>
            <CardHeader title="Image Prediction Distribution" subtitle="Count per class (image model)" icon={ImageIcon} />
            <EmptyState icon={ImageIcon} title="No data" message="Analyze ECG images to populate." />
           </Card>
        )
      }
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Confidence Distribution" subtitle="Bucket of model confidence (%) — both models" icon={Gauge} />
          {confData.length === 0 ? (
            <EmptyState icon={Gauge} title="No data" message="Analyze ECGs to populate analytics." />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={confData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Bar dataKey="count" fill="#0891b2" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Processing Time" subtitle="Average per analysis" icon={Timer} />
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="font-display text-3xl font-extrabold text-slate-800 dark:text-slate-100">
                {stats.average_processing_time.toFixed(3)} s
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">mean processing time</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Analyses Over Time" subtitle="Daily analysis count" icon={Timer} />
        {trendData.length === 0 ? (
          <EmptyState icon={Timer} title="No trend data" message="Analyze ECGs to see trends." />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
              <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>

      <div className="card p-5 text-center">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          All statistics are computed live from records in your analysis database — no values are hardcoded.
        </p>
        <Link to="/analyze" className="btn-primary mt-4">
          Analyze another ECG
        </Link>
      </div>
    </div>
  )
}

export default Analytics
