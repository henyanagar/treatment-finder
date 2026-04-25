import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import FavoritesPage from './pages/FavoritesPage'
import HomePage from './pages/HomePage'
import MyAppointments from './pages/MyAppointments'

function App() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/favorites" element={<FavoritesPage />} />
        <Route path="/appointments" element={<MyAppointments />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  )
}

export default App
