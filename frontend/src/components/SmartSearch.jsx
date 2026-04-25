import { useState } from 'react'
import { api } from '../services/api'

/**
 * AI-assisted treatment intent search input.
 * @param {{onResult: (result: object | null) => void}} props
 */
function SmartSearch({ onResult }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErrorMessage('')

    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      setErrorMessage('Please describe what treatment you are looking for.')
      onResult(null)
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/ai/consult', { query: trimmedQuery })
      onResult(response)
    } catch (error) {
      onResult(null)
      setErrorMessage(`Smart search failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <label className="mb-2 block text-left text-2xl font-semibold text-slate-800">
        Ask our AI Consultant
      </label>
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              ✨
            </span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g., What treatment is best for reducing fine lines around my eyes?"
              className="w-full rounded-2xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-slate-700 outline-none transition focus:border-slate-400"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="rounded-2xl bg-[#1A2B3C] px-6 py-3 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'AI is thinking...' : 'Ask AI'}
          </button>
        </div>
      </form>

      {errorMessage && (
        <p className="mt-4 rounded-md bg-rose-100 px-3 py-2 text-rose-700">{errorMessage}</p>
      )}
    </div>
  )
}

export default SmartSearch
