"""
Tools package — custom tools that the AI agent can invoke.

Each tool is decorated with @tool from LangChain and follows
the ReAct pattern: the agent reasons about when to call it
and interprets the result.
"""

from tools.calculator import calculator
from tools.knowledge_base import knowledge_lookup
from tools.datetime_tool import get_current_datetime

__all__ = ["calculator", "knowledge_lookup", "get_current_datetime"]
