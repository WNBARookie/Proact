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


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

calendarID = "vorcc5hji4duuk2llo532gl3o8@group.calendar.google.com"

# Main function
def main():
    # task = CreateTask()
    # AddTask(task)
    # task = GetCalendarData()[0]
    # UpdateTask(task)
    # DeleteTask(task)
    CreateTask()
    # PrintEvents(GetCalendarData(7),7)
    # Menu()


# Function that displays the menu that the user interacts with
def Menu():

    print(
        r"""
======================================================
  _____                      _   
 |  __ \                    | |  
 | |__) | __ ___   __ _  ___| |_ 
 |  ___/ '__/ _ \ / _` |/ __| __|
 | |   | | | (_) | (_| | (__| |_ 
 |_|   |_|  \___/ \__,_|\___|\__|
                                                              
======================================================                                 
"""
    )

    notDecided = True
    choice = ""
    while notDecided:
        print("\n\nWould you like to :")
        print("1 - View all of your tasks")
        print("2 - Add a task")
        print("3 - Update a task")
        print("4 - Delete a task")
        try:
            x = int(input())
            if x != 1 and x != 2 and x != 3 and x != 4:
                print("Please enter 1, 2, 3, or 4")
            else:
                choice = x
                notDecided = False
        except:
            print("Please enter 1, 2, 3, or 4")

    if choice == 1:
        PrintEvents(GetCalendarData(7), 7)
    elif choice == 2:
        CreateTask()
    elif choice == 3:
        print("Which task would you like to update?")


# Creating task based on user input
def CreateTask():
    """
    -get task input
    -calculate how much time per day
    -create the string for the description
    -add to calendar everyday until the day before the due date
    """

    # get task input
    summary, dueDate, hoursEstimate = GetTaskInput()
    # summary, dueDate, hoursEstimate = ("Homework", datetime(2019, 12, 28).date(), 6)

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
    # print(events)
    # ----update each event
    # ------add to CSV
    AddToCSV(events[0], description, summary, dueDate, hoursEstimate)
    for x in range(len(events)):
        UpdateTask(events[x], description, 1)


# """
# get the difference in between the current date and day before due date
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


# Prints out all of the events in the calendar for the upcoming week
def PrintEvents(events, days):
    """
    -date
    -description(has events/tasks and duration)
    """
    eventsFound = False
    try:
        e = events[0]
        eventsFound = True
    except:
        print("There are no events for the next " + str(days) + " days. Take a break!")
    if eventsFound:
        print("Here are the events for the next " + str(days) + " days:")
        for x in range(len(events)):
            # print(x)
            event = events[x]
            # for event in events:
            # print()
            # print("---------------")
            # print(event)
            # print("---------------")
            # print()

            date = event["start"].get("date")
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
            description = event["description"]
            print(description.splitlines())
            print()
            print(date)
            print("---------------")
            print(description)
            print("---------------")
            print()
        """
        #formatted date
        date = event["start"].get("dateTime").split("T")[0]
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %m, %Y")
        #start/end time
        start = event["start"].get("dateTime")
        end = event["end"].get("dateTime")
        #title/description
        title = event["summary"]
        description=event['description']
        #time duration
        time1=start.split('T')[1].split("-")[0]
        time2=end.split('T')[1].split("-")[0]
        timeFormat = '%H:%M:%S'
        duration = datetime.strptime(time2, timeFormat) - datetime.strptime(time1, timeFormat)
        duration=str(duration).split(":")
        hours=duration[0]
        mins=duration[1]
        mins =mins[1:] if mins[0]=="0" else mins #getting rid of leading zero if single digit

        #printing event information
        print()
        print("---------------")
        print("Event: " + title)
        print("Date: " + date)
        print("Description: " + description)
        print("Duration: " + hours +" hours and " + mins + " seconds.")
        print("---------------")
        print()
        """


# Makes call to Google Calendar API and gets events
def GetCalendarData(days):
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
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    # print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId=calendarID,
            timeMin=now,
            maxResults=days,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    # if not events:
    #     print("No upcoming events found.")

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
def DeleteTask(task):
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
    -else modify description on all events it is on
    """

    eventID = task["id"]

    # Deleting event
    service.events().delete(calendarId=calendarID, eventId=eventID).execute()


def AddToCSV(task, description, summary, dueDate, hoursEstimated):
    # file/path name
    path = "C:\\Users\\tmaro\\Documents\\Code\\Projects\\Proact Git\\Proact\\"
    fileName = "calendar_data.csv"

    # creating dataframe
    df = pd.read_csv(path + fileName, sep="\t")
    headers = list(df.columns)

    # creating 2nd dataframe and appending it to original
    df2 = pd.DataFrame(
        [[summary, dueDate, hoursEstimated, description]], columns=headers
    )
    df = df.append(df2, ignore_index=True)

    print(df)
    # writing to csv
    df.to_csv(path + "calendar_data.csv", sep="\t", index=False)


if __name__ == "__main__":
    main()
