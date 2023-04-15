"""
tools/browse.py

This file contains a tool that provides the agent the current date and time.
"""

import datetime


def get_datetime():
    return datetime.datetime.now()


def get_date_formatted():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_time_formatted():
    return datetime.datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    print("Datetime: ", get_datetime())
    print("Date: ", get_date_formatted())
    print("Time: ", get_time_formatted())
