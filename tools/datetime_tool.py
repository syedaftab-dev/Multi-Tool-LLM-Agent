"""
DateTime Tool — Returns the current date, time, and timezone info.

Useful for time-aware conversations where the agent needs to know
the current date or time.
"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_datetime(format: str = "full") -> str:
    """Get the current date and time.

    Use this tool when someone asks about the current date, time,
    day of the week, or anything time-related.

    Args:
        format: One of 'full', 'date', 'time', or 'day'.
                - 'full'  → '2024-03-15 14:30:45 (Friday)'
                - 'date'  → '2024-03-15'
                - 'time'  → '14:30:45'
                - 'day'   → 'Friday'

    Returns:
        A formatted date/time string.
    """
    now = datetime.now()

    match format.strip().lower():
        case "date":
            return f"Current date: {now.strftime('%Y-%m-%d')}"
        case "time":
            return f"Current time: {now.strftime('%H:%M:%S')}"
        case "day":
            return f"Today is: {now.strftime('%A')}"
        case _:
            return (
                f"Current date and time: "
                f"{now.strftime('%Y-%m-%d %H:%M:%S')} "
                f"({now.strftime('%A')})"
            )
