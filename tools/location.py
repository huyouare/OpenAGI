"""
tools/browse.py

This file provides to provide the user's location to the agent.

The location can either be provided by prompting the user, or by IP address.
"""

import requests


class Location():
    def __init__(self):
        self.user_provided_location: str = None
        self.geo_info: dict = None

    def get_geo_from_ip(self):
        # Get the user's IP address
        ip_address = requests.get('https://api.ipify.org').text
        # Get the user's geo information
        self.geo_info = requests.get(
            'https://get.geojs.io/v1/ip/geo/' + ip_address + '.json').json()
        return self.geo_info

    def get_location_from_user(self):
        # Prompt the user for the location
        self.user_provided_location = input("Please enter your location: ")

        # TODO: Use an LLM to validate the location

        return self.user_provided_location


if __name__ == "__main__":
    location = Location()
    location.get_location_from_user()
    print(location.geo_info)
    location.get_geo_from_ip()
    print(location.geo_info)
