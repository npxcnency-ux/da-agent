# tests/test_executor.py

import pytest
import tempfile
import shutil
from pathlib import Path

from lib.executor import Executor


class TestExecutor:
    """Test code execution"""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace"""
        workspace = Path(tempfile.mkdtemp(prefix="da_agent_exec_"))
        yield workspace
        shutil.rmtree(workspace)

    @pytest.fixture
    def executor(self, workspace):
        """Create Executor instance"""
        return Executor(workspace)

    def test_execute_simple_code(self, executor, workspace):
        """Should execute Python code and return output"""
        code = '''
print("Hello from executor")
result = 2 + 2
print(f"Result: {result}")
'''

        output = executor.execute(code)

        assert "Hello from executor" in output
        assert "Result: 4" in output

    def test_capture_errors(self, executor, workspace):
        """Should capture execution errors"""
        code = '''
print("Starting...")
x = 1 / 0  # This will raise ZeroDivisionError
print("Never gets here")
'''

        with pytest.raises(Exception) as exc_info:
            executor.execute(code)

        assert "ZeroDivisionError" in str(exc_info.value)

    def test_isolated_execution(self, executor, workspace):
        """Should execute in isolated namespace"""
        code1 = "x = 42"
        code2 = "print(x)"  # Should fail - no shared state

        executor.execute(code1)

        with pytest.raises(Exception):
            executor.execute(code2)
