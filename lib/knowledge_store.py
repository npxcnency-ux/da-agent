"""
KnowledgeStore - SQLite-based knowledge base for DA-Agent

Stores:
- Tasks: Historical analysis tasks with metadata
- Code Templates: Reusable code snippets with usage tracking
- Business Terms: Terminology with conflict detection
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class KnowledgeStore:
    """SQLite-based knowledge base for storing tasks, templates, and business terms"""

    def __init__(self, db_path: str = "knowledge.db"):
        """
        Initialize KnowledgeStore with SQLite database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                structured_req TEXT,
                complexity_score REAL,
                execution_mode TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)

        # Create code_templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                template_code TEXT NOT NULL,
                tags TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Create business_terms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL,
                definition TEXT NOT NULL,
                sql_logic TEXT,
                source TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Create index for case-insensitive term lookup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_business_terms_lower_term
            ON business_terms (LOWER(term))
        """)

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with Row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Task Operations

    def save_task(
        self,
        description: str,
        structured_req: Optional[Dict[str, Any]],
        complexity_score: Optional[float],
        execution_mode: str
    ) -> int:
        """
        Save analysis task to database

        Args:
            description: Task description
            structured_req: Structured requirement (dict)
            complexity_score: Complexity score (0-1)
            execution_mode: Execution mode (sql/python/hybrid)

        Returns:
            Task ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Convert structured_req to JSON string
        structured_req_json = json.dumps(structured_req) if structured_req else None

        cursor.execute("""
            INSERT INTO tasks (description, structured_req, complexity_score, execution_mode, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            description,
            structured_req_json,
            complexity_score,
            execution_mode,
            datetime.utcnow().isoformat()
        ))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve task by ID

        Args:
            task_id: Task ID

        Returns:
            Task dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        # Convert to dictionary
        task = dict(row)

        # Parse structured_req JSON
        if task["structured_req"]:
            task["structured_req"] = json.loads(task["structured_req"])

        return task

    def search_similar_tasks(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for tasks containing keyword (LIKE-based search)

        Args:
            keyword: Search keyword

        Returns:
            List of matching tasks
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use LIKE for simple keyword search
        # Escape special SQL characters
        keyword_escaped = keyword.replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{keyword_escaped}%"

        cursor.execute(
            "SELECT * FROM tasks WHERE description LIKE ? ESCAPE '\\'",
            (search_pattern,)
        )
        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        tasks = []
        for row in rows:
            task = dict(row)
            if task["structured_req"]:
                task["structured_req"] = json.loads(task["structured_req"])
            tasks.append(task)

        return tasks

    def update_task_status(self, task_id: int, status: str) -> None:
        """
        Update task status

        Args:
            task_id: Task ID
            status: New status (pending/in_progress/completed)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )

        conn.commit()
        conn.close()

    # Template Operations

    def save_code_template(
        self,
        name: str,
        category: str,
        template_code: str,
        tags: str
    ) -> int:
        """
        Save code template to database

        Args:
            name: Template name (unique identifier)
            category: Template category
            template_code: Template code with placeholders
            tags: Comma-separated tags

        Returns:
            Template ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO code_templates (name, category, template_code, tags, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            category,
            template_code,
            tags,
            datetime.utcnow().isoformat()
        ))

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return template_id

    def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve code template by name

        Args:
            name: Template name

        Returns:
            Template dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM code_templates WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return dict(row)

    def increment_template_usage(self, name: str) -> None:
        """
        Increment template usage count

        Args:
            name: Template name
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE code_templates SET usage_count = usage_count + 1 WHERE name = ?",
            (name,)
        )

        conn.commit()
        conn.close()

    # Business Term Operations

    def save_business_term(
        self,
        term: str,
        definition: str,
        sql_logic: str,
        source: str
    ) -> Union[int, bool]:
        """
        Save business term to database with conflict detection

        Args:
            term: Business term name
            definition: Term definition
            sql_logic: SQL logic for the term
            source: Source of the definition

        Returns:
            - int: Term ID if saved successfully
            - True: If conflict detected (term exists with different definition)
            - False: If term exists with same definition (no conflict)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check for existing term (case-insensitive)
        cursor.execute(
            "SELECT * FROM business_terms WHERE LOWER(term) = LOWER(?)",
            (term,)
        )
        existing = cursor.fetchone()

        if existing:
            # Term already exists - check if definitions match
            existing_dict = dict(existing)

            # Normalize whitespace for comparison
            existing_def = " ".join(existing_dict["definition"].split())
            new_def = " ".join(definition.split())

            if existing_def == new_def:
                # Same definition - no conflict
                conn.close()
                return False
            else:
                # Different definition - conflict detected
                conn.close()
                return True

        # No existing term - save new term
        cursor.execute("""
            INSERT INTO business_terms (term, definition, sql_logic, source, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            term,
            definition,
            sql_logic,
            source,
            datetime.utcnow().isoformat()
        ))

        term_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return term_id

    def get_business_term(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve business term by name (case-insensitive)

        Args:
            term: Business term name

        Returns:
            Term dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM business_terms WHERE LOWER(term) = LOWER(?)",
            (term,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return dict(row)
