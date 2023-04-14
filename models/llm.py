"""
models/llm.py

This file defines the class to call an LLM from OpenAI.

"""

import openai
import os
from models.prompts import SYSTEM_PROMPT

# Set api key from env vars
openai.api_key = os.environ["OPENAI_API_KEY"]


class LLM:
    def __init__(self,
                 model="gpt-3.5-turbo",
                 temperature=0.0,
                 max_tokens=200,
                 system_prompt=SYSTEM_PROMPT):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt

    def generate_chat_completion(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content
