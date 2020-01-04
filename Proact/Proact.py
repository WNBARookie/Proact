from __future__ import print_function
from datetime import datetime, timezone, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Event import Event
import json
from tzlocal import get_localzone
import pandas as pd
import sys


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

calendarID = "vorcc5hji4duuk2llo532gl3o8@group.calendar.google.com"


def main():
    pass


# Creating task based on user input
def CreateTask(summary, dueDate, hoursEstimate):
    """
    -get task input
    -calculate how much time per day
    -create the string for the description
    -add to calendar everyday until the day before the due date
    """
    # get task input
    dueDate = datetime.strptime(dueDate, "%m-%d-%Y").date()

    # calculate how much time per day (time starts the day after task is created and ends the day before the due date)
    daysBetween = GetDayDiff(dueDate)
    hours, minutes = GetTimePerDay(hoursEstimate, daysBetween)

    # create the string for the description
    description = CreateDescription(hours, minutes, summary)

    # """
    # add to calendar everyday until the day before the due date
    # -- get all dates from current day to day before due date

    currentDate = datetime.today().date()
    days = [
        currentDate + timedelta(days=x) for x in range((dueDate - currentDate).days)
    ]

    # --creating comparison array for dates that have events in google calendar
    events = GetCalendarData(len(days))
    comparisonArray = []
    for i in range(len(days)):
        comparisonArray.append(".")

    for event in events:
        date = datetime.strptime(event["start"].get("date"), "%Y-%m-%d").date()
        comparisonArray[days.index(date)] = date
    # --create an event for all days that don't have an event in the date range
    for x in range(len(days)):
        # print(days[x] == comparisonArray[x])
        if days[x] != comparisonArray[x]:
            start = str(days[x])
            end = str(days[x] + timedelta(days=1))
            event = {
                "summary": "Proact",
                "description": " ",
                "start": {"date": start},
                "end": {"date": end},
            }
            AddTask(event)

    # --adding the description to all the dates

    # ----get all events in date range
    events = GetCalendarData(len(days))
    # ----update each event
    for x in range(len(events)):
        UpdateTask(events[x], description, 1)


# """
# get the difference in between the current date and day before due date(datetime)
def GetDayDiff(dueDate):
    currentDate = datetime.today().date()
    # dayBeforeDueDate = dueDate - timedelta(days=1)
    dayBeforeDueDate = dueDate
    daysBetween = (dayBeforeDueDate - currentDate).days

    return daysBetween


# get amount of time per day
def GetTimePerDay(hours, daysBetween):
    timePerDay = hours / daysBetween
    hours = int(timePerDay)
    minutes = int((timePerDay * 60) % 60)

    return hours, minutes


# creates description line for calendar
def CreateDescription(hours, minutes, summary):
    description = ""
    minsString = str(minutes) + " minutes"
    hoursString = str(hours) + " hours"

    if minutes == 1 or minutes == 0:
        if minutes == 1:
            minsString = "1 minute"
        elif minutes == 0:
            minsString = ""
    if hours == 1 or hours == 0:
        if hours == 1:
            hoursString = "1 hour"
        elif hours == 0:
            hoursString = ""

    if minsString == "" or hoursString == "":
        if minsString == "":
            description = hoursString
        elif hoursString == "":
            description = minsString
    else:
        description = hoursString + " and " + minsString
    description = "- " + summary + " --> " + description + "\n"

    return description


# Creating the task based on the information given by the user
def GetTaskInput():

    """
    -task summary
    -due date
    -how long they think it will take (in hours)
    """
    print("\n\nWhat is the task?")
    summary = str(input())
    date = ""
    hours = ""

    # getting date
    invalidDate = True
    while invalidDate:
        print("\n\nWhen is the task due? (has to at least be 2 days from now)")
        print("\nDate format: YYYY-DD-MM")
        try:
            date = str(input())
            print()
            # splitDate = date.split("-")
            # check if date is valid
            try:
                date = datetime.strptime(date, "%Y-%d-%m").date()
            except:
                print(
                    "\n\nPlease enter a valid date that is at least 2 days after today's date"
                )
                continue

            # check if date is after today
            if date > datetime.today().date() + timedelta(days=1):
                invalidDate = False

            else:
                print(
                    "\n\nPlease enter a valid date that is at least 2 days after today's date"
                )
        except:
            print(
                "\n\nPlease enter a valid date that is at least 2 days after today's date"
            )

    # getting hours
    invalidHours = True
    while invalidHours:
        print("\n\nHow long do you think it will take (in hours)?")
        try:
            hours = str(input())
            print()
            try:
                hours = float(hours)
                invalidHours = False
            except:
                print("\n\nPlease enter a valid number")
        except:
            print("\n\nPlease enter a valid number")

    return summary, date, hours


# Makes call to Google Calendar API and gets events
def GetCalendarData(days, overdue=False):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    colors = service.colors().get(fields="event").execute()

    # Call the Calendar API
    now = ""
    weekAgo = ""
    weekFromNow = ""
    timeMin = ""
    timeMax = ""
    if overdue:
        weekAgo = datetime.utcnow() - timedelta(days=7)
        weekAgo = weekAgo.isoformat() + "Z"
        now = datetime.utcnow() - timedelta(days=1)
        now = now.isoformat() + "Z"

        timeMin = weekAgo
        timeMax = now
    else:
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        weekFromNow = datetime.utcnow() + timedelta(days=7)
        weekFromNow = weekFromNow.isoformat() + "Z"

        timeMin = now
        timeMax = weekFromNow

    events_result = (
        service.events()
        .list(
            calendarId=calendarID,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=7,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    return events


# Adds task to Google Calendar
def AddTask(task):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    # calendarId='vorcc5hji4duuk2llo532gl3o8@group.calendar.google.com'
    event = service.events().insert(calendarId=calendarID, body=task).execute()

    print("Event created: %s" % (event.get("htmlLink")))


# Updates a task in Google Calendar
def UpdateTask(task, description, type):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    """
    -adding new task
    -modifying task
    """

    taskID = task["id"]
    # First retrieve the event from the API.
    event = service.events().get(calendarId=calendarID, eventId=taskID).execute()

    newDescription = ""

    # adding new task
    if type == 1:
        # print(task)
        # check if there is already a description in the calendar
        split = task["description"].splitlines()
        # print(len(split))
        if len(split) == 1:  # no items in description yet
            if split[0] == " ":
                split.remove(" ")
            newDescription = description + "\n"
        else:  # 1 or more descriptions so far
            split[:] = (value for value in split if value != "")
            if split[0] == " ":
                split.remove(" ")
            split.append(description)
            for x in range(len(split)):
                newDescription = newDescription + "\n" + split[x]
    # updating task
    elif type == 2:
        split = event["description"].splitlines()
        split.append("wow this is a new line")
        # print(split)

        split = [x for x in split if "This" not in x]

        # print(split)

        for x in range(len(split)):
            newDescription = newDescription + "\n" + split[x]

    # """
    # updating task
    event["description"] = newDescription

    updated_event = (
        service.events()
        .update(calendarId=calendarID, eventId=event["id"], body=event)
        .execute()
    )

    # # Print the updated date.
    print("Updated: " + str(updated_event["updated"]))
    print("New Description: " + newDescription)
    # """


# deletes task from google calendar
def DeleteTask(task, description, dueDate):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    """
    -if task is last one left on a day, delete the whole event
    -else update description on all events it is on

    TODO
    -get info from csv
    -figure out if task is last one
    -adjust task/event accordingly
    """
    dueDate = datetime.strptime(dueDate, "%m-%d-%Y").date()

    # figure out if task is last one on event

    # --get dates from today to day before due date
    currentDate = datetime.today().date()
    days = [
        currentDate + timedelta(days=x) for x in range((dueDate - currentDate).days)
    ]

    # --get all the events from this ^ date range from google calendar
    events = GetCalendarData(len(days))
    # --check how many descriptions are per day
    for event in events:
        descriptionOfEvent = event["description"]
        split = descriptionOfEvent.splitlines()
        eventID = event["id"]
        if len(split) <= 2:  # only 1 task, delete this event
            service.events().delete(calendarId=calendarID, eventId=eventID).execute()
            print("deleted event on: " + str(event["start"].get("date")))
        else:  # get rid of it on description and update description
            split = [x for x in split if description not in x]
            if split[0] == "":
                split.pop(0)

            newDescription = ""

            for x in range(len(split)):
                newDescription = newDescription + "\n" + split[x]

            # updating task
            event["description"] = newDescription
            updated_event = (
                service.events()
                .update(calendarId=calendarID, eventId=event["id"], body=event)
                .execute()
            )


# gets rid of task in description on google calendar
def markAsComplete(description, date, completed):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    # get the formatted utc timestamp of the selected date
    result_utc_datetime = getUTCTime(date)

    # get the event from specific date in GC
    events_result = (
        service.events()
        .list(
            calendarId=calendarID,
            timeMin=result_utc_datetime,
            maxResults=1,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    event = events[0]

    # take the description and remove it from the event in GC
    descriptionOfEvent = event["description"]
    split = descriptionOfEvent.splitlines()

    description = "- " + description
    if split[0] == "":
        split.pop(0)

    if description in split:
        split.remove(description)

    newDescription = ""

    for x in range(len(split)):
        newDescription = newDescription + "\n" + split[x]

    # updating task
    event["description"] = newDescription
    updated_event = (
        service.events()
        .update(calendarId=calendarID, eventId=event["id"], body=event)
        .execute()
    )

    # # # Print the updated date.
    # print("Updated: " + str(updated_event["updated"]))
    # print("New Description: " + newDescription)
    # # """


# gets the utc time of a given date and formats it for google calendar
def getUTCTime(date):
    utc_offset_timedelta = datetime.utcnow() - datetime.now()
    local_datetime = datetime.strptime(date, "%b %d, %Y")
    result_utc_datetime = local_datetime + utc_offset_timedelta
    result_utc_datetime = result_utc_datetime.isoformat() + "Z"
    return result_utc_datetime


def reschedule(description, date, dueDate):

    """
    - remove task from current date in google calendar
    - figure out the new amount of time per day
    - update all of the descriptions
    """

    # remove task from calendar
    # markAsComplete(description, date, False)

    # figure out the amount of time per day

    # -- figure out how many of the tasks are overdue at currently

    overdueEvents = GetCalendarData(7, True)
    overdueTaskCounter = 0
    activeEvents = GetCalendarData(7, True)
    activeTaskCounter = 0

    for event in overdueEvents:
        desc = event["description"]
        if description in desc:
            overdueTaskCounter = overdueTaskCounter + 1
    print(overdueTaskCounter)

    for event in activeEvents:
        desc = event["description"]
        if description in desc:
            activeTaskCounter = activeTaskCounter + 1
    print(activeTaskCounter)

    print("RESCHEDULE")


if __name__ == "__main__":
    main()
