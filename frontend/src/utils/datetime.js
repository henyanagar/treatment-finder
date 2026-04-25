/** Local calendar date as YYYY-MM-DD (avoid UTC drift from toISOString()). */
export function formatLocalDateKey(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function parseLocalDateKey(ymd) {
  const [y, m, d] = ymd.split('-').map(Number)
  return new Date(y, m - 1, d, 12, 0, 0, 0)
}

/** UTC ISO range for the user's local calendar day [start, end). */
export function localDayUtcRangeIso(ymd) {
  const [y, m, d] = ymd.split('-').map(Number)
  const startLocal = new Date(y, m - 1, d, 0, 0, 0, 0)
  const endLocal = new Date(y, m - 1, d + 1, 0, 0, 0, 0)
  return { startIso: startLocal.toISOString(), endIso: endLocal.toISOString() }
}

/** Wall-clock instant in the user's timezone. */
export function combineLocalDateAndTime(ymd, hhmm) {
  const [y, mo, d] = ymd.split('-').map(Number)
  const [hh, mm] = hhmm.split(':').map(Number)
  return new Date(y, mo - 1, d, hh, mm, 0, 0)
}

export function toUtcIsoString(date) {
  return date.toISOString()
}

export function formatSlotLabel(hhmm) {
  const [h, m] = hhmm.split(':').map(Number)
  const anchor = new Date(2000, 0, 1, h, m, 0, 0)
  return anchor.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function normalizeOccupiedIso(iso) {
  return new Date(iso).toISOString()
}
