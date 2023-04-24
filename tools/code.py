"""
tools/code.py

This file contains code generation, validation, and execution tools.
"""

from core.tool import BaseTool, InputSpec, OutputSpec
from models import llm
from io import StringIO
from contextlib import redirect_stdout


class PythonRunner(BaseTool):
    def __init__(self):
        self.code: str = None

    def description(self) -> str:
        return "Executes Python code."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("code", "The Python code to execute", "string"),
        ]

    def output_spec(self) -> list[OutputSpec]:
        return [
            OutputSpec("output", "The output of the code", "string"),
        ]

    def parse_input(self, input_str: str):
        # Validate the input
        if "code" not in input_str:
            raise ValueError("The input must contain code.")

        self.code = input_str["code"]

    def run(self):
        # Execute the code and capture the output
        string_io = StringIO()
        with redirect_stdout(string_io):
            exec(self.code)
        output = string_io.getvalue()

        return {
            "output": output,
        }



# class CodeExecutor(BaseTool):
#     def __init__(self):
#         self.language: str = None
#         self.code: str = None

#     def description(self) -> str:
#         return "Executes code for a given language."

#     def input_spec(self) -> list[InputSpec]:
#         return [
#             InputSpec("language", "The language to execute code for", "string"),
#             InputSpec("code", "The code to execute", "string"),
#         ]

#     def output_spec(self) -> list[OutputSpec]:
#         return [
#             OutputSpec("output", "The output of the code", "string"),
#         ]

#     def parse_input(self, input_str: str):
#         # Validate the input
#         if "language" not in input_str:
#             raise ValueError("The input must contain language.")
#         if "code" not in input_str:
#             raise ValueError("The input must contain code.")

#         self.language = input_str["language"]
#         self.code = input_str["code"]

#     def run(self):
#         return {
#             "output": llm.execute(self.language, self.code),
#         }



# class CodeGenerator(BaseTool):
#     def __init__():
#         self.language: str = None
#         self.prompt: str = None

#     def description(self) -> str:
#         return "Generates code for a given language."

#     def input_spec(self) -> list[InputSpec]:
#         return [
#             InputSpec("language", "The language to generate code for", "string"),
#             InputSpec("prompt", "Prompt to ChatGPT for the code should generate", "string"),
#         ]

#     def output_spec(self) -> list[OutputSpec]:
#         return [
#             OutputSpec("code", "The generated code", "string"),
#         ]

#     def parse_input(self, input_str: str):
#         # Validate the input
#         if "language" not in input_str:
#             raise ValueError("The input must contain language.")
#         if "prompt" not in input_str:
#             raise ValueError("The input must contain prompt.")

#         self.language = input_str["language"]
#         self.prompt = input_str["prompt"]

#     def run(self):
#         return