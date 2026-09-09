import sqlite3
import json
import os

class HistoryDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            from config import DATABASE_PATH
            db_path = DATABASE_PATH
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize tables for projects and audit records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seo_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    input_type TEXT NOT NULL,
                    target_keyword TEXT,
                    seo_score REAL NOT NULL,
                    word_count INTEGER,
                    meta_title TEXT,
                    meta_description TEXT,
                    search_intent TEXT,
                    raw_data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_analysis(self, project_name: str, input_type: str, target_keyword: str, seo_score: float, word_count: int, meta_title: str, meta_description: str, search_intent: str, full_report_data: dict) -> int:
        """Saves analysis results to SQLite database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO seo_projects (
                    project_name, input_type, target_keyword, seo_score,
                    word_count, meta_title, meta_description, search_intent, raw_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_name,
                input_type,
                target_keyword,
                seo_score,
                word_count,
                meta_title,
                meta_description,
                search_intent,
                json.dumps(full_report_data, ensure_ascii=False)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_projects(self):
        """Retrieves list of all saved projects summarized."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, project_name, input_type, target_keyword, seo_score, word_count, search_intent, created_at
                FROM seo_projects
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_project_by_id(self, project_id: int):
        """Retrieves a specific project record by ID."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM seo_projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['raw_data'] = json.loads(data['raw_data_json'])
                return data
            return None

    def delete_project(self, project_id: int) -> bool:
        """Deletes a project record from history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM seo_projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0
