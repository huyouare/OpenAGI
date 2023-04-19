"""
tools/browse.py

This file contains the web browsing tool used by the agent.

The search tool scrapes the web page and returns the content.
"""

from bs4 import BeautifulSoup
import json
import os
import re
import requests
from core.tool import BaseTool, InputSpec, OutputSpec


def get_text_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}

    # Make a HTTP request to the webpage
    try:
        response = requests.get(url, headers=headers)
    except:
        return ""

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove all script tags and their contents
    for script in soup(["script"]):
        script.decompose()

    # Remove extraneous whitespace from the HTML content
    text = soup.get_text().strip()

    # Clean up the text by removing unnecessary characters and HTML tags
    # Remove multiple spaces and newlines using regular expressions
    text = re.sub('\n+', '\n', text)
    text = re.sub(' +', ' ', text)
    text = re.sub(r'\[[^\]]+\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)

    return text


def create_filename(title):
    # Remove non-alphanumeric characters from the title
    title = re.sub('[^0-9a-zA-Z ]+', '', title)
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    # Convert to lowercase
    filename = title.lower()
    return filename


def process_article(url, title, dir_name='data'):
    # Create directory if not already exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    text = get_text_from_page(url)

    # Create a dictionary representing the JSON object
    data = {
        'title': title,
        'url': url,
        'body': text,
    }
    # Serialize the dictionary to a JSON string
    json_str = json.dumps(data, indent=4)
    # Save the JSON string to a file
    filename = create_filename(title)
    with open(f'{dir_name}/{filename}.json', 'w') as f:
        f.write(json_str)

    return data['body']


class BrowseTool(BaseTool):
    def __init__(self):
        # Set by parse_input
        self.url = None
        self.title = None

    def description(self) -> str:
        return "Scrapes the web page and returns the content."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("url", "The URL of the web page", "string"),
            InputSpec("title", "The title of the web page", "string")
        ]

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("body", "The body of the web page", "string")
        ]

    def parse_input(self, input_str: str):
        # Validate input and throw error if not found
        if "url" not in input_str:
            raise ValueError("Missing url in input")
        if "title" not in input_str:
            raise ValueError("Missing title in input")

        self.url = input_str["url"]
        self.title = input_str["title"]

    def run(self):
        return {
            "body": process_article(self.url, self.title)
        }


if __name__ == '__main__':
    tool = BrowseTool()
    tool.parse_input({
        "url": "https://www.nytimes.com/2021/01/06/us/politics/trump-impeachment.html",
        "title": "Trump Impeached for Second Time, Conviction in Senate Now Unlikely"
    })
    print(tool.run())
