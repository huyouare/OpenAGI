"""
core/agent.py

This file contains the agent implementation.
"""

import json
from models import llm
from textwrap import dedent
from tools import browse, code, datetime_tool, email, location, phone_call, search, summarize, terminal, user_input


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
        self.assistant_messages = []

    def initialize(self):
        self.state = AgentState.INITIALIZING
        # Initialize all known tools
        self.tools = [
            # browse.BrowseTool(),
            # code.PythonRunner(),
            datetime_tool.DatetimeTool(),
            email.SendEmail(),
            # location.IPGeoLocation(),
            location.UserProvidedLocation(),
            phone_call.PhoneCall(),
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

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{self.tool_prompt}

If you (an LLM) can do a task yourself, then you do not need to use a tool.
However, do not hallucinate or make up any facts.
If there is a task you cannot currently do, you can prompt the user for help via UserInput.

You should minimize the number of steps you take and tools used, while maximizing the quality of the results.

Now, generate completion criteria and a plan to achieve the objective.
"""
        )
        print(prompt)
        response = self.model.generate_chat_completion(prompt)
        print(response)
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append({"role": "assistant", "content": response})
        self.initial_plan = self.current_plan = response
        self.state = AgentState.RUNNING

    def run(self):
        tool_output = None

        while self.state == AgentState.RUNNING:
            # Generate a chat completion
            prompt = dedent(
                f"""
If provided, the output (or error) from the tool used is provided below:
{tool_output}

Now, continue working towards the objective.

Use the following structure to your response:
1. REFLECT: Reflect on the previous action and its output.
2. PLAN: Define the next action, re-planning if necessary.
3. ACTION: Provide the next action in JSON format. ONLY output JSON.

If the you feel that the task is complete, use the UserInput tool to confirm.
If you are stuck, ask the UserInput for clarification.

At the end of your response, output the action in the following JSON format.
Do NOT include any other text in your ACTION.

{{
    "action": "tool_name",
    "input": {{ "input_name": "input_value" }}
}}

REFLECT:"""
            )
            print(prompt)
            response = self.model.generate_chat_completion(prompt, self.messages + self.assistant_messages)
            print(response)
            if len(self.assistant_messages) > 10:
                self.assistant_messages.pop(0)
                self.assistant_messages.pop(0)
            self.assistant_messages.append({"role": "user", "content": prompt})
            self.assistant_messages.append({"role": "assistant", "content": response})

            # Parse the text response after "ACTION" as JSON.
            action_str = response.split("ACTION:")[1]
            output = json.loads(action_str)
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
            try:
                tool.parse_input(output["input"])
                
                # If no errors, run the tool and capture the output.
                tool_output = tool.run()
            except Exception as error:
                tool_output = str(error)
                print("Error: " + tool_output)

            if output["action"] == "UserInput":
                self.assistant_messages.append({"role": "user", "content": str(tool_output)})
            
            # # Fake the tool being run by getting user input
            # tool_output = input("Please enter the output from the tool:\n")


if __name__ == "__main__":
    agent = Agent()
    agent.initialize()
    agent.run()
