import json
import logging
from datetime import date
from pathlib import Path

from livekit.agents import RunContext, function_tool

from utils.json_logger import json_logger, Timer

logger = logging.getLogger(__name__)


_OPENING_HOURS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "opening_hours.json"
with _OPENING_HOURS_PATH.open(encoding="utf-8") as f:
    _OPENING_HOURS = json.load(f)

# Niedersachsen holidays for 2026
HOLIDAYS_2026 = {
    "2026-01-01": "Neujahr",
    "2026-04-03": "Karfreitag",
    "2026-04-06": "Ostermontag",
    "2026-05-01": "Tag der Arbeit",
    "2026-05-14": "Christi Himmelfahrt",
    "2026-05-25": "Pfingstmontag",
    "2026-10-03": "Tag der Deutschen Einheit",
    "2026-10-31": "Reformationstag",
    "2026-12-25": "Erster Weihnachtstag",
    "2026-12-26": "Zweiter Weihnachtstag",
}


@function_tool()
async def getOpeningHours(context: RunContext) -> str:
    """
    Get opening hours for ALL city departments with current date and holiday information.

    Returns complete opening hours data as JSON including today's date and holidays.
    """
    logger.info("Tool call: getOpeningHours()")

    # Time the entire tool call
    with Timer() as timer:
        # Tell user we're looking up hours (improves UX)
        await context.session.say("Einen Moment, ich suche die Informationen für Sie heraus.")

        today = date.today()
        today_str = today.isoformat()
        weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

        # Return all data as JSON
        response = {
            "current_date": today_str,
            "current_weekday": weekday_names[today.weekday()],
            "is_holiday": today_str in HOLIDAYS_2026,
            "holiday_name": HOLIDAYS_2026.get(today_str),
            "holidays_2026": HOLIDAYS_2026,
            "opening_hours": _OPENING_HOURS,
        }

        result = json.dumps(response, ensure_ascii=False, indent=2)

    # Log tool call
    json_logger.log_tool_call(
        tool="getOpeningHours",
        duration_ms=timer.duration_ms
    )

    return result
