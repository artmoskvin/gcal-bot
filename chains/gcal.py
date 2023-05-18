import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain.chains import APIChain
from langchain.llms import OpenAI

from chains.gcal_list_docs import GCAL_LIST_DOCS

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GCalChain:
    def __init__(self, verbose=False) -> None:
        llm = OpenAI(temperature=0)
        creds = self.get_credentials()
        headers = {"Authorization": f"Bearer {creds.token}"}
        self.chain = APIChain.from_llm_and_api_docs(
            llm=llm,
            api_docs=GCAL_LIST_DOCS,
            headers=headers,
            verbose=verbose,
        )

    def get_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def get_response(self, question):
        return self.chain.run(question)
