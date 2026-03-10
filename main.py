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
from production_config import ProductionConfig, performance_monitor
from health_monitor import health_monitor, DatabaseHealthChecker, APIHealthChecker

# Load environment variables
load_dotenv()

# Setup production logging
ProductionConfig.setup_logging()

# Configure logging
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
    allow_origins=ProductionConfig.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scraper_service = ScraperService()
gemini_service = GeminiService()
firestore_service = FirestoreService()
scheduler_service = SchedulerService(scraper_service, gemini_service, firestore_service)

# Initialize health checkers
db_health_checker = DatabaseHealthChecker(firestore_service)
api_health_checker = APIHealthChecker(gemini_service, scraper_service)

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
    """Comprehensive health check with system metrics"""
    try:
        # Check service health
        services = {
            "scraper": scraper_service,
            "gemini": gemini_service,
            "firestore": firestore_service,
            "scheduler": scheduler_service
        }
        
        service_health = await health_monitor.check_service_health(services)
        
        # Check database health
        db_health = await db_health_checker.check_connection()
        
        # Check API health
        gemini_health = await api_health_checker.check_gemini_api()
        
        # Get system metrics
        system_health = health_monitor.get_health_summary()
        
        # Get performance metrics
        metrics = performance_monitor.get_metrics()
        
        # Get alerts
        alerts = health_monitor.get_alerts()
        
        health_data = {
            "status": "healthy",
            "services": service_health,
            "database": db_health,
            "apis": {
                "gemini": gemini_health
            },
            "system": system_health,
            "performance": metrics,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
        
        # Record health check
        health_monitor.record_health_check(health_data)
        
        return health_data
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/news", response_model=NewsResponse)
async def get_news(category: str = None, limit: int = 50):
    """Get news from Firestore"""
    try:
        performance_monitor.increment("requests_total")
        
        news_items = await firestore_service.get_news(category=category, limit=limit)
        
        performance_monitor.increment("requests_success")
        
        return NewsResponse(
            success=True,
            data=news_items,
            count=len(news_items),
            message=f"Retrieved {len(news_items)} news items"
        )
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        performance_monitor.increment("requests_error")
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

@app.get("/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        return {
            "performance": performance_monitor.get_metrics(),
            "system": health_monitor.get_system_info(),
            "uptime": health_monitor.get_uptime(),
            "alerts": health_monitor.get_alerts(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics/reset")
async def reset_metrics():
    """Reset performance metrics"""
    try:
        performance_monitor.reset_metrics()
        return {
            "success": True,
            "message": "Performance metrics reset",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
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
        performance_monitor.increment("scraping_runs")
        
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
                performance_monitor.increment("ai_enhancements")
            except Exception as e:
                logger.error(f"Error processing item {item.get('id', 'unknown')}: {e}")
                # Keep original item if processing fails
                processed_news.append(item)
        
        # Store in Firestore
        await firestore_service.update_scraping_status("storing", f"Storing {len(processed_news)} items...")
        
        stored_count = await firestore_service.store_news_batch(processed_news)
        performance_monitor.increment("items_processed", stored_count)
        performance_monitor.increment("database_writes", stored_count)
        
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