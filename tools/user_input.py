"""
tools/user_input.py

This file provides a tool to ask for the user's input.
"""

from core.tool import BaseTool, InputSpec, OutputSpec


class UserInput(BaseTool):
    def __init__(self):
        self.agent_question: str = None

    def description(self) -> str:
        return "Asks the user for input."

    def input_spec(self) -> list[InputSpec]:
        return [
            OutputSpec("agent_question", "The question from the agent", "string"),
        ]

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("user_response", "The user's response", "string"),
        ]
    
    def parse_input(self, input_str: str):
        # Validate the input
        if "agent_question" not in input_str:
            raise ValueError("The input must contain agent_question.")
        
        self.agent_question = input_str["agent_question"]

    def run(self):
        return {
            "user_response": input(self.agent_question) + "\n",
        }
