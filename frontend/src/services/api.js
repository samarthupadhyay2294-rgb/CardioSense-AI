const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`
  let res
  try {
    res = await fetch(url, options)
  } catch (e) {
    // Network error or CORS error
    const error = new Error(`Network error: ${e.message}. Backend may be unreachable or CORS is misconfigured.`)
    error.status = 0
    error.originalError = e
    throw error
  }
  const contentType = res.headers.get('content-type') || ''
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    if (contentType.includes('application/json')) {
      try {
        const data = await res.json()
        if (typeof data.detail === 'string') detail = data.detail
        else if (Array.isArray(data.detail)) detail = data.detail.map((d) => d.msg).join('; ')
      } catch (e) {
        // If parsing JSON fails, use status text
        detail = res.statusText || detail
      }
    } else {
      detail = res.statusText || detail
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  if (res.status === 204) return null
  if (contentType.includes('application/json')) return res.json()
  return res
}

export const api = {
  getHealth: () => request('/api/health'),
  getModelInfo: () => request('/api/model/info'),
  getImageModelInfo: () => request('/api/model/image-info'),
  getModelStatus: () => request('/api/model/status'),
  getStatistics: () => request('/api/statistics'),

  analyzeECG: (files, skipInterpretation = true) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    const url = skipInterpretation ? '/api/ecg/analyze?skip_interpretation=true' : '/api/ecg/analyze'
    return request(url, { method: 'POST', body: form })
  },

  analyzeECGImage: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/api/ecg-image/analyze', { method: 'POST', body: form })
  },

  getAnalysis: (id) => request(`/api/ecg/${id}`),
  getImageAnalysis: (id) => request(`/api/ecg-image/${id}`),

  deleteAnalysis: (id) => request(`/api/ecg/${id}`, { method: 'DELETE' }),

  getHistory: (params = {}) => {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') qs.set(k, v)
    })
    return request(`/api/ecg/history?${qs.toString()}`)
  },

  getSummary: (id) => request(`/api/ecg/${id}/summary`, { method: 'POST' }),
  getImageSummary: (id) => request(`/api/ecg-image/${id}/summary`, { method: 'POST' }),

  askAssistant: (id, question) => {
    const form = new FormData()
    form.append('question', question)
    return request(`/api/ecg/${id}/assistant`, { method: 'POST', body: form })
  },
  askImageAssistant: (id, question) => {
    const form = new FormData()
    form.append('question', question)
    return request(`/api/ecg-image/${id}/assistant`, { method: 'POST', body: form })
  },

  getReportUrl: (id) => `${API_BASE}/api/ecg/report/${id}`,
  getImageReportUrl: (id) => `${API_BASE}/api/ecg-image/report/${id}`,
  getImageUrl: (id) => `${API_BASE}/api/ecg-image/${id}/image`,
  getGradcamUrl: (id) => `${API_BASE}/api/ecg-image/${id}/gradcam`,

  getGeminiInterpretation: (analysisId) => {
    return request('/api/interpretation/gemini', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_id: analysisId })
    })
  },

  generateInterpretation: (analysisId) => {
    return request(`/api/ecg/${analysisId}/interpretation`, { method: 'POST' })
  }
}
