import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Homepage from './pages/Homepage'
import Dashboard from './pages/Dashboard'
import RiskZonesMap from './pages/RiskZonesMap'
import Login from './pages/Login'
import AlertsDashboard from './pages/AlertsDashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#020617] to-[#020617]">
        <Navbar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/risk-zones" element={<RiskZonesMap />} />
          <Route path="/alerts" element={<AlertsDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
