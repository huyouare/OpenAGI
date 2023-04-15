"""
tools/retrieval.py

This file contains the retrieval tool used by the agent.

This tool ingests a set of documents, stores chunks in a vector store, and then
allows the agent to query the vector store for similar chunks.
"""

import tiktoken


def count_tokens(text: str) -> int:
    """Use tiktoken to count the number of tokens in a text."""
    enc = tiktoken.encoding_for_model("gpt-4")
    return len(enc.encode(text))


if __name__ == "__main__":
    print(count_tokens("""
        The GPT family of models process text using tokens, which are common sequences of characters found in text.
        The models understand the statistical relationships between these tokens, and excel at producing the next token in a sequence of tokens.
        You can use the tool below to understand how a piece of text would be tokenized by the API, and the total count of tokens in that piece of text.
        """))
    print(count_tokens("Hello world!"))
