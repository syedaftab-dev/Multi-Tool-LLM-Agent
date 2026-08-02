"""
Calculator Tool — Evaluates mathematical expressions safely.

The agent can invoke this tool to perform arithmetic calculations.
Supports basic operations: +, -, *, /, **, (), and common math functions.
"""

import math
from langchain_core.tools import tool


# Whitelist of safe names for the expression evaluator
_SAFE_GLOBALS = {
    "__builtins__": {},
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "sum": sum,
    "int": int,
    "float": float,
    # Math module functions
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "pi": math.pi,
    "e": math.e,
    "ceil": math.ceil,
    "floor": math.floor,
}


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Use this tool when you need to perform arithmetic calculations.
    Input should be a valid mathematical expression like '2 + 3 * 4'
    or 'sqrt(144)'. Supports: +, -, *, /, **, (), sqrt, sin, cos,
    tan, log, pi, e, abs, round, min, max, pow, ceil, floor.

    Args:
        expression: A mathematical expression string to evaluate.

    Returns:
        The result of the computation as a string, or an error message.
    """
    try:
        # Use eval with restricted globals for safety
        result = eval(expression, _SAFE_GLOBALS, {})
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except SyntaxError:
        return f"Error: Invalid mathematical expression: '{expression}'"
    except Exception as e:
        return f"Error evaluating expression: {e}"
