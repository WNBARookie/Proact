from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime, timezone, timedelta
from flask import flash
from flaskapp.models import Task


class AddTaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    dueDate = StringField("Date", validators=[DataRequired()])
    hoursEstimated = FloatField(
        "Hours Estimated",
        validators=[DataRequired("Hour estimate needs to be greater than 0.")],
    )
    submit = SubmitField("Add Task")

    def validate_task(self, task):
        print("TASK")
        task = Task.query.filter_by(task=task.data).first()
        if task:
            raise ValidationError(
                "That task is already currently active. Please choose a different one."
            )

    def validate_hoursEstimated(self, hoursEstimated):
        if hoursEstimated.data <= 0:
            raise ValidationError("Hour estimate needs to be greater than 0.")

    def validate_dueDate(self, dueDate):
        date = dueDate.data
        try:
            date = datetime.strptime(date, "%m-%d-%Y").date()
        except:
            raise ValidationError(
                "Please enter a valid date that is at least 2 days after today's date using the format MM-DD-YYYY."
            )

        # check if date is after today
        if date > datetime.today().date() + timedelta(days=1):
            invalidDate = False

        else:
            raise ValidationError(
                "Please enter a valid date that is at least 2 days after today's date using the format MM-DD-YYYY."
            )


class UpdateTaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    dueDate = StringField("Date", validators=[DataRequired()])
    hoursEstimated = FloatField("Hours Estimated", validators=[DataRequired()])
    submit = SubmitField("Update Task")
    delete = SubmitField("Delete")

    def validate_hoursEstimated(self, hoursEstimated):
        if hoursEstimated.data <= 0:
            raise ValidationError("Hour estimate needs to be greater than 0.")

    def validate_dueDate(self, dueDate):
        date = dueDate.data
        try:
            date = datetime.strptime(date, "%m-%d-%Y").date()
        except:
            raise ValidationError(
                "Please enter a valid date that is at least 2 days after today's date using the format MM-DD-YYYY."
            )

        # check if date is after today
        if date > datetime.today().date() + timedelta(days=1):
            invalidDate = False

        else:
            raise ValidationError(
                "Please enter a valid date that is at least 2 days after today's date using the format MM-DD-YYYY."
            )
