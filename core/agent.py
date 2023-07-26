"""
core/agent.py

This file contains the agent implementation.
"""

import ast
import json
from models import llm
from textwrap import dedent
from tools import (
    browse,
    code,
    datetime_tool,
    email,
    location,
    phone_call,
    search,
    summarize,
    terminal,
    user_input,
)
from dataviz.visualizer.visualizer import Visualizer


USE_FUNCTION_CALLS = True

INTRO_PROMPT = """You are an intelligent agent that is given the following objective:
{objective}

You also have multiple tools at your disposal.
For each task, you may use choose to use a tool or none at all.
If you can achieve a task without a tool, you should do so.
You may use a tool multiple times. The tools are:
{tool_prompt}

If you (an LLM) can do a task yourself, then you do not need to use a tool.
However, do not hallucinate or make up any facts.
If there is a task you cannot currently do, you can prompt the user for help via UserInput.

You should minimize the number of steps you take and tools used, while maximizing the quality of the results.

Now, generate a very concise plan (no complete sentences or explanation) to achieve the objective."""

ORIG_TOOL_PROMPT = """
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

{{ "action": "tool_name", "input": {{ "input_name": "input_value" }} }}

REFLECT:"""

FUNC_CALL_PROMPT = """
If provided, the output (or error) from the tool used is provided below:
{tool_output}

Now, continue working towards the objective.

As a reminder, here are the tools you can use:
{tool_prompt}

If the you feel that the task is complete, use the UserInput tool to confirm.
If you are stuck, ask the UserInput for clarification.

ALWAYS call a function.
Do NOT return any text other than your function call.
"""


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
        self.model = llm.LLM(model="gpt-3.5-turbo", max_tokens=1000, temperature=0.0)
        self.visualizer = Visualizer("/tmp/openagi_data.json")
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
            browse.BrowseTool(),
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

        tool_strings = [str(tool.json_openai()) for tool in self.tools]
        self.tool_prompt = "\n".join(tool_strings)

        # Ask the user for what the agent objective is
        self.objective = input(
            """\033[1m
Hi, my name is DAN. I am a general agent that can Do Anything Now.
What can I do for you today?\n\n\033[0m> """
        )

        self.visualizer.add_new_stage(title="Objective", content=self.objective)

        # Generate a chat completion
        prompt = dedent(
            INTRO_PROMPT.format(objective=self.objective, tool_prompt=self.tool_prompt)
        )
        print("\033[95m" + prompt + "\033[0m")
        viz_id = self.visualizer.add_new_stage(title="Planning", content="Thinking...")
        response = self.model.generate_chat_completion(prompt)
        print("\033[94m" + response)
        self.visualizer.amend_stage(stage_id=viz_id, content=response)
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append({"role": "assistant", "content": response})
        self.initial_plan = self.current_plan = response
        self.state = AgentState.RUNNING

    def run(self):
        tool_output = None

        while self.state == AgentState.RUNNING:
            # Generate a chat completion
            prompt = dedent(
                FUNC_CALL_PROMPT.format(
                    tool_output=tool_output, tool_prompt=self.tool_prompt
                )
                if USE_FUNCTION_CALLS
                else ORIG_TOOL_PROMPT.format(tool_output=tool_output)
            )
            print("\033[95m" + prompt + "\033[0m")
            viz_id = self.visualizer.add_new_stage(
                title="Reflection", content="Thinking..."
            )

            if USE_FUNCTION_CALLS:
                functions = [tool.json_openai() for tool in self.tools]
                print("Functions:", functions)
                message = self.model.generate_chat_completion_with_functions(
                    prompt, self.messages + self.assistant_messages, functions
                )

                try:
                    print("Message:", message)
                    response = None
                    if "function_call" in message:
                        print(
                            "\033[94m"
                            + "Function call: "
                            + str(message.function_call)
                            + "\033[0m"
                        )
                        response = message.function_call
                    else:
                        print("\033[94m" + str(message.content) + "\033[0m")
                        response = ast.literal_eval(message.content)
                        # Strip out "function."
                        if "function." in response["name"]:
                            response["name"] = response["name"].split(".")[1]
                except Exception as error:
                    print(f"Error parsing message.content: {error}")

                # Use the function call to get the tool by name
                function_name = response["name"]
                tool = None
                for t in self.tools:
                    if type(t).__name__ == function_name:
                        tool = t
                        break

                print("RUNNING TOOL:", tool)

                # Set the tool's input
                try:
                    print("INPUTS:", response["arguments"])
                    tool.parse_input(json.loads(response["arguments"]))
                    # If no errors, run the tool and capture the output.
                    tool_output = tool.run()
                except Exception as error:
                    tool_output = str(error)
                    print("Error: " + tool_output)

            else:
                response = self.model.generate_chat_completion(
                    prompt, self.messages + self.assistant_messages
                )
                print("\033[94m" + response + "\033[0m")

                # Parse the text response after "ACTION" as JSON.
                action_str = response.split("ACTION:")[1]
                viz_id = self.visualizer.add_new_stage(
                    title="Action", content=action_str
                )
                self.visualizer.amend_stage(
                    stage_id=viz_id, content=response.split("ACTION:")[0]
                )

                print("Action str:", action_str)

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

                viz_id = self.visualizer.add_new_stage(
                    title=output["action"], content=str(tool_output)
                )

            if len(self.assistant_messages) > 10:
                self.assistant_messages.pop(0)
                self.assistant_messages.pop(0)
            self.assistant_messages.append({"role": "user", "content": prompt})
            self.assistant_messages.append(
                {"role": "assistant", "content": str(response)}
            )

            # TODO: Add the tool input and output to messages
            # if output["action"] == "UserInput":
            #     self.assistant_messages.append({"role": "user", "content": str(tool_output)})

            # # Fake the tool being run by getting user input
            # tool_output = input("Please enter the output from the tool:\n")


if __name__ == "__main__":
    agent = Agent()
    agent.initialize()
    agent.run()
