"""
Database connection and operations.

Supports MongoDB for conversation storage and session management.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self, database_url: str, database_name: str):
        """
        Connect to MongoDB.
        
        Args:
            database_url: MongoDB connection string
            database_name: Database name
        """
        try:
            self.client = AsyncIOMotorClient(database_url)
            self.db = self.client[database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB: {database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for performance"""
        # Conversations collection
        await self.db.conversations.create_index("session_id")
        await self.db.conversations.create_index("patient_id")
        await self.db.conversations.create_index("created_at")
        
        # Sessions collection
        await self.db.sessions.create_index("session_id", unique=True)
        await self.db.sessions.create_index("patient_id")
        await self.db.sessions.create_index("expires_at")
        
        logger.info("Database indexes created")
    
    # Conversation operations
    
    async def save_conversation(
        self,
        session_id: str,
        patient_id: str,
        message: str,
        response: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save a conversation exchange.
        
        Args:
            session_id: Session identifier
            patient_id: Patient identifier
            message: User message
            response: Agent response
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        conversation = {
            "session_id": session_id,
            "patient_id": patient_id,
            "message": message,
            "response": response,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
        }
        
        result = await self.db.conversations.insert_one(conversation)
        return str(result.inserted_id)
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
            
        Returns:
            List of conversation exchanges
        """
        cursor = self.db.conversations.find(
            {"session_id": session_id}
        ).sort("created_at", -1).limit(limit)
        
        conversations = await cursor.to_list(length=limit)
        
        # Reverse to get chronological order
        conversations.reverse()
        
        return conversations
    
    async def get_patient_conversations(
        self,
        patient_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a patient.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of conversations
            
        Returns:
            List of conversations
        """
        cursor = self.db.conversations.find(
            {"patient_id": patient_id}
        ).sort("created_at", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    # Session operations
    
    async def create_session(
        self,
        session_id: str,
        patient_id: str,
        expires_in_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            session_id: Session identifier
            patient_id: Patient identifier
            expires_in_minutes: Session expiry time
            
        Returns:
            Session document
        """
        session = {
            "session_id": session_id,
            "patient_id": patient_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "active": True,
        }
        
        await self.db.sessions.insert_one(session)
        return session
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session document or None
        """
        session = await self.db.sessions.find_one({"session_id": session_id})
        
        if session and session.get("expires_at") < datetime.utcnow():
            # Session expired
            await self.invalidate_session(session_id)
            return None
        
        return session
    
    async def invalidate_session(self, session_id: str):
        """
        Invalidate a session.
        
        Args:
            session_id: Session identifier
        """
        await self.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"active": False}}
        )
    
    async def extend_session(self, session_id: str, minutes: int = 30):
        """
        Extend session expiry time.
        
        Args:
            session_id: Session identifier
            minutes: Additional minutes
        """
        await self.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"expires_at": datetime.utcnow() + timedelta(minutes=minutes)}}
        )
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        result = await self.db.sessions.delete_many(
            {"expires_at": {"$lt": datetime.utcnow()}}
        )
        logger.info(f"Cleaned up {result.deleted_count} expired sessions")


# Global database instance
db = Database()


async def init_db(settings):
    """Initialize database connection"""
    await db.connect(settings.DATABASE_URL, settings.DATABASE_NAME)


async def close_db():
    """Close database connection"""
    await db.disconnect()


def get_db() -> Database:
    """
    Dependency for getting database instance.
    
    Returns:
        Database instance
    """
    return db