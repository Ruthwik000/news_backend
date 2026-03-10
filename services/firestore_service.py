"""
Firestore service for storing and retrieving news data
"""

import firebase_admin
from firebase_admin import credentials, firestore
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import json

from models.news_models import NewsItem, ScrapingStatus

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        self.db = None
        self.is_initialized = False
        self.collection_name = "agricultural_news"
        self.status_collection = "scraping_status"
    
    async def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Get Firebase credentials from environment
                firebase_config = {
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL', '')}"
                }
                
                # Validate required fields
                required_fields = ["project_id", "private_key", "client_email"]
                missing_fields = [field for field in required_fields if not firebase_config.get(field)]
                
                if missing_fields:
                    logger.error(f"Missing Firebase configuration: {missing_fields}")
                    raise ValueError(f"Missing Firebase configuration: {missing_fields}")
                
                # Initialize Firebase
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                
                logger.info("Firebase Admin SDK initialized successfully")
            
            self.db = firestore.client()
            self.is_initialized = True
            
            # Initialize scraping status if not exists
            await self._initialize_scraping_status()
            
        except Exception as e:
            logger.error(f"Error initializing Firestore: {e}")
            self.is_initialized = False
            raise
    
    async def _initialize_scraping_status(self):
        """Initialize scraping status document"""
        try:
            status_ref = self.db.collection(self.status_collection).document("current")
            status_doc = status_ref.get()
            
            if not status_doc.exists:
                initial_status = {
                    "status": "idle",
                    "message": "System initialized",
                    "last_run": None,
                    "items_processed": 0,
                    "next_run": None,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP
                }
                status_ref.set(initial_status)
                logger.info("Initialized scraping status document")
                
        except Exception as e:
            logger.error(f"Error initializing scraping status: {e}")
    
    async def store_news_batch(self, news_items: List[NewsItem]) -> int:
        """Store a batch of news items in Firestore"""
        if not self.is_initialized:
            raise RuntimeError("Firestore not initialized")
        
        try:
            batch = self.db.batch()
            stored_count = 0
            
            for news_item in news_items:
                try:
                    # Convert NewsItem to dict
                    news_data = self._news_item_to_dict(news_item)
                    
                    # Reference to document
                    doc_ref = self.db.collection(self.collection_name).document(news_item.id)
                    
                    # Add to batch
                    batch.set(doc_ref, news_data, merge=True)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error preparing news item {news_item.id}: {e}")
                    continue
            
            # Commit batch
            if stored_count > 0:
                batch.commit()
                logger.info(f"Successfully stored {stored_count} news items")
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing news batch: {e}")
            raise
    
    async def get_news(self, category: Optional[str] = None, limit: int = 50) -> List[NewsItem]:
        """Get news items from Firestore"""
        if not self.is_initialized:
            raise RuntimeError("Firestore not initialized")
        
        try:
            query = self.db.collection(self.collection_name)
            
            # Filter by category if specified
            if category:
                query = query.where("category", "==", category)
            
            # Filter active items
            query = query.where("is_active", "==", True)
            
            # Order by creation date (newest first)
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            # Limit results
            query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            news_items = []
            for doc in docs:
                try:
                    news_item = self._dict_to_news_item(doc.id, doc.to_dict())
                    news_items.append(news_item)
                except Exception as e:
                    logger.error(f"Error converting document {doc.id}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return []
    
    async def get_news_by_id(self, news_id: str) -> Optional[NewsItem]:
        """Get a specific news item by ID"""
        if not self.is_initialized:
            raise RuntimeError("Firestore not initialized")
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(news_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return self._dict_to_news_item(doc.id, doc.to_dict())
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting news item {news_id}: {e}")
            return None
    
    async def update_news_item(self, news_id: str, news_item: NewsItem):
        """Update a specific news item"""
        if not self.is_initialized:
            raise RuntimeError("Firestore not initialized")
        
        try:
            news_data = self._news_item_to_dict(news_item)
            news_data["updated_at"] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection(self.collection_name).document(news_id)
            doc_ref.update(news_data)
            
            logger.info(f"Updated news item {news_id}")
            
        except Exception as e:
            logger.error(f"Error updating news item {news_id}: {e}")
            raise
    
    async def delete_old_news(self, days_old: int = 30):
        """Delete news items older than specified days"""
        if not self.is_initialized:
            raise RuntimeError("Firestore not initialized")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = self.db.collection(self.collection_name).where(
                "created_at", "<", cutoff_date
            )
            
            docs = query.stream()
            batch = self.db.batch()
            deleted_count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                deleted_count += 1
                
                # Commit in batches of 500 (Firestore limit)
                if deleted_count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            # Commit remaining
            if deleted_count % 500 != 0:
                batch.commit()
            
            logger.info(f"Deleted {deleted_count} old news items")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old news: {e}")
            return 0
    
    async def update_scraping_status(
        self, 
        status: str, 
        message: str, 
        items_processed: Optional[int] = None
    ):
        """Update scraping status"""
        if not self.is_initialized:
            return
        
        try:
            status_data = {
                "status": status,
                "message": message,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            
            if status == "running":
                status_data["last_run"] = firestore.SERVER_TIMESTAMP
            
            if items_processed is not None:
                status_data["items_processed"] = items_processed
            
            if status == "completed":
                # Calculate next run (3 hours from now)
                next_run = datetime.now() + timedelta(hours=3)
                status_data["next_run"] = next_run
                status_data["status"] = "idle"  # Set back to idle after completion
            
            status_ref = self.db.collection(self.status_collection).document("current")
            status_ref.set(status_data, merge=True)
            
        except Exception as e:
            logger.error(f"Error updating scraping status: {e}")
    
    async def get_scraping_status(self) -> ScrapingStatus:
        """Get current scraping status"""
        if not self.is_initialized:
            return ScrapingStatus(
                status="error",
                message="Firestore not initialized"
            )
        
        try:
            status_ref = self.db.collection(self.status_collection).document("current")
            status_doc = status_ref.get()
            
            if status_doc.exists:
                data = status_doc.to_dict()
                return ScrapingStatus(
                    status=data.get("status", "unknown"),
                    message=data.get("message", "No message"),
                    last_run=data.get("last_run"),
                    items_processed=data.get("items_processed"),
                    next_run=data.get("next_run")
                )
            else:
                return ScrapingStatus(
                    status="idle",
                    message="No status available"
                )
                
        except Exception as e:
            logger.error(f"Error getting scraping status: {e}")
            return ScrapingStatus(
                status="error",
                message=str(e)
            )
    
    def _news_item_to_dict(self, news_item: NewsItem) -> Dict[str, Any]:
        """Convert NewsItem to dictionary for Firestore"""
        data = {
            "title": {
                "en": news_item.title.en,
                "hi": news_item.title.hi,
                "te": news_item.title.te
            },
            "summary": {
                "en": news_item.summary.en,
                "hi": news_item.summary.hi,
                "te": news_item.summary.te
            },
            "category": news_item.category.value,
            "source": news_item.source,
            "url": news_item.url,
            "image_url": news_item.image_url,
            "date": news_item.date,
            "is_active": news_item.is_active,
            "created_at": news_item.created_at or firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        # Add category-specific fields
        if news_item.commodity:
            data["commodity"] = news_item.commodity
        if news_item.variety:
            data["variety"] = news_item.variety
        if news_item.price:
            data["price"] = news_item.price
        if news_item.unit:
            data["unit"] = news_item.unit
        if news_item.market:
            data["market"] = news_item.market
        if news_item.change:
            data["change"] = news_item.change
        if news_item.description:
            data["description"] = {
                "en": news_item.description.en,
                "hi": news_item.description.hi,
                "te": news_item.description.te
            }
        if news_item.eligibility:
            data["eligibility"] = {
                "en": news_item.eligibility.en,
                "hi": news_item.eligibility.hi,
                "te": news_item.eligibility.te
            }
        if news_item.benefits:
            data["benefits"] = news_item.benefits
        if news_item.application_url:
            data["application_url"] = news_item.application_url
        
        return data
    
    def _dict_to_news_item(self, doc_id: str, data: Dict[str, Any]) -> NewsItem:
        """Convert Firestore document to NewsItem"""
        from models.news_models import MultilingualText, NewsCategory
        
        # Handle multilingual text
        title_data = data.get("title", {})
        summary_data = data.get("summary", {})
        
        news_item_data = {
            "id": doc_id,
            "title": MultilingualText(
                en=title_data.get("en", ""),
                hi=title_data.get("hi", ""),
                te=title_data.get("te", "")
            ),
            "summary": MultilingualText(
                en=summary_data.get("en", ""),
                hi=summary_data.get("hi", ""),
                te=summary_data.get("te", "")
            ),
            "category": NewsCategory(data.get("category", "news")),
            "source": data.get("source", ""),
            "url": data.get("url", ""),
            "image_url": data.get("image_url"),
            "date": data.get("date", ""),
            "is_active": data.get("is_active", True),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at")
        }
        
        # Add category-specific fields if they exist
        optional_fields = [
            "commodity", "variety", "price", "unit", "market", "change", 
            "benefits", "application_url"
        ]
        
        for field in optional_fields:
            if field in data:
                news_item_data[field] = data[field]
        
        # Handle multilingual optional fields
        if "description" in data:
            desc_data = data["description"]
            news_item_data["description"] = MultilingualText(
                en=desc_data.get("en", ""),
                hi=desc_data.get("hi", ""),
                te=desc_data.get("te", "")
            )
        
        if "eligibility" in data:
            elig_data = data["eligibility"]
            news_item_data["eligibility"] = MultilingualText(
                en=elig_data.get("en", ""),
                hi=elig_data.get("hi", ""),
                te=elig_data.get("te", "")
            )
        
        return NewsItem(**news_item_data)