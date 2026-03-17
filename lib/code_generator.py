# lib/code_generator.py

"""
Code generation for simple analysis tasks.

Phase 1: Simple aggregations only
Phase 2+: Complex analysis, statistical tests, modeling
"""

from pathlib import Path
from typing import Dict
import jinja2


class CodeGenerator:
    """
    Generate Python code for data analysis tasks.

    Uses Jinja2 templates for different analysis patterns.
    """

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
        """
        analysis_type = task.get("analysis_type")

        if analysis_type == "aggregation":
            return self._generate_aggregation(task)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")

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
