import json
import re

import requests
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from runner.api_runner_prompt import api_request_prompt, \
    api_response_prompt


class ApiRunner:
    def __init__(self, api_docs, chat_llm):
        self.api_docs = api_docs
        self.chat_llm = chat_llm

    def run(self, question):
        messages = [SystemMessage(content=api_request_prompt.format(api_docs=self.api_docs)),
                    HumanMessage(content=question)]

        prediction = self.predict(messages)

        print(f"Thought: {prediction}")

        url, response = self.call_api(prediction)

        print(f"Response: {response}")

        messages.append(AIMessage(content=url))
        messages.append(HumanMessage(content=api_response_prompt.format(api_response=response)))

        return self.predict(messages)

    def call_api(self, prediction):
        url, method, payload = self.parse_prediction(prediction)
        if method == "POST" and not payload:
            raise Exception(f"No payload found for POST {url}")

        if method == "GET":
            response = requests.get(url)
            if response.status_code != requests.codes.ok:
                raise Exception(f"Request failed. {response.reason}")
            return url, response.text

        if method == "POST":
            response = requests.post(url, json=json.loads(payload))
            if response.status_code != 201:
                raise Exception(f"Request failed. {response.reason}")
            return url, response.text

        raise Exception(f"Invalid combination of url:{url}, method:{method}, and payload: {payload}")

    def predict(self, messages):
        return self.chat_llm(messages).content

    def parse_prediction(self, prediction):
        url_patterns = [r'(?<=API URL: )https?://\S+', r'(?<=URL: )https?://\S+']
        method_pattern = r'(?<=Method: )\w+'
        payload_pattern = r'(?<=Payload:\n```json\n)(.*?)(?=`)'

        url = None

        for url_pattern in url_patterns:
            url = re.search(url_pattern, prediction)
            if url:
                url = url.group()
                break

        if not url:
            raise Exception(f"No URL found in {prediction}")

        method = re.search(method_pattern, prediction)

        if method:
            method = method.group()
        else:
            raise Exception(f"No method found in {prediction}")

        payload = re.search(payload_pattern, prediction, re.DOTALL)

        if payload and payload != "N/A":
            payload = payload.group().strip()
        else:
            payload = None

        return url, method, payload
