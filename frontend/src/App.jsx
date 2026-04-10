import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Homepage from './pages/Homepage'
import Dashboard from './pages/Dashboard'
import RiskZonesMap from './pages/RiskZonesMap'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/risk-zones" element={<RiskZonesMap />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
