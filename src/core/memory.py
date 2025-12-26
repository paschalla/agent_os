"""
andy-os Persistent Memory

SQLite-based conversation storage for persistent context.
"""

import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self, db_path: str = None):
        if db_path is None:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".andy-os")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "memory.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    summary TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            conn.commit()
    
    def create_conversation(self) -> int:
        """Create a new conversation and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO conversations DEFAULT VALUES")
            conn.commit()
            return cursor.lastrowid
    
    def save_message(self, conversation_id: int, role: str, content: str, metadata: Dict = None):
        """Save a message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, json.dumps(metadata) if metadata else None)
            )
            conn.commit()
    
    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> List[Dict]:
        """Get messages from a specific conversation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT role, content, metadata, created_at 
                   FROM messages 
                   WHERE conversation_id = ? 
                   ORDER BY created_at DESC 
                   LIMIT ?""",
                (conversation_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        """Get the most recent messages across all conversations."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT role, content, created_at 
                   FROM messages 
                   ORDER BY created_at DESC 
                   LIMIT ?""",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def get_or_create_conversation(self, session_id: Optional[str] = None) -> int:
        """Get the most recent conversation or create a new one."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if there's a recent conversation (within last hour)
            cursor = conn.execute(
                """SELECT id FROM conversations 
                   WHERE created_at > datetime('now', '-1 hour')
                   ORDER BY created_at DESC LIMIT 1"""
            )
            row = cursor.fetchone()
            if row:
                return row[0]
            return self.create_conversation()


# Global instance
memory = MemoryStore()
