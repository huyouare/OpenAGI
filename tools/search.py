"""
tools/search.py

This file contains the search tool used by the agent.

The search tool calls the SERP API for a given query and returns the results with URLs.
"""

from collections import namedtuple
import os
from serpapi import GoogleSearch
from core.tool import BaseTool, InputSpec, OutputSpec


SearchResult = namedtuple("SearchResult",
                          ["position", "title", "snippet", "url"])

SERP_API_BASE_URL = "https://serpapi.com/search"


class SearchTool(BaseTool):
    def __init__(self):
        self.api_key = os.environ["SERP_API_KEY"]
        self.base_url = SERP_API_BASE_URL
        
        # Variables set by parse_input
        self.query = None
        self.num_results = None

    def description(self) -> str:
        return "Searches the web for a query and returns the results."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("query", "The query to search for", "string"),
            InputSpec("num_results", "The number of results to return", "int")
        ]

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("search_results", "The search results", "list")
        ]
    
    def parse_input(self, input_str: dict):
        # Validate input and throw error if not found
        if "query" not in input_str:
            raise ValueError("Missing query in input")
        if "num_results" not in input_str:
            raise ValueError("Missing num_results in input")

        self.query = input_str["query"]
        self.num_results = input_str["num_results"]

    def run(self):
        return {
            "search_results": self.search_query(self.query, self.num_results)
        }

    def search_query(self, query, num_results=10):
        search = GoogleSearch({
            "q": query,
            "num": num_results,
            "location": "San Francisco, CA",
            "api_key": self.api_key
        })
        results = search.get_dict()
        results = results['organic_results'] if 'organic_results' in results else []
        search_results = []
        for result in results:
            search_result = SearchResult(
                position=result['position'],
                title=result['title'],
                snippet=result['snippet'] if 'snippet' in result else "",
                url=result['link']
            )
            search_results.append(search_result)
        return search_results


if __name__ == "__main__":
    tool = SearchTool()
    tool.parse_input({
        "query": "python",
        "num_results": 10
    })
    print(tool.run())
