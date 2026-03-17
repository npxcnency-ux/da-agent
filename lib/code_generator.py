# lib/code_generator.py

"""
Code generation for simple analysis tasks.

Phase 1: Simple aggregations only
Phase 2+: Complex analysis, statistical tests, modeling
"""

from pathlib import Path
from typing import Dict
import jinja2
import re


class ValidationError(Exception):
    """Raised when task validation fails"""
    pass


class CodeGenerator:
    """
    Generate Python code for data analysis tasks.

    Uses Jinja2 templates for different analysis patterns.
    """

    # Allowlist for aggregation functions
    ALLOWED_AGG_FUNCTIONS = {'sum', 'mean', 'count', 'min', 'max', 'std', 'median'}

    # Allowlist for analysis types
    ALLOWED_ANALYSIS_TYPES = {'aggregation'}

    def __init__(self, templates_dir: Path):
        """
        Initialize code generator.

        Args:
            templates_dir: Directory containing .jinja2 templates
        """
        self.templates_dir = Path(templates_dir)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, task: Dict) -> str:
        """
        Generate code for task.

        Args:
            task: Structured task specification

        Returns:
            Python code as string

        Raises:
            ValidationError: If task contains invalid parameters
            ValueError: If analysis type is unsupported
        """
        # Validate task before generation
        self._validate_task(task)

        analysis_type = task.get("analysis_type")

        if analysis_type == "aggregation":
            return self._generate_aggregation(task)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")

    def _validate_task(self, task: Dict) -> None:
        """
        Validate task parameters to prevent injection attacks.

        Args:
            task: Task specification to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate analysis type
        analysis_type = task.get("analysis_type")
        if not analysis_type:
            raise ValidationError("Missing required parameter: analysis_type")
        if analysis_type not in self.ALLOWED_ANALYSIS_TYPES:
            raise ValidationError(f"Invalid analysis_type: {analysis_type}")

        # Validate aggregation-specific parameters
        if analysis_type == "aggregation":
            operation = task.get("operation")
            if not operation:
                raise ValidationError("Missing required parameter: operation")

            # Validate column names (alphanumeric + underscore only)
            if operation == "top_n":
                sort_by = task.get("sort_by")
                if not sort_by:
                    raise ValidationError("Missing required parameter: sort_by")
                self._validate_column_name(sort_by)

                limit = task.get("limit")
                if limit is None:
                    raise ValidationError("Missing required parameter: limit")
                if not isinstance(limit, int) or limit <= 0:
                    raise ValidationError(f"Invalid limit: must be positive integer, got {limit}")

            elif operation == "groupby":
                group_by = task.get("group_by")
                if not group_by:
                    raise ValidationError("Missing required parameter: group_by")
                self._validate_column_name(group_by)

                agg_column = task.get("agg_column")
                if not agg_column:
                    raise ValidationError("Missing required parameter: agg_column")
                self._validate_column_name(agg_column)

                agg_function = task.get("agg_function", "sum")
                if agg_function not in self.ALLOWED_AGG_FUNCTIONS:
                    raise ValidationError(
                        f"Invalid agg_function: {agg_function}. "
                        f"Must be one of: {', '.join(sorted(self.ALLOWED_AGG_FUNCTIONS))}"
                    )

        # Validate data source (basic check)
        data_source = task.get("data_source")
        if not data_source:
            raise ValidationError("Missing required parameter: data_source")

    def _validate_column_name(self, column_name: str) -> None:
        """
        Validate column name to prevent injection attacks.

        Args:
            column_name: Column name to validate

        Raises:
            ValidationError: If column name is invalid
        """
        if not isinstance(column_name, str):
            raise ValidationError(f"Column name must be string, got {type(column_name)}")

        # Allow alphanumeric and underscore only (valid Python identifier pattern)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name):
            raise ValidationError(
                f"Invalid column name: '{column_name}'. "
                "Must contain only letters, numbers, and underscores, and cannot start with a number."
            )

    def _generate_aggregation(self, task: Dict) -> str:
        """Generate code for aggregation task"""
        template = self.env.get_template("simple_aggregation.py.jinja2")

        return template.render(
            data_source=task.get("data_source"),
            operation=task.get("operation"),
            group_by=task.get("group_by"),
            sort_by=task.get("sort_by"),
            limit=task.get("limit"),
            agg_column=task.get("agg_column"),
            agg_function=task.get("agg_function", "sum")
        )
