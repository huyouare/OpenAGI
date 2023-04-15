"""
core/agent.py

This file contains the agent implementation.
"""

from models import llm
from textwrap import dedent
from tools import browse, datetime_tool, location, search, summarize


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
        self.model = llm.LLM(model="gpt-4", max_tokens=1000)
        self.tools = []
        self.tool_prompt = ""

    def initialize(self):
        self.state = AgentState.INITIALIZING
        # Initialize all known tools
        self.tools = [
            browse.BrowseTool(),
            datetime_tool.DatetimeTool(),
            location.IPGeoLocation(),
            location.UserProvidedLocation(),
            search.SearchTool(),
            summarize.SummarizeTool(),
        ]

        tool_strings = [str(tool) for tool in self.tools]
        self.tool_prompt = '\n'.join(tool_strings)

        # Ask the user for what the agent objective is
        self.objective = input("What is my objective?\n")

    def run(self):
        self.state = AgentState.RUNNING
        # Generate a chat completion
        prompt = dedent(f"""
You are an intelligent given the following objective:
{self.objective}

Make a list of tasks to take to achieve your objective.

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{self.tool_prompt}

You should minimize the number of steps you take and tools used, while maximizing the quality of the results.
        """)
        print(prompt)
        response = self.model.generate_chat_completion(prompt)
        print(response)
