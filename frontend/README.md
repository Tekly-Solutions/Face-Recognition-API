# Face Recognition API - React Frontend

A modern React frontend for the Face Recognition API with training, verification, and employee management.

## Features

- 🏥 **Health Check** - Monitor API and system status
- 📸 **Train Faces** - Train new faces with multiple photos
- ✅ **Verify Faces** - Verify and identify faces in images
- 👔 **Save Employee Photos** - Save employee photos for records
- 📊 **Database Management** - View and manage trained faces
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Prerequisites

- Node.js 14+
- npm or yarn
- Face Recognition API running (http://localhost:8000)

## Installation

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file (or update existing):

```
REACT_APP_API_URL=http://localhost:8000
```

## Running the Frontend

### Development Mode

```bash
npm start
```

The app will open at `http://localhost:3000`

### Production Build

```bash
npm run build
```

Output will be in the `build/` directory.

## API Configuration

Update `REACT_APP_API_URL` in `.env` to point to your API server:

- **Local Development**: `http://localhost:8000`
- **Docker**: `http://face-recognition-api:8000`
- **Cloud Deployment**: `https://your-domain.com`

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # React components
│   │   ├── Health.js
│   │   ├── Train.js
│   │   ├── Verify.js
│   │   ├── SaveEmployeePhotos.js
│   │   └── Database.js
│   ├── App.js           # Main app component
│   ├── App.css          # Styling
│   └── index.js         # React entry point
├── .env                 # Environment variables
└── package.json         # Dependencies
```

## Components

### Health

- Checks API and system status
- Displays initialized state and database count

### Train

- Upload multiple images for a person
- Train new faces with validation
- Image preview gallery

### Verify

- Upload a test image
- Get verification results with confidence scores
- Show person name if verified

### Save Employee Photos

- Save employee photos with metadata (ID, Name)
- Organize by employee folder
- No training required

### Database

- View all trained persons
- See image count per person
- Rebuild model from dataset
- Display threshold settings

## Features

### Image Upload

- Single or multiple file uploads
- Image preview gallery
- Remove unwanted images
- Base64 encoding for API transmission

### Error Handling

- User-friendly error messages
- Validation on all inputs
- Network error recovery

### Responsive Design

- Mobile-friendly layout
- Flexible grid system
- Touch-friendly buttons

## Styling

The frontend uses:

- CSS3 with flexbox and grid
- Gradient backgrounds
- Smooth transitions and animations
- Consistent color scheme (purple theme)

## Troubleshooting

### API Connection Errors

1. Ensure API is running:

```bash
curl http://localhost:8000/health
```

2. Check `.env` file has correct `REACT_APP_API_URL`

3. Restart the frontend:

```bash
npm start
```

### CORS Issues

The API should have CORS enabled. If you see CORS errors:

- Update API to include CORS headers
- Ensure FastAPI has CORSMiddleware configured

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

## Deployment

### Docker

Build Docker image from repo root:

```bash
docker build -f Dockerfile.frontend -t face-recognition-frontend:latest frontend/
```

Run:

```bash
docker run -p 3000:3000 face-recognition-frontend:latest
```

### Netlify / Vercel

1. Push code to GitHub
2. Connect repo to Netlify/Vercel
3. Set build command: `npm run build`
4. Set publish directory: `build/`
5. Add environment variable: `REACT_APP_API_URL=https://your-api-url.com`

## License

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.

## Support

For issues or questions, contact Tekly IT Solutions.
