import { Link } from 'react-router-dom'
import { Mountain, Bell } from 'lucide-react'

const Navbar = () => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('userEmail')
    window.location.href = '/'
  }

  return (
    <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="bg-gradient-to-br from-cyan-500/20 to-blue-600/20 p-2 rounded-lg mr-3 border border-cyan-500/30">
              <Mountain className="h-6 w-6 text-cyan-400" />
            </div>
            <span className="ml-2 text-xl font-bold text-white bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Rockfall Prediction
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Link
              to="/"
              className="text-gray-400 hover:text-cyan-400 hover:bg-white/5 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Home
            </Link>
            <Link
              to="/dashboard"
              className="text-gray-400 hover:text-cyan-400 hover:bg-white/5 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/risk-zones"
              className="text-gray-400 hover:text-cyan-400 hover:bg-white/5 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Risk Zones Map
            </Link>
            <Link
              to="/alerts"
              className="text-red-400 hover:text-red-300 hover:bg-red-500/10 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center"
            >
              <Bell className="h-4 w-4 mr-2" />
              Alerts
            </Link>
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="text-gray-400 hover:text-cyan-400 hover:bg-white/5 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            ) : (
              <Link
                to="/login"
                className="ml-auto bg-gradient-to-r from-cyan-500 to-blue-600 hover:scale-105 text-white px-4 py-2 rounded-md text-sm font-medium transition-all shadow-lg shadow-cyan-500/30"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
