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

# @app.route("/report", methods=["GET"])
# def report_time():
#     entries = TimeEntry.get_all_entries()
#     return render_template("report.html", entries=entries)

# @app.route("/reports", methods=["GET"])
# def reports():
#     empid = request.args.get("employee")
#     start_date = request.args.get("start")
#     end_date = request.args.get("end")
#
#     entries = TimeEntry.get_time_entries_filtered(
#         empid=empid,
#         start_date=start_date,
#         end_date=end_date
#     )
#
#     all_employees = TimeEntry.get_all_employees()
#
#     return render_template("report.html",
#                            entries=entries,
#                            employees=all_employees)
@app.route("/report", methods=["GET"])
def filter_report():
    empid = request.args.get("employee")
    start = request.args.get("start")
    end = request.args.get("end")

    # If any filters are provided, apply them
    if start:
        start += " 00:00:00"
    if end:
        end += " 23:59:59"

    is_filtering = any([empid, start, end])

    if is_filtering:
        entries = TimeEntry.get_time_entries_filtered(
            empid=empid if empid else None,
            start_date=start if start else None,
            end_date=end if end else None
        )
    else:
        entries = TimeEntry.get_all_entries()

    # Debug print
    print("Filters used - empid:", empid, "start:", start, "end:", end)

    all_employees = TimeEntry.get_all_employees()

    return render_template("report.html",
                           entries=entries,
                           employees=all_employees)

if __name__ == "__main__":
    app.run(debug=True)
