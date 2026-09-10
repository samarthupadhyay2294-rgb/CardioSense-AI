import React from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  FileSearch,
  Trash2,
  Activity,
  ImageIcon,
} from 'lucide-react'
import { api } from '../services/api'
import { Card, LoadingState, ErrorState, EmptyState } from '../components/Card'
import { formatDate, formatConfidence, getClassColor, signalQualityBadge, PREDICTION_CODE_MAP } from '../utils/helpers'

const PAGE_SIZE = 10

const SORT_COLUMNS = [
  { key: 'created_at', label: 'Date' },
  { key: 'prediction', label: 'Prediction' },
  { key: 'confidence', label: 'Confidence' },
  { key: 'signal_quality', label: 'Quality' },
]

const TYPE_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'signal', label: 'Signal' },
  { value: 'image', label: 'Image' },
]

function History() {
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState(null)
  const [search, setSearch] = React.useState('')
  const [prediction, setPrediction] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('')
  const [sortBy, setSortBy] = React.useState('created_at')
  const [sortOrder, setSortOrder] = React.useState('desc')
  const [page, setPage] = React.useState(1)
  const [deletingId, setDeletingId] = React.useState(null)

  const load = async (overrides = {}) => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        page: overrides.page ?? page,
        page_size: PAGE_SIZE,
        search: overrides.search ?? search,
        prediction: overrides.prediction ?? prediction,
        analysis_type: overrides.analysisType ?? analysisType,
        sort_by: overrides.sortBy ?? sortBy,
        sort_order: overrides.sortOrder ?? sortOrder,
      }
      const res = await api.getHistory(params)
      setData(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const toggleSort = (key) => {
    const order = sortBy === key && sortOrder === 'asc' ? 'desc' : 'asc'
    setSortBy(key)
    setSortOrder(order)
    load({ sortBy: key, sortOrder: order, page: 1 })
    setPage(1)
  }

  const applyFilters = () => {
    setPage(1)
    load({ page: 1 })
  }

  const goToPage = (p) => {
    setPage(p)
    load({ page: p })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this analysis?')) return
    setDeletingId(id)
    try {
      await api.deleteAnalysis(id)
      await load()
    } catch (e) {
      setError(e.message)
    } finally {
      setDeletingId(null)
    }
  }

  const sortIcon = (key) => (
    <ArrowUpDown className={`h-3.5 w-3.5 ${sortBy === key ? 'text-primary-500' : 'text-slate-400'}`} />
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="section-title">Prediction History</h1>
        <p className="section-subtitle mt-1">Search, filter, and review past ECG analyses.</p>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              className="input !pl-9"
              placeholder="Search by file name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
            />
          </div>
          <select className="input w-auto" value={analysisType} onChange={(e) => setAnalysisType(e.target.value)}>
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <select className="input w-auto" value={prediction} onChange={(e) => setPrediction(e.target.value)}>
            <option value="">All predictions</option>
            {Object.entries(PREDICTION_CODE_MAP).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
          <button className="btn-secondary" onClick={applyFilters}>Apply</button>
        </div>
      </Card>

      {loading ? (
        <LoadingState message="Loading history..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => load()} />
      ) : !data || data.total === 0 ? (
        <Card>
          <EmptyState
            icon={FileSearch}
            title="No analyses found"
            message="Upload an ECG to get started."
            action={
              <Link to="/analyze" className="btn-primary">
                Analyze ECG
              </Link>
            }
          />
        </Card>
      ) : (
        <>
          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/50">
                    <th className="px-5 py-3 font-semibold text-slate-500 dark:text-slate-400">Type</th>
                    <th className="px-5 py-3 font-semibold text-slate-500 dark:text-slate-400">File</th>
                    {SORT_COLUMNS.map((c) => (
                      <th key={c.key} className="px-5 py-3">
                        <button className="inline-flex items-center gap-1.5 font-semibold text-slate-500 hover:text-primary-600 dark:text-slate-400" onClick={() => toggleSort(c.key)}>
                          {c.label}
                          {sortIcon(c.key)}
                        </button>
                      </th>
                    ))}
                    <th className="px-5 py-3 text-right font-semibold text-slate-500 dark:text-slate-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => {
                    const color = getClassColor(item.prediction)
                    const quality = signalQualityBadge(item.signal_quality)
                    const isImgType = item.analysis_type === 'image'
                    return (
                      <tr key={item.id} className="border-b border-slate-100 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50">
                        <td className="px-5 py-3">
                          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-300">
                            {isImgType ? <ImageIcon className="h-4 w-4" /> : <Activity className="h-4 w-4" />}
                          </span>
                        </td>
                        <td className="max-w-[200px] px-5 py-3">
                          <Link to={`/results/${item.id}`} className="group flex items-center gap-3">
                            <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${color.bg} ${color.text} ${color.darkBg}`}>
                              <Activity className="h-4 w-4" />
                            </span>
                            <span className="truncate font-medium text-slate-800 group-hover:text-primary-600 dark:text-slate-100">
                              {item.file_name}
                            </span>
                          </Link>
                        </td>
                        <td className="px-5 py-3">
                          <span className="badge border border-slate-200 dark:border-slate-600">{item.prediction}</span>
                        </td>
                        <td className="px-5 py-3 font-semibold text-slate-700 dark:text-slate-200">
                          {formatConfidence(item.confidence)}
                        </td>
                        <td className="px-5 py-3">
                          <span className={`badge ${quality.cls}`}>{item.signal_quality ? quality.label : item.model_name || ''}</span>
                        </td>
                        <td className="px-5 py-3 text-xs text-slate-400">{formatDate(item.created_at)}</td>
                        <td className="px-5 py-3 text-right">
                          <div className="inline-flex items-center gap-1">
                            <Link
                              to={`/history/${item.id}`}
                              className="btn-ghost !px-2.5 !py-1.5 !text-xs"
                            >
                              Details
                            </Link>
                            <button
                              className="btn-ghost !px-2.5 !py-1.5 !text-xs !text-red-500"
                              onClick={() => handleDelete(item.id)}
                              disabled={deletingId === item.id}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {data.total_pages > 1 && (
              <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3 dark:border-slate-700">
                <p className="text-xs text-slate-400">
                  Page {data.page} of {data.total_pages} · {data.total} analyses
                </p>
                <div className="flex items-center gap-1">
                  <button className="btn-ghost !px-2.5 !py-1.5" disabled={data.page <= 1} onClick={() => goToPage(data.page - 1)}>
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <button className="btn-ghost !px-2.5 !py-1.5" disabled={data.page >= data.total_pages} onClick={() => goToPage(data.page + 1)}>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}

export default History
