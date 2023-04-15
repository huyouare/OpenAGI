"""
tools/search.py

This file contains the search tool used by the agent.

The search tool calls the SERP API for a given query and returns the results with URLs.
"""

from collections import namedtuple
import os
from serpapi import GoogleSearch


SearchResult = namedtuple("SearchResult",
                          ["position", "title", "snippet", "url"])

SERP_API_BASE_URL = "https://serpapi.com/search"

class Search:
    def __init__(self):
        self.api_key = os.environ["SERP_API_KEY"]
        self.base_url = SERP_API_BASE_URL

    def search_query(self, query, num_results=10):
        search = GoogleSearch({
            "q": query, 
            "num": num_results,
            "location": "San Francisco, CA",
            "api_key": self.api_key
        })
        results = search.get_dict()['organic_results']
        search_results = []
        for result in results:
            search_result = SearchResult(
                position=result['position'],
                title=result['title'],
                snippet=result['snippet'],
                url=result['link']
            )
            search_results.append(search_result)
        return search_results


if __name__ == "__main__":
    search_instance = Search()
    results = search_instance.search_query("obama")
    print(results)
