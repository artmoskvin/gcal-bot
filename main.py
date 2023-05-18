import os

from langchain.tools import Tool

from agent import Agent
from chains.gcal import GCalChain
from tools.tools import today_date_tool, day_of_week_tool
from tools.gcal import CalendarSearchTool

VERBOSE = True

os.environ["OPENAI_API_KEY"] = "YOUR_KEY"


def main():
    # gcal_chain = GCalChain(VERBOSE)

    tools = [
        today_date_tool,
        # day_of_week_tool,
        CalendarSearchTool()
    ]

    agent = Agent(tools, VERBOSE)

    print("Welcome to the ChatGPT chatbot. Type 'quit' to exit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break

        response = agent.get_response(user_input)

        print("Assistant:", response)


if __name__ == "__main__":
    main()
