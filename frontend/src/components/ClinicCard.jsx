import { useFavorites } from '../context/FavoritesContext.jsx'

/**
 * Reusable clinic preview card used in search and favorites grids.
 * @param {{clinic: {clinicId:number, clinicName:string, city?:string, rating?:number, image_url?:string, imageUrl?:string, services?:string[]}, onBookNow: (clinicId:number, matchedServiceName?:string)=>void}} props
 */
function ClinicCard({ clinic, onBookNow }) {
  const clinicImage = clinic.image_url || clinic.imageUrl
  const { isFavorite, toggleFavorite } = useFavorites()
  const favoriteActive = isFavorite(clinic.clinicId)

  const handleFavoriteClick = (event) => {
    event.preventDefault()
    event.stopPropagation()
    toggleFavorite(clinic.clinicId)
  }

  const favoriteAccent = 'rgb(183, 110, 121)'

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md">
      <div className="relative h-36 bg-gradient-to-br from-slate-100 via-slate-50 to-slate-200">
        {clinicImage && (
          <img
            src={clinicImage}
            alt={clinic.clinicName}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        )}
        <button
          type="button"
          onClick={handleFavoriteClick}
          aria-pressed={favoriteActive}
          aria-label={favoriteActive ? 'Remove from favorites' : 'Add to favorites'}
          className={`absolute right-3 top-3 z-10 flex size-10 shrink-0 items-center justify-center rounded-full border-0 bg-white p-0 shadow-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1A2B3C]/25 ${
            favoriteActive ? '' : 'text-slate-400 hover:text-[rgb(183,110,121)]'
          }`}
          style={{ color: favoriteActive ? favoriteAccent : undefined }}
        >
          {favoriteActive ? (
            <svg
              viewBox="0 0 24 24"
              className="h-[18px] w-[18px] shrink-0"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden
            >
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          ) : (
            <svg
              viewBox="0 0 24 24"
              className="h-[18px] w-[18px] shrink-0"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden
            >
              <path
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
              />
            </svg>
          )}
        </button>
      </div>
      <div className="space-y-3 p-4">
        <h3 className="text-xl font-semibold text-slate-800">{clinic.clinicName}</h3>
        <div className="flex items-center gap-4 text-sm text-slate-600">
          <span className="font-medium text-amber-500">★ {clinic.rating ?? '4.8'}</span>
          <span>📍 {clinic.city}</span>
        </div>
      </div>
      <div className="px-4 pb-4 pt-1">
        <button
          type="button"
          className="w-full rounded-2xl bg-[#1A2B3C] px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110"
          onClick={() => onBookNow(clinic.clinicId, clinic.services[0])}
        >
          Book Now
        </button>
      </div>
    </div>
  )
}

export default ClinicCard
