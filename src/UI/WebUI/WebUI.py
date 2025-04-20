from flask import Flask, render_template, request
from src.Logic.TimeEntry import TimeEntry
from datetime import datetime


app = Flask(__name__)

@app.route("/")
def home():
    menu_choices = {
        "/report": "View Time Report"
    }
    return render_template("index.html", menu_choices=menu_choices)

@app.route("/report", methods=["GET"])
def report_time():
    entries = TimeEntry.get_all_entries()
    return render_template("report.html", entries=entries)

@app.route("/reports", methods=["GET"])
def reports():
    empid = request.args.get("employee")
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    entries = TimeEntry.get_time_entries_filtered(
        empid=empid,
        start_date=start_date,
        end_date=end_date
    )

    all_employees = TimeEntry.get_all_employees()

    return render_template("report.html",  # Make sure this matches your template name
                           entries=entries,
                           employees=all_employees)


if __name__ == "__main__":
    app.run(debug=True)
