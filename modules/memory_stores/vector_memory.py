"""
memory_stores/list_memory.py

Stores memories as a vector store.
"""

import numpy as np
from models.embedding import EmbeddingModel
from numpy.linalg import norm


class VectorStoreItem:
    def __init__(self, embedding: np.array, value: str):
        self.embedding: np.array = embedding
        self.value: str = value


class VectorStore:
    """ An in-memory vector store.

    TODO: support removal and use an ordered dict
    """

    def __init__(self):
        self.items: list[VectorStoreItem] = []
        self.model = EmbeddingModel()

    def add(self, value: str) -> None:
        """ Adds a value to the vector store. """
        # Create embedding of the value using OpenAI
        embedding = self.model.get_embedding(value)
        item = VectorStoreItem(np.array(embedding), value)
        self.items.append(item)

    def cosine_similarity(self, a: np.array, b: np.array) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def query(self, query_string: str, top_k: int) -> list[str]:
        """ Query the vector store using a query string. """
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


if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.add("banana")
    vector_store.add("apple")
    vector_store.add("shoe")
    print(vector_store.query("grapes", 2))
