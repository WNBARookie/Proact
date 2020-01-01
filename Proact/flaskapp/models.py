from flaskapp import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    dueDate = db.Column(db.String(200))
    estimatedHours = db.Column(db.Float())
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
        return f"Task('{self.task}','{self.dueDate}','{self.estimatedHours}','{self.complete}')"
