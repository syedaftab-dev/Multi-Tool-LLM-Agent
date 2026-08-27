"""
Unit tests for agent tools.

Run with: python -m pytest tests/test_tools.py -v
"""

from tools.calculator import calculator
from tools.knowledge_base import knowledge_lookup
from tools.datetime_tool import get_current_datetime


class TestCalculatorTool:
    """Tests for the calculator tool."""

    def test_basic_addition(self):
        result = calculator.invoke({"expression": "2 + 3"})
        assert "5" in result

    def test_multiplication(self):
        result = calculator.invoke({"expression": "7 * 8"})
        assert "56" in result

    def test_complex_expression(self):
        result = calculator.invoke({"expression": "(10 + 5) * 3 - 2"})
        assert "43" in result

    def test_sqrt_function(self):
        result = calculator.invoke({"expression": "sqrt(144)"})
        assert "12" in result

    def test_division_by_zero(self):
        result = calculator.invoke({"expression": "1 / 0"})
        assert "Error" in result

    def test_invalid_expression(self):
        result = calculator.invoke({"expression": "not a math expression +-+-"})
        assert "Error" in result

    def test_power(self):
        result = calculator.invoke({"expression": "2 ** 10"})
        assert "1024" in result

    def test_pi(self):
        result = calculator.invoke({"expression": "pi"})
        assert "3.14" in result


class TestKnowledgeBaseTool:
    """Tests for the knowledge base lookup tool."""

    def test_exact_match(self):
        result = knowledge_lookup.invoke({"topic": "python"})
        assert "Python" in result
        assert "programming language" in result

    def test_case_insensitive(self):
        result = knowledge_lookup.invoke({"topic": "LANGCHAIN"})
        assert "LangChain" in result or "Langchain" in result

    def test_not_found(self):
        result = knowledge_lookup.invoke({"topic": "quantum_computing_xyz"})
        assert "not found" in result.lower()

    def test_partial_match(self):
        result = knowledge_lookup.invoke({"topic": "lang"})
        # Should find langchain and/or langgraph
        assert "lang" in result.lower()


class TestDateTimeTool:
    """Tests for the datetime tool."""

    def test_full_format(self):
        result = get_current_datetime.invoke({"format": "full"})
        assert "Current date and time" in result

    def test_date_only(self):
        result = get_current_datetime.invoke({"format": "date"})
        assert "Current date" in result

    def test_time_only(self):
        result = get_current_datetime.invoke({"format": "time"})
        assert "Current time" in result

    def test_day_only(self):
        result = get_current_datetime.invoke({"format": "day"})
        assert "Today is" in result
