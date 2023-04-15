"""
tools/search.py

This file contains the summarization tool used by the agent.
"""


import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import openai

summarize_prompt = """
You are an expert summarizer. Your goal is to summarize the user's content as truthfully and concisely as possible.
DO NOT HALLUCINATE ANY FACTS.

You will provide a 1-paragraph summary up to 100 words, followed by a list 3-5 bullet points for the most important facts and takeaways of the article.

The user will provide a title and URL for the page, followed by the raw text of the entire webpage.
Only consider text that sounds like it is from the main article and author of the page.
The main article will be a blog post or a news article, written in paragraph form.
You must ignore any extraneous text such as as headers, commands and ads.
If the entire text seems to be extraneous (headers, comments, ads, etc.) then output only an empty string.

Output format (unless empty):
```
<1-paragraph summary>

Key takeaways:
* <bullet point 1>
* <bullet point 2>
* <bullet point 3>
```

Current date: 2023-04-14
"""

reduce_prompt = """
You are an expert summarizer. Your goal is to summarize existing summaries as truthfully and concisely as possible.
DO NOT HALLUCINATE ANY FACTS.

The user will provide a title and URL for the page, followed by generated summaries of successive chunks of the raw webpage.
Give more weight to the first existing summary, and give less weight to any summaries that are from comments or opinion.
Given multiple summaries and key takeaways, merge these into a 1-paragraph summary up to 100 words, followed by a list of up to 3-5 bullet points for the most important facts and takeaways of the article.
If none of the summaries seem to be related to the title, then output text along the lines of "no summary available".

Output format (if summary available):
```
<1-paragraph summary>

Key takeaways:
* <bullet point 1>
* <bullet point 2>
* <bullet point 3>
```

Current date: 2023-04-14
"""


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_summary(title, url, text, prompt=summarize_prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": f"Title: {title}"},
                  {"role": "user", "content": f"URL: {url}"},
                  {"role": "user", "content": f"Raw Text: ```{text}```"},
                  ]
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def reduce_summary(title, url, text):
    return get_summary(title, url, text, prompt=reduce_prompt)


def get_summary_recursive(title, url, text):
    print("Calling get_summary_recursive")

    # Define the chunk size and the overlap size
    # Assuming 4 chars per token, we aim for 2500 tokens.
    chunk_size = 10000
    overlap_size = 100

    # Split the text content into chunks at the end of a sentence or line with a window overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            end = len(text)
            chunks.append(text[start:end])
            break
        else:
            # Search for the last period, exclamation point, or question mark character before the end position,
            # or for the last newline character
            end = max(text.rfind(".", start, end), text.rfind("!", start, end), text.rfind(
                "?", start, end), text.rfind("\n", start, end))
            if end < start + overlap_size:
                # If the last sentence or line is within the overlap size of the start position,
                # set the end position to the chunk size to avoid overlapping with the previous chunk
                end = start + chunk_size
            else:
                # Include the period, exclamation point, question mark, or newline character in the chunk
                end += 1
        chunks.append(text[start:end])
        start = end - overlap_size

    summaries = []
    # Only summarize the first 5 chunks
    for index, chunk in enumerate(chunks[:5]):
        print(f"\nSummarizing chunk #{index}")
        summaries.append(get_summary(title, url, chunk))

    print("\nSUMMARIES:", summaries)
    all_summaries = '\n'.join(summaries)
    if len(all_summaries) < chunk_size:
        print("Calling reduce_summary!!!")
        return reduce_summary(title, url, all_summaries)
    else:
        print("Calling get_summary_recursive?")
        return get_summary_recursive(title, url, all_summaries)


if __name__ == "__main__":
    # Read file from data/barack_obama.json
    with open("data/barack_obama.json", "r") as f:
        data = json.load(f)
        title = data["title"]
        url = data["url"]
        text = data["body"]
        # Get the summary
        summary = get_summary_recursive(title, url, text)
        print(summary)
