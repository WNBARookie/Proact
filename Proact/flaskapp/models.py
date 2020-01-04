from flaskapp import db
from datetime import datetime, timezone, timedelta


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    dueDate = db.Column(db.String(200))
    description = db.Column(db.String(200))
    estimatedHours = db.Column(db.Float())
    entryDate = db.Column(db.String(200), default=str(datetime.today().date()))
    timePerDay = db.Column(db.Float())
    timeRemaining = db.Column(db.Float())
    complete = db.Column(db.Boolean)

    """
    -entry date
    -task
    -duedate
    -estimated hours
    -description?
    -completed
    """

    def __repr__(self):
        return f"Task('{self.task}','{self.dueDate}','{self.estimatedHours}','{self.entryDate}','{self.timePerDay}','{self.timeRemaining}','{self.complete}')"
