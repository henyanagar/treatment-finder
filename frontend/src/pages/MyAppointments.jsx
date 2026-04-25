import { useCallback, useEffect, useMemo, useState } from 'react'
import BookingForm from '../components/BookingForm'
import CancelAppointmentModal from '../components/CancelAppointmentModal'
import RatingModal from '../components/RatingModal'
import { CURRENT_USER } from '../constants/currentUser'
import { api } from '../services/api'
import {
  combineLocalDateAndTime,
  formatLocalDateKey,
  toUtcIsoString,
} from '../utils/datetime'

const emptyForm = {
  serviceId: '',
  clinicId: '',
  appointmentDate: '',
  appointmentTime: '',
  notes: '',
}

/**
 * Appointment management page for upcoming/past visits, rescheduling, cancellation, and ratings.
 */
function MyAppointments() {
  const [appointments, setAppointments] = useState([])
  const [services, setServices] = useState([])
  const [clinics, setClinics] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reschedulingAppointment, setReschedulingAppointment] = useState(null)
  const [booking, setBooking] = useState(false)
  const [formData, setFormData] = useState(emptyForm)
  const [bookingError, setBookingError] = useState('')
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [appointmentToCancel, setAppointmentToCancel] = useState(null)
  const [cancelLoading, setCancelLoading] = useState(false)
  const [bookAgainAppointment, setBookAgainAppointment] = useState(null)
  const [ratingAppointment, setRatingAppointment] = useState(null)
  const [ratingSuccessMessage, setRatingSuccessMessage] = useState('')
  const [ratingSubmitting, setRatingSubmitting] = useState(false)
  const [ratingSubmitError, setRatingSubmitError] = useState('')

  const serviceById = useMemo(
    () => new Map(services.map((service) => [service.id, service])),
    [services],
  )
  const clinicById = useMemo(
    () => new Map(clinics.map((clinic) => [clinic.id, clinic])),
    [clinics],
  )

  const loadData = async () => {
    setLoading(true)
    try {
      const [appointmentsResponse, servicesResponse, clinicsResponse] = await Promise.all([
        api.get(`/appointments?user_id=${CURRENT_USER.id}`),
        api.get('/services'),
        api.get('/clinics'),
      ])
      setAppointments(appointmentsResponse)
      setServices(servicesResponse)
      setClinics(clinicsResponse)
      setError('')
    } catch (fetchError) {
      setError(`Failed to load appointments: ${fetchError.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const formatDate = (isoDate) =>
    new Date(isoDate).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })

  const formatTime = (isoDate) =>
    new Date(isoDate).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    })

  const handleRescheduleFormChange = useCallback((event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }, [])

  const openReschedule = (appointment) => {
    const dt = new Date(appointment.appointment_datetime)
    setBookAgainAppointment(null)
    setReschedulingAppointment(appointment)
    setBookingError('')
    const hh = String(dt.getHours()).padStart(2, '0')
    const mm = String(dt.getMinutes()).padStart(2, '0')
    setFormData({
      serviceId: String(appointment.service_id),
      clinicId: String(appointment.clinic_id),
      appointmentDate: formatLocalDateKey(dt),
      appointmentTime: `${hh}:${mm}`,
      notes: appointment.notes ?? '',
    })
  }

  const openBookAgain = (appointment) => {
    setReschedulingAppointment(null)
    setBookAgainAppointment({
      ...appointment,
      status: 'UPCOMING',
    })
    setBookingError('')
    setFormData({
      serviceId: String(appointment.service_id),
      clinicId: String(appointment.clinic_id),
      appointmentDate: '',
      appointmentTime: '',
      notes: appointment.notes ?? '',
    })
  }

  const handleRescheduleSubmit = async (event) => {
    event.preventDefault()
    if (!reschedulingAppointment) return

    setBookingError('')
    setBooking(true)

    try {
      const serviceId = Number.parseInt(formData.serviceId, 10)
      const clinicId = Number.parseInt(formData.clinicId, 10)
      const appointmentDateTime = combineLocalDateAndTime(
        formData.appointmentDate,
        formData.appointmentTime,
      )

      if (
        Number.isNaN(serviceId) ||
        Number.isNaN(clinicId) ||
        Number.isNaN(appointmentDateTime.getTime())
      ) {
        throw new Error('Please select valid date, time, clinic, and service.')
      }

      if (appointmentDateTime <= new Date()) {
        throw new Error('Please choose a future date and time.')
      }

      await api.patch(`/appointments/${reschedulingAppointment.id}`, {
        user_id: CURRENT_USER.id,
        service_id: serviceId,
        clinic_id: clinicId,
        notes: formData.notes?.trim() || null,
        appointment_datetime: toUtcIsoString(appointmentDateTime),
      })

      setReschedulingAppointment(null)
      setFormData(emptyForm)
      await loadData()
    } catch (submitError) {
      setBookingError(`Could not reschedule: ${submitError.message}`)
    } finally {
      setBooking(false)
    }
  }

  const handleBookAgainSubmit = async (event) => {
    event.preventDefault()
    if (!bookAgainAppointment) return

    setBookingError('')
    setBooking(true)
    try {
      const serviceId = Number.parseInt(formData.serviceId, 10)
      const clinicId = Number.parseInt(formData.clinicId, 10)
      const appointmentDateTime = combineLocalDateAndTime(
        formData.appointmentDate,
        formData.appointmentTime,
      )

      if (
        Number.isNaN(serviceId) ||
        Number.isNaN(clinicId) ||
        Number.isNaN(appointmentDateTime.getTime())
      ) {
        throw new Error('Please select valid date and time.')
      }

      if (appointmentDateTime <= new Date()) {
        throw new Error('Please choose a future date and time.')
      }

      await api.post('/appointments', {
        user_id: CURRENT_USER.id,
        service_id: serviceId,
        clinic_id: clinicId,
        notes: formData.notes?.trim() || null,
        appointment_datetime: toUtcIsoString(appointmentDateTime),
      })

      setBookAgainAppointment(null)
      setFormData(emptyForm)
      await loadData()
    } catch (submitError) {
      setBookingError(`Could not create appointment: ${submitError.message}`)
    } finally {
      setBooking(false)
    }
  }

  const openCancelModal = (appointment) => {
    setAppointmentToCancel(appointment)
    setShowCancelModal(true)
  }

  const confirmCancel = async () => {
    if (!appointmentToCancel) return
    setCancelLoading(true)
    try {
      await api.del(`/appointments/${appointmentToCancel.id}?user_id=${CURRENT_USER.id}`)
      setShowCancelModal(false)
      setAppointmentToCancel(null)
      await loadData()
    } catch (deleteError) {
      setError(`Could not cancel appointment: ${deleteError.message}`)
    } finally {
      setCancelLoading(false)
    }
  }

  const openRatingModal = (appointment) => {
    setRatingAppointment(appointment)
    setRatingSuccessMessage('')
    setRatingSubmitError('')
  }

  const submitRating = async (payload) => {
    if (!ratingAppointment) return
    setRatingSubmitting(true)
    setRatingSubmitError('')
    try {
      await api.post(`/appointments/${ratingAppointment.id}/reviews?user_id=${CURRENT_USER.id}`, payload)
      await loadData()
      setRatingSuccessMessage('Thank you for your review! The clinic rating has been updated.')
      setRatingAppointment(null)
    } catch (submitError) {
      setRatingSubmitError(`Could not submit review: ${submitError.message}`)
    } finally {
      setRatingSubmitting(false)
    }
  }

  const getAppointmentStatus = useCallback((appointment) => {
    const rawStatus = String(appointment.status ?? '').toUpperCase()
    if (rawStatus === 'UPCOMING' || rawStatus === 'COMPLETED' || rawStatus === 'CANCELLED') {
      return rawStatus
    }
    return new Date(appointment.appointment_datetime) > new Date() ? 'UPCOMING' : 'COMPLETED'
  }, [])

  const upcomingAppointments = useMemo(
    () =>
      appointments
        .filter((appointment) => getAppointmentStatus(appointment) === 'UPCOMING')
        .sort(
          (a, b) =>
            new Date(a.appointment_datetime).getTime() - new Date(b.appointment_datetime).getTime(),
        ),
    [appointments, getAppointmentStatus],
  )

  const pastAppointments = useMemo(
    () =>
      appointments
        .filter((appointment) => {
          const status = getAppointmentStatus(appointment)
          return status === 'COMPLETED' || status === 'CANCELLED'
        })
        .sort(
          (a, b) =>
            new Date(b.appointment_datetime).getTime() - new Date(a.appointment_datetime).getTime(),
        ),
    [appointments, getAppointmentStatus],
  )

  const renderAppointmentCard = (appointment, isPastSection) => {
    const clinic = clinicById.get(appointment.clinic_id)
    const service = serviceById.get(appointment.service_id)
    const status = getAppointmentStatus(appointment)
    const isUpcoming = status === 'UPCOMING'
    const canRate = status === 'COMPLETED'
    const isAlreadyRated = Boolean(appointment.rating_id)
    const canOpenRating = canRate && !isAlreadyRated

    return (
      <article
        key={appointment.id}
        className={`rounded-2xl border p-4 ${
          isPastSection
            ? 'border-slate-200/80 bg-slate-50 shadow-sm transition hover:bg-slate-100 hover:shadow-md'
            : 'border-slate-200 bg-white shadow-md transition hover:bg-slate-50 hover:shadow-lg'
        }`}
      >
        <div className="flex items-start justify-between">
          <div className="flex flex-col gap-1 text-base font-semibold leading-6 text-slate-800 sm:flex-row sm:items-center sm:gap-4">
            <span className="inline-flex items-center gap-2">
              <span className="text-xs text-slate-400">📅</span>
              {formatDate(appointment.appointment_datetime)}
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="text-xs text-slate-400">🕘</span>
              {formatTime(appointment.appointment_datetime)}
            </span>
          </div>
          <span
            className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
              isUpcoming
                ? 'bg-[#DDF3EE] text-[#1E7665]'
                : status === 'CANCELLED'
                  ? 'bg-slate-200 text-slate-600'
                  : 'bg-slate-200 text-slate-700'
            }`}
          >
            {isUpcoming ? 'Upcoming' : status === 'CANCELLED' ? 'Cancelled' : 'Completed'}
          </span>
        </div>

        <div className="mt-3">
          <h2 className="text-base font-semibold leading-6 tracking-tight text-slate-900">
            {appointment.clinic_name ?? clinic?.name ?? `Clinic #${appointment.clinic_id}`}
          </h2>
          <p className="mt-0.5 text-sm leading-5 text-slate-600">
            {appointment.service_name ?? service?.name ?? `Service #${appointment.service_id}`}
          </p>
        </div>

        <div className="mt-3 border-t border-slate-200 pt-3 text-sm leading-5 text-slate-500">
          <p className="mb-2 inline-flex items-center gap-2">
            <span className="text-xs text-slate-400">📞</span>
            {appointment.user_phone}
          </p>
          <p className="inline-flex items-center gap-2">
            <span className="text-xs text-slate-400">📍</span>
            {clinic ? `${clinic.address}, ${clinic.city}` : 'Address unavailable'}
          </p>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-3">
          {isUpcoming ? (
            <>
              <button
                type="button"
                onClick={() => openReschedule(appointment)}
                className="inline-flex h-9 items-center justify-center gap-2 rounded-full bg-slate-100 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
              >
                <span className="text-xs text-slate-500">↻</span>
                Reschedule
              </button>
              <button
                type="button"
                onClick={() => openCancelModal(appointment)}
                className="inline-flex h-9 items-center justify-center gap-2 rounded-full border border-rose-200 bg-white px-3 text-sm font-medium text-rose-600 transition hover:bg-rose-50"
              >
                <span className="text-xs">✕</span>
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={() => canOpenRating && openRatingModal(appointment)}
                disabled={!canOpenRating}
                className={`inline-flex h-12 items-center justify-center gap-2 rounded-full px-4 text-sm font-semibold transition ${
                  canOpenRating
                    ? 'bg-[#C9DCE0] text-[#1A2B3C] hover:brightness-95'
                    : 'cursor-not-allowed bg-slate-200 text-slate-500'
                }`}
              >
                <span className="text-sm leading-none">{isAlreadyRated ? '✓' : '☆'}</span>
                {isAlreadyRated ? 'Already Rated' : 'Rate Visit'}
              </button>
              <button
                type="button"
                onClick={() => openBookAgain(appointment)}
                className="inline-flex h-12 items-center justify-center rounded-full bg-[#1A2B3C] px-4 text-sm font-semibold text-white transition hover:brightness-110"
              >
                Book Again
              </button>
            </>
          )}
        </div>
      </article>
    )
  }

  return (
    <section className="mx-auto max-w-3xl px-5 py-8">
      <h1 className="text-2xl font-semibold leading-tight tracking-tight text-slate-900">
        My Appointments ({CURRENT_USER.name})
      </h1>
      <p className="mt-1 text-sm leading-5 tracking-normal text-slate-500">
        Manage your upcoming and past appointments
      </p>

      {error && <p className="mt-4 rounded-lg bg-rose-100 px-4 py-3 text-rose-700">{error}</p>}

      {loading && <p className="mt-6 text-xl text-slate-500">Loading appointments...</p>}
      {!loading && upcomingAppointments.length === 0 && pastAppointments.length === 0 && (
        <p className="mt-4 rounded-xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
          No appointments found.
        </p>
      )}

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-slate-900">Upcoming Appointments</h2>
        {loading ? null : upcomingAppointments.length === 0 ? (
          <p className="mt-3 rounded-xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
            No upcoming appointments
          </p>
        ) : (
          <div className="mt-3 grid gap-4 md:grid-cols-2">
            {upcomingAppointments.map((appointment) => renderAppointmentCard(appointment, false))}
          </div>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold text-slate-900">Past Visits</h2>
        {loading ? null : pastAppointments.length === 0 ? (
          <p className="mt-3 rounded-xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
            No past visits
          </p>
        ) : (
          <div className="mt-3 grid gap-4 md:grid-cols-2">
            {pastAppointments.map((appointment) => renderAppointmentCard(appointment, true))}
          </div>
        )}
      </section>

      {ratingSuccessMessage && (
        <p className="mt-4 rounded-lg bg-emerald-100 px-4 py-3 text-emerald-800">
          {ratingSuccessMessage}
        </p>
      )}

      <BookingForm
        key={
          reschedulingAppointment
            ? `reschedule-${reschedulingAppointment.id}`
            : bookAgainAppointment
              ? `book-again-${bookAgainAppointment.id}`
              : 'booking-modal-closed'
        }
        isOpen={Boolean(reschedulingAppointment || bookAgainAppointment)}
        onClose={() => {
          setReschedulingAppointment(null)
          setBookAgainAppointment(null)
        }}
        title={reschedulingAppointment ? 'Reschedule Appointment' : 'Book Again'}
        submitLabel={reschedulingAppointment ? 'Confirm Reschedule' : 'Confirm Booking'}
        variant="reschedule"
        selectedClinicName={
          reschedulingAppointment
            ? clinicById.get(reschedulingAppointment.clinic_id)?.name
            : bookAgainAppointment
              ? clinicById.get(bookAgainAppointment.clinic_id)?.name
              : ''
        }
        selectedServiceName={
          reschedulingAppointment
            ? serviceById.get(reschedulingAppointment.service_id)?.name ?? ''
            : bookAgainAppointment
              ? serviceById.get(bookAgainAppointment.service_id)?.name ?? ''
              : ''
        }
        currentAppointmentLabel={
          reschedulingAppointment
            ? `${formatDate(reschedulingAppointment.appointment_datetime)} at ${formatTime(
                reschedulingAppointment.appointment_datetime,
              )}`
            : ''
        }
        formData={formData}
        services={services}
        clinics={clinics}
        booking={booking}
        successMessage=""
        errorMessage={bookingError}
        onChange={handleRescheduleFormChange}
        onSubmit={reschedulingAppointment ? handleRescheduleSubmit : handleBookAgainSubmit}
        excludeAppointmentId={reschedulingAppointment?.id ?? null}
      />

      <CancelAppointmentModal
        isOpen={Boolean(showCancelModal && appointmentToCancel)}
        clinicName={
          appointmentToCancel
            ? clinicById.get(appointmentToCancel.clinic_id)?.name ?? 'Clinic'
            : 'Clinic'
        }
        serviceName={
          appointmentToCancel
            ? serviceById.get(appointmentToCancel.service_id)?.name ?? 'Service'
            : 'Service'
        }
        dateTimeLabel={
          appointmentToCancel
            ? `${formatDate(appointmentToCancel.appointment_datetime)} at ${formatTime(
                appointmentToCancel.appointment_datetime,
              )}`
            : ''
        }
        loading={cancelLoading}
        onConfirm={confirmCancel}
        onClose={() => setShowCancelModal(false)}
      />

      {ratingAppointment && (
        <RatingModal
          isOpen
          appointment={ratingAppointment}
          appointmentRated={Boolean(ratingAppointment.rating_id)}
          clinicName={clinicById.get(ratingAppointment.clinic_id)?.name ?? 'Clinic'}
          serviceName={serviceById.get(ratingAppointment.service_id)?.name ?? 'Service'}
          timeLabel={`${formatDate(ratingAppointment.appointment_datetime)} at ${formatTime(
            ratingAppointment.appointment_datetime,
          )}`}
          onClose={() => setRatingAppointment(null)}
          onSubmit={submitRating}
          submitting={ratingSubmitting}
          submitError={ratingSubmitError}
        />
      )}
    </section>
  )
}

export default MyAppointments
