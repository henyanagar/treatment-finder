import { NavLink } from 'react-router-dom'
import { CURRENT_USER } from '../constants/currentUser'

/** Top navigation with route links and the current mock user profile chip. */
function Navbar() {
  const initials = CURRENT_USER.name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')

  const navItemClass = ({ isActive }) =>
    `inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium transition ${
      isActive
        ? 'text-[#0f2340]'
        : 'text-slate-700 hover:bg-slate-50 hover:text-[#0f2340]'
    }`

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-3.5 lg:px-8">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[#0f2340] text-sm text-white shadow-sm">
            ✦
          </span>
          <span className="text-xl font-semibold tracking-tight text-[#0f2340]">TreatmentFinder AI</span>
        </div>

        <nav className="hidden flex-1 items-center justify-center gap-2 sm:flex">
          <NavLink
            to="/"
            className={navItemClass}
          >
            <IconSearch />
            Search
          </NavLink>
          <NavLink
            to="/appointments"
            className={navItemClass}
          >
            <IconCalendar />
            Appointments
          </NavLink>
          <NavLink
            to="/favorites"
            className={navItemClass}
          >
            <IconHeart />
            My Favorites
          </NavLink>
        </nav>

        <div className="hidden items-center gap-4 sm:flex">
          <div className="h-10 w-px bg-slate-200" />
          <div className="text-right">
            <p className="text-sm font-semibold leading-tight text-[#0f2340]">{CURRENT_USER.name}</p>
            <p className="text-xs text-slate-500">{CURRENT_USER.email}</p>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#cba2d4] to-[#a879be] text-xs font-semibold text-white shadow-sm">
            {initials}
          </div>
        </div>
      </div>
    </header>
  )
}

/** Search tab icon. */
function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="m16 16 5 5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  )
}

/** Appointments tab icon. */
function IconCalendar() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <rect x="3.5" y="5.5" width="17" height="15" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8 3.5v4M16 3.5v4M3.5 9.5h17" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  )
}

/** Favorites tab icon. */
function IconHeart() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
      <path
        d="M12 20.5s-7-4.1-7-10.1c0-2.8 2.2-4.9 5-4.9 1.7 0 3.2.8 4 2.1.8-1.3 2.3-2.1 4-2.1 2.8 0 5 2.1 5 4.9 0 6-7 10.1-7 10.1Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default Navbar
