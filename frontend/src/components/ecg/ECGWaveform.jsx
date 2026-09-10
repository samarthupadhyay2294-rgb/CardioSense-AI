import React from 'react'

function generateWave() {
  const points = 400
  const data = []
  let phase = 0
  for (let i = 0; i < points; i++) {
    const t = i / points
    let val = 0.15 * Math.sin(2 * Math.PI * 0.3 * t * 10 + phase)
    // P wave
    val += 0.08 * Math.exp(-Math.pow((t % 1) * 10 - 0.2, 2) / 0.005)
    // QRS complex
    val -= 0.15 * Math.exp(-Math.pow((t % 1) * 10 - 0.5, 2) / 0.0008)
    val += 0.5 * Math.exp(-Math.pow((t % 1) * 10 - 0.52, 2) / 0.0004)
    val -= 0.1 * Math.exp(-Math.pow((t % 1) * 10 - 0.55, 2) / 0.0006)
    // T wave
    val += 0.12 * Math.exp(-Math.pow((t % 1) * 10 - 0.8, 2) / 0.01)
    phase += 0.02
    data.push(val)
  }
  return data
}

function ECGWaveform() {
  const data = React.useMemo(generateWave, [])
  const width = 800
  const height = 200
  const path = React.useMemo(() => {
    const stepX = width / (data.length - 1)
    const max = Math.max(...data.map(Math.abs)) * 1.2
    return data
      .map((v, i) => {
        const x = i * stepX
        const y = height / 2 - (v / max) * (height / 2 - 12)
        return `${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ')
  }, [data, width, height])

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" aria-hidden="true">
      <defs>
        <linearGradient id="waveGlow" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#22d3ee" />
          <stop offset="100%" stopColor="#3b82f6" />
        </linearGradient>
      </defs>
      <path
        d={path}
        fill="none"
        stroke="url(#waveGlow)"
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  )
}

export default ECGWaveform
