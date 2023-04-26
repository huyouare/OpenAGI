"""
core/agent.py

This file contains an experimental agent implementation.
"""

import json
from models import llm
from textwrap import dedent
from modules.memory_stores.vector_store import VectorStore
from tools import browse, code, datetime_tool, location, search, summarize, terminal, user_input
import tiktoken


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
        self.primary_model = llm.LLM(model="gpt-4", max_tokens=1000)
        self.secondary_model = llm.LLM(model="gpt-3.5-turbo", max_tokens=500)
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
            code.PythonRunner(),
            datetime_tool.DatetimeTool(),
            # location.IPGeoLocation(),
            location.UserProvidedLocation(),
            search.SearchTool(),
            # summarize.SummarizeTool(),
            terminal.Terminal(),
            # user_input.UserInput(),
        ]

        tool_strings = [str(tool) for tool in self.tools]
        self.tool_prompt = "\n".join(tool_strings)

        # Ask the user for what the agent objective is
        self.objective = input("What is my objective?\n")
        self.memory = VectorStore(dedent(
            """
            On a scale of 1 to 10, where 1 is completely useless, and 10 is actually achieving the goal, rate the importance
            of the following piece of memory when it comes to achieving the following goal.
            Goal: {}
            Use the following format: FORMAT: <rating>
            Do not return anything other than the format.

            Rate this piece of memory:
            {}
            """
        ), self.objective)
        self.state = AgentState.RUNNING

    def run(self):
        tool_output = None

        while self.state == AgentState.RUNNING:
            # The agent follows a high level strategy as follows:
            #   1. Plan
            #      1a. Retrieve memory.
            #   2. Action
            #   3. Summarize/Reflection
            #      3a. Save summary to memory

            # Start the planning phase now
            memory_str = ""
            if not self.memory.empty():
                memories = self.memory.query("af;j;lkasdflkj", 100)
                memory_str = "Here are some relevant memories for you:\n"
                for memory in memories:
                       memory_str += f"* {memory}\n"
                memory_str = memory_str.strip()       
                
            planning_prompt = dedent(
                f"""
You are an intelligent agent that is given the following objective: {self.objective}.
{memory_str}

Make a list of tasks to take to achieve your objective.

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{self.tool_prompt}

If you (an LLM) can do a task yourself, then you do not need to use a tool.
If there is a task you cannot currently do, then you should try to generate and execute code via Terminal.

You should minimize the number of steps you take and tools used, while maximizing the quality of the results.
                """
            )
            print("Printing planning prompt: ", planning_prompt)
            planning_response = self.primary_model.generate_chat_completion_stateful(planning_prompt)
            print("Printing planning response: ", planning_response)

            # Planning is over. Now start the action phase.
            action_prompt = dedent(
                f"""
You are an intelligent agent that is given the following objective: {self.objective}.
Previously, you came up with a plan to achieve this goal. Here is the plan:
{planning_response}

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{self.tool_prompt}

Recall that your objective is {self.objective}.
Continue working towards your objective.
Output your next action in the following JSON format:

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
    "output": "<The final result for the user>"
}}
```
            """
            )
            print("Printing action prompt: ", action_prompt)
            action_response = self.primary_model.generate_chat_completion(action_prompt)
            print("Printing action response: ", action_response)

            # Parse the text response as JSON, 
            output = json.loads(action_response)
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

            # Action is over, now entering reflection stage.
            reflection_prompt = dedent(
                f"""
You are an AI agent tasked with solving the following objective: {self.objective}.

As part of your efforts to solve this objective, you recently took the following action: {output["action"]}.
The input to your action was: {output["input"]}.
The response output of this action was: {tool_output}.

Summarize the output of this action into a form that can help you achieve your objective in the future.
We will save your summary and give it to you again in the future.
You should summarize the actual output itself, not just meta-information about the output. So, if you used the date tool and found the current date was "01-01-2020", you need to include the actual date in your summary.
The output itself will be discarded, and only your summary will be kept. So, if there is anything you want to remember, put it in your summary.
                """
            )
            print("Printing reflection prompt: ", reflection_prompt)
            reflection_response = self.secondary_model.generate_chat_completion(reflection_prompt)
            print("Printing reflection response: ", reflection_response)
            self.memory.add(reflection_response)
            dummy = input("PAUSE")
            
            # # Fake the tool being run by getting user input
            # tool_output = input("Please enter the output from the tool:\n")
    
    def build_reflection_prompt(self, action, input_str, output):
        base_prompt = dedent(f"""
        You are an AI agent tasked with solving the following objective: {self.objective}.

As part of your efforts to solve this objective, you recently took the following action: {action}.
The input to your action was: {input_str}.
The response output of this action was: OUTPUT.

Summarize the output of this action into a form that can help you achieve your objective in the future.
We will save your summary and give it to you again in the future.
You should summarize the actual output itself, not just meta-information about the output. So, if you used the date tool and found the current date was "01-01-2020", you need to include the actual date in your summary.
The output itself will be discarded, and only your summary will be kept. So, if there is anything you want to remember, put it in your summary.
        """)
    
        encoding = tiktoken.get_encoding("cl100k_base")
        system_prompt_tokens = len(encoding.encode(self.secondary_model.system_prompt))
        base_prompt_tokens = len(encoding.encode(base_prompt))
        tokens_remaining = 4096 - system_prompt_tokens - base_prompt_tokens - self.secondary_model.max_tokens

        output_encoding = encoding.encode(output)
        # We have to make sure we don't overflow the context window.
        output_encoding = output_encoding[:tokens_remaining]
        output = encoding.decode(output_encoding)
        return dedent(f"""
 You are an AI agent tasked with solving the following objective: {self.objective}.

As part of your efforts to solve this objective, you recently took the following action: {action}.
The input to your action was: {input_str}.
The response output of this action was: {output}.

Summarize the output of this action into a form that can help you achieve your objective in the future.
We will save your summary and give it to you again in the future.
You should summarize the actual output itself, not just meta-information about the output. So, if you used the date tool and found the current date was "01-01-2020", you need to include the actual date in your summary.
The output itself will be discarded, and only your summary will be kept. So, if there is anything you want to remember, put it in your summary.
        """)







if __name__ == "__main__":
    agent = Agent()
    agent.initialize()
    agent.run()
