# EasyBets API Server

This is the API server for EasyBets Android app. It provides odds data scraped from SportPesa and match predictions using machine learning.

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/odds` - Get all matches odds
- `GET /api/odds/<match_id>` - Get odds for a specific match
- `GET /api/predictions` - Get ML predictions for upcoming matches

## Local Development

### Requirements
- Python 3.9+
- Chrome browser (required for Selenium scraping)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
# On Windows
run.bat

# On macOS/Linux
flask run
```

The server will be available at http://127.0.0.1:5000

## Deploying to Firebase Cloud Functions

### Prerequisites

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Initialize Firebase project (if not already done):
```bash
firebase init functions
```
   - Select your Firebase project
   - Choose Python as the language
   - Say NO to ESLint
   - Say YES to installing dependencies

### Deployment

1. Install production dependencies:
```bash
cd server
pip install -r requirements-firebase.txt -t lib/
```

2. Deploy to Firebase:
```bash
firebase deploy --only functions
```

3. After deployment, you'll get a URL like:
```
https://<region>-<project-id>.cloudfunctions.net/easybets_api
```

## Alternative Deployment: Heroku

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create easybets-api
```

3. Deploy your app:
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

## Connecting the Android App

In your Android app, update the `OddsApiService.kt` to use your deployed API URL:

```kotlin
private const val BASE_URL = "https://<your-firebase-function-url>/api/"
```
