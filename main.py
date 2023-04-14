"""
main.py

This file is used for testing the agent.

"""

from models import llm


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

    def initialize(self):
        self.state = AgentState.INITIALIZING
        # Ask the user for what the agent objective is
        self.objective = input("What is my objective?\n")

    def run(self):
        self.state = AgentState.RUNNING
        # Generate a chat completion
        prompt = f"""
        I am an intelligent agent with the following objective:
        {self.objective}
        The following is my next task to complete:
        """
        response = self.model.generate_chat_completion(prompt)
        print(response)


def main():
    agent = Agent()
    agent.initialize()
    agent.run()


if __name__ == "__main__":
    main()
