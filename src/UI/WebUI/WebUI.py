from flask import Flask, render_template, request, redirect
from src.Logic.TimeEntry import TimeEntry
from src.Data.Database import Database
from src.Logic.Login import Login
from src.Logic.Employee import Employee
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

@app.route("/create-account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        empid = request.form.get("empid")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dptid = request.form.get("dptid")
        email = request.form.get("email")
        mgr_empid = request.form.get("mgr_empid") or None
        emp_role = request.form.get("emp_role")
        password = request.form.get("password")

        # Create employee
        try:
            Database.add_employee(empid, first_name, last_name, dptid, email, mgr_empid, active=1, emp_role=emp_role)
        except Exception as e:
            return f"❌ Error creating employee: {e}"

        # Create login
        try:
            login = Login(loginid=f"login_{empid}", empid=empid, password=password)
            login.save_to_database()
        except Exception as e:
            return f"❌ Error creating login: {e}"

        # return redirect("/")  # or render_template("account_created.html")
        return redirect("/login") # test redirect to login

    return render_template("createAccount.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        login_record = Login.get_by_email(email)

        if login_record and login_record.get_password() == password:
            return redirect("/")
        else:
            return "❌ Invalid email or password."

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
