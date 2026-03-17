# tests/test_code_generator.py

import pytest
from pathlib import Path

from lib.code_generator import CodeGenerator, ValidationError


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

    def test_reject_code_injection_in_column_name(self, generator):
        """Should reject SQL injection attempts in column names"""
        task = {
            "analysis_type": "aggregation",
            "operation": "top_n",
            "data_source": "data.csv",
            "sort_by": '"); import os; os.system("rm -rf /"); #',
            "limit": 10
        }

        with pytest.raises(ValidationError) as exc_info:
            generator.generate(task)

        assert "Invalid column name" in str(exc_info.value)

    def test_reject_invalid_agg_function(self, generator):
        """Should reject invalid aggregation functions"""
        task = {
            "analysis_type": "aggregation",
            "operation": "groupby",
            "data_source": "sales.csv",
            "group_by": "region",
            "agg_column": "revenue",
            "agg_function": "eval"  # Dangerous function
        }

        with pytest.raises(ValidationError) as exc_info:
            generator.generate(task)

        assert "Invalid agg_function" in str(exc_info.value)

    def test_reject_missing_required_parameter(self, generator):
        """Should reject tasks with missing parameters"""
        task = {
            "analysis_type": "aggregation",
            "operation": "top_n",
            "data_source": "data.csv",
            # Missing sort_by and limit
        }

        with pytest.raises(ValidationError) as exc_info:
            generator.generate(task)

        assert "Missing required parameter" in str(exc_info.value)

    def test_reject_unsupported_analysis_type(self, generator):
        """Should reject unsupported analysis types"""
        task = {
            "analysis_type": "machine_learning",
            "data_source": "data.csv"
        }

        with pytest.raises(ValidationError) as exc_info:
            generator.generate(task)

        assert "Invalid analysis_type" in str(exc_info.value)

    def test_reject_invalid_limit_type(self, generator):
        """Should reject non-integer limits"""
        task = {
            "analysis_type": "aggregation",
            "operation": "top_n",
            "data_source": "data.csv",
            "sort_by": "revenue",
            "limit": "10"  # String instead of int
        }

        with pytest.raises(ValidationError) as exc_info:
            generator.generate(task)

        assert "Invalid limit" in str(exc_info.value)

    def test_accept_valid_agg_functions(self, generator):
        """Should accept all valid aggregation functions"""
        valid_functions = ['sum', 'mean', 'count', 'min', 'max', 'std', 'median']

        for func in valid_functions:
            task = {
                "analysis_type": "aggregation",
                "operation": "groupby",
                "data_source": "sales.csv",
                "group_by": "region",
                "agg_column": "revenue",
                "agg_function": func
            }

            code = generator.generate(task)
            assert f'["{task["agg_column"]}"].{func}()' in code

