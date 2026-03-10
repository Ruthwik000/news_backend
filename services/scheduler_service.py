"""
Scheduler service for automated news scraping and processing
"""

import schedule
import threading
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, scraper_service, gemini_service, firestore_service):
        self.scraper_service = scraper_service
        self.gemini_service = gemini_service
        self.firestore_service = firestore_service
        self.scheduler_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.stop_event = threading.Event()
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Schedule jobs
        self._schedule_jobs()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.is_running = True
        
        logger.info("Scheduler service started")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        self.stop_event.set()
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Clear all scheduled jobs
        schedule.clear()
        
        logger.info("Scheduler service stopped")
    
    def _schedule_jobs(self):
        """Schedule all recurring jobs"""
        # Schedule news scraping every 3 hours
        schedule.every(3).hours.do(self._run_news_pipeline)
        
        # Schedule cleanup every day at 2 AM
        schedule.every().day.at("02:00").do(self._run_cleanup)
        
        # Schedule status update every hour
        schedule.every().hour.do(self._update_status)
        
        logger.info("Scheduled jobs configured")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        logger.info("Scheduler thread started")
        
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler thread: {e}")
                time.sleep(60)
        
        logger.info("Scheduler thread stopped")
    
    def _run_news_pipeline(self):
        """Run the news scraping and processing pipeline"""
        try:
            logger.info("Starting scheduled news pipeline")
            
            # Run the async pipeline in a new event loop
            asyncio.run(self._async_news_pipeline())
            
        except Exception as e:
            logger.error(f"Error in scheduled news pipeline: {e}")
    
    async def _async_news_pipeline(self):
        """Async news pipeline"""
        try:
            # Update status
            await self.firestore_service.update_scraping_status(
                "running", 
                "Starting scheduled news scraping..."
            )
            
            # Scrape news from all sources
            raw_news = await self.scraper_service.scrape_all_sources()
            logger.info(f"Scraped {len(raw_news)} raw news items")
            
            if not raw_news:
                await self.firestore_service.update_scraping_status(
                    "completed", 
                    "No new items found during scraping"
                )
                return
            
            # Process with Gemini AI
            await self.firestore_service.update_scraping_status(
                "processing", 
                f"Processing {len(raw_news)} items with AI..."
            )
            
            processed_news = []
            for i, item in enumerate(raw_news):
                try:
                    enhanced_item = await self.gemini_service.enhance_news_item(item)
                    processed_news.append(enhanced_item)
                    
                    # Update progress every 5 items
                    if (i + 1) % 5 == 0:
                        await self.firestore_service.update_scraping_status(
                            "processing", 
                            f"Processed {i + 1}/{len(raw_news)} items..."
                        )
                        
                except Exception as e:
                    logger.error(f"Error processing item {item.title}: {e}")
                    continue
            
            # Store in Firestore
            await self.firestore_service.update_scraping_status(
                "storing", 
                f"Storing {len(processed_news)} processed items..."
            )
            
            stored_count = await self.firestore_service.store_news_batch(processed_news)
            
            # Update final status
            await self.firestore_service.update_scraping_status(
                "completed", 
                f"Successfully processed and stored {stored_count} news items",
                stored_count
            )
            
            logger.info(f"Scheduled news pipeline completed. Stored {stored_count} items.")
            
        except Exception as e:
            logger.error(f"Error in async news pipeline: {e}")
            await self.firestore_service.update_scraping_status(
                "error", 
                f"Pipeline failed: {str(e)}"
            )
    
    def _run_cleanup(self):
        """Run cleanup tasks"""
        try:
            logger.info("Starting scheduled cleanup")
            asyncio.run(self._async_cleanup())
        except Exception as e:
            logger.error(f"Error in scheduled cleanup: {e}")
    
    async def _async_cleanup(self):
        """Async cleanup tasks"""
        try:
            # Delete news older than 30 days
            deleted_count = await self.firestore_service.delete_old_news(days_old=30)
            logger.info(f"Cleanup completed. Deleted {deleted_count} old items.")
            
        except Exception as e:
            logger.error(f"Error in async cleanup: {e}")
    
    def _update_status(self):
        """Update system status"""
        try:
            # This could include health checks, metrics updates, etc.
            logger.debug("Status update completed")
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def trigger_immediate_scraping(self):
        """Trigger immediate news scraping"""
        try:
            logger.info("Triggering immediate news scraping")
            threading.Thread(target=self._run_news_pipeline, daemon=True).start()
        except Exception as e:
            logger.error(f"Error triggering immediate scraping: {e}")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time"""
        try:
            jobs = schedule.get_jobs()
            if jobs:
                next_run = min(job.next_run for job in jobs)
                return next_run
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None
    
    def get_schedule_info(self) -> dict:
        """Get information about scheduled jobs"""
        try:
            jobs = schedule.get_jobs()
            job_info = []
            
            for job in jobs:
                job_info.append({
                    "job": str(job.job_func),
                    "next_run": job.next_run.isoformat() if job.next_run else None,
                    "interval": str(job.interval),
                    "unit": job.unit
                })
            
            return {
                "total_jobs": len(jobs),
                "jobs": job_info,
                "is_running": self.is_running
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule info: {e}")
            return {"error": str(e)}