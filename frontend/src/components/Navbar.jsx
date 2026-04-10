import { Link } from 'react-router-dom'
import { Mountain } from 'lucide-react'

const Navbar = () => {
  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Mountain className="h-8 w-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">
              Rockfall Prediction
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Link
              to="/"
              className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Home
            </Link>
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
