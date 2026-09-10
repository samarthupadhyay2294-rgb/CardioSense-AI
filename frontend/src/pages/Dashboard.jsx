import React from 'react'
import { Link } from 'react-router-dom'
import {
  FileSearch,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Gauge,
  TrendingUp,
  ArrowRight,
  RefreshCw,
  ImageIcon,
} from 'lucide-react'
import { api } from '../services/api'
import StatCard from '../components/dashboard/StatCard'
import { Card, CardHeader, LoadingState, ErrorState, EmptyState } from '../components/Card'
import { formatDate, formatConfidence, getClassColor, signalQualityBadge } from '../utils/helpers'
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
  Legend,
} from 'recharts'

const CHART_COLORS = ['#16a34a', '#dc2626', '#d97706', '#2563eb', '#9333ea']

function Dashboard() {
  const [stats, setStats] = React.useState(null)
  const [recent, setRecent] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [s, h] = await Promise.all([api.getStatistics(), api.getHistory({ page_size: 6 })])
      setStats(s)
      setRecent(h.items)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    load()
  }, [load])

  if (loading) return <LoadingState message="Loading dashboard..." />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!stats) return null

  const pieData = Object.entries(stats.prediction_distribution || {}).map(([name, value]) => ({ name, value }))
  const confData = Object.entries(stats.confidence_distribution || {}).map(([name, value]) => ({
    name: name.replace('%', ''),
    count: value,
  }))
  const trendData = (stats.trend_data || []).map((t) => ({
    name: t.date.slice(5),
    count: t.count,
  }))

  const abnormalPct = stats.total_analyses > 0 ? (stats.abnormal_count / stats.total_analyses) * 100 : 0

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="section-title">Dashboard</h1>
          <p className="section-subtitle mt-1">Live statistics computed from your analysis history.</p>
        </div>
        <button className="btn-secondary" onClick={load}>
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="Total Analyses" value={stats.total_analyses} icon={FileSearch} color="primary" />
        <StatCard label="Signal Analyses" value={stats.signal_count} icon={Activity} color="teal" />
        <StatCard label="Image Analyses" value={stats.image_count} icon={ImageIcon} color="purple" />
        <StatCard label="Normal" value={stats.normal_count} icon={CheckCircle2} color="success" />
        <StatCard label="Abnormal" value={stats.abnormal_count} icon={AlertTriangle} color="danger" sub={`${abnormalPct.toFixed(1)}% of analyses`} />
      </div>

      <Card className="p-5">
        <CardHeader
          title="Analysis Mix"
          subtitle="Signal vs Image analysis distribution"
          icon={Activity}
        />
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3 dark:bg-slate-800/50">
            <span className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
              <Activity className="h-4 w-4 text-teal-500" /> Signal
            </span>
            <span className="font-semibold text-slate-800 dark:text-slate-100">{stats.signal_count}</span>
          </div>
          <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3 dark:bg-slate-800/50">
            <span className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
              <ImageIcon className="h-4 w-4 text-purple-500" /> Image
            </span>
            <span className="font-semibold text-slate-800 dark:text-slate-100">{stats.image_count}</span>
          </div>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader
              title="Recent Analyses"
              subtitle="Latest ECG predictions"
              icon={Activity}
              action={
                <Link to="/history" className="btn-ghost !px-3 !py-1.5 !text-xs">
                  View all
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              }
            />
            {recent.length === 0 ? (
              <EmptyState
                icon={FileSearch}
                title="No analyses yet"
                message="Upload an ECG to get started."
                action={
                  <Link to="/analyze" className="btn-primary">
                    Analyze ECG
                  </Link>
                }
              />
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {recent.map((item) => {
                  const color = getClassColor(item.prediction)
                  const quality = signalQualityBadge(item.signal_quality)
                  return (
                    <Link
                      key={item.id}
                      to={`/results/${item.id}`}
                      className="flex flex-wrap items-center gap-3 py-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
                    >
                      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${color.bg} ${color.text} ${color.darkBg}`}>
                        <Activity className="h-5 w-5" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">{item.file_name}</p>
                        <p className="text-xs text-slate-400">{formatDate(item.created_at)}</p>
                      </div>
                      <span className={`hidden sm:inline-flex badge ${quality.cls}`}>{quality.label}</span>
                      <span className={`badge ${color.bg} ${color.text} ${color.darkBg}`}>{item.prediction}</span>
                      <span className="w-16 text-right text-sm font-semibold text-slate-700 dark:text-slate-200">
                        {formatConfidence(item.confidence)}
                      </span>
                    </Link>
                  )
                })}
              </div>
            )}
          </Card>

          <Card>
            <CardHeader title="Analyses Trend" subtitle="Over time" icon={TrendingUp} />
            {trendData.length === 0 ? (
              <EmptyState icon={TrendingUp} title="No trend data yet" message="Analyze ECGs to see trends." />
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                  <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#94a3b8' }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                  <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Prediction Distribution" icon={Activity} />
            {pieData.length === 0 ? (
              <EmptyState icon={Activity} title="No data" message="Analyze ECGs to populate." />
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
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

          <Card>
            <CardHeader title="Confidence Distribution" icon={Gauge} />
            {confData.length === 0 ? (
              <EmptyState icon={Gauge} title="No data" message="Analyze ECGs to populate." />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={confData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                  <Bar dataKey="count" fill="#0891b2" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>

          <div className="card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Most common</p>
                <p className="mt-1 font-display text-lg font-bold text-slate-900 dark:text-white">{stats.most_common_prediction}</p>
              </div>
              <p className="text-xs text-slate-400">Avg processing {stats.average_processing_time.toFixed(3)} s</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
