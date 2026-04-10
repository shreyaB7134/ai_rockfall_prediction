import { useState, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import { Mountain, MapPin, Activity, Droplets, Thermometer, Leaf, AlertTriangle, CheckCircle, Map, X, ChevronDown } from 'lucide-react'
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

const MapClickHandler = ({ onLocationSelect, enabled }) => {
  useMapEvents({
    click: (e) => {
      if (enabled) {
        onLocationSelect(e.latlng)
      }
    }
  })
  return null
}

// Mining region data with coordinates
const MINING_REGIONS = {
  talcher: {
    name: 'Talcher Coalfield',
    lat: 20.95,
    lon: 85.10,
    zoom: 12
  },
  korba: {
    name: 'Korba Coalfield',
    lat: 22.35,
    lon: 82.68,
    zoom: 12
  }
}

const Dashboard = () => {
  const [inputMode, setInputMode] = useState('map') // 'map', 'manual', or 'region'
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [manualLat, setManualLat] = useState('')
  const [manualLon, setManualLon] = useState('')
  const [selectedRegion, setSelectedRegion] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const mapRef = useRef(null)

  const handleLocationSelect = (latlng) => {
    setSelectedLocation(latlng)
    setManualLat(latlng.lat.toFixed(6))
    setManualLon(latlng.lng.toFixed(6))
    setPrediction(null)
    setError(null)
  }

  const handleManualInput = () => {
    const lat = parseFloat(manualLat)
    const lon = parseFloat(manualLon)
    
    if (isNaN(lat) || isNaN(lon)) {
      setError('Please enter valid latitude and longitude')
      return
    }
    
    if (lat < -90 || lat > 90) {
      setError('Latitude must be between -90 and 90')
      return
    }
    
    if (lon < -180 || lon > 180) {
      setError('Longitude must be between -180 and 180')
      return
    }
    
    setSelectedLocation({ lat, lng: lon })
    setPrediction(null)
    setError(null)
  }

  const handleRegionSelect = async (regionKey) => {
    setSelectedRegion(regionKey)
    const region = MINING_REGIONS[regionKey]
    
    if (region) {
      setSelectedLocation({ lat: region.lat, lng: region.lon })
      setManualLat(region.lat.toFixed(6))
      setManualLon(region.lon.toFixed(6))
      setPrediction(null)
      setError(null)
      
      // Auto-zoom map to region
      if (mapRef.current) {
        mapRef.current.setView([region.lat, region.lon], region.zoom)
      }
      
      // Auto-predict
      setLoading(true)
      try {
        const response = await axios.post('http://localhost:5000/api/predict', {
          lat: region.lat,
          lon: region.lon
        })
        setPrediction(response.data)
      } catch (err) {
        setError('Failed to make prediction. Please ensure the backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handlePredict = async () => {
    if (!selectedLocation) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('http://localhost:5000/api/predict', {
        lat: selectedLocation.lat,
        lon: selectedLocation.lng
      })

      setPrediction(response.data)
    } catch (err) {
      setError('Failed to make prediction. Please ensure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getFeatureLevel = (value, type) => {
    if (type === 'slope') {
      if (value > 30) return { level: 'High', color: 'danger' }
      if (value > 15) return { level: 'Medium', color: 'warning' }
      return { level: 'Low', color: 'success' }
    }
    if (type === 'rainfall') {
      if (value > 2000) return { level: 'High', color: 'danger' }
      if (value > 1000) return { level: 'Medium', color: 'warning' }
      return { level: 'Low', color: 'success' }
    }
    if (type === 'ndvi') {
      if (value > 0.6) return { level: 'High', color: 'success' }
      if (value > 0.3) return { level: 'Medium', color: 'warning' }
      return { level: 'Low', color: 'danger' }
    }
    return { level: 'Medium', color: 'warning' }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-full mx-auto">
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Mountain className="h-7 w-7 mr-3 text-primary-600" />
              Rockfall Prediction Dashboard
            </h1>
          </div>
        </div>

        <div className="flex h-[calc(100vh-73px)]">
          {/* Left Sidebar - Input System */}
          <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
            <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
              <MapPin className="h-5 w-5 mr-2 text-primary-600" />
              Location Input
            </h2>

            {/* Toggle Input Mode */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Input Method
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    value="map"
                    checked={inputMode === 'map'}
                    onChange={(e) => setInputMode(e.target.value)}
                    className="h-4 w-4 text-primary-600"
                  />
                  <span className="ml-3 text-sm text-gray-700">Click on Map</span>
                </label>
                <label className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    value="manual"
                    checked={inputMode === 'manual'}
                    onChange={(e) => setInputMode(e.target.value)}
                    className="h-4 w-4 text-primary-600"
                  />
                  <span className="ml-3 text-sm text-gray-700">Enter Coordinates</span>
                </label>
                <label className="flex items-center p-3 border border-primary-200 bg-primary-50 rounded-lg cursor-pointer hover:bg-primary-100 transition-colors">
                  <input
                    type="radio"
                    value="region"
                    checked={inputMode === 'region'}
                    onChange={(e) => setInputMode(e.target.value)}
                    className="h-4 w-4 text-primary-600"
                  />
                  <span className="ml-3 text-sm text-gray-700 font-medium">Select Mining Region</span>
                </label>
              </div>
            </div>

            {/* Region Selection Dropdown */}
            {inputMode === 'region' && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Region
                </label>
                <div className="relative">
                  <select
                    value={selectedRegion}
                    onChange={(e) => handleRegionSelect(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 appearance-none bg-white cursor-pointer"
                  >
                    <option value="">Choose a mining region...</option>
                    {Object.entries(MINING_REGIONS).map(([key, region]) => (
                      <option key={key} value={key}>
                        {region.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="h-5 w-5 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Select a region to auto-zoom map and predict risk
                </p>
              </div>
            )}

            {/* Manual Input Fields */}
            {inputMode === 'manual' && (
              <div className="mb-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={manualLat}
                    onChange={(e) => setManualLat(e.target.value)}
                    placeholder="e.g., 20.95"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={manualLon}
                    onChange={(e) => setManualLon(e.target.value)}
                    placeholder="e.g., 85.10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <button
                  onClick={handleManualInput}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-900 py-2 rounded-lg font-medium transition-colors"
                >
                  Set Location
                </button>
              </div>
            )}

            {/* Selected Location Info */}
            {selectedLocation && (
              <div className="bg-gray-50 rounded-xl p-4 mb-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Selected Location</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Latitude:</span>
                    <span className="font-medium">{selectedLocation.lat.toFixed(6)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Longitude:</span>
                    <span className="font-medium">{selectedLocation.lng.toFixed(6)}</span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectedLocation(null)
                    setManualLat('')
                    setManualLon('')
                    setPrediction(null)
                    setError(null)
                  }}
                  className="mt-3 text-sm text-gray-500 hover:text-gray-700 flex items-center"
                >
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </button>
              </div>
            )}

            {/* Predict Button */}
            <button
              onClick={handlePredict}
              disabled={!selectedLocation || loading}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Predicting...</span>
                </>
              ) : (
                <>
                  <Mountain className="h-5 w-5" />
                  <span>Predict Risk</span>
                </>
              )}
            </button>

            {error && (
              <div className="mt-4 bg-danger-50 border border-danger-200 rounded-lg p-3">
                <p className="text-danger-700 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Center - Map */}
          <div className="flex-1 p-6">
            <div className="bg-white rounded-xl shadow-lg h-full overflow-hidden">
              <div className="h-full">
                <MapContainer
                  ref={mapRef}
                  center={[20.5937, 78.9629]}
                  zoom={5}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                  />
                  <MapClickHandler 
                    onLocationSelect={handleLocationSelect}
                    enabled={inputMode === 'map'}
                  />
                  {selectedLocation && (
                    <Marker position={[selectedLocation.lat, selectedLocation.lng]}>
                      <Popup>
                        <div className="text-sm">
                          <p><strong>Latitude:</strong> {selectedLocation.lat.toFixed(6)}</p>
                          <p><strong>Longitude:</strong> {selectedLocation.lng.toFixed(6)}</p>
                        </div>
                      </Popup>
                    </Marker>
                  )}
                </MapContainer>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="w-96 bg-white border-l border-gray-200 p-6 overflow-y-auto">
            <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
              <Activity className="h-5 w-5 mr-2 text-primary-600" />
              Prediction Results
            </h2>

            {!prediction && !loading && (
              <div className="text-center py-12">
                <Map className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">
                  {selectedLocation 
                    ? 'Click "Predict Risk" to see results'
                    : 'Select a location to begin'
                  }
                </p>
              </div>
            )}

            {prediction && (
              <div className="space-y-6">
                {/* Risk Level Badge */}
                <div className={`p-4 rounded-xl border-2 ${
                  prediction.risk === 'HIGH' 
                    ? 'bg-danger-50 border-danger-300' 
                    : prediction.risk === 'MEDIUM'
                    ? 'bg-warning-50 border-warning-300'
                    : 'bg-success-50 border-success-300'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {prediction.risk === 'HIGH' ? (
                        <AlertTriangle className="h-8 w-8 text-danger-600 mr-3" />
                      ) : prediction.risk === 'MEDIUM' ? (
                        <AlertTriangle className="h-8 w-8 text-warning-600 mr-3" />
                      ) : (
                        <CheckCircle className="h-8 w-8 text-success-600 mr-3" />
                      )}
                      <span className={`text-2xl font-bold ${
                        prediction.risk === 'HIGH' 
                          ? 'text-danger-700' 
                          : prediction.risk === 'MEDIUM'
                          ? 'text-warning-700'
                          : 'text-success-700'
                      }`}>
                        {prediction.risk} RISK
                      </span>
                    </div>
                  </div>
                </div>

                {/* Probability */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">Risk Probability</span>
                    <span className="text-lg font-bold text-gray-900">
                      {(prediction.probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        prediction.risk === 'HIGH' ? 'bg-danger-500' : 
                        prediction.risk === 'MEDIUM' ? 'bg-warning-500' : 'bg-success-500'
                      }`}
                      style={{ width: `${prediction.probability * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Feature Explanations */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-gray-900">Feature Analysis</h3>
                  
                  <FeatureExplanation
                    icon={<Activity className="h-5 w-5" />}
                    label="Slope"
                    value={prediction.features.slope.toFixed(1)}
                    unit="°"
                    level={getFeatureLevel(prediction.features.slope, 'slope')}
                  />
                  <FeatureExplanation
                    icon={<Droplets className="h-5 w-5" />}
                    label="Rainfall"
                    value={prediction.features.rainfall.toFixed(1)}
                    unit="mm/yr"
                    level={getFeatureLevel(prediction.features.rainfall, 'rainfall')}
                  />
                  <FeatureExplanation
                    icon={<Leaf className="h-5 w-5" />}
                    label="NDVI"
                    value={prediction.features.ndvi.toFixed(3)}
                    unit=""
                    level={getFeatureLevel(prediction.features.ndvi, 'ndvi')}
                  />
                </div>

                {/* Additional Features */}
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <h3 className="text-sm font-semibold text-gray-900">Additional Data</h3>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Elevation:</span>
                    <span className="font-medium">{prediction.features.elevation.toFixed(1)} m</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Temperature:</span>
                    <span className="font-medium">{prediction.features.temperature.toFixed(1)} °C</span>
                  </div>
                </div>

                {/* Alert System for High Risk */}
                {prediction.risk === 'HIGH' && (
                  <div className="bg-danger-50 border-2 border-danger-300 rounded-xl p-5">
                    <div className="flex items-start">
                      <AlertTriangle className="h-6 w-6 text-danger-600 mr-3 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-bold text-danger-900 mb-2">⚠️ High Rockfall Risk</h4>
                        <p className="text-sm text-danger-800 mb-3">Immediate attention required</p>
                        <div className="text-sm text-danger-700 space-y-1">
                          <p>• Avoid heavy machinery in the area</p>
                          <p>• Monitor slope stability closely</p>
                          <p>• Alert personnel and evacuate if necessary</p>
                          <p>• Implement additional safety measures</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const FeatureExplanation = ({ icon, label, value, unit, level }) => {
  const colorClasses = {
    danger: 'bg-danger-100 text-danger-800 border-danger-300',
    warning: 'bg-warning-100 text-warning-800 border-warning-300',
    success: 'bg-success-100 text-success-800 border-success-300'
  }

  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          {icon}
          <span className="ml-2 text-sm font-medium text-gray-700">{label}</span>
        </div>
        <span className="font-bold text-gray-900">{value}{unit}</span>
      </div>
      <div className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${colorClasses[level.color]}`}>
        {level.level}
      </div>
    </div>
  )
}

export default Dashboard
