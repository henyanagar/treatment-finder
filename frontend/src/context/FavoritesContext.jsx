/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useState } from 'react'

const STORAGE_KEY = 'treatmentfinder:favorite-clinic-ids'

function readStoredIds() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.map(Number).filter((n) => Number.isFinite(n) && n > 0)
  } catch {
    return []
  }
}

const FavoritesContext = createContext(null)

export function FavoritesProvider({ children }) {
  const [favoriteIds, setFavoriteIds] = useState(readStoredIds)

  const toggleFavorite = useCallback(
    (clinicId) => {
      const id = Number(clinicId)
      if (!Number.isFinite(id) || id <= 0) return
      setFavoriteIds((prev) => {
        const set = new Set(prev)
        if (set.has(id)) set.delete(id)
        else set.add(id)
        const next = [...set].sort((a, b) => a - b)
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
        return next
      })
    },
    [],
  )

  const isFavorite = useCallback((clinicId) => favoriteIds.includes(Number(clinicId)), [favoriteIds])

  const value = useMemo(
    () => ({ favoriteIds, toggleFavorite, isFavorite }),
    [favoriteIds, toggleFavorite, isFavorite],
  )

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) {
    throw new Error('useFavorites must be used within FavoritesProvider')
  }
  return ctx
}
