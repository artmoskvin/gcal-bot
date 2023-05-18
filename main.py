import os

from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

from agent import Agent
from chains.api_chain import ApiChain
from chains.api_chain_prompt import api_request_prompt, api_response_prompt
from chains.gcal import GCalChain
from chains.gcal_list_docs import GCAL_LIST_DOCS
from tools.tools import today_date_tool, day_of_week_tool
from tools.gcal import CalendarSearchTool

VERBOSE = True

os.environ["OPENAI_API_KEY"] = "YOUR_KEY"


def main():
    gcal_chain = ApiChain(request_prompt=api_request_prompt, response_prompt=api_response_prompt,
                          api_docs=GCAL_LIST_DOCS, chat_llm=ChatOpenAI(temperature=0))

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
