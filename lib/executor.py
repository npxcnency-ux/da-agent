# lib/executor.py

"""
Safe code execution for DA-Agent.

Runs generated Python code in isolated environment.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict


class ExecutionError(Exception):
    """Raised when code execution fails"""
    pass


class Executor:
    """
    Execute generated Python code safely.

    Runs code in subprocess for isolation.
    """

    def __init__(self, workspace: Path):
        """
        Initialize executor.

        Args:
            workspace: Working directory for execution
        """
        self.workspace = Path(workspace)

    def execute(self, code: str, timeout: int = 30) -> str:
        """
        Execute Python code.

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Combined stdout/stderr output

        Raises:
            ExecutionError: If execution fails
        """
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=self.workspace,
            delete=False
        ) as f:
            f.write(code)
            code_file = Path(f.name)

        try:
            # Execute in subprocess using same Python interpreter
            result = subprocess.run(
                [sys.executable, str(code_file)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Check for errors
            if result.returncode != 0:
                raise ExecutionError(
                    f"Execution failed with code {result.returncode}\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            # Return output
            return result.stdout + result.stderr

        finally:
            # Cleanup
            code_file.unlink(missing_ok=True)
