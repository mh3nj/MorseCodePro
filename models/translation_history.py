import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class TranslationHistory:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    input_text TEXT,
                    output_text TEXT,
                    input_type TEXT,  -- 'text' or 'morse'
                    language TEXT,
                    confidence_score REAL,
                    metadata TEXT  -- JSON for additional data
                )
            ''')
            
            # Create index for faster queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON translations(timestamp)')
    
    def add_translation(self, input_text: str, output_text: str, 
                       input_type: str, language: str, 
                       confidence_score: float = None, metadata: Dict = None):
        """Add a new translation to history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO translations 
                (input_text, output_text, input_type, language, confidence_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                input_text, output_text, input_type, language,
                confidence_score, json.dumps(metadata) if metadata else None
            ))
    
    def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get translation history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM translations 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            results = []
            for row in cursor:
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                results.append(result)
            
            return results
    
    def search_history(self, query: str) -> List[Dict]:
        """Search history by input or output text"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM translations 
                WHERE input_text LIKE ? OR output_text LIKE ?
                ORDER BY timestamp DESC
            ''', (f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor]
    
    def delete_translation(self, translation_id: int):
        """Delete a translation from history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM translations WHERE id = ?', (translation_id,))
    
    def clear_history(self):
        """Clear all translation history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM translations')
    
    def get_stats(self) -> Dict:
        """Get history statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT language) as languages,
                    AVG(confidence_score) as avg_confidence
                FROM translations
            ''')
            row = cursor.fetchone()
            
            return {
                'total_translations': row[0],
                'languages_used': row[1],
                'avg_confidence': round(row[2], 2) if row[2] else 0
            }