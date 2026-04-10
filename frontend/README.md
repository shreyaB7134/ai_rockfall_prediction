# Rockfall Prediction - React Frontend

Modern React + Tailwind CSS frontend for the rockfall prediction system.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- Python backend running on port 5000

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open browser:
```
http://localhost:3000
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Navbar.jsx
│   ├── pages/
│   │   ├── Homepage.jsx
│   │   └── Dashboard.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

## 🎨 Features

### Homepage
- Beautiful hero section
- Feature cards highlighting key capabilities
- Statistics section
- Call-to-action buttons
- Responsive design

### Dashboard
- Interactive Leaflet map centered on India
- Click-to-select location
- Real-time prediction via API
- Color-coded risk levels
- Feature breakdown display
- Risk assessment messages

## 🔧 Backend Setup

The React frontend requires a Flask API backend running on port 5000.

### Start Backend:
```bash
# From project root
python api_server.py
```

### API Endpoints:
- `GET /api/health` - Health check
- `POST /api/predict` - Prediction endpoint
  - Body: `{ "lat": 20.95, "lon": 85.10 }`
  - Response: Prediction results

## 🎯 Usage

1. Start the Flask API backend
2. Start the React development server
3. Navigate to Homepage
4. Click "Go to Dashboard"
5. Click on map to select location
6. Click "Predict Risk" button
7. View prediction results

## 📦 Dependencies

- React 18
- React Router
- Leaflet + React-Leaflet
- Axios
- Lucide React (icons)
- Tailwind CSS
- Vite

## 🎨 Styling

Built with Tailwind CSS for:
- Responsive design
- Modern UI components
- Consistent color scheme
- Professional appearance

## 🚀 Deployment

### Build for Production:
```bash
npm run build
```

### Preview Production Build:
```bash
npm run preview
```

## 🔧 Configuration

Vite configuration in `vite.config.js`:
- Development server on port 3000
- API proxy to backend on port 5000

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1920px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🎯 Key Features

✅ Modern React architecture  
✅ Tailwind CSS styling  
✅ Interactive Leaflet maps  
✅ Real-time API integration  
✅ Beautiful UI/UX  
✅ Responsive design  
✅ Fast development with Vite  
✅ Component-based structure  

## 🐛 Troubleshooting

### Backend not responding
- Ensure Flask server is running on port 5000
- Check CORS configuration
- Verify API endpoint URLs

### Map not displaying
- Check Leaflet CSS import
- Verify map container height
- Check browser console for errors

### Build errors
- Clear node_modules and reinstall
- Check Node.js version (16+)
- Verify all dependencies installed

## 📞 Support

For issues:
1. Check main README.md
2. Review COMPLETE_DOCUMENTATION.md
3. Check backend API logs
