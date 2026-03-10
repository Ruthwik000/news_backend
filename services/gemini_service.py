"""
Gemini AI service for content enhancement and image URL finding
"""

import google.generativeai as genai
import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
import re

from models.news_models import RawNewsItem, NewsItem, MultilingualText, NewsCategory

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.model = None
        self.session = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini AI service initialized")
        else:
            logger.warning("Gemini API key not found")
    
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return self.api_key is not None and self.model is not None
    
    async def enhance_news_item(self, raw_item: RawNewsItem) -> NewsItem:
        """Enhance a raw news item with AI processing"""
        try:
            if not self.is_configured():
                return self._create_fallback_news_item(raw_item)
            
            # Generate enhanced content using Gemini
            enhanced_content = await self._generate_enhanced_content(raw_item)
            
            # Find relevant image URL
            image_url = await self._find_relevant_image(raw_item, enhanced_content)
            
            # Create the enhanced news item
            news_item = self._create_news_item_from_enhanced_content(
                raw_item, enhanced_content, image_url
            )
            
            return news_item
            
        except Exception as e:
            logger.error(f"Error enhancing news item: {e}")
            return self._create_fallback_news_item(raw_item)
    
    async def _generate_enhanced_content(self, raw_item: RawNewsItem) -> Dict[str, Any]:
        """Generate enhanced content using Gemini AI"""
        try:
            prompt = self._create_enhancement_prompt(raw_item)
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            # Parse the JSON response
            content_text = response.text.strip()
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                enhanced_content = json.loads(json_str)
                return enhanced_content
            else:
                logger.warning("Could not extract JSON from Gemini response")
                return self._create_fallback_enhanced_content(raw_item)
                
        except Exception as e:
            logger.error(f"Error generating enhanced content: {e}")
            return self._create_fallback_enhanced_content(raw_item)
    
    def _create_enhancement_prompt(self, raw_item: RawNewsItem) -> str:
        """Create a prompt for content enhancement"""
        category_specific_instructions = {
            "news": "Focus on agricultural impact, farmer benefits, and implementation details.",
            "price": "Include market analysis, price trends, and factors affecting the price.",
            "scheme": "Detail eligibility criteria, application process, and benefits for farmers."
        }
        
        category_instruction = category_specific_instructions.get(
            raw_item.category, "Provide comprehensive agricultural context."
        )
        
        prompt = f"""
You are an agricultural news expert. Enhance the following {raw_item.category} item with accurate, detailed information in multiple languages.

Original Title: {raw_item.title}
Original Content: {raw_item.content or "No content provided"}
Source: {raw_item.source}
Category: {raw_item.category}

Instructions:
1. {category_instruction}
2. Create translations in English, Hindi, and Telugu
3. Ensure accuracy and relevance to Indian agriculture
4. Keep titles concise but informative
5. Make summaries comprehensive but readable

Please respond with a JSON object in this exact format:
{{
    "title": {{
        "en": "Enhanced English title",
        "hi": "Enhanced Hindi title",
        "te": "Enhanced Telugu title"
    }},
    "summary": {{
        "en": "Detailed English summary (150-200 words)",
        "hi": "Detailed Hindi summary (150-200 words)",
        "te": "Detailed Telugu summary (150-200 words)"
    }},
    "image_search_keywords": "relevant keywords for finding images",
    "category_specific_data": {{
        // Add relevant fields based on category
    }}
}}

For price category, include: commodity, variety, price, unit, market, change
For scheme category, include: eligibility, benefits, application_url
For news category, include: impact, implementation_date, affected_regions
"""
        
        return prompt
    
    async def _find_relevant_image(self, raw_item: RawNewsItem, enhanced_content: Dict[str, Any]) -> str:
        """Find relevant image URL using search APIs and AI"""
        try:
            # Get search keywords from enhanced content or generate them
            search_keywords = enhanced_content.get("image_search_keywords", "")
            
            if not search_keywords:
                search_keywords = await self._generate_image_search_keywords(raw_item)
            
            # Try multiple image sources
            image_url = await self._search_unsplash_image(search_keywords)
            
            if not image_url:
                image_url = await self._search_free_images(search_keywords)
            
            if not image_url:
                image_url = self._get_fallback_image(raw_item.category)
            
            return image_url
            
        except Exception as e:
            logger.error(f"Error finding relevant image: {e}")
            return self._get_fallback_image(raw_item.category)
    
    async def _generate_image_search_keywords(self, raw_item: RawNewsItem) -> str:
        """Generate image search keywords using Gemini"""
        try:
            prompt = f"""
Generate 3-5 relevant keywords for finding images related to this agricultural {raw_item.category}:

Title: {raw_item.title}
Content: {raw_item.content or ""}
Category: {raw_item.category}

Return only the keywords separated by commas, focusing on:
- Agricultural themes
- Indian farming context
- Visual elements that would make good news images
- Avoid text-heavy or complex concepts

Example: "indian farmer, agriculture, crops, farming, rural india"
"""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                )
            )
            
            keywords = response.text.strip().replace('\n', ' ')
            return keywords
            
        except Exception as e:
            logger.error(f"Error generating image keywords: {e}")
            return self._get_default_keywords(raw_item.category)
    
    async def _search_unsplash_image(self, keywords: str) -> Optional[str]:
        """Search for images on Unsplash"""
        if not self.unsplash_key:
            return None
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": keywords,
                "per_page": 5,
                "orientation": "landscape",
                "content_filter": "high"
            }
            headers = {
                "Authorization": f"Client-ID {self.unsplash_key}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("results"):
                        # Get the first high-quality image
                        image = data["results"][0]
                        return image["urls"]["regular"]
                
        except Exception as e:
            logger.error(f"Error searching Unsplash: {e}")
        
        return None
    
    async def _search_free_images(self, keywords: str) -> Optional[str]:
        """Search for free images using alternative sources"""
        try:
            # Use Pixabay API as alternative
            pixabay_key = os.getenv("PIXABAY_API_KEY")
            if not pixabay_key:
                return None
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = "https://pixabay.com/api/"
            params = {
                "key": pixabay_key,
                "q": keywords,
                "image_type": "photo",
                "orientation": "horizontal",
                "category": "nature",
                "per_page": 5,
                "safesearch": "true"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("hits"):
                        return data["hits"][0]["webformatURL"]
                
        except Exception as e:
            logger.error(f"Error searching free images: {e}")
        
        return None
    
    def _get_fallback_image(self, category: str) -> str:
        """Get fallback image URL based on category"""
        fallback_images = {
            "news": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800&h=400&fit=crop",
            "price": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&h=400&fit=crop",
            "scheme": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&h=400&fit=crop"
        }
        return fallback_images.get(category, fallback_images["news"])
    
    def _get_default_keywords(self, category: str) -> str:
        """Get default search keywords by category"""
        default_keywords = {
            "news": "indian agriculture, farming, crops, rural india",
            "price": "market, vegetables, crops, agriculture, trading",
            "scheme": "government, agriculture, support, farmers, india"
        }
        return default_keywords.get(category, "agriculture, farming, india")
    
    def _create_news_item_from_enhanced_content(
        self, 
        raw_item: RawNewsItem, 
        enhanced_content: Dict[str, Any], 
        image_url: str
    ) -> NewsItem:
        """Create NewsItem from enhanced content"""
        try:
            # Extract multilingual content
            title = enhanced_content.get("title", {})
            summary = enhanced_content.get("summary", {})
            
            # Create base news item
            news_item_data = {
                "id": f"{raw_item.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(raw_item.title) % 10000}",
                "title": MultilingualText(
                    en=title.get("en", raw_item.title),
                    hi=title.get("hi", raw_item.title),
                    te=title.get("te", raw_item.title)
                ),
                "summary": MultilingualText(
                    en=summary.get("en", raw_item.content or "No summary available"),
                    hi=summary.get("hi", raw_item.content or "कोई सारांश उपलब्ध नहीं"),
                    te=summary.get("te", raw_item.content or "సారాంశం అందుబాటులో లేదు")
                ),
                "category": NewsCategory(raw_item.category),
                "source": raw_item.source,
                "url": raw_item.url,
                "image_url": image_url,
                "date": raw_item.date or datetime.now().isoformat(),
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Add category-specific data
            category_data = enhanced_content.get("category_specific_data", {})
            if raw_item.raw_data:
                category_data.update(raw_item.raw_data)
            
            if raw_item.category == "price":
                news_item_data.update({
                    "commodity": category_data.get("commodity"),
                    "variety": category_data.get("variety"),
                    "price": category_data.get("price"),
                    "unit": category_data.get("unit", "quintal"),
                    "market": category_data.get("market"),
                    "change": category_data.get("change")
                })
            elif raw_item.category == "scheme":
                eligibility = category_data.get("eligibility", {})
                if isinstance(eligibility, str):
                    eligibility = {"en": eligibility, "hi": eligibility, "te": eligibility}
                
                news_item_data.update({
                    "description": news_item_data["summary"],  # Use summary as description
                    "eligibility": MultilingualText(**eligibility) if eligibility else None,
                    "benefits": category_data.get("benefits"),
                    "application_url": category_data.get("application_url")
                })
            
            return NewsItem(**news_item_data)
            
        except Exception as e:
            logger.error(f"Error creating news item from enhanced content: {e}")
            return self._create_fallback_news_item(raw_item)
    
    def _create_fallback_news_item(self, raw_item: RawNewsItem) -> NewsItem:
        """Create a fallback news item when AI processing fails"""
        return NewsItem(
            id=f"{raw_item.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(raw_item.title) % 10000}",
            title=MultilingualText(
                en=raw_item.title,
                hi=raw_item.title,
                te=raw_item.title
            ),
            summary=MultilingualText(
                en=raw_item.content or "No summary available",
                hi=raw_item.content or "कोई सारांश उपलब्ध नहीं",
                te=raw_item.content or "సారాంశం అందుబాటులో లేదు"
            ),
            category=NewsCategory(raw_item.category),
            source=raw_item.source,
            url=raw_item.url,
            image_url=self._get_fallback_image(raw_item.category),
            date=raw_item.date or datetime.now().isoformat(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Add raw data if available
            **(raw_item.raw_data or {})
        )
    
    def _create_fallback_enhanced_content(self, raw_item: RawNewsItem) -> Dict[str, Any]:
        """Create fallback enhanced content"""
        return {
            "title": {
                "en": raw_item.title,
                "hi": raw_item.title,
                "te": raw_item.title
            },
            "summary": {
                "en": raw_item.content or "No summary available",
                "hi": raw_item.content or "कोई सारांश उपलब्ध नहीं",
                "te": raw_item.content or "సారాంశం అందుబాటులో లేదు"
            },
            "image_search_keywords": self._get_default_keywords(raw_item.category),
            "category_specific_data": raw_item.raw_data or {}
        }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()