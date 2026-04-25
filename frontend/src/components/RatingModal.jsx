import { useState } from 'react'

const ACCENT_COLOR = 'rgb(183, 110, 121)'

/**
 * Modal used to submit a post-visit rating and optional review.
 * @param {{
 *   isOpen: boolean,
 *   appointment: {id:number, clinic_id:number} | null,
 *   appointmentRated?: boolean,
 *   clinicName: string,
 *   serviceName?: string,
 *   timeLabel?: string,
 *   onClose: () => void,
 *   onSubmit: (payload: {rating:number, title:string, review:string, clinic_id:number, appointment_id:number}) => void,
 *   submitting?: boolean,
 *   submitError?: string
 * }} props
 */
function RatingModal({
  isOpen,
  appointment,
  appointmentRated = false,
  clinicName,
  serviceName,
  timeLabel,
  onClose,
  onSubmit,
  submitting = false,
  submitError = '',
}) {
  const [rating, setRating] = useState(0)
  const [review, setReview] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    if (submitting || rating < 1 || appointmentRated) return
    onSubmit({
      rating,
      title: '',
      review: review.trim(),
      clinic_id: appointment.clinic_id,
      appointment_id: appointment.id,
    })
  }

  if (!isOpen || !appointment) return null

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        className="absolute inset-0 bg-slate-900/45 backdrop-blur-[2px]"
        onClick={onClose}
        aria-label="Close rating modal"
      />
      <form
        className="absolute left-1/2 top-1/2 w-[92%] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-3xl bg-white p-6 shadow-2xl"
        onSubmit={handleSubmit}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-3 rounded-full p-1 text-xl leading-none text-slate-500 transition hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={submitting}
        >
          ✕
        </button>

        <h3 className="text-xl font-semibold leading-tight tracking-tight text-slate-800">
          How was your experience?
        </h3>
        <p className="mt-1 text-sm text-slate-500">at {clinicName}</p>
        {serviceName && <p className="mt-1 text-sm text-slate-400">{serviceName}</p>}
        {timeLabel && <p className="text-sm text-slate-400">{timeLabel}</p>}

        <div className="mt-4">
          <div className="flex items-center justify-center gap-1">
            {[1, 2, 3, 4, 5].map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setRating(value)}
                disabled={submitting}
                className={`text-3xl leading-none transition disabled:cursor-not-allowed ${
                  value <= rating ? '' : 'text-slate-300 hover:text-slate-400'
                }`}
                aria-label={`Rate ${value} star${value > 1 ? 's' : ''}`}
                style={value <= rating ? { color: ACCENT_COLOR } : undefined}
              >
                {value <= rating ? '★' : '☆'}
              </button>
            ))}
          </div>
        </div>

        <label className="mt-4 block">
          <span className="mb-1.5 block text-sm font-medium leading-tight text-slate-700">
            Share your thoughts <span className="font-normal text-slate-500">(optional)</span>
          </span>
          <textarea
            value={review}
            onChange={(event) => setReview(event.target.value)}
            rows={3}
            maxLength={1500}
            disabled={submitting}
            className="w-full rounded-2xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm leading-5 text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-300 disabled:cursor-not-allowed disabled:bg-slate-50"
            placeholder="Tell us about your experience..."
          />
        </label>

        {submitError && <p className="mt-4 text-sm text-rose-600">{submitError}</p>}

        <button
          type="submit"
          disabled={submitting || rating < 1 || appointmentRated}
          className="mt-4 w-full rounded-full bg-[#8A96A3] px-4 py-3 text-sm font-semibold leading-tight text-white transition hover:brightness-105 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {appointmentRated ? 'Already Rated' : submitting ? 'Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  )
}

export default RatingModal
