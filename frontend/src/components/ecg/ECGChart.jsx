import React from 'react'
import Plot from 'react-plotly.js'
import { useTheme } from '../../context/ThemeContext'

const LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

const LEAD_COLORS = [
  '#2563eb', '#0d9488', '#7c3aed', '#dc2626',
  '#ea580c', '#0891b2', '#16a34a', '#4f46e5',
  '#9333ea', '#db2777', '#ca8a04', '#0369a1',
]

function buildTraces(signal, leadNames, theme, highlight) {
  const traces = []
  signal.forEach((leadData, idx) => {
    const name = leadNames[idx] || `Lead ${idx + 1}`
    const y = Array.isArray(leadData) ? leadData : Array.from(leadData)
    const x = y.map((_, i) => (i / 100).toFixed(2))
    traces.push({
      x,
      y,
      type: 'scatter',
      mode: 'lines',
      name,
      hovertemplate: `${name}: %{y:.3f} mV<extra></extra>`,
      line: { color: LEAD_COLORS[idx % LEAD_COLORS.length], width: 1.4 },
    })
  })
  if (highlight && highlight.length > 0) {
    const yMax = Math.max(...signal.flat().map(Math.abs)) * 1.2
    traces.push({
      x: Array.from({ length: highlight.length }, (_, i) => (i / 100).toFixed(2)),
      y: highlight.map((v) => v * yMax),
      type: 'scatter',
      mode: 'lines',
      name: 'Importance',
      line: { color: 'rgba(34, 211, 238, 0.85)', width: 2.5 },
      yaxis: 'y2',
      hovertemplate: 'Importance: %{y:.3f}<extra></extra>',
    })
  }
  return traces
}

function ECGChart({ signal, leadNames = LEAD_NAMES, height = 480, highlight = null }) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const traceColor = isDark ? '#334155' : '#e2e8f0'
  const textColor = isDark ? '#94a3b8' : '#475569'
  const gridColor = isDark ? 'rgba(148,163,184,0.12)' : 'rgba(148,163,184,0.18)'

  const layout = {
    height,
    autosize: true,
    margin: { l: 48, r: 24, t: 24, b: 40 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: textColor, family: 'Inter, sans-serif', size: 11 },
    xaxis: {
      title: { text: 'Time (s)', font: { color: textColor } },
      gridcolor: gridColor,
      zerolinecolor: gridColor,
      rangeslider: { visible: true, thickness: 0.12 },
      rangeselector: {
        buttons: [
          { count: 2, label: '2s', step: 'second', stepmode: 'backward' },
          { count: 5, label: '5s', step: 'second', stepmode: 'backward' },
          { label: 'All', step: 'all' },
        ],
      },
    },
    yaxis: {
      title: { text: 'Amplitude (mV)', font: { color: textColor } },
      gridcolor: gridColor,
      zerolinecolor: gridColor,
    },
    yaxis2: {
      title: { text: 'Importance', font: { color: textColor } },
      overlaying: 'y',
      side: 'right',
      showgrid: false,
      zeroline: false,
    },
    legend: {
      orientation: 'h',
      y: -0.25,
      x: 0,
      font: { color: textColor },
      bgcolor: 'rgba(0,0,0,0)',
    },
    hoverlabel: {
      bgcolor: isDark ? '#1e293b' : '#ffffff',
      bordercolor: gridColor,
      font: { color: isDark ? '#e2e8f0' : '#0f172a', family: 'Inter, sans-serif' },
    },
  }

  const config = {
    displaylogo: false,
    responsive: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
  }

  const data = buildTraces(signal, leadNames, theme, highlight)

  return (
    <div className="w-full overflow-hidden rounded-xl">
      <Plot
        data={data}
        layout={layout}
        config={config}
        useResizeHandler
        style={{ width: '100%', height }}
        className="h-full w-full"
      />
    </div>
  )
}

export default ECGChart
