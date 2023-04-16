"""
main.py

This file is used for testing the agent.

"""

from core.agent import Agent


def main():
    agent = Agent()
    agent.initialize()
    agent.run()

if __name__ == "__main__":
    main()
