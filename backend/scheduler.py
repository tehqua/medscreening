"""
Background tasks scheduler for maintenance operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable

from .services.orchestrator_service import get_orchestrator_service
from .services.file_service import cleanup_old_files
from .database import get_db
from .config import get_settings

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """
    Background task scheduler for periodic maintenance.
    
    Runs tasks like:
    - Session cleanup
    - File cleanup  
    - Database cleanup
    """
    
    def __init__(self):
        self.tasks = []
        self.running = False
        self.settings = get_settings()
    
    async def start(self):
        """Start all scheduled tasks"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        logger.info("Starting background scheduler")
        
        # Schedule tasks
        self.tasks = [
            asyncio.create_task(self._run_periodic(
                self._cleanup_sessions,
                interval_minutes=30
            )),
            asyncio.create_task(self._run_periodic(
                self._cleanup_files,
                interval_minutes=60
            )),
            asyncio.create_task(self._run_periodic(
                self._cleanup_database,
                interval_minutes=120
            )),
        ]
    
    async def stop(self):
        """Stop all scheduled tasks"""
        self.running = False
        logger.info("Stopping background scheduler")
        
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
    
    async def _run_periodic(self, func: Callable, interval_minutes: int):
        """
        Run a function periodically.
        
        Args:
            func: Async function to run
            interval_minutes: Interval in minutes
        """
        while self.running:
            try:
                await func()
            except Exception as e:
                logger.error(f"Error in scheduled task {func.__name__}: {e}", exc_info=True)
            
            # Wait for next interval
            await asyncio.sleep(interval_minutes * 60)
    
    async def _cleanup_sessions(self):
        """Clean up inactive sessions"""
        try:
            logger.info("Running session cleanup")
            orchestrator = get_orchestrator_service()
            await orchestrator.cleanup_inactive_sessions(
                inactive_minutes=self.settings.SESSION_EXPIRE_MINUTES
            )
        except Exception as e:
            logger.error(f"Session cleanup error: {e}", exc_info=True)
    
    async def _cleanup_files(self):
        """Clean up old uploaded files"""
        try:
            logger.info("Running file cleanup")
            await cleanup_old_files(
                upload_dir=self.settings.UPLOAD_DIR,
                days_old=7  # Delete files older than 7 days
            )
        except Exception as e:
            logger.error(f"File cleanup error: {e}", exc_info=True)
    
    async def _cleanup_database(self):
        """Clean up expired database records"""
        try:
            logger.info("Running database cleanup")
            db = get_db()
            await db.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Database cleanup error: {e}", exc_info=True)


# Global scheduler instance
scheduler = BackgroundScheduler()


async def start_scheduler():
    """Start the background scheduler"""
    await scheduler.start()


async def stop_scheduler():
    """Stop the background scheduler"""
    await scheduler.stop()