"""
core/tool.py

This file contains the generic class of a tool.
"""

from abc import ABC, abstractmethod


class InputSpec:
    """ Describes the format and descrption of a tool input. """

    def __init__(self, name, description, type):
        self.name = name
        # Description should be < 50 words.
        self.description = description
        self.type = type


class OutputSpec:
    """ Describes the format and descrption of a tool output. """

    def __init__(self, name, description, type):
        self.name = name
        # Description should be < 50 words.
        self.description = description
        self.type = type


class BaseTool(ABC):
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def input_spec(self) -> list[InputSpec]:
        pass

    @abstractmethod
    def output_spec(self) -> list[OutputSpec]:
        # TODO: error handling
        pass

    @abstractmethod
    def parse_input(self, input_str: str):
        """Parse the JSON input to the tool and set the tool's input variables."""
        pass

    @abstractmethod
    def run(self):
        pass

    def __str__(self):
        """Generate a string representation of the tool in JSON, including class name, descrption, and input/output spec."""
        return str({
            "name": self.__class__.__name__,
            "description": self.description(),
            "input_spec": [vars(input) for input in self.input_spec()],
            "output_spec": [vars(output) for output in self.output_spec()]
        })

    def json_openai(self):
        """Generate the tool spec in OpenAI function call format."""

        # First, format inputs in the proper format
        # "parameters": {
        #     "type": "object",
        #     "properties": {
        #         "location": {
        #             "type": "string",
        #             "description": "The city and state, e.g. San Francisco, CA",
        #         },
        #         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        #     },
        #     "required": ["reasoning", "location"],
        # },
        properties = {}
        required = []
        for input in self.input_spec():
            properties[input.name] = {
                # Cast type 'int' to 'number' for OpenAI
                "type": "number" if input.type == "int" else input.type,
                "description": input.description
            }
            # All inputs are required
            required.append(input.name)

        obj = {
            "name": self.__class__.__name__,
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

        # Return json
        return obj
