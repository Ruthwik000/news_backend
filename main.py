"""
Agricultural News Backend API
FastAPI backend for scraping, processing, and storing agricultural news
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

from services.scraper_service import ScraperService
from services.gemini_service import GeminiService
from services.firestore_service import FirestoreService
from services.scheduler_service import SchedulerService
from models.news_models import NewsResponse, NewsItem, ScrapingStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agricultural News Backend",
    description="Backend service for scraping and processing agricultural news",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "https://your-frontend-domain.com",  # Your production frontend
        # Add your actual frontend URLs here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scraper_service = ScraperService()
gemini_service = GeminiService()
firestore_service = FirestoreService()
scheduler_service = SchedulerService(scraper_service, gemini_service, firestore_service)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Agricultural News Backend...")
    
    # Initialize Firebase
    await firestore_service.initialize()
    
    # Start scheduler for automatic news updates
    scheduler_service.start()
    
    logger.info("Backend initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Agricultural News Backend...")
    scheduler_service.stop()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Agricultural News Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "scraper": "active",
            "gemini": "active" if gemini_service.is_configured() else "not configured",
            "firestore": "active" if firestore_service.is_initialized else "not initialized",
            "scheduler": "active" if scheduler_service.is_running else "stopped"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/news", response_model=NewsResponse)
async def get_news(category: str = None, limit: int = 50):
    """Get news from Firestore"""
    try:
        news_items = await firestore_service.get_news(category=category, limit=limit)
        return NewsResponse(
            success=True,
            data=news_items,
            count=len(news_items),
            message=f"Retrieved {len(news_items)} news items"
        )
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape")
async def trigger_scraping(background_tasks: BackgroundTasks):
    """Manually trigger news scraping"""
    try:
        background_tasks.add_task(run_scraping_pipeline)
        return {
            "success": True,
            "message": "Scraping pipeline started in background"
        }
    except Exception as e:
        logger.error(f"Error triggering scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraping-status")
async def get_scraping_status():
    """Get current scraping status"""
    try:
        status = await firestore_service.get_scraping_status()
        return status
    except Exception as e:
        logger.error(f"Error getting scraping status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/news/{news_id}/regenerate")
async def regenerate_news_content(news_id: str, background_tasks: BackgroundTasks):
    """Regenerate content for a specific news item using Gemini"""
    try:
        background_tasks.add_task(regenerate_single_news, news_id)
        return {
            "success": True,
            "message": f"Content regeneration started for news item {news_id}"
        }
    except Exception as e:
        logger.error(f"Error regenerating news content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_scraping_pipeline():
    """Run the complete scraping and processing pipeline"""
    try:
        logger.info("Starting scraping pipeline...")
        
        # Update scraping status
        await firestore_service.update_scraping_status("running", "Starting news scraping...")
        
        # Scrape news from all sources
        raw_news = await scraper_service.scrape_all_sources()
        logger.info(f"Scraped {len(raw_news)} raw news items")
        
        # Process with Gemini AI
        await firestore_service.update_scraping_status("processing", f"Processing {len(raw_news)} items with AI...")
        
        processed_news = []
        for item in raw_news:
            try:
                enhanced_item = await gemini_service.enhance_news_item(item)
                processed_news.append(enhanced_item)
            except Exception as e:
                logger.error(f"Error processing item {item.get('id', 'unknown')}: {e}")
                # Keep original item if processing fails
                processed_news.append(item)
        
        # Store in Firestore
        await firestore_service.update_scraping_status("storing", f"Storing {len(processed_news)} items...")
        
        stored_count = await firestore_service.store_news_batch(processed_news)
        
        # Update final status
        await firestore_service.update_scraping_status(
            "completed", 
            f"Successfully processed and stored {stored_count} news items",
            stored_count
        )
        
        logger.info(f"Scraping pipeline completed. Stored {stored_count} items.")
        
    except Exception as e:
        logger.error(f"Error in scraping pipeline: {e}")
        await firestore_service.update_scraping_status("error", str(e))

async def regenerate_single_news(news_id: str):
    """Regenerate content for a single news item"""
    try:
        # Get existing news item
        news_item = await firestore_service.get_news_by_id(news_id)
        if not news_item:
            logger.error(f"News item {news_id} not found")
            return
        
        # Regenerate with Gemini
        enhanced_item = await gemini_service.enhance_news_item(news_item)
        
        # Update in Firestore
        await firestore_service.update_news_item(news_id, enhanced_item)
        
        logger.info(f"Successfully regenerated content for news item {news_id}")
        
    except Exception as e:
        logger.error(f"Error regenerating news item {news_id}: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # For production deployment
    if port == 10000:  # Render's default port
        debug = False
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )