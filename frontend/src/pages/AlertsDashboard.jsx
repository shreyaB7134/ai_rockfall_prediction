import { useState, useEffect, useRef } from 'react'
import { AlertTriangle, Bell, Volume2, VolumeX, Clock, MapPin, Users, Play, Square, Send, Shield, AlertCircle } from 'lucide-react'

const AlertsDashboard = () => {
  const [alerts, setAlerts] = useState([])
  const [activeAlert, setActiveAlert] = useState(null)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [isAlarmPlaying, setIsAlarmPlaying] = useState(false)
  const [broadcastMessage, setBroadcastMessage] = useState('')
  const [isBroadcasting, setIsBroadcasting] = useState(false)
  const audioContextRef = useRef(null)
  const oscillatorRef = useRef(null)
  const gainNodeRef = useRef(null)

  // Simulate incoming alerts
  useEffect(() => {
    const simulateAlert = () => {
      const locations = ['Talcher Sector A', 'Korba Sector B', 'Talcher Sector C', 'Korba Sector D']
      const risks = ['HIGH', 'MEDIUM']
      const risk = risks[Math.floor(Math.random() * risks.length)]
      
      const newAlert = {
        id: Date.now(),
        risk: risk,
        location: locations[Math.floor(Math.random() * locations.length)],
        time: new Date(),
        acknowledged: false
      }

      setAlerts(prev => [newAlert, ...prev])

      if (risk === 'HIGH') {
        setActiveAlert(newAlert)
        if (soundEnabled) {
          playAlarm()
        }
      }
    }

    // Simulate an alert every 30 seconds for demo
    const interval = setInterval(simulateAlert, 30000)
    
    // Add initial alert after 5 seconds
    const initialAlert = setTimeout(simulateAlert, 5000)

    return () => {
      clearInterval(interval)
      clearTimeout(initialAlert)
      stopAlarm()
    }
  }, [soundEnabled])

  // Play alarm sound
  const playAlarm = () => {
    if (!soundEnabled || isAlarmPlaying) return

    try {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      oscillatorRef.current = audioContextRef.current.createOscillator()
      gainNodeRef.current = audioContextRef.current.createGain()

      oscillatorRef.current.connect(gainNodeRef.current)
      gainNodeRef.current.connect(audioContextRef.current.destination)

      oscillatorRef.current.frequency.value = 800
      oscillatorRef.current.type = 'sawtooth'
      gainNodeRef.current.gain.value = 0.2

      oscillatorRef.current.start()
      setIsAlarmPlaying(true)

      // Loop the alarm
      const loopAlarm = () => {
        if (!isAlarmPlaying) return
        oscillatorRef.current.frequency.value = oscillatorRef.current.frequency.value === 800 ? 600 : 800
        setTimeout(loopAlarm, 500)
      }
      loopAlarm()
    } catch (err) {
      console.error('Error playing alarm:', err)
    }
  }

  // Stop alarm sound
  const stopAlarm = () => {
    if (oscillatorRef.current) {
      try {
        oscillatorRef.current.stop()
        oscillatorRef.current = null
      } catch (err) {
        console.error('Error stopping oscillator:', err)
      }
    }
    if (audioContextRef.current) {
      try {
        audioContextRef.current.close()
        audioContextRef.current = null
      } catch (err) {
        console.error('Error closing audio context:', err)
      }
    }
    setIsAlarmPlaying(false)
  }

  // Acknowledge alert
  const acknowledgeAlert = (alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ))
    if (activeAlert && activeAlert.id === alertId) {
      setActiveAlert(null)
      stopAlarm()
    }
  }

  // Send broadcast
  const sendBroadcast = () => {
    setIsBroadcasting(true)
    setBroadcastMessage('Sending alert to all workers...')
    
    setTimeout(() => {
      setBroadcastMessage('✅ Alert sent to all workers successfully!')
      setTimeout(() => {
        setBroadcastMessage('')
        setIsBroadcasting(false)
      }, 3000)
    }, 2000)
  }

  // Test alert
  const testAlert = () => {
    const testAlert = {
      id: Date.now(),
      risk: 'HIGH',
      location: 'Test Location',
      time: new Date(),
      acknowledged: false
    }
    setAlerts(prev => [testAlert, ...prev])
    setActiveAlert(testAlert)
    if (soundEnabled) {
      playAlarm()
    }
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'HIGH': return 'danger'
      case 'MEDIUM': return 'warning'
      default: return 'success'
    }
  }

  const getRiskBgColor = (risk) => {
    switch (risk) {
      case 'HIGH': return 'bg-danger-500'
      case 'MEDIUM': return 'bg-warning-500'
      default: return 'bg-success-500'
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Active Alert Popup Modal */}
      {activeAlert && !activeAlert.acknowledged && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-[9999]">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden border-4 border-danger-500">
            {/* Alert Header */}
            <div className="bg-danger-600 p-6 text-center">
              <div className="flex justify-center mb-4">
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center animate-pulse">
                  <AlertTriangle className="h-12 w-12 text-danger-600" />
                </div>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">🚨 HIGH RISK DETECTED</h2>
              <p className="text-danger-100 text-lg">Immediate action required</p>
            </div>

            {/* Alert Details */}
            <div className="p-6">
              <div className="space-y-4 mb-6">
                <div className="flex items-center p-4 bg-danger-50 rounded-lg border border-danger-200">
                  <MapPin className="h-6 w-6 text-danger-600 mr-4 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-gray-600">Location</p>
                    <p className="text-lg font-bold text-gray-900">{activeAlert.location}</p>
                  </div>
                </div>

                <div className="flex items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <Clock className="h-6 w-6 text-gray-600 mr-4 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-gray-600">Time</p>
                    <p className="text-lg font-bold text-gray-900">
                      {activeAlert.time.toLocaleTimeString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: true
                      })}
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommended Actions */}
              <div className="bg-danger-50 rounded-lg p-4 mb-6 border border-danger-200">
                <h3 className="font-bold text-danger-900 mb-3 flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Recommended Actions
                </h3>
                <ul className="space-y-2 text-danger-800">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Stop all mining operations immediately</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Evacuate workers from affected area</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Alert emergency response team</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Secure equipment and machinery</span>
                  </li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={sendBroadcast}
                  disabled={isBroadcasting}
                  className="w-full bg-danger-600 hover:bg-danger-700 text-white py-3 rounded-lg font-semibold transition-colors flex items-center justify-center disabled:opacity-50"
                >
                  <Send className="h-5 w-5 mr-2" />
                  {isBroadcasting ? 'Sending...' : 'Send Alert to Workers'}
                </button>

                {broadcastMessage && (
                  <div className="text-center py-2 bg-success-50 rounded-lg border border-success-200">
                    <p className="text-success-700 font-medium">{broadcastMessage}</p>
                  </div>
                )}

                <button
                  onClick={() => acknowledgeAlert(activeAlert.id)}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 rounded-lg font-semibold transition-colors"
                >
                  Acknowledge Alert
                </button>
              </div>
            </div>

            {/* Stop Alarm Button */}
            {isAlarmPlaying && (
              <div className="bg-gray-100 p-4 border-t border-gray-200">
                <button
                  onClick={stopAlarm}
                  className="w-full bg-gray-800 hover:bg-gray-900 text-white py-3 rounded-lg font-semibold transition-colors flex items-center justify-center"
                >
                  <Square className="h-5 w-5 mr-2" />
                  Stop Alarm Sound
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <div className="bg-danger-600 p-3 rounded-xl mr-4">
              <Bell className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Live Alerts Dashboard</h1>
              <p className="text-gray-400">Real-time mine safety monitoring system</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Sound Toggle */}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`p-3 rounded-lg transition-colors ${
                soundEnabled 
                  ? 'bg-success-600 text-white hover:bg-success-700' 
                  : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
              title={soundEnabled ? 'Disable sound' : 'Enable sound'}
            >
              {soundEnabled ? <Volume2 className="h-6 w-6" /> : <VolumeX className="h-6 w-6" />}
            </button>

            {/* Test Alert Button */}
            <button
              onClick={testAlert}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg font-semibold transition-colors flex items-center"
            >
              <Play className="h-5 w-5 mr-2" />
              Test Alert
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Alerts</p>
                <p className="text-3xl font-bold text-white">{alerts.length}</p>
              </div>
              <AlertCircle className="h-12 w-12 text-gray-600" />
            </div>
          </div>

          <div className="bg-danger-900 rounded-xl p-6 border border-danger-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-danger-300 text-sm">High Risk</p>
                <p className="text-3xl font-bold text-danger-100">
                  {alerts.filter(a => a.risk === 'HIGH').length}
                </p>
              </div>
              <AlertTriangle className="h-12 w-12 text-danger-500" />
            </div>
          </div>

          <div className="bg-warning-900 rounded-xl p-6 border border-warning-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-warning-300 text-sm">Medium Risk</p>
                <p className="text-3xl font-bold text-warning-100">
                  {alerts.filter(a => a.risk === 'MEDIUM').length}
                </p>
              </div>
              <AlertCircle className="h-12 w-12 text-warning-500" />
            </div>
          </div>

          <div className="bg-success-900 rounded-xl p-6 border border-success-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-success-300 text-sm">Acknowledged</p>
                <p className="text-3xl font-bold text-success-100">
                  {alerts.filter(a => a.acknowledged).length}
                </p>
              </div>
              <Shield className="h-12 w-12 text-success-500" />
            </div>
          </div>
        </div>

        {/* Alert History */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-bold text-white flex items-center">
              <Clock className="h-6 w-6 mr-3 text-gray-400" />
              Alert History
            </h2>
          </div>

          <div className="divide-y divide-gray-700">
            {alerts.length === 0 ? (
              <div className="p-12 text-center">
                <Bell className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No alerts yet. System monitoring...</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-6 hover:bg-gray-750 transition-colors ${
                    alert.acknowledged ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        alert.risk === 'HIGH' ? 'bg-danger-600' : 'bg-warning-600'
                      }`}>
                        <AlertTriangle className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-3 mb-1">
                          <span className={`text-lg font-bold ${
                            alert.risk === 'HIGH' ? 'text-danger-400' : 'text-warning-400'
                          }`}>
                            {alert.risk} RISK
                          </span>
                          {alert.acknowledged && (
                            <span className="px-2 py-1 bg-success-600 text-white text-xs rounded-full">
                              Acknowledged
                            </span>
                          )}
                        </div>
                        <div className="flex items-center text-gray-400 text-sm space-x-4">
                          <span className="flex items-center">
                            <MapPin className="h-4 w-4 mr-1" />
                            {alert.location}
                          </span>
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {alert.time.toLocaleString('en-IN', {
                              day: 'numeric',
                              month: 'short',
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: true
                            })}
                          </span>
                        </div>
                      </div>
                    </div>

                    {!alert.acknowledged && (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        Acknowledge
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AlertsDashboard
