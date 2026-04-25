import { useCallback, useEffect, useMemo, useState } from 'react'
import BookingForm from '../components/BookingForm'
import { CURRENT_USER } from '../constants/currentUser'
import { api } from '../services/api'
import { combineLocalDateAndTime, toUtcIsoString } from '../utils/datetime'
import ClinicCard from '../components/ClinicCard'
import Hero from '../components/Hero'

const emptyForm = {
  serviceId: '',
  clinicId: '',
  appointmentDate: '',
  appointmentTime: '',
  notes: '',
}

/**
 * Main exploration page with hero search, clinic grid, and booking entry point.
 */
function HomePage() {
  const [services, setServices] = useState([])
  const [allClinics, setAllClinics] = useState([])
  const [displayedClinics, setDisplayedClinics] = useState([])
  const [aiResult, setAiResult] = useState(null)
  const [formData, setFormData] = useState(emptyForm)
  const [booking, setBooking] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [bookingOpen, setBookingOpen] = useState(false)
  const [selectedClinicName, setSelectedClinicName] = useState('')
  const [loadingClinics, setLoadingClinics] = useState(false)
  const [searchAttempted, setSearchAttempted] = useState(false)
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [sortOption, setSortOption] = useState('default')

  const loadInitialData = async () => {
    setLoadingClinics(true)
    try {
      const [servicesResponse, clinicsResponse] = await Promise.all([
        api.get('/services'),
        api.get('/clinics'),
      ])
      setServices(servicesResponse)
      const serviceNameById = new Map(servicesResponse.map((service) => [service.id, service.name]))
      const clinicsForCards = await Promise.all(
        clinicsResponse.map(async (clinic) => {
          let clinicServices = []
          try {
            const links = await api.get(`/clinics/${clinic.id}/services`)
            clinicServices = links
              .filter((link) => link.is_available !== false)
              .map((link) => serviceNameById.get(link.service_id))
              .filter(Boolean)
          } catch {
            clinicServices = []
          }

          return {
            clinicId: clinic.id,
            clinicName: clinic.name,
            city: clinic.city,
            rating: clinic.rating,
            image_url: clinic.image_url ?? '',
            services: clinicServices,
          }
        }),
      )
      setAllClinics(clinicsForCards)
      setDisplayedClinics(clinicsForCards)
      setErrorMessage('')
    } catch (error) {
      setErrorMessage(`Failed to load clinics data: ${error.message}`)
    } finally {
      setLoadingClinics(false)
    }
  }

  useEffect(() => {
    loadInitialData()
  }, [])

  const handleChange = useCallback((event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }, [])

  const handleBookNow = (clinicId, matchedServiceName = '') => {
    const matchedService = services.find(
      (service) => service.name.toLowerCase() === matchedServiceName?.toLowerCase(),
    )
    const selectedClinic = [...displayedClinics, ...allClinics].find(
      (clinic) => clinic.clinicId === clinicId,
    )

    setFormData((prev) => ({
      ...prev,
      clinicId: String(clinicId),
      serviceId: matchedService ? String(matchedService.id) : prev.serviceId,
      appointmentDate: prev.appointmentDate,
      appointmentTime: prev.appointmentTime,
    }))
    setSelectedClinicName(selectedClinic?.clinicName ?? 'Selected Clinic')
    setBookingOpen(true)
    setSuccessMessage('')
    setErrorMessage('')
  }

  const handleAiResult = (result) => {
    setAiResult(result)
    if (!result) {
      setDisplayedClinics(allClinics)
      setSearchAttempted(false)
      return
    }

    const aiClinics = (result.clinics ?? []).map((clinic) => {
      const fallbackClinic = allClinics.find((item) => item.clinicId === clinic.clinic_id)
      return {
        clinicId: clinic.clinic_id,
        clinicName: clinic.clinic_name,
        city: clinic.city,
        rating: clinic.rating,
        image_url: fallbackClinic?.image_url ?? '',
        services: result.matched_service_names ?? [],
      }
    })

    setDisplayedClinics(aiClinics)
    setSearchAttempted(true)
  }

  const handleSearchResults = (results) => {
    setSearchAttempted(true)
    setDisplayedClinics(results)
  }

  const categoryOptions = useMemo(
    () =>
      Array.from(new Set(services.map((service) => service.name)))
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b)),
    [services],
  )

  const filteredClinics = useMemo(() => {
    let rows = [...displayedClinics]
    if (categoryFilter !== 'all') {
      const categoryNeedle = categoryFilter.toLowerCase()
      rows = rows.filter((clinic) =>
        (clinic.services ?? []).some((serviceName) => serviceName.toLowerCase() === categoryNeedle),
      )
    }
    if (sortOption === 'highest-rated') {
      rows = rows.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0))
    }
    return rows
  }, [displayedClinics, categoryFilter, sortOption])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSuccessMessage('')
    setErrorMessage('')

    if (!formData.serviceId || !formData.clinicId) {
      setErrorMessage('Please select both a service and a clinic.')
      return
    }

    if (!formData.appointmentDate || !formData.appointmentTime) {
      setErrorMessage('Please choose both a date and time for the appointment.')
      return
    }

    setBooking(true)
    try {
      const serviceId = Number.parseInt(formData.serviceId, 10)
      const clinicId = Number.parseInt(formData.clinicId, 10)

      if (Number.isNaN(serviceId) || Number.isNaN(clinicId)) {
        throw new Error('Service and clinic selections are invalid.')
      }

      const appointmentDateTime = combineLocalDateAndTime(
        formData.appointmentDate,
        formData.appointmentTime,
      )

      if (Number.isNaN(appointmentDateTime.getTime())) {
        throw new Error('Selected date or time is invalid.')
      }

      if (appointmentDateTime <= new Date()) {
        throw new Error('Please choose a future date and time.')
      }

      const payload = {
        user_id: CURRENT_USER.id,
        service_id: serviceId,
        clinic_id: clinicId,
        notes: formData.notes?.trim() || null,
        appointment_datetime: toUtcIsoString(appointmentDateTime),
      }

      await api.post('/appointments', payload)
      setSuccessMessage('Appointment booked successfully!')
      setFormData(emptyForm)
      setBookingOpen(false)
    } catch (error) {
      setErrorMessage(`Could not book appointment: ${error.message}`)
    } finally {
      setBooking(false)
    }
  }

  return (
    <>
      <Hero onAiResult={handleAiResult} onSearchResults={handleSearchResults} />

      {aiResult && (
        <section id="results" className="mx-auto mb-8 max-w-6xl px-6">
          <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-2 text-3xl font-semibold text-slate-800">AI Recommendation</h2>
            <p className="text-slate-700">{aiResult.explanation}</p>
            <p className="mt-3 text-sm text-slate-500">{aiResult.reason}</p>

            {aiResult.matched_service_names?.length > 0 && (
              <div className="mt-5">
                <p className="mb-2 text-sm font-semibold text-slate-500">
                  Recommended Services:
                </p>
                <div className="flex flex-wrap gap-2">
                  {aiResult.matched_service_names.map((serviceName) => (
                    <span
                      key={serviceName}
                      className="rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold text-teal-900"
                    >
                      {serviceName}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </article>
        </section>
      )}

      <section id="results" className="mx-auto max-w-6xl px-6 pb-12">
        <div className="mb-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <h2 className="text-4xl font-semibold text-slate-800">Featured Clinics</h2>
          <div className="flex flex-wrap items-end gap-3">
            <label className="flex flex-col text-sm text-slate-600">
              Category
              <select
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                className="mt-1 min-w-44 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
              >
                <option value="all">All Categories</option>
                {categoryOptions.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-sm text-slate-600">
              Sort
              <select
                value={sortOption}
                onChange={(event) => setSortOption(event.target.value)}
                className="mt-1 min-w-40 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
              >
                <option value="default">Default</option>
                <option value="highest-rated">Highest Rated</option>
              </select>
            </label>
          </div>
        </div>
        <p className="mb-4 mt-1 text-slate-500">{filteredClinics.length} clinics available</p>

        {loadingClinics && (
          <p className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
            Loading clinics...
          </p>
        )}

        {!loadingClinics && filteredClinics.length === 0 && (
          <p className="rounded-xl border border-dashed border-slate-200 bg-white px-4 py-6 text-center text-sm text-slate-600">
            {searchAttempted ? 'No results for this search.' : 'No clinics found.'}
          </p>
        )}

        {!loadingClinics && filteredClinics.length > 0 && (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {filteredClinics.map((clinic) => (
              <ClinicCard key={clinic.clinicId} clinic={clinic} onBookNow={handleBookNow} />
            ))}
          </div>
        )}
      </section>

      <BookingForm
        isOpen={bookingOpen}
        onClose={() => setBookingOpen(false)}
        selectedClinicName={selectedClinicName}
        formData={formData}
        services={services}
        clinics={allClinics.map((clinic) => ({ id: clinic.clinicId, name: clinic.clinicName }))}
        booking={booking}
        successMessage={successMessage}
        errorMessage={errorMessage}
        onChange={handleChange}
        onSubmit={handleSubmit}
      />
    </>
  )
}

export default HomePage
