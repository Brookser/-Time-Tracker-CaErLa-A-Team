from datetime import datetime, timedelta
from src.Logic.TimeEntry import TimeEntry


# ***************
# UNCOMMENT EACH TEST TO RUN IT - EDIT DATA WHERE NEEDED
# ***************

# --------------
# DEPARTMENT
# --------------
# def create_department():
#     print("🏗️ Creating department D001...")
#     Database.connect()
#     cursor = Database._Database__connection.cursor()
#
#     # Check if department already exists
#     cursor.execute("SELECT * FROM department WHERE DPTID = ?", ("D001",))
#     if cursor.fetchone():
#         print("✅ Department D001 already exists.")
#         return
#
#     cursor.execute(
#         "INSERT INTO department (DPTID, DPT_NAME) VALUES (?, ?)",
#         ("D001", "Engineering")
#     )
#     Database._Database__connection.commit()
#     print("✅ Department D001 created.")
#
# def main():
#     create_department()

# --------------
# EMPLOYEE
# --------------
# def create_employee():
#     print("👤 Creating employee E001...")
#     try:
#         Database.add_employee(
#             empid="E001",
#             first_name="Casey",
#             last_name="Hill",
#             dptid="D001",
#             email="casey.hill@example.com",
#             mgr_empid=None,
#             active=1
#         )
#         print("✅ Employee E001 created!")
#     except Exception as e:
#         print("❌ Failed to create employee:")
#         print(e)
#
# def main():
#     create_employee()


# --------------
# LOGIN
# --------------
#
# def create_login():
#     print("🔐 Creating login for E001...")
#
#     login = Login(
#         loginid="login_casey",
#         empid="E001",  # needs to exist
#         password="secret123"
#     )
#
#     try:
#         login.save_to_database()
#         print("✅ Login created for EMPID E001.")
#     except Exception as e:
#         print("❌ Failed to create login:")
#         print(e)
#
# def main():
#     create_login()
#


# --------------
# PROJECT
# --------------
# from Logic.Project import Project

# def create_project():
#     print("📁 Creating sample project...")
#
#     project = Project(
#         projectid="P001",
#         name="Time Tracker DB tests",
#         created_by="E001",
#         prior_projectid=None
#     )
#
#     try:
#         project.save_to_database()
#         print("✅ Project P001 created.")
#     except Exception as e:
#         print("❌ Failed to create project:")
#         print(e)
#
# def main():
#     create_project()


# --------------
# TIME ENTRY
# --------------
# from Logic.TimeEntry import TimeEntry

def create_time_entry():
    print("⏱️ Creating time entry...")

    # Set up start/stop for demo (1 hour span)
    start_time = datetime.now() - timedelta(hours=1)
    stop_time = datetime.now()

    entry = TimeEntry(
        empid="E001",  # Must exist
        projectid="P001",  # Must exist
        start_time=start_time,
        stop_time=stop_time,
        notes="Worked on initial setup",
        manual_entry=1
    )

    try:
        entry.save_to_database()
        print("✅ Time entry saved.")
    except Exception as e:
        print("❌ Failed to save time entry:")
        print(e)


def main():
    create_time_entry()


# ALWAYS LEAVE UNCOMMENTED
if __name__ == "__main__":
    main()
