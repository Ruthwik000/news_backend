# 🌾 Agricultural News Backend

A comprehensive, production-ready FastAPI backend for agricultural news aggregation with AI enhancement and real-time data processing.

## ✨ Features

### 🔄 Automated Data Pipeline
- **3-hour automated scraping** from PIB Agriculture, eNAM, and MyScheme
- **AI-powered content enhancement** using Gemini 2.5 Flash
- **Multilingual support** (English, Hindi, Telugu)
- **Real-time data storage** in Firebase Firestore
- **Intelligent image discovery** via Unsplash API

### 🚀 Production-Ready Architecture
- **FastAPI framework** with async/await support
- **Comprehensive health monitoring** with system metrics
- **Performance tracking** and alerting
- **Docker containerization** ready
- **Environment-based configuration**
- **Structured logging** and error handling

### 📊 Advanced Monitoring
- **System health checks** (CPU, memory, disk usage)
- **Service status monitoring** (database, AI, scheduler)
- **Performance metrics** (requests, success rates, processing times)
- **Real-time alerts** for system issues
- **Health history tracking**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGRICULTURAL NEWS BACKEND                    │
├─────────────────────────────────────────────────────────────────┤
│  Timer (3hr) → Scheduler → Scraper → Gemini AI → Firestore     │
│                     ↓                                           │
│              FastAPI Endpoints ← React Frontend                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Firebase project with Firestore
- Gemini API key
- (Optional) Unsplash API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ruthwik000/news_backend.git
   cd news_backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the application**
   ```bash
   python start.py
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Optional: Unsplash API
UNSPLASH_ACCESS_KEY=your-unsplash-key

# Server Configuration
PORT=8001
HOST=0.0.0.0
DEBUG=False
LOG_LEVEL=INFO

# Performance Tuning
SCRAPING_INTERVAL_HOURS=3
MAX_ITEMS_PER_SOURCE=50
MAX_CONCURRENT_REQUESTS=10
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Basic health check
- `GET /health` - Comprehensive system health with metrics
- `GET /news` - Retrieve processed news items
- `GET /news?category=price` - Get market prices
- `GET /news?category=scheme` - Get government schemes
- `POST /scrape` - Manually trigger scraping pipeline
- `GET /scraping-status` - Check pipeline status

### Monitoring Endpoints
- `GET /metrics` - System performance metrics
- `POST /metrics/reset` - Reset performance counters

### Example Response
```json
{
  "success": true,
  "data": [
    {
      "id": "news_001",
      "title": {
        "en": "New Agricultural Subsidy Scheme Launched",
        "hi": "नई कृषि सब्सिडी योजना शुरू की गई",
        "te": "కొత్త వ్యవసాయ సబ్సిడీ పథకం ప్రారంభించబడింది"
      },
      "summary": {
        "en": "Government announces new subsidy scheme...",
        "hi": "सरकार ने नई सब्सिडी योजना की घोषणा...",
        "te": "ప్రభుత్వం కొత్త సబ్సిడీ పథకాన్ని..."
      },
      "category": "news",
      "source": "PIB Agriculture",
      "url": "https://pib.gov.in/news-item",
      "imageUrl": "https://images.unsplash.com/photo-...",
      "date": "2024-03-10T10:00:00Z",
      "is_active": true
    }
  ],
  "count": 1,
  "message": "Retrieved 1 news items"
}
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t agricultural-news-backend .

# Run container
docker run -p 8001:8000 --env-file .env agricultural-news-backend
```

### Docker Compose
```yaml
version: '3.8'
services:
  agricultural-news-backend:
    build: .
    ports:
      - "8001:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## ☁️ Cloud Deployment

### Render (Recommended)
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python start.py`
4. Add environment variables in dashboard

### Railway
1. Connect repository
2. Add `Procfile`: `web: python start.py`
3. Configure environment variables

### Google Cloud Run
```bash
gcloud run deploy agricultural-news-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Testing

### Run Test Suite
```bash
python test_backend.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test news endpoint
curl http://localhost:8001/news

# Trigger manual scraping
curl -X POST http://localhost:8001/scrape
```

## 📊 Monitoring & Metrics

### Health Monitoring
- **System Metrics**: CPU, memory, disk usage
- **Service Health**: Database, AI, scheduler status
- **Performance Tracking**: Request rates, success rates
- **Alert System**: Automated threshold-based alerts

### Accessing Metrics
```bash
# Get comprehensive health status
curl http://localhost:8001/health

# Get performance metrics
curl http://localhost:8001/metrics

# Reset metrics
curl -X POST http://localhost:8001/metrics/reset
```

## 🔄 Data Flow

1. **Automated Scraping** (Every 3 hours)
   - PIB Agriculture → News articles
   - eNAM → Market prices
   - MyScheme → Government schemes

2. **AI Enhancement**
   - Gemini 2.5 Flash processes content
   - Generates multilingual titles/summaries
   - Finds relevant images

3. **Storage**
   - Structured data saved to Firestore
   - Real-time updates to frontend

4. **API Access**
   - RESTful endpoints for data retrieval
   - Real-time status monitoring

## 🛠️ Development

### Project Structure
```
agricultural-news-backend/
├── main.py                 # FastAPI application
├── start.py               # Application startup script
├── production_config.py   # Production configuration
├── health_monitor.py      # System health monitoring
├── test_backend.py        # Comprehensive test suite
├── models/
│   └── news_models.py     # Pydantic data models
├── services/
│   ├── scraper_service.py    # Web scraping logic
│   ├── gemini_service.py     # AI enhancement
│   ├── firestore_service.py  # Database operations
│   └── scheduler_service.py  # Automated scheduling
└── requirements.txt       # Python dependencies
```

### Adding New Sources
1. Update `scraper_service.py` with new source logic
2. Add source configuration to environment
3. Update data models if needed
4. Test with `python test_backend.py`

## 🔒 Security

- Environment variable configuration
- Firebase security rules
- Input validation with Pydantic
- CORS configuration
- Rate limiting support
- Non-root Docker user

## 📈 Performance

- **Processing Capacity**: ~100-200 articles per cycle
- **AI Enhancement**: 3-5 seconds per item
- **API Response Time**: <500ms average
- **Uptime**: 99%+ with proper deployment
- **Data Freshness**: Updated every 3 hours

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_backend.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the [deployment checklist](DEPLOYMENT_CHECKLIST.md)
2. Review [system architecture](SYSTEM_ARCHITECTURE.md)
3. Check [data flow documentation](DATA_FLOW_DOCUMENTATION.md)
4. Open an issue on GitHub

---

**Built with ❤️ for farmers and agricultural communities**