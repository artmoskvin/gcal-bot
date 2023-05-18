from langchain import PromptTemplate

API_REQUEST_PROMPT_TEMPLATE = """You are given the below API Documentation:

{api_docs}

Using this documentation, generate the full API url to call for answering the user question. Respond with URL, method, \
and payload only. If a payload is not needed, leave it empty.
"""

api_request_prompt = PromptTemplate(
    input_variables=["api_docs"],
    template=API_REQUEST_PROMPT_TEMPLATE,
)

API_RESPONSE_PROMPT_TEMPLATE = """Here's the response from the API: 

{api_response}

Summarize this response to answer the original question."""

api_response_prompt = PromptTemplate(
    input_variables=["api_response"],
    template=API_RESPONSE_PROMPT_TEMPLATE
)
