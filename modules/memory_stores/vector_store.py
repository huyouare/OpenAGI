"""
memory_stores/vector_store.py

Stores items within a vector store.
"""

import datetime
import numpy as np
import math
from models.embedding import EmbeddingModel
from models.llm import LLM
from numpy.linalg import norm
from textwrap import dedent

from typing import List


class VectorStoreItem:
    def __init__(self, embedding: np.array, value: str, timestamp: float, importance: int):
        self.embedding: np.array = embedding
        self.value: str = value
        self.timestamp: float = timestamp
        self.importance: int = importance


class VectorStore:
    """An in-memory vector store.

    TODO: support removal and use an ordered dict
    """
    DEFAULT_IMPORTANCE_PROMPT = dedent("""
    On a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed)
    and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.
    Use the following format: FORMAT: <rating>
    """)

    def __init__(self, importance_prompt = DEFAULT_IMPORTANCE_PROMPT, use_real_time = False):
        self.items: list[VectorStoreItem] = []
        self.model = EmbeddingModel()
        # Real time is useful for things like simulations, but isn't as useful for
        # things like agents, where time doesn't have as much meaning.
        # Instead of real time, we can just use a counter.
        self.use_real_time = use_real_time
        self.time_counter = 0 # Only used when not using real time.
        self.llm = LLM(system_prompt=importance_prompt.strip())

    def add(self, value: str) -> None:
        """ Adds a value to the vector store. """
        # Create embedding of the value using OpenAI
        embedding = self.model.get_embedding(value)
        importance_str = self.llm.generate_chat_completion(value).split("FORMAT:")[1].strip()
        importance = int(importance_str)
        item = VectorStoreItem(np.array(embedding), value, datetime.datetime.now().timestamp() if self.use_real_time else self.time_counter, importance)
        self.items.append(item)
        if not self.use_real_time:
            self.time_counter += 1



    def cosine_similarity(self, a: np.array, b: np.array) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def query_recent(self, top_k: int) -> List[str]:
        """Returns the top k most recent entries from the vector store."""
        top_vector_items = sorted(self.items, key=lambda item: item.timestamp, reverse=True)[:top_k]
        return [item.value for item in top_vector_items]

    def query_relevance(self, query_string: str, top_k: int) -> List[str]:
        """Returns the top k most relevant entries from the vector store."""
        raw_embedding = self.model.get_embedding(query_string)
        query_embedding = np.array(raw_embedding)

        # Find the k items with highest cosine similarity to the query
        similarities = []
        for item in self.items:
            similarity = self.cosine_similarity(
                query_embedding, item.embedding)
            similarities.append(similarity)
        similarities = np.array(similarities)

        # Return the top k items. If there are less than k items, return all.
        if len(self.items) < top_k:
            top_k = len(self.items)
        top_k_indices = reversed(similarities.argsort()[-top_k:])
        top_k_items = [self.items[i].value for i in top_k_indices]
        return top_k_items
    
    def query(self, query_string: str, top_k: int) -> List[str]:
        """Returns the top k scored entries from the vector store."""
        raw_embedding = self.model.get_embedding(query_string)
        query_embedding = np.array(raw_embedding)

        current_time = datetime.datetime.now().timestamp if self.use_real_time else self.time_counter
    
        # Calculate the raw scores for each item.
        scores = []
        for item in self.items:
            relevance = self.cosine_similarity(query_embedding, item.embedding)
            recency = math.exp(-1 * (current_time - item.timestamp) * (1 - 0.99)) # Decay rate of 0.99
            scores.append((relevance, recency, item.importance))
        
        # Normalize the scores.
        min_relevance = min(scores, key=lambda x: x[0])[0]
        max_relevance = max(scores, key=lambda x: x[0])[0]
        min_recency = min(scores, key=lambda x: x[1])[1]
        max_recency = max(scores, key=lambda x: x[1])[1]
        min_importance = min(scores, key=lambda x: x[2])[2]
        max_importance = max(scores, key=lambda x: x[2])[2]
        normalized_scores = [
            (
                (relevance - min_relevance) / (max_relevance - min_relevance),
                (recency - min_recency) / (max_recency - min_recency),
                (importance - min_importance) / (max_importance - min_importance)
            )
            for relevance, recency, importance in scores
        ]
        combined_scores = [relevance + recency + importance for relevance, recency, importance in normalized_scores]
        scored_items = zip(combined_scores, self.items)
        return [item.value for _, item in sorted(scored_items, key=lambda tuple: tuple[0], reverse=True)[:top_k]]



if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.add("banana")
    vector_store.add("apple")
    vector_store.add("shoe")
    print(vector_store.query("grapes", 2))
