// Base URL for all frontend API calls. Defaults to Vite proxy path in local development.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

/** Shared HTTP wrapper with normalized JSON/text parsing and friendly error messages. */
const request = async (endpoint, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    const contentType = response.headers.get('content-type')

    if (contentType && contentType.includes('application/json')) {
      const errorBody = await response.json()
      if (typeof errorBody?.detail === 'string') {
        message = errorBody.detail
      } else if (Array.isArray(errorBody?.detail) && errorBody.detail.length > 0) {
        message = errorBody.detail
          .map((item) => item?.msg)
          .filter(Boolean)
          .join(', ')
      }
    } else {
      const errorText = await response.text()
      if (errorText) {
        message = errorText
      }
    }

    throw new Error(message)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

/** Query occupancy for a clinic within a UTC half-open interval [range_start, range_end). */
export async function fetchAppointmentOccupancy({
  clinicId,
  rangeStartIso,
  rangeEndIso,
  excludeAppointmentId,
}) {
  const params = new URLSearchParams({
    clinic_id: String(clinicId),
    range_start: rangeStartIso,
    range_end: rangeEndIso,
  })
  if (excludeAppointmentId != null) {
    params.set('exclude_appointment_id', String(excludeAppointmentId))
  }
  return request(`/appointments/occupancy?${params}`)
}

export async function fetchClinicServices(clinicId) {
  return request(`/clinics/${clinicId}/services`)
}

/** Lightweight REST helpers used by page/components for CRUD operations. */
export const api = {
  get: (endpoint, options = {}) => request(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options = {}) =>
    request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint, body, options = {}) =>
    request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: (endpoint, body, options = {}) =>
    request(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  del: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' }),
}
