# 🌾 Agricultural News Backend

FastAPI backend service for scraping, processing, and storing agricultural news using AI enhancement.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd news-backend
pip install -r requirements.txt
```

### 2. Basic Setup Test
```bash
python test_basic.py
```

### 3. Configure Firebase
```bash
python setup_firebase.py
```
Follow the prompts to add your Firebase service account credentials.

### 4. Test All Connections
```bash
python test_connection.py
```

### 5. Start the Server
```bash
python start.py
```

The server will be available at:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

## 📋 Configuration

### Environment Variables (.env)
```env
# Firebase Configuration (Required)
FIREBASE_PROJECT_ID=kisanconnect-402db
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@kisanconnect-402db.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Gemini AI Configuration (Required)
GEMINI_API_KEY=your-gemini-api-key

# Unsplash API Configuration (Optional - for images)
UNSPLASH_ACCESS_KEY=your-unsplash-access-key
UNSPLASH_SECRET_KEY=your-unsplash-secret-key

# Server Configuration
PORT=8001
HOST=0.0.0.0
DEBUG=True
```

## 🔥 Firebase Setup

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed instructions.

**Quick steps:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `kisanconnect-402db`
3. Project Settings → Service Accounts
4. Generate new private key
5. Run `python setup_firebase.py`

## 🤖 Features

### Data Sources
- **PIB Agriculture**: Government press releases and news
- **eNAM**: Market price data for agricultural commodities
- **MyScheme**: Government schemes and subsidies

### AI Enhancement
- **Content Enhancement**: Uses Gemini 2.5 Flash for content improvement
- **Multi-language Support**: Translates to English, Hindi, and Telugu
- **Image Finding**: Searches for relevant images using Unsplash API

### Data Storage
- **Firestore Integration**: Stores all processed data in Firebase Firestore
- **Real-time Updates**: Supports real-time data subscriptions
- **Automatic Cleanup**: Removes old data automatically

### Automation
- **Scheduled Scraping**: Runs every 6 hours automatically
- **Background Processing**: Non-blocking data processing
- **Status Monitoring**: Real-time scraping status updates

## 🛠 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /news` - Get all news items
- `GET /news?category=price` - Get market prices
- `GET /news?category=scheme` - Get government schemes

### Management Endpoints
- `POST /scrape` - Manually trigger scraping
- `GET /scraping-status` - Get current scraping status
- `POST /news/{id}/regenerate` - Regenerate specific news item

### Query Parameters
- `category`: Filter by category (news, price, scheme)
- `limit`: Limit number of results (default: 50)

## 📊 Data Flow

1. **Scraping**: Collects raw data from government websites
2. **AI Processing**: Enhances content with Gemini AI
3. **Image Finding**: Searches for relevant images
4. **Storage**: Saves to Firestore `agricultural_news` collection
5. **API**: Serves processed data to frontend

## 🧪 Testing

### Basic Tests
```bash
python test_basic.py
```
Tests package imports, environment setup, and FastAPI creation.

### Connection Tests
```bash
python test_connection.py
```
Tests Firebase, Gemini API, and scraper connections.

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test news endpoint
curl http://localhost:8001/news?limit=5

# Trigger manual scraping
curl -X POST http://localhost:8001/scrape
```

## 🔧 Troubleshooting

### Common Issues

**"Firebase credentials not found"**
- Run `python setup_firebase.py`
- Check that .env file has correct Firebase credentials

**"Gemini API error"**
- Verify GEMINI_API_KEY in .env file
- Check API quota and billing in Google Cloud Console

**"Permission denied" in Firestore**
- Ensure service account has proper permissions
- Check Firestore rules allow write access

**"Module not found" errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### Debug Mode
Set `DEBUG=True` in .env for detailed logging.

### Logs
- Console output shows real-time status
- Firestore stores scraping status and history

## 🔒 Security

- **Environment Variables**: Keep .env file secure
- **Service Account**: Don't commit Firebase credentials
- **API Keys**: Protect Gemini and Unsplash keys
- **CORS**: Configure properly for production

## 📈 Monitoring

### Health Checks
- `/health` endpoint shows service status
- `/scraping-status` shows data collection status

### Metrics
- Items processed per run
- Success/failure rates
- Last run timestamps
- Next scheduled run

## 🚀 Production Deployment

### Environment Setup
1. Set `DEBUG=False`
2. Configure proper CORS origins
3. Use production Firebase project
4. Set up proper logging

### Scaling
- Use multiple worker processes
- Configure load balancing
- Set up monitoring and alerts
- Implement rate limiting