import requests
import json

# Test the API with various coordinates to find HIGH risk
url = "http://localhost:5000/api/predict"

# Test various locations - steep, rainy, low vegetation areas
test_cases = [
    {"name": "Talcher (Mining)", "lat": 20.95, "lon": 85.10},
    {"name": "Korba (Mining)", "lat": 22.35, "lon": 82.68},
    {"name": "Himalayan Region (Steep)", "lat": 28.0, "lon": 88.0},
    {"name": "Western Ghats (Steep + Rainy)", "lat": 19.0, "lon": 73.0},
    {"name": "Northeast India (High Rain)", "lat": 25.5, "lon": 91.0},
    {"name": "Meghalaya (Very High Rain)", "lat": 25.5, "lon": 91.5},
    {"name": "Sikkim (Steep)", "lat": 27.5, "lon": 88.5},
    {"name": "Kerala (High Rain)", "lat": 10.0, "lon": 77.0},
]

high_risk_locations = []

for test in test_cases:
    data = {
        "lat": test["lat"],
        "lon": test["lon"]
    }
    
    print(f"\n{'='*70}")
    print(f"Testing API with {test['name']} coordinates...")
    print(f"Request: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        result = response.json()
        print(f"Risk Level: {result['risk']}")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Probability: {result['probability']:.3f}")
        print(f"\nFeatures:")
        print(f"  Rainfall: {result['features']['rainfall']:.1f} mm/year")
        print(f"  Slope: {result['features']['slope']:.1f}°")
        print(f"  NDVI: {result['features']['ndvi']:.3f}")
        print(f"  Elevation: {result['features']['elevation']:.1f} m")
        print(f"  Temperature: {result['features']['temperature']:.1f} °C")
        
        if result['risk'] == 'HIGH':
            high_risk_locations.append({
                'name': test['name'],
                'lat': test['lat'],
                'lon': test['lon'],
                'risk_score': result['risk_score'],
                'features': result['features']
            })
    except Exception as e:
        print(f"Error: {e}")

print(f"\n{'='*70}")
print("HIGH RISK LOCATIONS FOUND:")
for loc in high_risk_locations:
    print(f"\n{loc['name']}:")
    print(f"  Lat: {loc['lat']}, Lon: {loc['lon']}")
    print(f"  Risk Score: {loc['risk_score']:.3f}")
    print(f"  Rainfall: {loc['features']['rainfall']:.1f} mm/year")
    print(f"  Slope: {loc['features']['slope']:.1f}°")
    print(f"  NDVI: {loc['features']['ndvi']:.3f}")

if not high_risk_locations:
    print("\nNo HIGH risk locations found in test. Try steeper or rainier areas.")
