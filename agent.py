from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory


class Agent:
    def __init__(self, tools, verbose=False) -> None:
        llm = ChatOpenAI(temperature=0)
        # memory = ConversationBufferMemory(memory_key="chat_history",
        #                                   return_messages=True)
        self.agent = initialize_agent(tools, llm,
                                      agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=verbose)

    def get_response(self, request):
        return self.agent.run(request)
