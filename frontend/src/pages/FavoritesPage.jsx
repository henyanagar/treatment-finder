import { useCallback, useEffect, useState } from 'react'
import BookingForm from '../components/BookingForm'
import ClinicCard from '../components/ClinicCard'
import { CURRENT_USER } from '../constants/currentUser'
import { useFavorites } from '../context/FavoritesContext.jsx'
import { api } from '../services/api'
import { combineLocalDateAndTime, toUtcIsoString } from '../utils/datetime'

const emptyForm = {
  serviceId: '',
  clinicId: '',
  appointmentDate: '',
  appointmentTime: '',
  notes: '',
}

/**
 * Loads favorites with enriched clinic-service details for card display.
 * @param {number[]} favoriteIds
 * @param {Array<{id:number, name:string, city:string, rating?:number, image_url?:string}>} clinicsResponse
 * @param {Array<{id:number, name:string}>} servicesCatalog
 */
async function enrichFavoriteClinics(favoriteIds, clinicsResponse, servicesCatalog) {
  const catalogById = new Map(servicesCatalog.map((s) => [s.id, s.name]))
  const clinicById = new Map(clinicsResponse.map((c) => [c.id, c]))

  const rows = await Promise.all(
    favoriteIds.map(async (id) => {
      const c = clinicById.get(id)
      if (!c) return null

      let services = []
      try {
        const links = await api.get(`/clinics/${id}/services`)
        services = links
          .filter((link) => link.is_available !== false)
          .map((link) => catalogById.get(link.service_id))
          .filter(Boolean)
      } catch {
        services = []
      }

      return {
        clinicId: c.id,
        clinicName: c.name,
        city: c.city,
        rating: c.rating,
        image_url: c.image_url ?? '',
        services,
      }
    }),
  )

  return rows.filter(Boolean)
}

/**
 * Saved clinics page with booking shortcuts for favorited clinics.
 */
function FavoritesPage() {
  const { favoriteIds } = useFavorites()
  const [clinicCards, setClinicCards] = useState([])
  const [services, setServices] = useState([])
  const [allClinicsOptions, setAllClinicsOptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const [formData, setFormData] = useState(emptyForm)
  const [booking, setBooking] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [bookingOpen, setBookingOpen] = useState(false)
  const [selectedClinicName, setSelectedClinicName] = useState('')

  const handleChange = useCallback((event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }, [])

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      setLoading(true)
      setLoadError('')
      try {
        const [servicesResponse, clinicsResponse] = await Promise.all([
          api.get('/services'),
          api.get('/clinics'),
        ])
        if (cancelled) return

        setServices(servicesResponse)
        setAllClinicsOptions(
          clinicsResponse.map((clinic) => ({
            id: clinic.id,
            name: clinic.name,
          })),
        )

        const enriched = await enrichFavoriteClinics(favoriteIds, clinicsResponse, servicesResponse)
        if (!cancelled) {
          setClinicCards(enriched)
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(err.message ?? 'Failed to load favorites.')
          setClinicCards([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [favoriteIds])

  const handleBookNow = (clinicId, matchedServiceName = '') => {
    const matchedService = services.find(
      (service) => service.name.toLowerCase() === matchedServiceName?.toLowerCase(),
    )
    const selectedClinic = clinicCards.find((clinic) => clinic.clinicId === clinicId)

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

  const count = clinicCards.length

  return (
    <>
      <section className="mx-auto max-w-6xl px-6 pb-12 pt-8">
        <div className="mb-6">
          <h1 className="text-4xl font-bold tracking-tight text-slate-800">
            My Favorites ({count} {count === 1 ? 'clinic' : 'clinics'})
          </h1>
          <p className="mt-1 text-slate-500">
            Clinics you have saved—book instantly or remove them from your list.
          </p>
        </div>

        {loadError && (
          <p className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {loadError}
          </p>
        )}

        {loading && (
          <p className="text-lg text-slate-500" aria-live="polite">
            Loading your favorites…
          </p>
        )}

        {!loading && !loadError && count === 0 && (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-10 text-center shadow-sm">
            <p className="text-lg font-medium text-slate-700">No favorites yet</p>
            <p className="mt-2 text-sm text-slate-500">
              Use the heart on any clinic card on Search to save it here.
            </p>
          </div>
        )}

        {!loading && count > 0 && (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {clinicCards.map((clinic) => (
              <ClinicCard
                key={clinic.clinicId}
                clinic={clinic}
                onBookNow={handleBookNow}
              />
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
        clinics={allClinicsOptions}
        booking={booking}
        successMessage={successMessage}
        errorMessage={errorMessage}
        onChange={handleChange}
        onSubmit={handleSubmit}
      />
    </>
  )
}

export default FavoritesPage
