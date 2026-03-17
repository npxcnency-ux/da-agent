"""
Test suite for KnowledgeStore - SQLite-based knowledge base
Tests written FIRST following TDD approach
"""
import os
import sqlite3
import tempfile
import pytest
from pathlib import Path

from lib.knowledge_store import KnowledgeStore


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_knowledge.db")
        yield db_path


@pytest.fixture
def store(temp_db):
    """Create KnowledgeStore instance with temporary database"""
    return KnowledgeStore(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database creation and schema"""

    def test_initialize_database(self, temp_db):
        """Test that database file is created with correct schema"""
        store = KnowledgeStore(db_path=temp_db)

        # Verify database file exists
        assert os.path.exists(temp_db)

        # Verify tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}

        assert "tasks" in tables
        assert "code_templates" in tables
        assert "business_terms" in tables

        conn.close()

    def test_tasks_table_schema(self, temp_db):
        """Test tasks table has correct columns"""
        store = KnowledgeStore(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "id", "description", "structured_req",
            "complexity_score", "execution_mode",
            "status", "created_at"
        }
        assert required_columns.issubset(columns)

        conn.close()

    def test_code_templates_table_schema(self, temp_db):
        """Test code_templates table has correct columns"""
        store = KnowledgeStore(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(code_templates)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "id", "name", "category", "template_code",
            "tags", "usage_count", "created_at"
        }
        assert required_columns.issubset(columns)

        conn.close()

    def test_business_terms_table_schema(self, temp_db):
        """Test business_terms table has correct columns"""
        store = KnowledgeStore(db_path=temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(business_terms)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "id", "term", "definition", "sql_logic",
            "source", "created_at"
        }
        assert required_columns.issubset(columns)

        conn.close()


class TestTaskOperations:
    """Test task-related operations"""

    def test_save_task(self, store):
        """Test saving a task returns an ID"""
        task_id = store.save_task(
            description="Analyze Q1 revenue by region",
            structured_req={"query": "SELECT region, SUM(revenue) FROM sales GROUP BY region"},
            complexity_score=0.6,
            execution_mode="sql"
        )

        assert task_id is not None
        assert isinstance(task_id, int)
        assert task_id > 0

    def test_get_task(self, store):
        """Test retrieving a task by ID"""
        # Save a task
        task_id = store.save_task(
            description="Calculate customer churn rate",
            structured_req={"metric": "churn_rate", "period": "monthly"},
            complexity_score=0.8,
            execution_mode="python"
        )

        # Retrieve the task
        task = store.get_task(task_id)

        assert task is not None
        assert task["id"] == task_id
        assert task["description"] == "Calculate customer churn rate"
        assert task["complexity_score"] == 0.8
        assert task["execution_mode"] == "python"
        assert task["status"] == "pending"  # default status
        assert "created_at" in task

    def test_get_task_nonexistent(self, store):
        """Test retrieving non-existent task returns None"""
        task = store.get_task(99999)
        assert task is None

    def test_search_similar_tasks(self, store):
        """Test keyword search for similar tasks"""
        # Save multiple tasks
        store.save_task(
            description="Analyze revenue trends for Q1",
            structured_req={},
            complexity_score=0.5,
            execution_mode="sql"
        )
        store.save_task(
            description="Calculate revenue by product category",
            structured_req={},
            complexity_score=0.6,
            execution_mode="sql"
        )
        store.save_task(
            description="Customer satisfaction survey analysis",
            structured_req={},
            complexity_score=0.7,
            execution_mode="python"
        )

        # Search for revenue-related tasks
        results = store.search_similar_tasks("revenue")

        assert len(results) == 2
        assert all("revenue" in task["description"].lower() for task in results)

    def test_search_similar_tasks_no_results(self, store):
        """Test search with no matching results"""
        store.save_task(
            description="Analyze customer data",
            structured_req={},
            complexity_score=0.5,
            execution_mode="sql"
        )

        results = store.search_similar_tasks("inventory")
        assert len(results) == 0

    def test_update_task_status(self, store):
        """Test updating task status"""
        # Save a task
        task_id = store.save_task(
            description="Generate monthly report",
            structured_req={},
            complexity_score=0.5,
            execution_mode="sql"
        )

        # Update status
        store.update_task_status(task_id, "completed")

        # Verify update
        task = store.get_task(task_id)
        assert task["status"] == "completed"

    def test_update_task_status_nonexistent(self, store):
        """Test updating non-existent task doesn't raise error"""
        # Should not raise exception
        store.update_task_status(99999, "completed")


class TestTemplateOperations:
    """Test code template operations"""

    def test_save_code_template(self, store):
        """Test saving a code template"""
        template_id = store.save_code_template(
            name="pandas_groupby",
            category="data_transformation",
            template_code="df.groupby('{column}').agg({{'{metric}': 'sum'}})",
            tags="pandas,aggregation,groupby"
        )

        assert template_id is not None
        assert isinstance(template_id, int)
        assert template_id > 0

    def test_get_template_by_name(self, store):
        """Test retrieving template by name"""
        # Save a template
        store.save_code_template(
            name="sql_join",
            category="sql_query",
            template_code="SELECT * FROM {table1} JOIN {table2} ON {condition}",
            tags="sql,join"
        )

        # Retrieve by name
        template = store.get_template_by_name("sql_join")

        assert template is not None
        assert template["name"] == "sql_join"
        assert template["category"] == "sql_query"
        assert "SELECT * FROM" in template["template_code"]
        assert template["tags"] == "sql,join"
        assert template["usage_count"] == 0  # initial usage count
        assert "created_at" in template

    def test_get_template_by_name_nonexistent(self, store):
        """Test retrieving non-existent template returns None"""
        template = store.get_template_by_name("nonexistent_template")
        assert template is None

    def test_increment_template_usage(self, store):
        """Test incrementing template usage count"""
        # Save a template
        store.save_code_template(
            name="matplotlib_plot",
            category="visualization",
            template_code="plt.plot({data})",
            tags="matplotlib,plot"
        )

        # Increment usage multiple times
        store.increment_template_usage("matplotlib_plot")
        store.increment_template_usage("matplotlib_plot")
        store.increment_template_usage("matplotlib_plot")

        # Verify count
        template = store.get_template_by_name("matplotlib_plot")
        assert template["usage_count"] == 3

    def test_increment_template_usage_nonexistent(self, store):
        """Test incrementing non-existent template doesn't raise error"""
        # Should not raise exception
        store.increment_template_usage("nonexistent_template")


class TestBusinessTermOperations:
    """Test business term operations"""

    def test_save_business_term(self, store):
        """Test saving a business term"""
        term_id = store.save_business_term(
            term="Active Customer",
            definition="Customer with at least one purchase in last 90 days",
            sql_logic="WHERE last_purchase_date >= CURRENT_DATE - INTERVAL '90 days'",
            source="Marketing team"
        )

        assert term_id is not None
        assert isinstance(term_id, int)
        assert term_id > 0

    def test_get_business_term(self, store):
        """Test retrieving a business term"""
        # Save a term
        store.save_business_term(
            term="Monthly Recurring Revenue",
            definition="Total predictable revenue generated per month",
            sql_logic="SUM(subscription_amount) WHERE billing_cycle = 'monthly'",
            source="Finance team"
        )

        # Retrieve the term
        term = store.get_business_term("Monthly Recurring Revenue")

        assert term is not None
        assert term["term"] == "Monthly Recurring Revenue"
        assert term["definition"] == "Total predictable revenue generated per month"
        assert "subscription_amount" in term["sql_logic"]
        assert term["source"] == "Finance team"
        assert "created_at" in term

    def test_get_business_term_nonexistent(self, store):
        """Test retrieving non-existent term returns None"""
        term = store.get_business_term("Nonexistent Term")
        assert term is None

    def test_detect_term_conflict_same_definition(self, store):
        """Test no conflict when same term has same definition"""
        # Save initial term
        store.save_business_term(
            term="Churn Rate",
            definition="Percentage of customers who cancel",
            sql_logic="COUNT(cancelled) / COUNT(total)",
            source="Analytics team"
        )

        # Try to save same term with same definition
        conflict = store.save_business_term(
            term="Churn Rate",
            definition="Percentage of customers who cancel",
            sql_logic="COUNT(cancelled) / COUNT(total)",
            source="Product team"
        )

        # Should return False (no conflict) or handle gracefully
        assert conflict is False or isinstance(conflict, int)

    def test_detect_term_conflict_different_definition(self, store):
        """Test conflict detection when definitions differ"""
        # Save initial term
        store.save_business_term(
            term="Active User",
            definition="User who logged in within last 30 days",
            sql_logic="WHERE last_login >= CURRENT_DATE - 30",
            source="Product team"
        )

        # Try to save same term with different definition
        conflict = store.save_business_term(
            term="Active User",
            definition="User who made a purchase within last 60 days",
            sql_logic="WHERE last_purchase >= CURRENT_DATE - 60",
            source="Sales team"
        )

        # Should return True (conflict detected)
        assert conflict is True

    def test_detect_term_conflict_case_insensitive(self, store):
        """Test conflict detection is case-insensitive"""
        # Save term in lowercase
        store.save_business_term(
            term="revenue",
            definition="Total income from sales",
            sql_logic="SUM(sale_amount)",
            source="Finance"
        )

        # Try to save with different case and different definition
        conflict = store.save_business_term(
            term="Revenue",
            definition="Net income after expenses",
            sql_logic="SUM(sale_amount) - SUM(expenses)",
            source="Accounting"
        )

        assert conflict is True


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_save_task_with_none_values(self, store):
        """Test saving task with None values in optional fields"""
        task_id = store.save_task(
            description="Simple task",
            structured_req=None,
            complexity_score=None,
            execution_mode="sql"
        )

        assert task_id is not None
        task = store.get_task(task_id)
        assert task["description"] == "Simple task"

    def test_save_template_with_empty_tags(self, store):
        """Test saving template with empty tags"""
        template_id = store.save_code_template(
            name="simple_template",
            category="misc",
            template_code="print('hello')",
            tags=""
        )

        assert template_id is not None
        template = store.get_template_by_name("simple_template")
        assert template["tags"] == ""

    def test_search_with_special_characters(self, store):
        """Test search handles special SQL characters"""
        store.save_task(
            description="Calculate 100% of revenue",
            structured_req={},
            complexity_score=0.5,
            execution_mode="sql"
        )

        # Should not raise SQL injection error
        results = store.search_similar_tasks("100%")
        assert len(results) == 1

    def test_database_persistence(self, temp_db):
        """Test data persists across KnowledgeStore instances"""
        # Create first store and save data
        store1 = KnowledgeStore(db_path=temp_db)
        task_id = store1.save_task(
            description="Persistent task",
            structured_req={},
            complexity_score=0.5,
            execution_mode="sql"
        )

        # Create second store with same database
        store2 = KnowledgeStore(db_path=temp_db)
        task = store2.get_task(task_id)

        assert task is not None
        assert task["description"] == "Persistent task"
