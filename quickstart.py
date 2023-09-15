from __future__ import print_function
import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pprint import pprint


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CalendarID = os.getenv("CalendarId")

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)  
        
        # 현재 시각으로부터 한달 전
        now = datetime.datetime.utcnow()
        one_month_ago = str((now - datetime.timedelta(days=30)).isoformat())+"Z"  
        
        # Google Calendar에 저장되어 있는 event 호출
        events_result = service.events().list(calendarId=CalendarID, timeMin= one_month_ago,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])    
                
        # summary만 저장
        events_summary = []
        for e in events :
            events_summary.append(e['summary'])

        if not events:
            print('No upcoming events found.')
            return

        # Jira API로 가져온 JSON file
        file_path = "JiraData.json"
        with open(file_path, "r") as json_file :
            json_data_list = json.load(json_file)
    
        for json_data in json_data_list :
            # GoogleCalendar에 저장되어 있는 summary와 JiraAPI로 얻은 summary가 같을 경우
            if json_data['summary'] in events_summary :
                
                # 해당되는 index 찾기
                find_index = events_summary.index(json_data['summary'])

                print("현재 캘린더에 저장 : ", events[find_index]['summary'], events[find_index]['start']['date'], events[find_index]['end']['date'])
                print("jira내용 : ",json_data['summary'], json_data['start']['date'], json_data['end']['date'])
                
                # 시작날짜 또는 종료날짜가 변경된 경우
                if events[find_index]['start']['date'] != json_data['start']['date'] or events[find_index]['end']['date'] != json_data['end']['date'] :
                    # 기존 일정 삭제 요청
                    service.events().delete(calendarId=CalendarID, eventId=events[find_index]['id']).execute()
                    # JIRA 일정 추가 요청
                    service.events().insert(calendarId=CalendarID, body=json_data).execute()
            
            else : 
                print("새로 캘린더에 추가 : ", json_data['summary'], json_data['start']['date'], json_data['end']['date'])
                # JIRA 일정 추가 요청
                service.events().insert(calendarId=CalendarID, body=json_data).execute()

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()