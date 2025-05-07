from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from src.Logic.TimeEntry import TimeEntry
from src.Data.Database import Database
from src.Logic.Login import Login
from src.Logic.Employee import Employee
from src.Logic.Project import Project
from datetime import datetime, timezone
import uuid

# helper function to normalize minutes column in entries
def normalize_minutes_column(entries, minute_index):
    normalized = []
    for entry in entries:
        entry = list(entry)
        try:
            entry[minute_index] = int(entry[minute_index])
        except (ValueError, TypeError):
            entry[minute_index] = 0
        normalized.append(tuple(entry))
    return normalized
# creates a decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("empid"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


app = Flask(__name__)
app.secret_key = "supersecretkey"

# reformats minutes into Xhr Ymin
@app.template_filter('format_minutes')
def format_minutes(total_minutes):
    try:
        minutes = int(total_minutes)
    except (ValueError, TypeError):
        return "0hr 0min"
    hours = minutes // 60
    remainder = minutes % 60
    return f"{hours}hr {remainder}min"

@app.context_processor
def inject_timer_state():
    return {
        "timer_running": "active_timer_id" in session,
        "log_timer_url": url_for("log_time") if "active_timer_id" in session else None
    }

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
        entries = normalize_minutes_column(entries, 7)
        employees = []

    elif emp_role == "manager":
        managed = Database.get_employees_managed_by(session_empid)
        dptid = Database.get_department_of_employee(session_empid)
        in_dept = Database.get_employees_in_department(dptid)
        all_ids = list(set(managed + in_dept + [session_empid]))

        # Apply filter only if selected empid is in allowed list
        if empid and empid in all_ids:
            filtered_ids = [empid]
        else:
            filtered_ids = all_ids

        entries = TimeEntry.get_entries_for_empids(filtered_ids, start, end)
        entries = normalize_minutes_column(entries, 7)
        employees = [emp for emp in TimeEntry.get_all_employees() if emp[0] in all_ids]

    else:  # future: customize for other roles like admin/project_manager
        entries = TimeEntry.get_time_entries_filtered(empid, start, end)
        entries = normalize_minutes_column(entries, 7)
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
        return redirect("/login")  # test redirect to login

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
        entries = normalize_minutes_column(entries, 7)

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
    entries = normalize_minutes_column(entries, 7)

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


@app.route("/report-todays-summary")
@login_required
def todays_summary_manager():
    if session.get("emp_role") != "manager":
        return redirect("/")

    empid = session.get("empid")
    dptid = Database.get_department_of_employee(empid)
    managed = Database.get_employees_managed_by(empid)
    in_dept = Database.get_employees_in_department(dptid)
    all_ids = list(set(managed + in_dept))

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59)
    today_start_date = today_start.strftime("%B %d, %Y")

    entries = TimeEntry.get_entries_for_empids(
        empids=all_ids,
        start_date=today_start.strftime("%Y-%m-%d %H:%M:%S"),
        end_date=today_end.strftime("%Y-%m-%d %H:%M:%S")
    )
    entries = normalize_minutes_column(entries, 7)

    summary = {}
    for entry in entries:
        emp_name = f"{entry[1]} {entry[2]}"  # first + last
        project = entry[3]  # project name
        minutes = int(entry[7])  # total minutes

        if emp_name not in summary:
            summary[emp_name] = {}

        summary[emp_name][project] = summary[emp_name].get(project, 0) + minutes

    project_totals = {}
    for entry in entries:
        project = entry[3]  # project name
        minutes = int(entry[7])
        project_totals[project] = project_totals.get(project, 0) + minutes

    return render_template("managerSummary.html", summary=summary, project_totals=project_totals,
                           today=today_start_date)


@app.route("/create-project", methods=["GET", "POST"])
@login_required
def create_project():
    empid = session.get("empid")
    role = session.get("emp_role")

    if role not in ["manager", "project_manager", "individual", "admin"]:
        return redirect("/")

    from src.Logic.Project import Project
    from uuid import uuid4

    if request.method == "POST":
        name = request.form.get("project_name")
        selected_empids = request.form.getlist("assigned_employees")

        if not name:
            return "❌ Project name is required."

        projectid = f"P_{uuid4().hex[:8]}"
        new_project = Project(
            projectid=projectid,
            name=name,
            created_by=empid
        )

        try:
            new_project.save_to_database()
            Database.add_employee_to_project(projectid, empid)  # always add creator

            if role in ["manager", "project_manager", "admin"]:
                for eid in selected_empids:
                    if eid != empid:
                        Database.add_employee_to_project(projectid, eid)

            return redirect("/manage-projects")
        except Exception as e:
            return f"❌ Error creating project: {e}"

    # GET request
    eligible_employees = []
    if role in ["manager", "project_manager", "admin"]:
        eligible_employees = Database.get_visible_employees(empid, role)

    return render_template("createProject.html", eligible_employees=eligible_employees)

# @app.route("/project-report", methods=["GET", "POST"])
# @login_required
# def project_report():
#     empid = session.get("empid")
#     role = session.get("emp_role")
#
#     if role != "project_manager":
#         return redirect("/")
#
#     # Projects created or assigned
#     created = [pid for pid, _ in Database.get_all_projects()
#                if Database.get_project_created_by(pid) == empid]
#     assigned = Database.get_project_ids_for_employee(empid)
#     all_visible_project_ids = list(set(created + assigned))
#
#     all_projects = [
#         (pid, name) for pid, name in Database.get_all_projects()
#         if pid in all_visible_project_ids
#     ]
#
#     selected_project = request.form.get("project_id")
#     start = request.form.get("start")
#     end = request.form.get("end")
#
#     entries = []
#
#     if selected_project:
#         if start:
#             start += " 00:00:00"
#         if end:
#             end += " 23:59:59"
#
#         entries = TimeEntry.get_time_entries_filtered(
#             start_date=start if start else None,
#             end_date=end if end else None
#         )
#         entries = [e for e in entries if e[3] == next(name for pid, name in all_projects if pid == selected_project)]
#
#     return render_template("projectReport.html",
#                            projects=all_projects,
#                            entries=entries,
#                            selected_project=selected_project)

@app.route("/project-report", methods=["GET", "POST"])
@login_required
def project_report():
    empid = session.get("empid")
    role = session.get("emp_role")

    if role != "project_manager":
        return redirect("/")

    # Determine view
    view_mode = request.args.get("view", "detailed")

    all_projects = Database.get_all_projects()
    owned_projects = [p for p in all_projects if Database.get_project_created_by(p[0]) == empid]
    assigned_ids = Database.get_project_ids_for_employee(empid)

    # Team projects = projects they're assigned to but don't own
    team_projects = [p for p in all_projects if p[0] in assigned_ids and p not in owned_projects]
    team_ids = [p[0] for p in team_projects]

    if view_mode == "summary":
        selected_project = request.args.get("project")
        summary_ids = [selected_project] if selected_project else team_ids

        summary = Database.get_project_summary(project_ids=summary_ids)
        return render_template("projectReport.html",
                               view_mode="summary",
                               summary=summary,
                               team_projects=team_projects,
                               selected_project=selected_project)

    # detailed view unchanged
    project_filter = request.args.get("project")
    start = request.args.get("start")
    end = request.args.get("end")

    entries = TimeEntry.get_entries_filtered_by_project_ids(
        project_ids=[p[0] for p in owned_projects],
        selected_project=project_filter,
        start=start,
        end=end
    )
    entries = normalize_minutes_column(entries, 6)

    return render_template("projectReport.html",
                           view_mode="detailed",
                           projects=owned_projects,
                           entries=entries,
                           selected_project=project_filter,
                           start=start,
                           end=end)

@app.route("/my-projects")
@login_required
def my_projects():
    empid = session.get("empid")
    all_projects = Database.get_all_projects()  # This returns (PROJECTID, PROJECT_NAME)

    # Filter to only show user's own projects
    my_projects = [
        (pid, name) for pid, name in all_projects
        if Database.get_project_created_by(pid) == empid
    ]

    return render_template("myProjects.html", projects=my_projects)


# @app.route("/manage-projects")
# @login_required
# def manage_projects():
#     empid = session.get("empid")
#     all_projects = Database.get_all_projects()
#     project_membership = Database.get_project_ids_for_employee(empid)
#
#     personal = []
#     team = []
#
#     for pid, name in all_projects:
#         creator = Database.get_project_created_by(pid)
#         members = Database.get_employees_assigned_to_project(pid)
#
#         if empid not in members:
#             continue  # skip if the current user isn’t on this project
#
#         if creator == empid and len(members) == 1:
#             personal.append((pid, name))
#         else:
#             team.append((pid, name))
#
#     return render_template("manageProjects.html", personal=personal, team=team, Database=Database)

# ALTernative version of manage_projects with sorting *****
@app.route("/manage-projects")
@login_required
def manage_projects():
    empid = session.get("empid")
    all_projects = Database.get_all_projects()
    project_membership = Database.get_project_ids_for_employee(empid)

    personal = []
    team = []

    for pid, name in all_projects:
        creator = Database.get_project_created_by(pid)
        members = Database.get_employees_assigned_to_project(pid)

        if empid not in members:
            continue  # skip if not part of project

        if creator == empid and len(members) == 1:
            personal.append((pid, name))
        else:
            owner = Database.get_employee_by_empid(creator)
            team.append({
                "pid": pid,
                "name": name,
                "owner_id": creator,
                "owner_name": f"{owner[1]} {owner[2]}" if owner else "Unknown"
            })

    # Sort team: owned first, then others; alphabetically by project name
    team.sort(key=lambda p: (p["owner_id"] != empid, p["name"].lower()))

    return render_template("altManagerProjectTemp.html", personal=personal, team=team)


@app.route("/project-summary", methods=["GET", "POST"])
@login_required
def project_summary():
    empid = session.get("empid")
    role = session.get("emp_role")

    if role != "project_manager":
        return redirect("/")

    # Get project IDs created or assigned
    created = [pid for pid, _ in Database.get_all_projects()
               if Database.get_project_created_by(pid) == empid]
    assigned = Database.get_project_ids_for_employee(empid)
    all_project_ids = list(set(created + assigned))

    start = request.form.get("start")
    end = request.form.get("end")

    summary = Database.get_project_summary(project_ids=all_project_ids, start=start, end=end)

    return render_template("projectSummary.html", summary=summary, start=start, end=end)

@app.route("/project-detail/<projectid>")
@login_required
def project_detail(projectid):
    # basic data for now, reuse existing functions
    project_name = next((name for pid, name in Database.get_all_projects() if pid == projectid), "Unknown Project")
    entries = TimeEntry.get_entries_filtered_by_project_ids(project_ids=[projectid])
    team = Database.get_employees_assigned_to_project(projectid)
    team_info = [Database.get_employee_by_empid(empid) for empid in team]

    start = request.args.get("start")
    end = request.args.get("end")
    entries = TimeEntry.get_time_entries_filtered(
        empid=None,
        start_date=start + " 00:00:00" if start else None,
        end_date=end + " 23:59:59" if end else None
    )
    entries = TimeEntry.get_entries_filtered_by_project_ids(
        project_ids=[projectid],
        start=start,
        end=end
    )
    entries = normalize_minutes_column(entries, 6)
    print("🔍 Entries for total_minutes:", entries)

    total_minutes = sum(int(e[6]) for e in entries)
    owner_id = Database.get_project_created_by(projectid)
    owner = Database.get_employee_by_empid(owner_id)
    owner_name = f"{owner[1]} {owner[2]}" if owner else "Unknown"

    return render_template("projectDetail.html",
                       projectid=projectid,
                       owner_name=owner_name,
                       team=team_info,
                       total_minutes=total_minutes,
                       entries=entries,
                       start=start,
                       end=end)

@app.route("/log-time", methods=["GET", "POST"])
@login_required
def log_time():
    empid = session.get("empid")

    # Check if timer is already running
    active_timer = Database.get_active_timer_for_user(empid)

    if request.method == "POST" and not active_timer:
        project_id = request.form.get("project_id")
        notes = request.form.get("notes", "")
        timeid = f"t-{uuid.uuid4().hex[:8]}"

        Database.start_time_entry(
            timeid=timeid,
            empid=empid,
            projectid=project_id,
            start_time=datetime.now(),
            notes=notes
        )

        session["active_timer_id"] = timeid
        flash("⏱️ Timer started!", "success")
        return redirect(url_for("log_time"))

    # Fetch user projects for dropdown
    projects = Project.get_projects_for_user(empid)
    print("📦 Projects for user:", projects)

    return render_template("logTime.html", projects=projects, active_timer=active_timer)

@app.route("/stop-timer", methods=["POST"])
@login_required
def stop_timer():
    empid = session.get("empid")
    Database.stop_time_entry(empid)
    session.pop("active_timer_id", None)
    return redirect("/log-time")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
