"""
models/embedding.py

Calls the embedding model from OpenAI.

"""

import openai
import os

# Set api key from env vars
openai.api_key = os.environ["OPENAI_API_KEY"]


class EmbeddingModel:
    def __init__(self, model="text-embedding-ada-002"):
        self.model = model

    def get_embedding(self, text):
        return openai.Embedding.create(input=[text], model=self.model)['data'][0]['embedding']
