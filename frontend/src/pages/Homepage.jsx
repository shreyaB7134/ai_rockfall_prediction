import { Link } from 'react-router-dom'
import { Mountain, ArrowRight, Database, Map, TrendingUp, AlertTriangle, Shield, Zap, Users, DollarSign } from 'lucide-react'

const Homepage = () => {
  return (
    <div className="bg-gradient-to-br from-primary-50 via-white to-gray-50 min-h-screen">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <div className="bg-primary-100 p-4 rounded-full">
              <Mountain className="h-16 w-16 text-primary-600" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            AI-Based Rockfall Prediction System
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-4xl mx-auto leading-relaxed">
            Advanced AI-powered geospatial analysis for predicting rockfall risks in open-pit mines 
            using real-time satellite data.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/dashboard"
              className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-semibold transition-all hover:shadow-lg flex items-center justify-center space-x-2"
            >
              <span>Go to Dashboard</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="https://github.com/shreyaB7134/ai_rockfall_prediction"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white hover:bg-gray-100 text-gray-900 px-8 py-4 rounded-xl font-semibold border-2 border-gray-300 transition-all hover:shadow-lg flex items-center justify-center"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Key Features</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">Comprehensive AI-driven solution for mining safety and risk management</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Database className="h-8 w-8 text-primary-600" />}
            title="Multi-Source Data Processing"
            description="Integrates data from satellite imagery, terrain models, climate sensors, and historical records for comprehensive analysis."
          />
          <FeatureCard
            icon={<Map className="h-8 w-8 text-primary-600" />}
            title="Real-Time Risk Maps"
            description="Interactive geospatial visualization of rockfall risk zones with live updates and historical trend analysis."
          />
          <FeatureCard
            icon={<TrendingUp className="h-8 w-8 text-primary-600" />}
            title="Probability-Based Forecasts"
            description="Advanced statistical models provide probability scores for risk prediction with confidence intervals."
          />
          <FeatureCard
            icon={<AlertTriangle className="h-8 w-8 text-primary-600" />}
            title="Automated Alert Mechanisms"
            description="Real-time warning system with customizable thresholds for immediate risk notification."
          />
          <FeatureCard
            icon={<Shield className="h-8 w-8 text-primary-600" />}
            title="Dashboard for Mine Planners"
            description="Professional interface designed for mine planners and safety officers with actionable insights."
          />
          <FeatureCard
            icon={<Zap className="h-8 w-8 text-primary-600" />}
            title="Open-Source & Scalable"
            description="Fully open-source solution that scales from single mines to multi-site operations."
          />
        </div>
      </div>

      {/* Impact Section */}
      <div className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Impact & Benefits</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">Transforming mining safety through AI innovation</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <ImpactCard
              icon={<Shield className="h-12 w-12 text-success-600" />}
              title="Safety"
              description="Proactive risk detection prevents accidents and protects workers in hazardous mining environments."
              color="success"
            />
            <ImpactCard
              icon={<Zap className="h-12 w-12 text-primary-600" />}
              title="Scalable"
              description="Cloud-based architecture supports expansion across multiple mining sites and regions."
              color="primary"
            />
            <ImpactCard
              icon={<DollarSign className="h-12 w-12 text-warning-600" />}
              title="Cost-Effective"
              description="Reduces operational costs through optimized planning and prevention of costly incidents."
              color="warning"
            />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl shadow-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Mining Safety?
          </h2>
          <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
            Join the future of mining safety with AI-powered rockfall prediction. Start making data-driven decisions today.
          </p>
          <Link
            to="/dashboard"
            className="bg-white hover:bg-gray-100 text-primary-700 px-8 py-4 rounded-xl font-semibold transition-all hover:shadow-lg inline-flex items-center space-x-2"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center mb-4">
                <Mountain className="h-8 w-8 text-primary-400" />
                <span className="ml-2 text-lg font-bold">Rockfall Prediction</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered geospatial analysis for mining safety and disaster management.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link to="/" className="hover:text-white transition-colors">Home</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link to="/map" className="hover:text-white transition-colors">Map</Link></li>
                <li><a href="https://github.com/shreyaB7134/ai_rockfall_prediction" className="hover:text-white transition-colors">GitHub</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Partners</h4>
              <p className="text-gray-400 text-sm">
                Ministry of Mines<br />
                NIRM<br />
                Disaster Management
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              © 2025 Ministry of Mines | NIRM | Disaster Management Theme
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

const FeatureCard = ({ icon, title, description }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
      <div className="flex justify-center mb-6">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-3 text-center">{title}</h3>
      <p className="text-gray-600 text-center leading-relaxed">{description}</p>
    </div>
  )
}

const ImpactCard = ({ icon, title, description, color }) => {
  const colorClasses = {
    success: 'bg-success-50 border-success-200',
    primary: 'bg-primary-50 border-primary-200',
    warning: 'bg-warning-50 border-warning-200'
  }

  return (
    <div className={`${colorClasses[color]} rounded-xl border-2 p-8 hover:shadow-xl transition-all duration-300`}>
      <div className="flex justify-center mb-6">{icon}</div>
      <h3 className="text-2xl font-bold text-gray-900 mb-3 text-center">{title}</h3>
      <p className="text-gray-700 text-center leading-relaxed">{description}</p>
    </div>
  )
}

export default Homepage
