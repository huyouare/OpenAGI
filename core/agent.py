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
        self.model = llm.LLM()
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
        I am an intelligent agent with the following objective:
        {self.objective}
        
        I have the following tools at my disposal:
        {self.tool_prompt}

        Make a list of tasks to take.
        """)
        print(prompt)
        response = self.model.generate_chat_completion(prompt)
        print(response)
