"""
Production configuration and optimization settings
"""

import os
import logging
from typing import Dict, Any

class ProductionConfig:
    """Production configuration settings"""
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8001))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Scraping configuration
    SCRAPING_INTERVAL_HOURS = int(os.getenv("SCRAPING_INTERVAL_HOURS", 3))
    MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", 50))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # AI processing configuration
    GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", 30))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
    
    # Database configuration
    FIRESTORE_TIMEOUT = int(os.getenv("FIRESTORE_TIMEOUT", 30))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 30))
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    @classmethod
    def setup_logging(cls):
        """Setup production logging"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("agricultural_news.log") if not cls.DEBUG else logging.NullHandler()
            ]
        )
    
    @classmethod
    def get_cors_origins(cls) -> list:
        """Get CORS origins from environment"""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        return [origin.strip() for origin in origins.split(",")]
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate production configuration"""
        issues = []
        
        # Check required environment variables
        required_vars = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_CLIENT_EMAIL",
            "GEMINI_API_KEY"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Check Firebase private key format
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        if private_key and not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            issues.append("FIREBASE_PRIVATE_KEY should start with '-----BEGIN PRIVATE KEY-----'")
        
        # Check port range
        if not (1000 <= cls.PORT <= 65535):
            issues.append(f"PORT {cls.PORT} is not in valid range (1000-65535)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "host": cls.HOST,
                "port": cls.PORT,
                "debug": cls.DEBUG,
                "log_level": cls.LOG_LEVEL,
                "scraping_interval": cls.SCRAPING_INTERVAL_HOURS,
                "cors_origins": cls.get_cors_origins()
            }
        }

# Performance monitoring
class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "scraping_runs": 0,
            "items_processed": 0,
            "ai_enhancements": 0,
            "database_writes": 0
        }
    
    def increment(self, metric: str, value: int = 1):
        """Increment a metric"""
        if metric in self.metrics:
            self.metrics[metric] += value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        success_rate = 0
        if self.metrics["requests_total"] > 0:
            success_rate = (self.metrics["requests_success"] / self.metrics["requests_total"]) * 100
        
        return {
            **self.metrics,
            "success_rate": round(success_rate, 2)
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = 0

# Global performance monitor instance
performance_monitor = PerformanceMonitor()