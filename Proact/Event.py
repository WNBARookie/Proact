from datetime import datetime, timezone

class Event:
    def __init__(self, summary, start, end, reminders, timezone, description):
        self.summary = summary
        self.start = start
        self.end = end
        self.reminders = reminders
        self.timezone = timezone
        self.description = description

        self.start = self.createTime(self.start)
        self.end = self.createTime(self.end)

    def createTime(self, time):
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        # print(time)
        time=time.split(" ")
        date = time[0]
        # time = time[1]

        dateObject=datetime.strptime(date, "%Y-%m-%d").date()

        # print(type(dateObject))
        # print(dateObject)
        # newTime = date + "T" + time + "-06:00"

        return str(dateObject)

    def createReminders(self):
        pass
