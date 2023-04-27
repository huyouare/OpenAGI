"""
tools/phone_call.py

A tool that allows the agent to make a phone call.

"""

from core.tool import BaseTool, InputSpec, OutputSpec

class PhoneCall(BaseTool):
    def __init__(self):
        self.phone_number: str = None
        self.context: str = None

    def description(self) -> str:
        return "Makes a phone call."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("phone_number", "The phone number to call", "string"),
            InputSpec("context", "The context of the phone call", "string"),
        ]

    def output_spec(self) -> list[OutputSpec]:
        return []

    def parse_input(self, input_str: str):
        self.phone_number = input_str["phone_number"]
        self.context = input_str["context"]

    def run(self):
        return {
            "output": f"Calling {self.phone_number} with context {self.context}",
        }
