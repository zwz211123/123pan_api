"""
Tests for HTTP request timeout configuration.
"""

import ast
import unittest
from pathlib import Path


class TestRequestTimeouts(unittest.TestCase):
    """Ensure outbound HTTP calls always include a timeout."""

    def test_all_requests_calls_include_timeout(self):
        source_path = Path(__file__).resolve().parents[1] / "api" / "pan_api.py"
        tree = ast.parse(source_path.read_text(), filename=str(source_path))

        calls_without_timeout = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr in {"get", "post"}
                and isinstance(func.value, ast.Name)
                and func.value.id == "requests"
            ):
                continue

            keyword_names = {keyword.arg for keyword in node.keywords}
            if "timeout" not in keyword_names:
                calls_without_timeout.append((func.attr, node.lineno))

        self.assertEqual([], calls_without_timeout)


if __name__ == "__main__":
    unittest.main()
