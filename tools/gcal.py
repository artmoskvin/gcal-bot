import os.path
from datetime import datetime, timedelta
from typing import Optional, Type
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from langchain.tools import BaseTool, tool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from pydantic import BaseModel, Field

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


# class SearchSchema(BaseModel):
#     date_time: str = Field(description="Lower bound (exclusive) of the search window. Must be a timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

class CalendarSearchTool(BaseTool):
    name = "calendar_search"
    description = "Use this when you need to search for events in the calendar. \
        The input should be a datetime in the ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). " \
                  "Always check the current date before using this tool. You need to know the current date." \
                  "You can't use inputs like 'today' or 'tomorrow'."

    # args_schema: Type[SearchSchema] = SearchSchema

    def _run(self, date_time: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""

        if not self.__is_valid_datetime(date_time, DATE_FORMAT):
            return f"The date_time parameter must be a datetime in the ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."

        creds = self.__get_credentials()

        # Build the Google Calendar API client
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API to fetch events
        events = self.__fetch_events(service, date_time, self.__get_upper_bound(date_time))

        if not events:
            return "No events founds"

        result = ""
        for event in events:
            result += f"- {event['summary']} at {event['start']['dateTime']}\n"
        return result

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    def __is_valid_datetime(self, date_string, date_format):
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False

    def __get_upper_bound(self, lowerbound, window_in_hours=24):
        """A hack to get a search window until we teach agent to input two dates"""
        return datetime.strftime(datetime.strptime(lowerbound, DATE_FORMAT) + timedelta(hours=window_in_hours),
                                 DATE_FORMAT)

    def __get_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def __fetch_events(self, service, time_min, time_max, calendar_id='primary', max_results=10, time_zone='UTC'):
        try:
            # Get events from the Google Calendar API
            events_result = service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max,
                                                  maxResults=max_results, singleEvents=True,
                                                  orderBy='startTime', timeZone=time_zone).execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
