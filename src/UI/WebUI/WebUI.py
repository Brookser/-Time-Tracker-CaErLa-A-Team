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
    entries = TimeEntry.get_all_entries()  # Will build this in a sec
    return render_template("report.html", entries=entries)

if __name__ == "__main__":
    app.run(debug=True)
