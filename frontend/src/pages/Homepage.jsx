import { Link } from 'react-router-dom'
import { Mountain, ArrowRight, Database, Map, TrendingUp, AlertTriangle, Shield, Zap, Users, DollarSign } from 'lucide-react'

const Homepage = () => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image - extends to entire page */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat bg-fixed"
        style={{
          backgroundImage: "url('/assets/rockfall.png')",
        }}
      >
        {/* Lighter Dark Overlay to make image more visible */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0f172a]/40 via-[#020617]/50 to-[#020617]/60"></div>
      </div>

      {/* Hero Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 pb-40">
        <div className="text-center">
          <div className="mb-8"></div>
          <div className="mb-24"></div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            AI-Based Rockfall Prediction System
          </h1>
          <p className="text-xl text-gray-400 mb-10 max-w-4xl mx-auto leading-relaxed">
            Advanced AI-powered geospatial analysis for predicting rockfall risks in open-pit mines
            using real-time satellite data.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to={isAuthenticated ? "/dashboard" : "/login"}
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:scale-105 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg shadow-cyan-500/30 flex items-center justify-center space-x-2"
            >
              <span>{isAuthenticated ? "Go to Dashboard" : "Get Started"}</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="https://github.com/shreyaB7134/ai_rockfall_prediction"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/5 backdrop-blur-xl border border-white/10 hover:bg-white/10 text-white px-8 py-4 rounded-xl font-semibold transition-all hover:shadow-lg hover:shadow-cyan-500/20 flex items-center justify-center"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Key Features</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">Comprehensive AI-driven solution for mining safety and risk management</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Database className="h-8 w-8 text-cyan-400" />}
            title="Real-Time Data"
            description="Live satellite data from Google Earth Engine for accurate predictions"
          />
          <FeatureCard
            icon={<Map className="h-8 w-8 text-cyan-400" />}
            title="Interactive Maps"
            description="Visualize risk zones with interactive Leaflet maps"
          />
          <FeatureCard
            icon={<TrendingUp className="h-8 w-8 text-cyan-400" />}
            title="AI Predictions"
            description="Advanced ML models for accurate risk assessment"
          />
          <FeatureCard
            icon={<AlertTriangle className="h-8 w-8 text-cyan-400" />}
            title="Risk Alerts"
            description="Real-time alerts for high-risk areas with sound notifications"
          />
          <FeatureCard
            icon={<Shield className="h-8 w-8 text-cyan-400" />}
            title="Safety First"
            description="Prioritize worker safety with actionable insights"
          />
          <FeatureCard
            icon={<Zap className="h-8 w-8 text-cyan-400" />}
            title="Fast Response"
            description="Quick predictions for immediate decision making"
          />
        </div>
      </div>

      {/* Impact Section */}
      <div className="relative z-10 bg-white/5 backdrop-blur-xl border border-white/10 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Impact & Benefits</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Transforming mining safety through AI innovation</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <ImpactCard
              icon={<Shield className="h-12 w-12 text-green-400" />}
              title="Safety"
              description="Proactive risk detection prevents accidents and protects workers in hazardous mining environments."
              color="success"
            />
            <ImpactCard
              icon={<Zap className="h-12 w-12 text-cyan-400" />}
              title="Scalable"
              description="Cloud-based architecture supports expansion across multiple mining sites and regions."
              color="primary"
            />
            <ImpactCard
              icon={<DollarSign className="h-12 w-12 text-yellow-400" />}
              title="Cost-Effective"
              description="Reduces operational costs through optimized planning and prevention of costly incidents."
              color="warning"
            />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-cyan-500/20 to-blue-600/20 backdrop-blur-xl border border-cyan-500/30 rounded-2xl shadow-[0_0_40px_rgba(6,182,212,0.3)] p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Mining Safety?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Join the future of mining safety with AI-powered rockfall prediction. Start making data-driven decisions today.
          </p>
          <Link
            to={isAuthenticated ? "/dashboard" : "/login"}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:scale-105 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg shadow-cyan-500/30 inline-flex items-center space-x-2"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 bg-[#020617]/90 backdrop-blur-xl text-white py-12 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center mb-4">
                <Mountain className="h-8 w-8 text-cyan-400" />
                <span className="ml-2 text-lg font-bold">Rockfall Prediction</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered geospatial analysis for mining safety and disaster management.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link to="/" className="hover:text-cyan-400 transition-colors">Home</Link></li>
                <li><Link to="/dashboard" className="hover:text-cyan-400 transition-colors">Dashboard</Link></li>
                <li><Link to="/risk-zones" className="hover:text-cyan-400 transition-colors">Risk Zones Map</Link></li>
                <li><Link to="/alerts" className="hover:text-cyan-400 transition-colors">Alerts</Link></li>
                <li><a href="https://github.com/shreyaB7134/ai_rockfall_prediction" className="hover:text-cyan-400 transition-colors">GitHub</a></li>
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
          <div className="border-t border-white/10 pt-8 text-center">
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
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:shadow-[0_0_30px_rgba(6,182,212,0.2)] transition-all duration-300 transform hover:-translate-y-1 hover:border-cyan-500/30">
      <div className="flex justify-center mb-6">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-3 text-center">{title}</h3>
      <p className="text-gray-400 text-center leading-relaxed">{description}</p>
    </div>
  )
}

const ImpactCard = ({ icon, title, description, color }) => {
  const colorClasses = {
    success: 'bg-green-500/10 border-green-500/30 shadow-[0_0_20px_rgba(34,197,94,0.2)]',
    primary: 'bg-cyan-500/10 border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.2)]',
    warning: 'bg-yellow-500/10 border-yellow-500/30 shadow-[0_0_20px_rgba(234,179,8,0.2)]'
  }

  return (
    <div className={`${colorClasses[color]} backdrop-blur-xl rounded-2xl border-2 p-8 hover:shadow-[0_0_30px_rgba(6,182,212,0.3)] transition-all duration-300`}>
      <div className="flex justify-center mb-6">{icon}</div>
      <h3 className="text-2xl font-bold text-white mb-3 text-center">{title}</h3>
      <p className="text-gray-400 text-center leading-relaxed">{description}</p>
    </div>
  )
}

export default Homepage
