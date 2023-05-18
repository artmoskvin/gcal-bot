import json
import re
from typing import List, Dict, Any, Optional

from langchain import BasePromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import requests


class ApiChain(Chain):
    request_prompt: BasePromptTemplate
    response_prompt: BasePromptTemplate
    api_docs: str
    chat_llm: BaseChatModel
    output_key: str = "text"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        # todo: what's it for?
        # return self.request_prompt.input_variables
        return []

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        messages = [SystemMessage(content=self.request_prompt.format(api_docs=self.api_docs)),
                    HumanMessage(content=inputs["question"])]

        prediction = self.chat_llm(messages).content

        print(f"Thought: {prediction}")

        # TODO: parse output before calling api
        url, response = self.__call_api(prediction)

        print(f"Response: {response}")

        messages.append(AIMessage(content=url))
        messages.append(HumanMessage(content=self.response_prompt.format(api_response=response)))

        return {self.output_key: self.chat_llm(messages).content}

    def __call_api(self, prediction):
        url, method, payload = self.__parse_prediction(prediction)
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

    def __parse_prediction(self, prediction):
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
