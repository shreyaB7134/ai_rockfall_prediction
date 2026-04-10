# React + Tailwind CSS Frontend Setup Guide

Complete guide for setting up and running the React frontend for the rockfall prediction system.

---

## 📋 Prerequisites

### Required Software
- **Node.js**: Version 16.0 or higher
- **npm**: Version 7.0 or higher (comes with Node.js)
- **Python**: Version 3.8 or higher (for backend API)
- **Git**: For version control

### Check Installation
```bash
node --version
npm --version
python --version
```

---

## 🚀 Installation Steps

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Node Dependencies
```bash
npm install
```

This will install:
- React 18
- React Router DOM
- Leaflet & React-Leaflet
- Axios
- Lucide React
- Vite
- Tailwind CSS and its dependencies

### Step 3: Verify Installation
```bash
npm list
```

---

## 🔧 Backend Setup

The React frontend requires a Flask API backend to handle predictions.

### Step 1: Install Flask Dependencies
```bash
cd ..
pip install flask flask-cors
```

### Step 2: Start the Flask API Server
```bash
python api_server.py
```

Expected output:
```
✅ Predictor initialized successfully
 * Running on http://0.0.0.0:5000
```

### Step 3: Verify API is Running
Open browser: http://localhost:5000/api/health

Expected response:
```json
{
  "status": "healthy",
  "service": "rockfall-prediction-api"
}
```

---

## 🎨 Running the React Frontend

### Development Mode
```bash
cd frontend
npm run dev
```

This will:
- Start Vite development server
- Open browser at http://localhost:3000
- Enable hot module replacement
- Show compilation errors in browser

### Production Build
```bash
npm run build
```

This will:
- Create optimized production build
- Output to `dist/` directory
- Minify and bundle all assets

### Preview Production Build
```bash
npm run preview
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Navbar.jsx          # Navigation bar
│   ├── pages/
│   │   ├── Homepage.jsx        # Landing page
│   │   └── Dashboard.jsx       # Prediction dashboard
│   ├── App.jsx                 # Main app with routing
│   ├── main.jsx                # Entry point
│   └── index.css               # Tailwind CSS imports
├── public/                     # Static assets
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS configuration
└── vite.config.js              # Vite configuration
```

---

## 🎯 Using the Application

### 1. Start Both Servers

**Terminal 1 - Backend:**
```bash
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Open Application

Navigate to: http://localhost:3000

### 3. Homepage Features
- Hero section with app description
- Feature cards highlighting capabilities
- Statistics display
- Call-to-action buttons
- GitHub link

### 4. Dashboard Features
- Interactive map centered on India
- Click to select location
- "Predict Risk" button
- Real-time prediction results
- Color-coded risk levels
- Feature breakdown display
- Risk assessment messages

---

## 🎨 Tailwind CSS Configuration

### Custom Colors
```javascript
// tailwind.config.js
colors: {
  primary: { /* Blue shades */ },
  danger: { /* Red shades */ },
  success: { /* Green shades */ }
}
```

### Usage in Components
```jsx
<div className="bg-primary-600 text-white">
  <div className="text-danger-500">
  <div className="bg-success-50">
```

---

## 🗺️ Map Configuration

### Default Center
- Latitude: 20.5937 (India center)
- Longitude: 78.9629
- Zoom: 5

### Map Layers
- OpenStreetMap (default)
- Can add more layers in Dashboard.jsx

### Marker Icons
- Uses Leaflet default markers
- Customizable via Leaflet Icon options

---

## 🔌 API Integration

### API Endpoints

#### Health Check
```javascript
GET http://localhost:5000/api/health
```

#### Prediction
```javascript
POST http://localhost:5000/api/predict
Content-Type: application/json

{
  "lat": 20.95,
  "lon": 85.10
}
```

### Response Format
```json
{
  "probability": 0.85,
  "risk_label": "HIGH RISK",
  "features": {
    "elevation": 125.0,
    "slope": 2.2,
    "rainfall": 3.2,
    "temperature": 26.3,
    "ndvi": 0.073
  }
}
```

---

## 🎨 Component Breakdown

### Navbar.jsx
- Navigation links
- Responsive design
- Logo with Mountain icon

### Homepage.jsx
- Hero section
- Feature cards
- Statistics section
- CTA section
- Footer

### Dashboard.jsx
- Interactive Leaflet map
- Location selection
- Prediction button
- Results display
- Feature breakdown
- Risk assessment

---

## 🚀 Deployment

### Option 1: Vercel (Recommended)
1. Push code to GitHub
2. Import project in Vercel
3. Configure build command: `npm run build`
4. Configure output directory: `dist`
5. Deploy

### Option 2: Netlify
1. Push code to GitHub
2. Import project in Netlify
3. Configure build command: `npm run build`
4. Configure publish directory: `dist`
5. Deploy

### Option 3: Traditional Hosting
1. Run `npm run build`
2. Upload `dist/` folder to web server
3. Configure server to serve static files

---

## 🔧 Troubleshooting

### Issue: "Module not found"
**Solution:**
```bash
cd frontend
npm install
```

### Issue: Backend not responding
**Solution:**
1. Ensure Flask server is running on port 5000
2. Check API logs for errors
3. Verify CORS configuration

### Issue: Map not displaying
**Solution:**
1. Check Leaflet CSS import in index.css
2. Verify map container has height
3. Check browser console for errors

### Issue: Build fails
**Solution:**
```bash
rm -rf node_modules
rm package-lock.json
npm install
npm run build
```

### Issue: Port 3000 already in use
**Solution:**
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- --port 3001
```

---

## 📱 Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1023px
- Desktop: ≥ 1024px

### Responsive Classes
```jsx
className="grid-cols-1 md:grid-cols-3"  // 1 col mobile, 3 col desktop
className="text-sm md:text-base"         // Smaller text on mobile
className="p-4 md:p-8"                   // Less padding on mobile
```

---

## 🎯 Best Practices

### Performance
- Use React.memo for expensive components
- Implement code splitting with React.lazy
- Optimize images and assets
- Use production build for deployment

### Code Organization
- Keep components small and focused
- Use custom hooks for reusable logic
- Separate UI from business logic
- Use TypeScript for type safety (optional)

### Styling
- Use Tailwind utility classes
- Avoid inline styles
- Use semantic HTML elements
- Follow mobile-first design

---

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Leaflet Documentation](https://leafletjs.com)
- [Vite Documentation](https://vitejs.dev)
- [React Router Documentation](https://reactrouter.com)

---

## 🆚 React vs Streamlit

| Feature | React + Tailwind | Streamlit |
|---------|-----------------|-----------|
| Customization | Full control | Limited |
| Performance | Optimized | Good |
| Mobile Support | Excellent | Limited |
| Deployment | Flexible | Simple |
| Development | Requires more setup | Very simple |
| UI/UX | Professional | Basic |

---

## ✅ Setup Checklist

- [ ] Node.js 16+ installed
- [ ] npm dependencies installed
- [ ] Flask dependencies installed
- [ ] Backend API running on port 5000
- [ ] Frontend dev server running on port 3000
- [ ] Homepage loads correctly
- [ ] Dashboard loads correctly
- [ ] Map displays properly
- [ ] Prediction API works
- [ ] Results display correctly

---

**Happy coding! 🚀🎨**
