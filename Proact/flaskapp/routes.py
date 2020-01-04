from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flaskapp import app, db
from flaskapp.forms import AddTaskForm, UpdateTaskForm
from flaskapp.models import Task

# from models import Task

import sys

sys.path.append("C:\\Users\\tmaro\\Documents\\Code\\testing\\proact_test")

# print(sys.path)

import Proact

# app = Flask(__name__)

# app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///proact.db"
# db = SQLAlchemy(app)


@app.route("/")
def home():
    global events, overdueEvents
    events = Proact.GetCalendarData(7)
    overdueEvents = Proact.GetCalendarData(7, True)
    checkEventToday = True
    if len(events) == 0:
        checkEventToday = False
    tasks = []
    overdueTasks = []
    for event in events:
        date = event["start"].get("date")
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        description = event["description"]
        desc = []
        for des in description.splitlines():
            if des != "":
                desc.append(des)
        tasks.append({"date": date, "description": desc})

    for event in overdueEvents:
        date = event["start"].get("date")
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        description = event["description"]
        desc = []
        for des in description.splitlines():
            if des != "":
                desc.append(des)
        overdueTasks.append({"date": date, "description": desc})

    if checkEventToday:
        firstDate = tasks[0].get("date")
        firstDate = datetime.strptime(firstDate, "%b %d, %Y").date()
        checkEventToday = firstDate == datetime.today().date()

    return render_template(
        "home.html",
        title="Home",
        tasks=tasks,
        overdueTasks=overdueTasks,
        today=True,
        eventToday=checkEventToday,
    )


@app.route("/", methods=["POST"])
def home_submit():
    # events = Proact.GetCalendarData(7)
    checkEventWeek = True
    checkEventToday = True
    if len(events) == 0:
        checkEventWeek = False
        checkEventToday = False
    tasks = []
    overdueTasks = []
    for event in events:
        date = event["start"].get("date")
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        description = event["description"]
        desc = []
        for des in description.splitlines():
            if des != "":
                desc.append(des)
        tasks.append({"date": date, "description": desc})
    for event in overdueEvents:
        date = event["start"].get("date")
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        description = event["description"]
        desc = []
        for des in description.splitlines():
            if des != "":
                desc.append(des)
        overdueTasks.append({"date": date, "description": desc})
    if checkEventToday:
        firstDate = tasks[0].get("date")
        firstDate = datetime.strptime(firstDate, "%b %d, %Y").date()
        checkEventToday = firstDate == datetime.today().date()
    if "today" in request.form:
        return render_template(
            "home.html",
            title="Home",
            tasks=tasks,
            overdueTasks=overdueTasks,
            today=True,
            eventToday=checkEventToday,
        )
    return render_template(
        "home.html",
        title="Home",
        tasks=tasks,
        overdueTasks=overdueTasks,
        today=False,
        eventsForWeek=checkEventWeek,
    )


@app.route("/add", methods=["POST", "GET"])
def add():
    print("ADD\n\n\n\n")

    form = AddTaskForm()
    # print(form.task.data)
    # print(form.dueDate.data)
    # print(form.hoursEstimated.data)
    if form.validate_on_submit():
        task = form.task.data
        dueDate = form.dueDate.data
        dueDate_datetime = datetime.strptime(dueDate, "%m-%d-%Y").date()
        estimatedHours = form.hoursEstimated.data
        timeRemaining = estimatedHours
        completed = False
        daysBetween = Proact.GetDayDiff(dueDate_datetime)
        timePerDay = estimatedHours / daysBetween
        hours, minutes = Proact.GetTimePerDay(estimatedHours, daysBetween)
        description = Proact.CreateDescription(hours, minutes, task)

        Proact.CreateTask(task, dueDate, estimatedHours)
        # print(task)
        # print(dueDate)
        # print(estimatedHours)
        # print(completed)
        # print(timeRemaining)
        # print(timePerDay)
        task = Task(
            task=task,
            dueDate=dueDate,
            description=description,
            estimatedHours=estimatedHours,
            timePerDay=timePerDay,
            timeRemaining=timeRemaining,
            complete=False,
        )

        db.session.add(task)
        db.session.commit()

        flash(f"{form.task.data} added!", "success")
        return redirect(url_for("home"))
    return render_template("form.html", title="Add", form=form, update=False)


@app.route("/update", methods=["POST", "GET"])
def update():
    form = UpdateTaskForm()
    originalTask = form.task.data
    # print(list(request.form.to_dict())[0])
    if "complete" in list(request.form.to_dict())[0]:  # marking as complete
        task = list(request.form.to_dict())[0]
        task = task.split("_")

        date = task[1]
        task = task[2].strip()

        Proact.markAsComplete(task, date, True)

        task = task.split("-->")[0]
        task = task.strip()
        flash(f"{task} for {date} has been marked as completed!", "success")
        return redirect(url_for("home"))

    elif (
        "reschedule" in list(request.form.to_dict())[0]
    ):  # rescheduling an oversheduled event
        # print("HERE")
        task = list(request.form.to_dict())[0]
        task = task.split("_")

        date = task[1]
        task = task[2].strip()
        taskName = task.split("-->")[0]
        taskName = taskName.strip()

        taskItem = Task.query.filter_by(task=taskName).first()
        dueDate = taskItem.dueDate
        # print(dueDate)
        Proact.reschedule(task, date, dueDate)

        return redirect(url_for("home"))
    try:
        task = list(request.form.to_dict())[0]
        task = task.split("-->")[0]
        task = task.strip()
        taskItem = Task.query.filter_by(task=task).first()

        global id
        try:
            id = taskItem.id
        except:
            pass

        task = taskItem.task
        dueDate = taskItem.dueDate
        # print(type(dueDate))
        # print(dueDate)
        # dueDate = datetime.strptime(dueDate, "%Y-%m-%d").date()
        # print(type(dueDate))
        # print(dueDate)
        # dueDate = datetime.strptime(dueDate, "%m-%d-%Y")
        hoursEstimated = taskItem.estimatedHours
        # print(dueDate)
        form.task.default = task
        form.dueDate.default = dueDate
        form.hoursEstimated.default = hoursEstimated
        form.process()
    except:
        print("HERE")
        task = form.task.data
        dueDate = form.dueDate.data
        estimatedHours = form.hoursEstimated.data
        completed = False
        if form.validate_on_submit():
            if "delete" in request.form:  # delete
                taskItem = Task.query.filter_by(id=id).first()
                # print(taskItem)
                # oldTask = taskItem.task
                Proact.DeleteTask(taskItem.task, taskItem.description, taskItem.dueDate)
                # Proact.DeleteCSV(oldTask)
                Task.query.filter_by(id=id).delete()
                db.session.commit()
                flash(f"{taskItem.task} deleted!", "success")
            else:  # update
                taskItem = Task.query.filter_by(id=id).first()
                oldTask = taskItem.task

                # description = taskItem.description.strip("\n")
                # entryDate = taskItem.entryDate
                # dueDate =taskItem.dueDate
                Proact.DeleteTask(taskItem.task, taskItem.description, taskItem.dueDate)
                # Proact.DeleteCSV(oldTask)
                Proact.CreateTask(task, dueDate, estimatedHours)
                taskItem.task = task
                taskItem.dueDate = dueDate
                taskItem.estimatedHours = estimatedHours
                db.session.commit()
                flash(f"{oldTask} updated to {taskItem.task}!", "success")
            return redirect(url_for("home"))

    return render_template("form.html", title="Update", form=form, update=True)


@app.route("/completed", methods=["POST", "GET"])
def completed():
    return "COMPLETE"


id = -1
events = []
overdueEvents = []

if __name__ == "__main__":
    app.run(debug=True)
