"""
tools/search.py

This file contains the search tool used by the agent.

The search tool calls the SERP API for a given query and returns the results with URLs.
"""

from collections import namedtuple
import os
from serpapi import GoogleSearch
from core.tool import BaseTool, InputSpec, OutputSpec
import multiprocessing
from itertools import repeat


SearchResult = namedtuple("SearchResult",
                          ["position", "title", "snippet", "url"])

SERP_API_BASE_URL = "https://serpapi.com/search"


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
from models import llm

MAX_CHUNKS_PER_PAGE = 5

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


def process_article(args, dir_name='data'):
    search_result, query, objective = args
    url = search_result.url
    title = search_result.title

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

    # # For now, simply truncate the page up to 4000 characters.
    # body = data['body'][:4000]

    # Iterate through the body and and call summarize on chunks of 4000 characters.
    body = data['body']
    chunks = [body[i:i+4000] for i in range(0, len(body), 4000)]
    summary = ""
    for chunk in chunks:
        summary += summarize_qa(chunk, query, objective) + "\n"

    return summary


def summarize_qa(text, query, objective, num_sentences=5):
    # Use llm to get the answer to the query based on the text.
    model = llm.LLM(model='gpt-3.5-turbo', max_tokens=200)
    prompt = f"""
Using the following text and query, provide only output that helps the user answer the query or meet the objective.
You may use up to {num_sentences} sentences in your output.
DO NOT MAKE UP ANY INFORMATION. ONLY USE INFORMATION FROM THE TEXT.

Text:
```
{text}
```

Query: {query}
Objective: {objective}
    """
    print("Summarize prompt: ", prompt, "\n")
    answer = model.generate_chat_completion(prompt)
    return answer


class SearchBrowseTool(BaseTool):
    def __init__(self):
        self.api_key = os.environ["SERP_API_KEY"]
        self.base_url = SERP_API_BASE_URL
        
        # Variables set by parse_input
        self.query = None
        self.num_results = None
        self.objective = None

    def description(self) -> str:
        return "Searches the web for a query and returns the results."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("query", "The query to search for", "string"),
            InputSpec("num_results", "The number of results to return", "int"),
            InputSpec("objective", "The user's objective", "string")
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
        self.objective = input_str["objective"]

    def run(self):
        search_results = self.search_query(self.query, self.num_results)

        # Fork processes to call the browse tool on each URL
        # Define the number of processes to use
        num_processes = 5
        # Create a pool of processes
        pool = multiprocessing.Pool(processes=num_processes)
        # Map the function to the list of articles using the pool of processes
        results = pool.imap_unordered(process_article, zip(search_results, repeat(self.query), repeat(self.objective)))

        # Collect the output in a list
        output = list(results)

        # Close the pool of processes
        pool.close()

        # Print the output
        print(output)

        # Summarize the output
        summary = summarize_qa("\n".join(output), self.query, self.objective)

        return {
            "search_results": summary
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
    tool = SearchBrowseTool()
    tool.parse_input({
        "query": "python",
        "num_results": 5,
        "objective": "Find the latest version of Python."
    })
    print(tool.run())

# if __name__ == '__main__':
#     tool = BrowseTool()
#     tool.parse_input({
#         "url": "https://www.nytimes.com/2021/01/06/us/politics/trump-impeachment.html",
#         "title": "Trump Impeached for Second Time, Conviction in Senate Now Unlikely"
#     })
#     print(tool.run())