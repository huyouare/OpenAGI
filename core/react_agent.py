from models.llm import LLM
import re

REACT_BASE_PROMPT = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will then be the result of running those actions.

Your available actions are:
python:
e.g. python: sum([x for x in range(10)])
Returns the result of the executed python code as a string.

google:
e.g. google: Who is the current president?
Returns the top result from Google for the given query.

You are free to call any number of actions you want, in any order, as many times as you want.

Here is one example:
Question: How many people live in Nevada and Wyoming combined?
Thought: I should look up how many people live in Nevada, and then look up how many people live in Wyoming, and then sum them in python.
Action: google: population of Nevada
PAUSE

You will then be called again with this:
Observation: 3.144 million
Thought: I should look up how many people live in Wyoming.
Action: google: population of Wyoming.
PAUSE

You will then be called again with this:
Observation: 578,803
Thought. Now, I should sum these two numbers in python.
Action: python: 3144000 + 578803
PAUSE

You will then be called again with this:
Observation: 3722803
You then output:
Answer: 3722803

Here is another example:
Question: What is the square root of pi?
Thought: I should use python to calculate the square root of pi.
Action: python: import math; math.sqrt(math.pi)
PAUSE

You will then be called again with this:
Observation: 1.77245
You then output:
Answer: 1.77245

Now you try.
""".strip()

def google(q):
    return input(f"Simulate a google search for {q}:\n")

def python(q):
    return input(f"Simulate a python eval for: {q}:\n")

known_actions = {
    "google": google,
    "python": python,
}

action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=5):
    i = 0
    bot = LLM(system_prompt=REACT_BASE_PROMPT)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot.generate_chat_completion_stateful(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return

# if __name__ == "__main__":
#     query("How tall is michael jordan?")