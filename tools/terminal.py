"""
tools/terminal.py

This class defines the terminal tool used by the agent.
"""

from core.tool import BaseTool, InputSpec, OutputSpec
import subprocess

class Terminal(BaseTool):
    def __init__(self) -> None:
        self.command: str = None

    def description(self) -> str:
        return "Executes a command in the terminal."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("command", "The command to execute", "string"),
        ]

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("output", "The output of the command", "string"),
        ]

    def parse_input(self, input_str: str):
        # Validate the input
        if "command" not in input_str:
            raise ValueError("The input must contain command.")
        
        self.command = input_str["command"]

    def run(self):
        # Execute the command and capture the output using subprocess
        output = subprocess.check_output(self.command, shell=True).decode("utf-8")
        return output
