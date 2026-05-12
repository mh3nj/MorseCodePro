"""
Translation History Database - Thread-safe version
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class HistoryDB:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "history.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.local = threading.local()
        self._init_tables()
    
    def _get_connection(self):
        """Get thread-local connection"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def _init_tables(self):
        """Initialize database tables"""
        conn = self._get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                input_text TEXT,
                output_text TEXT,
                input_type TEXT,
                language TEXT
            )
        ''')
        conn.commit()
    
    def add(self, input_text: str, output_text: str, input_type: str, language: str):
        """Add translation to history (thread-safe)"""
        try:
            conn = self._get_connection()
            conn.execute(
                'INSERT INTO translations (timestamp, input_text, output_text, input_type, language) VALUES (?, ?, ?, ?, ?)',
                (datetime.now().isoformat(), input_text[:200], output_text[:200], input_type, language)
            )
            conn.commit()
        except Exception as e:
            print(f"History add error: {e}")
    
    def get_all(self, limit: int = 50) -> List[Dict]:
        """Get translation history (thread-safe)"""
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                'SELECT * FROM translations ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"History get error: {e}")
            return []
    
    def clear(self):
        """Clear all history (thread-safe)"""
        try:
            conn = self._get_connection()
            conn.execute('DELETE FROM translations')
            conn.commit()
        except Exception as e:
            print(f"History clear error: {e}")
    
    def close(self):
        """Close all connections"""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
