"""
tools/browse.py

This file contains a tool that provides the agent the current date and time.
"""

import datetime
from core.tool import BaseTool, InputSpec, OutputSpec


def get_datetime():
    return datetime.datetime.now()


def get_date_formatted():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_time_formatted():
    return datetime.datetime.now().strftime("%H:%M:%S")


class DatetimeTool(BaseTool):
    def description(self) -> str:
        return "Provides the current date and time."

    def input_spec(self) -> list[InputSpec]:
        return []

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("datetime", "The current date and time", "datetime"),
            OutputSpec("date", "The current date", "string"),
            OutputSpec("time", "The current time", "string")
        ]

    def run(self):
        return {
            "datetime": get_datetime(),
            "date": get_date_formatted(),
            "time": get_time_formatted()
        }


if __name__ == "__main__":
    tool = DatetimeTool()
    print(tool.run())
