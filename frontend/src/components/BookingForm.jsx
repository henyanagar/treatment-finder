import { useEffect, useMemo, useRef, useState } from 'react'
import { CURRENT_USER } from '../constants/currentUser'
import { fetchAppointmentOccupancy, fetchClinicServices } from '../services/api'
import {
  combineLocalDateAndTime,
  formatLocalDateKey,
  formatSlotLabel,
  localDayUtcRangeIso,
  normalizeOccupiedIso,
  parseLocalDateKey,
} from '../utils/datetime'

const ALL_TIME_SLOTS = [
  '09:00',
  '10:00',
  '11:00',
  '12:00',
  '13:00',
  '14:00',
  '15:00',
  '16:00',
  '17:00',
]

/**
 * Shared booking modal for new booking, reschedule, and book-again flows.
 * @param {{
 *   isOpen: boolean,
 *   onClose: () => void,
 *   title?: string,
 *   submitLabel?: string,
 *   variant?: 'booking' | 'reschedule',
 *   selectedClinicName?: string,
 *   selectedServiceName?: string,
 *   currentAppointmentLabel?: string,
 *   formData: {serviceId:string, clinicId:string, appointmentDate:string, appointmentTime:string, notes:string},
 *   services: Array<{id:number, name:string}>,
 *   clinics: Array<{id:number, name:string, services?: Array<{service_id:number, price?:number, is_available?:boolean}>}>,
 *   booking: boolean,
 *   successMessage?: string,
 *   errorMessage?: string,
 *   onChange: (event: {target: {name: string, value: string}}) => void,
 *   onSubmit: (event: Event) => void,
 *   excludeAppointmentId?: number | null
 * }} props
 */
function BookingForm({
  isOpen,
  onClose,
  title = 'Book Appointment',
  submitLabel = 'Confirm Booking',
  variant = 'booking',
  selectedClinicName,
  selectedServiceName = '',
  currentAppointmentLabel = '',
  formData,
  services,
  clinics,
  booking,
  successMessage,
  errorMessage,
  onChange,
  onSubmit,
  excludeAppointmentId = null,
}) {
  const dateInputRef = useRef(null)
  const appointmentDate = formData?.appointmentDate ?? ''
  const appointmentTime = formData?.appointmentTime ?? ''
  const [calendarMonth, setCalendarMonth] = useState(() =>
    appointmentDate ? parseLocalDateKey(appointmentDate) : new Date(),
  )
  const [bookingCalendarMonth, setBookingCalendarMonth] = useState(() =>
    appointmentDate ? parseLocalDateKey(appointmentDate) : new Date(),
  )
  const [isBookingDatePickerOpen, setIsBookingDatePickerOpen] = useState(false)
  const [isBookingTimeOpen, setIsBookingTimeOpen] = useState(false)
  const [occupancyLoading, setOccupancyLoading] = useState(false)
  const [availableSlots, setAvailableSlots] = useState([])
  const [clinicServices, setClinicServices] = useState([])
  const [clinicServicesLoading, setClinicServicesLoading] = useState(false)

  const todayKey = useMemo(() => formatLocalDateKey(new Date()), [])
  const clinicNumericId = Number.parseInt(formData?.clinicId, 10)
  const clinicReady = Number.isFinite(clinicNumericId) && clinicNumericId > 0
  const serviceById = useMemo(() => new Map(services.map((service) => [service.id, service])), [services])

  const serviceOptions = useMemo(() => {
    const selectedClinic = clinics.find((clinic) => String(clinic.id) === String(formData?.clinicId))
    const embeddedLinks = Array.isArray(selectedClinic?.services) ? selectedClinic.services : null
    const links = embeddedLinks ?? clinicServices

    return links
      .map((link) => {
        const serviceId = Number.parseInt(String(link.service_id ?? link.serviceId), 10)
        if (!Number.isFinite(serviceId)) return null
        const serviceName = link.service_name ?? link.serviceName ?? serviceById.get(serviceId)?.name
        if (!serviceName) return null
        const price = link.price
        const hasPrice = typeof price === 'number' && Number.isFinite(price)
        const label = hasPrice ? `${serviceName} - $${price.toFixed(2)}` : serviceName
        return { id: serviceId, label }
      })
      .filter(Boolean)
  }, [clinics, formData?.clinicId, clinicServices, serviceById])

  const hasServiceOptions = serviceOptions.length > 0
  const selectedServiceLabel = useMemo(() => {
    const selectedId = Number.parseInt(String(formData?.serviceId ?? ''), 10)
    if (!Number.isFinite(selectedId)) return selectedServiceName
    const byOption = serviceOptions.find((option) => option.id === selectedId)?.label
    if (byOption) return byOption
    return selectedServiceName
  }, [formData?.serviceId, selectedServiceName, serviceOptions])

  useEffect(() => {
    if (!isOpen || !appointmentDate || !clinicReady) {
      setAvailableSlots([])
      return undefined
    }

    let cancelled = false

    const load = async () => {
      setOccupancyLoading(true)
      try {
        const { startIso, endIso } = localDayUtcRangeIso(appointmentDate)
        const data = await fetchAppointmentOccupancy({
          clinicId: clinicNumericId,
          rangeStartIso: startIso,
          rangeEndIso: endIso,
          excludeAppointmentId:
            excludeAppointmentId != null ? excludeAppointmentId : undefined,
        })
        const occupied = new Set(
          (data.occupied_datetimes ?? []).map((iso) => normalizeOccupiedIso(iso)),
        )

        const slotsAfterPastFilter = ALL_TIME_SLOTS.filter((slot) => {
          const instant = combineLocalDateAndTime(appointmentDate, slot)
          return instant > new Date()
        })

        const free = slotsAfterPastFilter.filter((slot) => {
          const iso = normalizeOccupiedIso(
            combineLocalDateAndTime(appointmentDate, slot).toISOString(),
          )
          return !occupied.has(iso)
        })

        if (!cancelled) {
          setAvailableSlots(free)
        }
      } catch {
        if (!cancelled) {
          setAvailableSlots([])
        }
      } finally {
        if (!cancelled) {
          setOccupancyLoading(false)
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [
    isOpen,
    appointmentDate,
    clinicNumericId,
    clinicReady,
    excludeAppointmentId,
  ])

  useEffect(() => {
    if (!isOpen || !clinicReady) {
      setClinicServices([])
      return undefined
    }

    const selectedClinic = clinics.find((clinic) => String(clinic.id) === String(formData?.clinicId))
    if (Array.isArray(selectedClinic?.services)) {
      setClinicServices([])
      return undefined
    }

    let cancelled = false
    const loadClinicServices = async () => {
      setClinicServicesLoading(true)
      try {
        const response = await fetchClinicServices(clinicNumericId)
        if (!cancelled) {
          setClinicServices(Array.isArray(response) ? response : [])
        }
      } catch {
        if (!cancelled) {
          setClinicServices([])
        }
      } finally {
        if (!cancelled) {
          setClinicServicesLoading(false)
        }
      }
    }

    loadClinicServices()
    return () => {
      cancelled = true
    }
  }, [isOpen, clinicReady, clinicNumericId, clinics, formData?.clinicId])

  const showTimeUi = Boolean(appointmentDate)
  const timeSlots = availableSlots
  const selectedDateTime = useMemo(() => {
    if (!appointmentDate || !appointmentTime) return null
    const value = combineLocalDateAndTime(appointmentDate, appointmentTime)
    if (Number.isNaN(value.getTime())) return null
    return value
  }, [appointmentDate, appointmentTime])
  const isFutureDateTime = Boolean(selectedDateTime && selectedDateTime > new Date())

  useEffect(() => {
    if (!appointmentDate || !appointmentTime) return
    if (!timeSlots.includes(appointmentTime)) {
      onChange({ target: { name: 'appointmentTime', value: '' } })
    }
  }, [appointmentDate, appointmentTime, timeSlots, onChange])

  useEffect(() => {
    if (variant === 'reschedule') return
    if (!formData.serviceId) return
    const selectedId = Number.parseInt(formData.serviceId, 10)
    if (!serviceOptions.some((option) => option.id === selectedId)) {
      onChange({ target: { name: 'serviceId', value: '' } })
    }
  }, [formData.serviceId, serviceOptions, onChange, variant])

  const prevClinicIdRef = useRef(undefined)
  useEffect(() => {
    if (variant !== 'booking') return
    if (prevClinicIdRef.current === undefined) {
      prevClinicIdRef.current = formData.clinicId
      return
    }
    if (prevClinicIdRef.current !== formData.clinicId) {
      prevClinicIdRef.current = formData.clinicId
      onChange({ target: { name: 'serviceId', value: '' } })
      onChange({ target: { name: 'appointmentTime', value: '' } })
    }
  }, [formData.clinicId, variant, onChange])

  const handleDateSelect = (value) => {
    onChange({ target: { name: 'appointmentDate', value } })
    onChange({ target: { name: 'appointmentTime', value: '' } })
  }

  const monthLabel = calendarMonth.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  })

  const dayCells = useMemo(() => {
    const cells = []
    const startOfMonth = new Date(calendarMonth.getFullYear(), calendarMonth.getMonth(), 1)
    const startWeekDay = startOfMonth.getDay()
    const currentMonth = calendarMonth.getMonth()
    const firstCellDate = new Date(startOfMonth)
    firstCellDate.setDate(1 - startWeekDay)

    for (let i = 0; i < 42; i += 1) {
      const date = new Date(firstCellDate)
      date.setDate(firstCellDate.getDate() + i)
      const dateValue = formatLocalDateKey(date)
      const isPastDate = dateValue < todayKey
      cells.push({
        label: date.getDate(),
        value: dateValue,
        inCurrentMonth: date.getMonth() === currentMonth,
        isSelected: appointmentDate === dateValue,
        isPastDate,
      })
    }

    return cells
  }, [calendarMonth, appointmentDate, todayKey])

  const bookingDayCells = useMemo(() => {
    const cells = []
    const startOfMonth = new Date(
      bookingCalendarMonth.getFullYear(),
      bookingCalendarMonth.getMonth(),
      1,
    )
    const startWeekDay = startOfMonth.getDay()
    const currentMonth = bookingCalendarMonth.getMonth()
    const firstCellDate = new Date(startOfMonth)
    firstCellDate.setDate(1 - startWeekDay)

    for (let i = 0; i < 42; i += 1) {
      const date = new Date(firstCellDate)
      date.setDate(firstCellDate.getDate() + i)
      const dateValue = formatLocalDateKey(date)
      const isPastDate = dateValue < todayKey
      cells.push({
        label: date.getDate(),
        value: dateValue,
        inCurrentMonth: date.getMonth() === currentMonth,
        isSelected: appointmentDate === dateValue,
        isPastDate,
      })
    }
    return cells
  }, [bookingCalendarMonth, appointmentDate, todayKey])

  const formatDateDisplay = (value) => {
    if (!value) return 'dd/mm/yyyy'
    const [year, month, day] = value.split('-')
    return `${day}/${month}/${year}`
  }

  if (!isOpen) return null

  if (variant === 'reschedule') {
    return (
      <div className="fixed inset-0 z-50">
        <button
          type="button"
          className="absolute inset-0 bg-slate-900/45 backdrop-blur-[2px]"
          onClick={onClose}
          aria-label="Close booking panel"
        />

        <div className="absolute left-1/2 top-1/2 w-[94%] max-w-[460px] -translate-x-1/2 -translate-y-1/2 rounded-3xl bg-white p-5 shadow-2xl">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-5 top-5 rounded-full p-1 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
          >
            ✕
          </button>

          <h2 className="text-base font-semibold text-slate-800">{title}</h2>
          <p className="mt-1 text-sm text-slate-600">Booking for: {CURRENT_USER.name}</p>
          <p className="mt-2 text-base font-semibold text-slate-800">{selectedClinicName}</p>
          {selectedServiceLabel && <p className="mt-0.5 text-sm text-slate-500">{selectedServiceLabel}</p>}
          {currentAppointmentLabel && (
            <p className="mt-1.5 text-sm text-slate-500">Current: {currentAppointmentLabel}</p>
          )}

          <form onSubmit={onSubmit} className="max-h-[70vh] overflow-y-auto pr-1">
            <div className="mt-5">
              <p className="mb-2 inline-flex items-center gap-2 text-base font-semibold text-slate-800">
                <span>📅</span>
                Select New Date
              </p>

              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4">
                <div className="mb-3 flex items-center justify-center gap-10">
                  <button
                    type="button"
                    onClick={() =>
                      setCalendarMonth(
                        new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() - 1, 1),
                      )
                    }
                    className="h-7 w-7 rounded-full border border-slate-200 text-slate-400 transition hover:bg-white hover:text-slate-700"
                  >
                    ‹
                  </button>
                  <p className="text-sm font-semibold text-slate-700">{monthLabel}</p>
                  <button
                    type="button"
                    onClick={() =>
                      setCalendarMonth(
                        new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1, 1),
                      )
                    }
                    className="h-7 w-7 rounded-full border border-slate-200 text-slate-400 transition hover:bg-white hover:text-slate-700"
                  >
                    ›
                  </button>
                </div>

                <div className="mb-1.5 grid grid-cols-7 text-center text-xs text-slate-500">
                  {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
                    <span key={day}>{day}</span>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-y-1 text-center text-sm">
                  {dayCells.map((cell) => (
                    <button
                      key={cell.value}
                      type="button"
                      disabled={cell.isPastDate}
                      onClick={() => {
                        if (!cell.isPastDate) handleDateSelect(cell.value)
                      }}
                      className={`mx-auto h-8 w-8 rounded-full transition ${
                        cell.isPastDate
                          ? 'cursor-not-allowed text-slate-300'
                          : cell.isSelected
                            ? 'bg-[#E8E1EE] text-slate-700'
                            : cell.inCurrentMonth
                              ? 'text-slate-700 hover:bg-slate-200'
                              : 'text-slate-400'
                      }`}
                    >
                      {cell.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div
              className={`overflow-hidden transition-all duration-300 ease-out ${
                showTimeUi ? 'mt-5 max-h-[280px] opacity-100' : 'max-h-0 opacity-0'
              }`}
            >
              <div>
                <p className="mb-2 inline-flex items-center gap-2 text-base font-semibold text-slate-800">
                  <span>🕘</span>
                  Select Time
                </p>
                {occupancyLoading && (
                  <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
                    Checking availability…
                  </p>
                )}
                {!occupancyLoading && clinicReady && timeSlots.length === 0 && (
                  <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-600">
                    No available slots for this date
                  </p>
                )}
                {!occupancyLoading && timeSlots.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {timeSlots.map((slot) => {
                      const isSelected = formData.appointmentTime === slot
                      return (
                        <button
                          key={slot}
                          type="button"
                          onClick={() =>
                            onChange({ target: { name: 'appointmentTime', value: slot } })
                          }
                          className={`rounded-xl border bg-white px-2 py-1.5 text-sm font-medium transition ${
                            isSelected
                              ? 'border-2 border-[#1A2B3C] text-[#1A2B3C]'
                              : 'border-slate-300 text-slate-700 hover:border-slate-400'
                          }`}
                        >
                          {formatSlotLabel(slot)}
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            <input
              ref={dateInputRef}
              type="date"
              name="appointmentDate"
              value={formData.appointmentDate}
              onChange={onChange}
              min={todayKey}
              className="sr-only"
              required
            />

            {errorMessage && (
              <p className="mt-4 rounded-md bg-rose-100 px-3 py-2 text-rose-700">{errorMessage}</p>
            )}

            <div className="mt-5 grid grid-cols-2 gap-2.5 border-t border-slate-200 pt-3.5">
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={
                  booking ||
                  !formData.serviceId ||
                  !appointmentDate ||
                  !formData.appointmentTime ||
                  occupancyLoading ||
                  !timeSlots.includes(formData.appointmentTime) ||
                  !isFutureDateTime
                }
                className="rounded-xl bg-[#1A2B3C] px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-100"
              >
                {booking ? 'Saving...' : submitLabel}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        className="absolute inset-0 bg-slate-900/45 backdrop-blur-[2px]"
        onClick={onClose}
        aria-label="Close booking panel"
      />

      <aside className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto bg-white p-6 shadow-2xl">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="text-[38px] font-semibold leading-tight text-slate-800">{title}</h2>
            <p className="mt-1 text-sm text-slate-500">{selectedClinicName || 'Select clinic'}</p>
            {selectedServiceLabel && <p className="mt-0.5 text-sm text-slate-500">{selectedServiceLabel}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
          >
            ✕
          </button>
        </div>

        <section className="mb-4 rounded-2xl border border-cyan-100 bg-[#f8fefe] px-4 py-2.5">
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 shrink-0 text-slate-500">
              <svg viewBox="0 0 24 24" className="h-4.5 w-4.5">
                <path
                  d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-3.31 0-6 1.79-6 4v1h12v-1c0-2.21-2.69-4-6-4Z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium leading-5 text-slate-500">Booking for</p>
              <p className="mt-0.5 text-sm font-semibold leading-5 text-slate-800">
                {CURRENT_USER.name}
              </p>
              <p className="mt-0.5 text-sm leading-5 text-slate-500">
                {CURRENT_USER.email}
              </p>
            </div>
          </div>
        </section>

        <form className="space-y-3.5" onSubmit={onSubmit}>
          <label className="block">
            <span className="mb-1.5 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
              <span>🩺</span>
              Service
            </span>
            <select
              name="serviceId"
              value={formData.serviceId}
              onChange={onChange}
              required
              disabled={!clinicReady || clinicServicesLoading || !hasServiceOptions}
              className="h-11 w-full rounded-xl border border-gray-200 bg-slate-50 px-4 text-sm text-slate-700 outline-none transition focus:border-slate-300 focus:bg-white disabled:cursor-not-allowed disabled:text-slate-400"
            >
              {!clinicReady ? (
                <option value="">Select clinic first</option>
              ) : clinicServicesLoading ? (
                <option value="">Loading services...</option>
              ) : !hasServiceOptions ? (
                <option value="">No services available for this clinic</option>
              ) : (
                <>
                  <option value="">Select a service</option>
                  {serviceOptions.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.label}
                    </option>
                  ))}
                </>
              )}
            </select>
          </label>

          <div className="grid grid-cols-2 gap-3">
            <div className="block">
              <span className="mb-1.5 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                <IconCalendar />
                Preferred Date
              </span>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setBookingCalendarMonth(
                      appointmentDate ? parseLocalDateKey(appointmentDate) : new Date(),
                    )
                    setIsBookingTimeOpen(false)
                    setIsBookingDatePickerOpen((prev) => !prev)
                  }}
                  className="flex h-11 w-full items-center justify-between rounded-xl border border-gray-200 bg-slate-50 px-4 text-sm text-slate-700 transition hover:bg-white"
                >
                  <span>{formatDateDisplay(appointmentDate)}</span>
                  <IconCalendar />
                </button>

                {isBookingDatePickerOpen && (
                  <div className="absolute left-0 top-12 z-20 w-[250px] rounded-xl border border-slate-200 bg-white p-3 shadow-lg">
                    <div className="mb-2 flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() =>
                          setBookingCalendarMonth(
                            new Date(
                              bookingCalendarMonth.getFullYear(),
                              bookingCalendarMonth.getMonth() - 1,
                              1,
                            ),
                          )
                        }
                        className="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100"
                      >
                        ‹
                      </button>
                      <span className="text-sm font-semibold text-slate-700">
                        {bookingCalendarMonth.toLocaleDateString('en-US', {
                          month: 'long',
                          year: 'numeric',
                        })}
                      </span>
                      <button
                        type="button"
                        onClick={() =>
                          setBookingCalendarMonth(
                            new Date(
                              bookingCalendarMonth.getFullYear(),
                              bookingCalendarMonth.getMonth() + 1,
                              1,
                            ),
                          )
                        }
                        className="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100"
                      >
                        ›
                      </button>
                    </div>

                    <div className="mb-1 grid grid-cols-7 text-center text-[11px] text-slate-500">
                      {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
                        <span key={day}>{day}</span>
                      ))}
                    </div>
                    <div className="grid grid-cols-7 gap-y-1 text-center text-xs">
                      {bookingDayCells.map((cell) => (
                        <button
                          key={cell.value}
                          type="button"
                          disabled={cell.isPastDate}
                          onClick={() => {
                            if (cell.isPastDate) return
                            onChange({ target: { name: 'appointmentDate', value: cell.value } })
                            onChange({ target: { name: 'appointmentTime', value: '' } })
                            setIsBookingDatePickerOpen(false)
                          }}
                          className={`mx-auto h-7 w-7 rounded-full ${
                            cell.isPastDate
                              ? 'cursor-not-allowed text-slate-300'
                              : cell.isSelected
                                ? 'bg-[#1A2B3C] text-white'
                                : cell.inCurrentMonth
                                  ? 'text-slate-700 hover:bg-slate-100'
                                  : 'text-slate-400'
                          }`}
                        >
                          {cell.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {!appointmentDate ? (
              <div className="block">
                <span className="mb-1.5 inline-flex items-center gap-2 text-sm font-medium text-slate-400">
                  <IconClock />
                  Preferred Time
                </span>
                <div className="flex h-11 items-center rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 text-sm text-slate-400">
                  Select a date first
                </div>
              </div>
            ) : (
              <label className="block">
                <span className="mb-1.5 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                  <IconClock />
                  Preferred Time
                </span>
                {!clinicReady ? (
                  <div className="flex h-11 items-center rounded-xl border border-amber-200 bg-amber-50 px-4 text-sm text-amber-900">
                    Select a clinic to see times
                  </div>
                ) : (
                  <div className="relative">
                    <button
                      type="button"
                      disabled={occupancyLoading}
                      onClick={() => {
                        setIsBookingDatePickerOpen(false)
                        if (!occupancyLoading) setIsBookingTimeOpen((prev) => !prev)
                      }}
                      className="flex h-11 w-full items-center justify-between rounded-xl border border-gray-200 bg-slate-50 px-4 text-sm text-slate-700 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <span>
                        {occupancyLoading
                          ? 'Checking availability…'
                          : appointmentTime
                            ? formatSlotLabel(appointmentTime)
                            : 'Select'}
                      </span>
                      <svg viewBox="0 0 20 20" className="h-3.5 w-3.5 text-slate-500">
                        <path d="m5 7 5 6 5-6H5Z" fill="currentColor" />
                      </svg>
                    </button>
                    {isBookingTimeOpen && !occupancyLoading && (
                      <div className="absolute left-0 top-12 z-20 max-h-56 w-full overflow-y-auto rounded-xl border border-slate-200 bg-white p-1 shadow-lg">
                        {timeSlots.length === 0 ? (
                          <p className="px-3 py-2.5 text-sm font-medium text-slate-600">
                            No available slots for this date
                          </p>
                        ) : (
                          <>
                            <button
                              type="button"
                              onClick={() => {
                                onChange({ target: { name: 'appointmentTime', value: '' } })
                                setIsBookingTimeOpen(false)
                              }}
                              className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-600 transition hover:bg-slate-100"
                            >
                              Select
                            </button>
                            {timeSlots.map((slot) => {
                              const selected = appointmentTime === slot
                              return (
                                <button
                                  key={slot}
                                  type="button"
                                  onClick={() => {
                                    onChange({ target: { name: 'appointmentTime', value: slot } })
                                    setIsBookingTimeOpen(false)
                                  }}
                                  className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                                    selected
                                      ? 'bg-slate-100 text-slate-800'
                                      : 'text-slate-700 hover:bg-slate-100'
                                  }`}
                                >
                                  {formatSlotLabel(slot)}
                                </button>
                              )
                            })}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </label>
            )}

            {!clinicReady && (
              <div className="col-span-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                Select a clinic from a card before choosing date/time.
              </div>
            )}

            {clinicReady && !hasServiceOptions && !clinicServicesLoading && (
              <div className="col-span-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                No services available for this clinic.
              </div>
            )}
          </div>

          <label className="block">
            <span className="mb-1.5 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
              <span>📝</span>
              Notes (Optional)
            </span>
            <textarea
              name="notes"
              value={formData.notes ?? ''}
              onChange={onChange}
              rows={3}
              className="w-full rounded-xl border border-gray-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-700 outline-none transition focus:border-slate-300 focus:bg-white"
              placeholder="Any specific requests or information for the clinic..."
            />
          </label>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-2xl bg-slate-100 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={
                booking ||
                !formData.serviceId ||
                !appointmentDate ||
                !appointmentTime ||
                !clinicReady ||
                occupancyLoading ||
                !timeSlots.includes(appointmentTime) ||
                !isFutureDateTime
              }
              className="rounded-2xl bg-[#1A2B3C] px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {booking ? 'Saving...' : submitLabel}
            </button>
          </div>
        </form>

        {successMessage && (
          <p className="mt-4 rounded-md bg-emerald-100 px-3 py-2 text-emerald-800">
            {successMessage}
          </p>
        )}

        {errorMessage && (
          <p className="mt-4 rounded-md bg-rose-100 px-3 py-2 text-rose-700">{errorMessage}</p>
        )}
      </aside>
    </div>
  )
}

/** Calendar icon used in date picker button. */
function IconCalendar() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 text-slate-400">
      <path
        d="M7 2a1 1 0 0 1 1 1v1h8V3a1 1 0 1 1 2 0v1h1a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1V3a1 1 0 1 1 2 0v1Zm12 7H5v9h14Zm0-2V6H5v1Z"
        fill="currentColor"
      />
    </svg>
  )
}

/** Clock icon used in time slot picker button. */
function IconClock() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 text-slate-400">
      <path
        d="M12 2a10 10 0 1 1-10 10A10 10 0 0 1 12 2Zm1 5a1 1 0 0 0-2 0v5.41l3.29 3.3a1 1 0 0 0 1.42-1.42L13 11.59Z"
        fill="currentColor"
      />
    </svg>
  )
}

export default BookingForm
