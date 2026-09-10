import React from 'react'
import { Send, Bot, X, Sparkles } from 'lucide-react'
import { api } from '../../services/api'

const SIGNAL_SUGGESTIONS = [
  'What is the prediction?',
  'How confident is the model?',
  'What leads were used?',
  'Explain the result',
  'What is the signal quality?',
]

const IMAGE_SUGGESTIONS = [
  'What is the predicted class?',
  'How confident is the model?',
  'What model architecture was used?',
  'Explain the Grad-CAM',
  'What are the top probabilities?',
]

function Assistant({ analysisId, isImage = false }) {
  const [open, setOpen] = React.useState(false)
  const [messages, setMessages] = React.useState([])
  const [input, setInput] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const messagesEndRef = React.useRef(null)
  const suggestions = isImage ? IMAGE_SUGGESTIONS : SIGNAL_SUGGESTIONS

  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, loading])

  const ask = async (question) => {
    if (!question.trim() || loading) return
    const userMsg = { role: 'user', content: question }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    try {
      const askFn = isImage ? api.askImageAssistant : api.askAssistant
      const res = await askFn(analysisId, question)
      setMessages((m) => [...m, { role: 'assistant', content: res.answer }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: 'Sorry, I could not process that question.' }])
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-aqua-500 text-white shadow-glow transition-transform hover:scale-105"
        aria-label="Open CardioSense Assistant"
      >
        <Sparkles className="h-6 w-6" />
      </button>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[540px] w-[400px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between border-b border-slate-100 bg-gradient-to-r from-primary-700 to-aqua-600 px-4 py-3 text-white dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          <div>
            <p className="text-sm font-semibold">CardioSense Assistant</p>
            <p className="text-[11px] opacity-80">
              Answers from this {isImage ? 'image' : 'signal'} analysis only
            </p>
          </div>
        </div>
        <button onClick={() => setOpen(false)} aria-label="Close assistant" className="rounded-lg p-1 hover:bg-white/20">
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="space-y-2">
            <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              Ask me anything about this ECG {isImage ? 'image' : 'signal'} analysis — the
              {isImage ? ' predicted class, confidence, model, or Grad-CAM' : ' prediction, confidence, leads, or statistics'}.{' '}
              I answer using only the data from this analysis and do not provide medical diagnosis.
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => ask(s)}
                  className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:border-primary-400 hover:text-primary-600 dark:border-slate-700 dark:text-slate-300"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                m.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1 rounded-2xl bg-slate-100 px-4 py-3 dark:bg-slate-800">
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.1s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.2s]" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          ask(input)
        }}
        className="flex items-center gap-2 border-t border-slate-100 p-3 dark:border-slate-800"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this analysis..."
          className="input flex-1"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="btn-primary !px-3 !py-2.5"
          aria-label="Send question"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  )
}

export default Assistant
