/**
 * Compact confirmation modal for cancelling an upcoming appointment.
 * @param {{
 *   isOpen: boolean,
 *   clinicName: string,
 *   serviceName: string,
 *   dateTimeLabel: string,
 *   loading?: boolean,
 *   onConfirm: () => void,
 *   onClose: () => void
 * }} props
 */
function CancelAppointmentModal({
  isOpen,
  clinicName,
  serviceName,
  dateTimeLabel,
  loading = false,
  onConfirm,
  onClose,
}) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        className="absolute inset-0 bg-slate-900/45 backdrop-blur-[2px]"
        onClick={onClose}
        aria-label="Close cancel confirmation"
      />

      <div className="absolute left-1/2 top-1/2 w-[92%] max-w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-3xl bg-white p-5 shadow-[0_16px_48px_rgba(15,23,42,0.18)] sm:p-6">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-3.5 top-3.5 rounded-full p-1 text-sm leading-none text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close"
        >
          ✕
        </button>

        <div className="mx-auto mb-3.5 flex h-12 w-12 items-center justify-center rounded-full bg-rose-50">
          <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border-2 border-[#FF3B30] text-sm font-bold leading-none text-[#FF3B30]">
            !
          </span>
        </div>

        <h3 className="text-center text-[1.25rem] font-bold leading-tight text-[#1A2B3C]">
          Cancel Appointment?
        </h3>
        <p className="mx-auto mt-2 max-w-[320px] text-center text-sm leading-6 text-slate-500">
          Are you sure you want to cancel this appointment? This action cannot be undone.
        </p>

        <div className="mt-4 rounded-2xl bg-slate-100 px-4 py-3.5 text-left">
          <p className="text-[1.05rem] font-bold text-[#1A2B3C]">{clinicName}</p>
          <p className="mt-0.5 text-[1rem] text-slate-500">{serviceName}</p>
          <p className="mt-1.5 text-[0.95rem] text-slate-500">{dateTimeLabel}</p>
        </div>

        <div className="mt-5 space-y-2.5">
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="w-full rounded-full bg-[#FF3B30] px-4 py-3 text-base font-bold text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Cancelling...' : 'Yes, Cancel Appointment'}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-full border border-slate-200 bg-white px-4 py-3 text-base font-semibold text-[#1A2B3C] transition hover:bg-slate-50"
          >
            Keep Appointment
          </button>
        </div>
      </div>
    </div>
  )
}

export default CancelAppointmentModal
