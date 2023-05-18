from datetime import datetime

from langchain.tools import Tool
from langchain.tools.base import StructuredTool

DATE_FORMAT = "%Y-%m-%d"


def today_date(unused):
    return datetime.now().strftime("%c")


def day_of_week(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, DATE_FORMAT)
        return dt.strftime("%A")
    except ValueError:
        return "input must be a date in format YYYY-MM-DD"


today_date_tool = Tool.from_function(today_date, name="current_date",
                                     description="Use it when you need to know the current date. This tool has no arguments. "
                                                 "You can also use this tool for getting tomorrow's date by get the current date "
                                                 "and adding 1 day")

day_of_week_tool = Tool.from_function(day_of_week,
                                      name="day of the week",
                                      description="use to get the day of the week, input is a date using format YYYY-MM-DD"
                                      )
