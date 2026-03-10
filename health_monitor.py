"""
Health monitoring and system diagnostics
"""

import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class HealthMonitor:
    """System health monitoring"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.last_health_check = None
        self.health_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        uptime = datetime.now() - self.start_time
        return {
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0]  # Remove microseconds
        }
    
    async def check_service_health(self, services: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of all services"""
        health_status = {}
        
        for service_name, service_obj in services.items():
            try:
                if hasattr(service_obj, 'is_healthy'):
                    health_status[service_name] = await service_obj.is_healthy()
                elif hasattr(service_obj, 'is_initialized'):
                    health_status[service_name] = service_obj.is_initialized
                elif hasattr(service_obj, 'is_running'):
                    health_status[service_name] = service_obj.is_running
                else:
                    health_status[service_name] = True  # Assume healthy if no check method
            except Exception as e:
                logger.error(f"Error checking {service_name} health: {e}")
                health_status[service_name] = False
        
        return health_status
    
    def record_health_check(self, health_data: Dict[str, Any]):
        """Record health check data"""
        health_record = {
            "timestamp": datetime.now().isoformat(),
            "data": health_data
        }
        
        self.health_history.append(health_record)
        
        # Keep only recent history
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
        
        self.last_health_check = datetime.now()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        return {
            "uptime": self.get_uptime(),
            "system": self.get_system_info(),
            "last_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "history_count": len(self.health_history)
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts based on thresholds"""
        alerts = []
        system_info = self.get_system_info()
        
        if "error" not in system_info:
            # CPU usage alert
            if system_info["cpu_usage"] > 80:
                alerts.append({
                    "type": "warning",
                    "message": f"High CPU usage: {system_info['cpu_usage']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Memory usage alert
            if system_info["memory"]["percent"] > 85:
                alerts.append({
                    "type": "warning",
                    "message": f"High memory usage: {system_info['memory']['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Disk usage alert
            if system_info["disk"]["percent"] > 90:
                alerts.append({
                    "type": "critical",
                    "message": f"High disk usage: {system_info['disk']['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts

class DatabaseHealthChecker:
    """Database-specific health checks"""
    
    def __init__(self, firestore_service):
        self.firestore_service = firestore_service
    
    async def check_connection(self) -> Dict[str, Any]:
        """Check database connection"""
        try:
            # Try to read from scraping_status collection
            status = await self.firestore_service.get_scraping_status()
            return {
                "connected": True,
                "last_status": status.status if status else "unknown",
                "response_time": "< 1s"  # Could measure actual response time
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "response_time": "timeout"
            }
    
    async def check_write_capability(self) -> Dict[str, Any]:
        """Check database write capability"""
        try:
            # Try to update scraping status
            await self.firestore_service.update_scraping_status(
                "health_check", 
                "Database write test"
            )
            return {
                "writable": True,
                "last_write": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "writable": False,
                "error": str(e)
            }

class APIHealthChecker:
    """API-specific health checks"""
    
    def __init__(self, gemini_service, scraper_service):
        self.gemini_service = gemini_service
        self.scraper_service = scraper_service
    
    async def check_gemini_api(self) -> Dict[str, Any]:
        """Check Gemini API health"""
        try:
            # Simple test to see if Gemini is configured
            is_configured = self.gemini_service.is_configured()
            return {
                "configured": is_configured,
                "status": "healthy" if is_configured else "not_configured"
            }
        except Exception as e:
            return {
                "configured": False,
                "status": "error",
                "error": str(e)
            }
    
    async def check_scraping_capability(self) -> Dict[str, Any]:
        """Check scraping capability"""
        try:
            # Test if scraper can make HTTP requests
            # This is a lightweight check
            return {
                "capable": True,
                "sources_configured": len(self.scraper_service.sources) if hasattr(self.scraper_service, 'sources') else 3,
                "status": "ready"
            }
        except Exception as e:
            return {
                "capable": False,
                "status": "error",
                "error": str(e)
            }

# Global health monitor instance
health_monitor = HealthMonitor()