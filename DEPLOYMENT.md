# 🚀 Render Deployment Guide

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Firebase Service Account**: Have your Firebase credentials ready

## Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Make sure all files are committed
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

### 2. Create Render Service

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **Web Service**
3. **Connect GitHub** repository
4. **Select** your repository
5. **Configure service**:
   - **Name**: `kisan-news-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free` (for testing)

### 3. Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=kisanconnect-402db
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@kisanconnect-402db.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Unsplash API Configuration (Optional)
UNSPLASH_ACCESS_KEY=your-unsplash-access-key
UNSPLASH_SECRET_KEY=your-unsplash-secret-key

# Server Configuration
PORT=10000
HOST=0.0.0.0
DEBUG=false
```

### 4. Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Get your URL**: `https://your-service-name.onrender.com`

### 5. Update Frontend

Update your frontend `.env` file:

```env
# Change this to your Render URL
VITE_NEWS_BACKEND_URL=https://your-service-name.onrender.com
```

## Testing Deployment

### Health Check
```bash
curl https://your-service-name.onrender.com/health
```

### Get News
```bash
curl https://your-service-name.onrender.com/news
```

### Trigger Scraping
```bash
curl -X POST https://your-service-name.onrender.com/scrape
```

## Production Considerations

### 1. **Upgrade to Paid Plan**
- Free tier has limitations (sleeps after 15 minutes of inactivity)
- Paid plans ($7/month) keep service always running

### 2. **Database Persistence**
- Consider using Render PostgreSQL for caching
- Firebase Firestore handles main data storage

### 3. **Monitoring**
- Set up health check endpoints
- Monitor logs in Render dashboard
- Set up alerts for failures

### 4. **Security**
- Use environment variables for all secrets
- Enable HTTPS (automatic on Render)
- Configure CORS properly for production

## Troubleshooting

### Build Failures
- Check `requirements.txt` for version conflicts
- Review build logs in Render dashboard
- Ensure Python version compatibility

### Runtime Errors
- Check application logs
- Verify environment variables
- Test Firebase connection

### Performance Issues
- Monitor resource usage
- Consider upgrading instance type
- Optimize database queries

## Automatic Deployments

Render automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update backend"
git push origin main
# Render will automatically deploy
```

## Custom Domain (Optional)

1. **Go to Settings** in Render dashboard
2. **Add Custom Domain**
3. **Update DNS** records
4. **SSL certificate** is automatic

## Scaling

For high traffic:
1. **Upgrade instance type**
2. **Enable auto-scaling**
3. **Use Redis for caching**
4. **Implement rate limiting**