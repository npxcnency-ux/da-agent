# tests/test_code_generator.py

import pytest
from pathlib import Path

from lib.code_generator import CodeGenerator


class TestCodeGenerator:
    """Test code generation for simple aggregations"""

    @pytest.fixture
    def generator(self):
        """Create CodeGenerator instance"""
        templates_dir = Path(__file__).parent.parent / "assets" / "sql_templates"
        return CodeGenerator(templates_dir)

    def test_generate_top_n_query(self, generator):
        """Should generate top N aggregation code"""
        task = {
            "analysis_type": "aggregation",
            "operation": "top_n",
            "data_source": "users.csv",
            "group_by": None,
            "sort_by": "revenue",
            "limit": 10
        }

        code = generator.generate(task)

        assert "import pandas as pd" in code
        assert "read_csv" in code
        assert "sort_values" in code
        assert "head(10)" in code

    def test_generate_groupby_sum(self, generator):
        """Should generate groupby aggregation code"""
        task = {
            "analysis_type": "aggregation",
            "operation": "groupby",
            "data_source": "sales.csv",
            "group_by": "region",
            "agg_column": "revenue",
            "agg_function": "sum"
        }

        code = generator.generate(task)

        assert 'groupby("region")' in code
        assert '["revenue"].sum()' in code

    def test_generate_with_security_validation(self, generator):
        """Should include security validation in generated code"""
        task = {
            "analysis_type": "aggregation",
            "operation": "top_n",
            "data_source": "data.csv",
            "sort_by": "value",
            "limit": 5
        }

        code = generator.generate(task)

        assert "SecureFileAccess" in code
        assert "validate_path" in code
