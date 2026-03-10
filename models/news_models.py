"""
Data models for the news backend
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NewsCategory(str, Enum):
    NEWS = "news"
    PRICE = "price"
    SCHEME = "scheme"

class MultilingualText(BaseModel):
    en: str
    hi: str
    te: str

class NewsItem(BaseModel):
    id: str
    title: MultilingualText
    summary: MultilingualText
    category: NewsCategory
    source: str
    url: str
    image_url: Optional[str] = None
    date: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Additional fields for different categories
    commodity: Optional[str] = None  # For price category
    variety: Optional[str] = None    # For price category
    price: Optional[float] = None    # For price category
    unit: Optional[str] = None       # For price category
    market: Optional[str] = None     # For price category
    change: Optional[str] = None     # For price category
    
    description: Optional[MultilingualText] = None  # For scheme category
    eligibility: Optional[MultilingualText] = None  # For scheme category
    benefits: Optional[str] = None                  # For scheme category
    application_url: Optional[str] = None           # For scheme category

class NewsResponse(BaseModel):
    success: bool
    data: List[NewsItem]
    count: int
    message: str

class ScrapingStatus(BaseModel):
    status: str  # running, completed, error, idle
    message: str
    last_run: Optional[datetime] = None
    items_processed: Optional[int] = None
    next_run: Optional[datetime] = None

class RawNewsItem(BaseModel):
    """Raw scraped news item before AI processing"""
    title: str
    content: Optional[str] = None
    url: str
    source: str
    category: str
    date: Optional[str] = None
    image_url: Optional[str] = None
    
    # Raw data specific to category
    raw_data: Optional[Dict[str, Any]] = None

class GeminiRequest(BaseModel):
    """Request model for Gemini AI processing"""
    raw_item: RawNewsItem
    target_languages: List[str] = ["en", "hi", "te"]
    enhance_content: bool = True
    generate_image: bool = True

class GeminiResponse(BaseModel):
    """Response model from Gemini AI processing"""
    enhanced_item: NewsItem
    processing_notes: Optional[str] = None
    confidence_score: Optional[float] = None