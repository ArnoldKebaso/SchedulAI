import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Config values
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', 'calendar/credentials.json')
CALENDAR_ID = os.getenv('CALENDAR_ID')

# Authenticate once
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=creds)


def list_events(time_min=None, time_max=None) -> list:
    """Return existing events between time_min and time_max"""
    iso_min = time_min.isoformat() + 'Z' if time_min else None
    iso_max = time_max.isoformat() + 'Z' if time_max else None
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=iso_min,
        timeMax=iso_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    # Normalize to our dict schema
    return [
        {
            'summary': e['summary'],
            'start': e['start'].get('dateTime', e['start'].get('date')),
            'end': e['end'].get('dateTime', e['end'].get('date'))
        }
        for e in events
    ]


def create_event(event_body: dict) -> dict:
    """Inserts an event into Google Calendar"""
    body = {
        'summary': event_body['summary'],
        'start': {'dateTime': event_body['start'], 'timeZone': event_body.get('timezone')},
        'end':   {'dateTime': event_body['end'],   'timeZone': event_body.get('timezone')},
    }
    created = service.events().insert(
        calendarId=CALENDAR_ID,
        body=body
    ).execute()
    return {
        'id': created['id'],
        'summary': created['summary'],
        'start': created['start']['dateTime'],
        'end': created['end']['dateTime']
    }