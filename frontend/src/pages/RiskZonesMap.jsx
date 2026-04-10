import { useState, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { ChevronDown, AlertTriangle, CheckCircle, MapPin, Loader2 } from 'lucide-react'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icon in react-leaflet
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom marker icons for different risk levels
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  })
}

// Generate grid points around a center
const generateGridPoints = (centerLat, centerLon, radiusKm, gridSize) => {
  const points = []
  const step = (radiusKm * 2) / gridSize
  
  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      const lat = centerLat + (i - gridSize / 2) * (step / 111)
      const lon = centerLon + (j - gridSize / 2) * (step / (111 * Math.cos(centerLat * Math.PI / 180)))
      points.push({ lat, lon })
    }
  }
  return points
}

// Region configurations
const REGION_CONFIGS = {
  talcher: {
    center: [20.95, 85.10],
    zoom: 11,
    radiusKm: 15,
    gridSize: 4
  },
  korba: {
    center: [22.35, 82.68],
    zoom: 11,
    radiusKm: 15,
    gridSize: 4
  }
}

const RiskZonesMap = () => {
  const [selectedRegion, setSelectedRegion] = useState('talcher')
  const [riskZones, setRiskZones] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const mapRef = useRef(null)

  // Fetch predictions for grid points
  const fetchPredictions = async (region) => {
    setLoading(true)
    setError(null)
    
    try {
      const config = REGION_CONFIGS[region]
      const points = generateGridPoints(
        config.center[0],
        config.center[1],
        config.radiusKm,
        config.gridSize
      )
      
      // Fetch predictions for all points
      const predictions = await Promise.all(
        points.map(async (point, index) => {
          try {
            const response = await axios.post('http://localhost:5000/api/predict', {
              lat: point.lat,
              lon: point.lon
            })
            return {
              id: index + 1,
              lat: point.lat,
              lon: point.lon,
              risk: response.data.risk,
              risk_score: response.data.risk_score,
              probability: response.data.probability,
              features: response.data.features
            }
          } catch (err) {
            console.error(`Failed to fetch prediction for point ${index}:`, err)
            return null
          }
        })
      )
      
      // Filter out failed predictions
      const validPredictions = predictions.filter(p => p !== null)
      setRiskZones(validPredictions)
      
    } catch (err) {
      setError('Failed to fetch predictions. Please ensure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Load predictions when region changes
  useEffect(() => {
    fetchPredictions(selectedRegion)
  }, [selectedRegion])

  const handleRegionChange = (e) => {
    const newRegion = e.target.value
    setSelectedRegion(newRegion)
    
    // Calculate center based on new region
    const regionCenter = newRegion === 'talcher' ? [20.95, 85.10] : [22.35, 82.68]
    const regionZoom = 11
    
    // Auto-zoom map to selected region
    if (mapRef.current) {
      mapRef.current.setView(regionCenter, regionZoom)
    }
  }

  const regionCenter = selectedRegion === 'talcher' ? [20.95, 85.10] : [22.35, 82.68]
  const regionZoom = 11

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'HIGH': return '#dc2626' // red
      case 'MEDIUM': return '#d97706' // yellow
      case 'LOW': return '#16a34a' // green
      default: return '#6b7280'
    }
  }

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'HIGH': return <AlertTriangle className="h-5 w-5 text-danger-600" />
      case 'MEDIUM': return <AlertTriangle className="h-5 w-5 text-warning-600" />
      case 'LOW': return <CheckCircle className="h-5 w-5 text-success-600" />
      default: return <MapPin className="h-5 w-5 text-gray-600" />
    }
  }

  const getRiskBadgeColor = (risk) => {
    switch (risk) {
      case 'HIGH': return 'bg-danger-100 text-danger-700 border-danger-300'
      case 'MEDIUM': return 'bg-warning-100 text-warning-700 border-warning-300'
      case 'LOW': return 'bg-success-100 text-success-700 border-success-300'
      default: return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const riskStats = {
    HIGH: riskZones.filter(z => z.risk === 'HIGH').length,
    MEDIUM: riskZones.filter(z => z.risk === 'MEDIUM').length,
    LOW: riskZones.filter(z => z.risk === 'LOW').length,
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Risk Zones Map</h1>
              <p className="text-sm text-gray-600 mt-1">
                Visualize rockfall risk zones in mining regions
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <select
                  value={selectedRegion}
                  onChange={handleRegionChange}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 text-sm font-medium focus:ring-2 focus:ring-primary-500 focus:border-primary-500 cursor-pointer"
                >
                  <option value="talcher">Talcher Coalfield</option>
                  <option value="korba">Korba Coalfield</option>
                </select>
                <ChevronDown className="h-5 w-5 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel - Stats */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Statistics</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-danger-50 rounded-lg border border-danger-200">
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-danger-600 mr-3"></div>
                    <span className="text-sm font-medium text-gray-700">HIGH Risk</span>
                  </div>
                  <span className="text-lg font-bold text-danger-700">{riskStats.HIGH}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg border border-warning-200">
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-warning-600 mr-3"></div>
                    <span className="text-sm font-medium text-gray-700">MEDIUM Risk</span>
                  </div>
                  <span className="text-lg font-bold text-warning-700">{riskStats.MEDIUM}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-success-50 rounded-lg border border-success-200">
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-success-600 mr-3"></div>
                    <span className="text-sm font-medium text-gray-700">LOW Risk</span>
                  </div>
                  <span className="text-lg font-bold text-success-700">{riskStats.LOW}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Legend</h2>
              <div className="space-y-2 text-sm">
                <div className="flex items-center">
                  <div className="w-4 h-4 rounded-full bg-danger-600 mr-3"></div>
                  <span className="text-gray-700">High Risk (Score &gt; 0.6)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 rounded-full bg-warning-600 mr-3"></div>
                  <span className="text-gray-700">Medium Risk (Score 0.4-0.6)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 rounded-full bg-success-600 mr-3"></div>
                  <span className="text-gray-700">Low Risk (Score &lt; 0.4)</span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 rounded-xl shadow-lg p-6 border border-blue-200">
              <h2 className="text-lg font-semibold text-blue-900 mb-3">Real-Time AI Predictions</h2>
              <p className="text-sm text-blue-800">
                This map displays real-time risk predictions from our AI model. Each marker represents a location where the system analyzed slope, rainfall, and vegetation data from Google Earth Engine to predict rockfall risk.
              </p>
            </div>
          </div>

          {/* Right Panel - Map */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="h-[600px] relative">
                {loading && (
                  <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-[1000]">
                    <div className="text-center">
                      <Loader2 className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
                      <p className="text-gray-700 font-medium">Fetching real-time predictions...</p>
                      <p className="text-sm text-gray-500 mt-1">Analyzing {REGION_CONFIGS[selectedRegion].gridSize * REGION_CONFIGS[selectedRegion].gridSize} locations</p>
                    </div>
                  </div>
                )}
                {error && (
                  <div className="absolute inset-0 bg-white bg-opacity-95 flex items-center justify-center z-[1000]">
                    <div className="text-center p-6">
                      <AlertTriangle className="h-12 w-12 text-danger-600 mx-auto mb-4" />
                      <p className="text-danger-700 font-medium mb-2">{error}</p>
                      <button
                        onClick={() => fetchPredictions(selectedRegion)}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                      >
                        Retry
                      </button>
                    </div>
                  </div>
                )}
                <MapContainer
                  ref={mapRef}
                  center={regionCenter}
                  zoom={regionZoom}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                  />
                  {riskZones.map((zone) => (
                    <Marker
                      key={zone.id}
                      position={[zone.lat, zone.lon]}
                      icon={createCustomIcon(getRiskColor(zone.risk))}
                    >
                      <Popup>
                        <div className="min-w-[200px]">
                          <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border mb-3 ${getRiskBadgeColor(zone.risk)}`}>
                            {getRiskIcon(zone.risk)}
                            <span className="ml-1">{zone.risk} RISK</span>
                          </div>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Risk Score:</span>
                              <span className="font-medium">{zone.risk_score.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Probability:</span>
                              <span className="font-medium">{(zone.probability * 100).toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Slope:</span>
                              <span className="font-medium">{zone.features.slope.toFixed(1)}°</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Rainfall:</span>
                              <span className="font-medium">{zone.features.rainfall.toFixed(1)} mm/yr</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">NDVI:</span>
                              <span className="font-medium">{zone.features.ndvi.toFixed(3)}</span>
                            </div>
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskZonesMap
