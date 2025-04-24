from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
from src.Logic.TimeEntry import TimeEntry
from src.Data.Database import Database
from src.Logic.Login import Login
from src.Logic.Employee import Employee
from datetime import datetime

print("🔎 Server datetime now:", datetime.now())


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("empid"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.secret_key = "supersecretkey"

# @app.route("/")
# def home():
#     menu_choices = {
#         "/report": "View Time Report"
#     }
#     return render_template("index.html", menu_choices=menu_choices)

@app.route("/")
def home():
    if "empid" not in session:
        return redirect("/login")

    role = session.get("emp_role", "user")  # default to user if missing

    menu_choices = {
        "/report": "View Time Report",
        "/log-time": "Log Time"
    }

    if role in ["admin", "manager", "project_manager"]:
        menu_choices["/manage-projects"] = "Projects"

    if role in ["admin", "manager"]:
        menu_choices["/manage-employees"] = "Employees"

    return render_template("index.html", menu_choices=menu_choices)


# @app.route("/report", methods=["GET"])
# @login_required
# def filter_report():
#     empid = request.args.get("employee")
#     start = request.args.get("start")
#     end = request.args.get("end")
#
#     # If any filters are provided, apply them
#     if start:
#         start += " 00:00:00"
#     if end:
#         end += " 23:59:59"
#
#     is_filtering = any([empid, start, end])
#
#     if is_filtering:
#         entries = TimeEntry.get_time_entries_filtered(
#             empid=empid if empid else None,
#             start_date=start if start else None,
#             end_date=end if end else None
#         )
#     else:
#         entries = TimeEntry.get_all_entries()
#
#     # Debug print
#     print("Filters used - empid:", empid, "start:", start, "end:", end)
#
#     all_employees = TimeEntry.get_all_employees()
#
#     return render_template("report.html",
#                            entries=entries,
#                            employees=all_employees)

@app.route("/report", methods=["GET"])
@login_required
def filter_report():
    empid = request.args.get("employee")
    start = request.args.get("start")
    end = request.args.get("end")

    if start:
        start += " 00:00:00"
    if end:
        end += " 23:59:59"

    emp_role = session.get("emp_role")
    session_empid = session.get("empid")

    if emp_role == "individual":
        empid = session_empid
        entries = TimeEntry.get_time_entries_filtered(empid, start, end)
        employees = []

    elif emp_role == "manager":
        managed = Database.get_employees_managed_by(session_empid)
        dptid = Database.get_department_of_employee(session_empid)
        in_dept = Database.get_employees_in_department(dptid)
        all_ids = list(set(managed + in_dept + [session_empid]))

        entries = TimeEntry.get_entries_for_empids(all_ids, start, end)
        employees = TimeEntry.get_all_employees()

    else:  # will need to add specifics in future sprint
        entries = TimeEntry.get_time_entries_filtered(empid, start, end)
        employees = TimeEntry.get_all_employees()

    return render_template("report.html",
                           entries=entries,
                           employees=employees)



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
            session["empid"] = login_record.get_empid()
            session["emp_role"] = login_record.get_role()

            # Get employee details
            employee = Database.get_employee_by_empid(login_record.get_empid())
            if employee:
                session["first_name"] = employee[1]  # assuming first_name is second column

            return redirect("/")
        else:
            return "❌ Invalid email or password."

    return render_template("login.html")


@app.route("/my-time", methods=["GET"])
@login_required
def my_time():
    empid = session.get("empid")
    start = request.args.get("start")
    end = request.args.get("end")

    if start:
        start += " 00:00:00"
    if end:
        end += " 23:59:59"

    if start or end:
        entries = TimeEntry.get_time_entries_filtered(
            empid=empid,
            start_date=start if start else None,
            end_date=end if end else None
        )
    else:
        entries = TimeEntry.get_time_entries_filtered(empid=empid)

    return render_template("myTime.html", entries=entries)


@app.route("/todays-summary")
@login_required

def todays_summary():
    empid = session.get("empid")
    if not empid:
        return redirect("/login")

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59)

    entries = TimeEntry.get_time_entries_filtered(
        empid=empid,
        start_date=today_start.strftime("%Y-%m-%d %H:%M:%S"),
        end_date=today_end.strftime("%Y-%m-%d %H:%M:%S")
    )

    # Summarize total time by project
    for entry in entries:
        print("🧾 Entry:", entry)

    project_summary = {}
    for entry in entries:
        project = entry[3]  # project_name
        minutes = entry[7]  # total_minutes
        minutes = int(minutes)  # throws error if minutes not converted to int
        project_summary[project] = project_summary.get(project, 0) + minutes

    return render_template("todaysSummary.html", entries=entries, project_summary=project_summary)




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
