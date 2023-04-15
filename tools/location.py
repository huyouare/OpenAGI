"""
tools/browse.py

This file provides to provide the user's location to the agent.

The location can either be provided by prompting the user, or by IP address.
"""

import requests
from core.tool import BaseTool, InputSpec, OutputSpec


class UserProvidedLocation(BaseTool):
    def __init__(self):
        self.user_provided_location: str = None

    def description(self) -> str:
        return "Provides the user's location based on the user's input."

    def input_spec(self) -> list[InputSpec]:
        return []

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("location", "The user's location", "string"),
        ]

    def run(self):
        if self.user_provided_location is None:
            self.get_location_from_user()
        return {
            "location": self.user_provided_location,
        }

    def get_location_from_user(self):
        # Prompt the user for the location
        self.user_provided_location = input("Please enter your location: ")

        # TODO: Use an LLM to validate the location

        return self.user_provided_location


class IPGeoLocation(BaseTool):
    def __init__(self):
        self.geo_info: dict = None

    def description(self) -> str:
        return "Provides the user's location based on IP address."

    def input_spec(self) -> list[InputSpec]:
        return []

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("geo_info", "The user's geo information", "dict")
        ]

    def run(self):
        self.get_geo_from_ip()
        return self.geo_info

    def get_geo_from_ip(self):
        # Get the user's IP address
        ip_address = requests.get('https://api.ipify.org').text
        # Get the user's geo information
        self.geo_info = requests.get(
            'https://get.geojs.io/v1/ip/geo/' + ip_address + '.json').json()
        return self.geo_info


if __name__ == "__main__":
    user_location = UserProvidedLocation()
    print(user_location.run())

    ip_location = IPGeoLocation()
    print(ip_location.run())
