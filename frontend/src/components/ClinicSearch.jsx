import { useMemo, useState } from 'react'
import { api } from '../services/api'

/**
 * Keyword search box for clinics/services via backend `/search`.
 * @param {{onResults: (results: Array<{clinicId:number, clinicName:string, city:string, rating?:number, image_url?:string, services:string[]}>) => void}} props
 */
function ClinicSearch({ onResults }) {
  const [query, setQuery] = useState('')
  const [rawResults, setRawResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const clinicCards = useMemo(() => {
    const groupedByClinic = new Map()

    rawResults.forEach((item) => {
      if (!groupedByClinic.has(item.clinic_id)) {
        groupedByClinic.set(item.clinic_id, {
          clinicId: item.clinic_id,
          clinicName: item.clinic_name,
          city: item.city,
          services: new Set(),
        })
      }
      groupedByClinic.get(item.clinic_id).services.add(item.matched_service_name)
    })

    return Array.from(groupedByClinic.values()).map((clinic) => ({
      ...clinic,
      services: Array.from(clinic.services),
    }))
  }, [rawResults])

  const handleSearch = async () => {
    setSearched(true)
    setErrorMessage('')

    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      setRawResults([])
      onResults([])
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams({ query: trimmedQuery })
      const response = await api.get(`/search?${params.toString()}`)
      setRawResults(response)
      onResults(
        Array.from(
          response.reduce((map, item) => {
            if (!map.has(item.clinic_id)) {
              map.set(item.clinic_id, {
                clinicId: item.clinic_id,
                clinicName: item.clinic_name,
                city: item.city,
                rating: item.rating,
                image_url: item.image_url ?? '',
                services: [],
              })
            }
            if (!map.get(item.clinic_id).services.includes(item.matched_service_name)) {
              map.get(item.clinic_id).services.push(item.matched_service_name)
            }
            return map
          }, new Map()).values(),
        ),
      )
    } catch (error) {
      setRawResults([])
      onResults([])
      setErrorMessage(`Search failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <label className="mb-2 block text-left text-2xl font-semibold text-slate-800">
        Search Clinics
      </label>
      <form
        className="mb-2 flex flex-col gap-3 sm:flex-row"
        onSubmit={(event) => {
          event.preventDefault()
          handleSearch()
        }}
      >
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by service, clinic, or city"
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 outline-none transition focus:border-slate-400 focus:bg-white"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {errorMessage && (
        <p className="mb-4 rounded-md bg-rose-100 px-3 py-2 text-rose-700">{errorMessage}</p>
      )}

      {searched && !loading && clinicCards.length === 0 && !errorMessage && (
        <p className="rounded-md bg-slate-100 px-3 py-2 text-slate-600">
          No clinics found for your search.
        </p>
      )}
    </div>
  )
}

export default ClinicSearch
