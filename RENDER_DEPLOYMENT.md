# Render Deployment Guide

## Quick Deploy Steps

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `https://github.com/Ruthwik000/news_backend.git`

2. **Configure Service**
   - **Name**: `news-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
   - **Instance Type**: Free tier is fine for testing

3. **Environment Variables**
   Add these in Render dashboard:
   ```
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY=your-private-key
   FIREBASE_CLIENT_EMAIL=your-client-email
   GEMINI_API_KEY=your-gemini-api-key
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy from your main branch

## Your Data Format

The backend now saves data in the exact format your frontend expects:

```json
{
  "id": "unique_document_id",
  "title": {
    "en": "English Title",
    "hi": "हिंदी शीर्षक", 
    "te": "తెలుగు శీర్షిక"
  },
  "summary": {
    "en": "English summary text",
    "hi": "हिंदी सारांश",
    "te": "తెలుగు సారాంశం"
  },
  "category": "news|price|scheme",
  "source": "PIB Agriculture|eNAM|MyScheme",
  "url": "https://original-source-url.com",
  "imageUrl": "https://image-url.com/image.jpg",
  "date": "2024-03-10T10:00:00Z",
  "is_active": true,
  "created_at": "2024-03-10T10:00:00Z",
  "updated_at": "2024-03-10T10:00:00Z"
}
```

### Category-Specific Fields:

**Price Items:**
```json
{
  "category": "price",
  "commodity": "Cotton",
  "variety": "Medium Staple",
  "price": "6500",
  "unit": "quintal", 
  "market": "Hyderabad APMC",
  "change": "+2.5%"
}
```

**Scheme Items:**
```json
{
  "category": "scheme",
  "benefits": "₹6000 per year",
  "application_url": "https://pmkisan.gov.in"
}
```

## API Endpoints

- `GET /` - Health check
- `GET /news` - Get all news
- `GET /news?category=price` - Get price news
- `GET /news/{id}` - Get specific news item
- `POST /scrape` - Trigger scraping (manual)

Your backend is now ready for production deployment!