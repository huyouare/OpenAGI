"""
core/agent.py

This file contains the agent implementation.
"""

import json
from models import llm
from textwrap import dedent
from tools import browse, code, datetime_tool, location, search, summarize, terminal, user_input


class AgentState:
    NOT_STARTED = 0
    INITIALIZING = 1
    RUNNING = 2
    STOPPED = 3


class Agent:
    def __init__(self):
        self.executor = None
        self.memory = None
        self.search = None
        self.state = AgentState.NOT_STARTED
        self.objective = ""
        self.model = llm.LLM(model="gpt-4", max_tokens=1000, temperature=0.0)
        self.tools = []
        self.tool_prompt = ""
        self.initial_plan = ""
        self.current_plan = ""
        self.messages = []

    def initialize(self):
        self.state = AgentState.INITIALIZING
        # Initialize all known tools
        self.tools = [
            browse.BrowseTool(),
            # code.PythonRunner(),
            datetime_tool.DatetimeTool(),
            # location.IPGeoLocation(),
            location.UserProvidedLocation(),
            search.SearchTool(),
            # summarize.SummarizeTool(),
            terminal.Terminal(),
            user_input.UserInput(),
        ]

        tool_strings = [str(tool) for tool in self.tools]
        self.tool_prompt = "\n".join(tool_strings)

        # Ask the user for what the agent objective is
        self.objective = input("What is my objective?\n")

        # Generate a chat completion
        prompt = dedent(
            f"""
You are an intelligent agent that is given the following objective:
{self.objective}

Make a list of tasks to take to achieve your objective.

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{self.tool_prompt}

If you (an LLM) can do a task yourself, then you do not need to use a tool.
If there is a task you cannot currently do, then you should try to generate and execute code via Terminal.
If that doesn't work, then you can prompt the user for help via UserInput.

You should minimize the number of steps you take and tools used, while maximizing the quality of the results.
        """
        )
        print(prompt)
        response = self.model.generate_chat_completion_stateful(prompt)
        print(response)

        self.initial_plan = self.current_plan = response
        self.state = AgentState.RUNNING

    def run(self):
        tool_output = None

        while self.state == AgentState.RUNNING:
            # Generate a chat completion
            prompt = dedent(
                f"""
If provided, the output from the tool used is provided below:
{tool_output}

Now, continue working towards the objective.
Output the next action in the following JSON format:

```
{{
    "action": "tool_name",
    "input": {{ "input_name": "input_value" }}
}}
```

If the task is complete, output the following JSON:
```
{{
    "action": "complete",
    "output": "The final result for the user"
}}
```
            """
            )
            print(prompt)
            response = self.model.generate_chat_completion_stateful(prompt)
            print(response)

            # Parse the text response as JSON, 
            output = json.loads(response)
            if "action" not in output:
                # TODO: handle error
                print("Error: no action specified")
            if output["action"] == "complete":
                self.state = AgentState.STOPPED
                print("Task complete!")
                print("FINAL RESULT:\n\n" + output["output"])
                return
            
            # Get the tool by name
            tool = None
            for t in self.tools:
                if type(t).__name__ == output["action"]:
                    tool = t
                    break
            
            # Set the tool's input
            tool.parse_input(output["input"])
            
            # If no errors, run the tool and capture the output.
            tool_output = tool.run()
            
            # # Fake the tool being run by getting user input
            # tool_output = input("Please enter the output from the tool:\n")


if __name__ == "__main__":
    agent = Agent()
    agent.initialize()
    agent.run()
