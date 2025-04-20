import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    __connection = None

    @classmethod
    def connect(cls):
        if cls.__connection is None:
            cls.__connection = mariadb.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                database=os.getenv("DB_NAME")
            )

    @classmethod
    def get_cursor(cls):
        cls.connect()
        return cls.__connection.cursor()

    @classmethod
    def commit(cls):
        cls.__connection.commit()


    # ======================
    # 🔹 Employee Queries
    # ======================

    @classmethod
    def add_employee(cls, empid, first_name, last_name, dptid, email=None, mgr_empid=None, active=1):
        cursor = cls.get_cursor()
        query = '''
            INSERT INTO employee_table
            (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (empid, first_name, last_name, dptid, email, mgr_empid, active))
        cls.commit()

    @classmethod
    def get_active_employees(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM employee_table WHERE EMP_ACTIVE = 1")
        return cursor.fetchall()


    # ======================
    # 🔹 Project Queries
    # ======================

    @classmethod
    def add_project(cls, projectid, name, created_by, date_created, prior_projectid=None, active=1):
        print("🚀 Calling DB insert for project:", projectid)
        print("📆 date_created type:", type(date_created))
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO projects 
            (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (projectid, name, created_by, date_created, prior_projectid, active))
        cls.commit()

    @classmethod
    def get_all_projects(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT PROJECTID, PROJECT_NAME FROM projects")
        return cursor.fetchall()

    @classmethod
    def get_active_projects(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT PROJECTID, PROJECT_NAME FROM projects WHERE PROJECT_ACTIVE = 1")
        return cursor.fetchall()


    # ======================
    # 🔹 Department Queries
    # ======================

    @classmethod
    def get_departments(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM department")
        return cursor.fetchall()

    # ======================
    # 🔹 Login Queries
    # ======================
    @classmethod
    def get_login_by_empid(cls, empid):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM login_table WHERE EMPID = ?", (empid,))
        return cursor.fetchone()

    @classmethod
    def add_login(cls, loginid, empid, password, last_reset=None, force_reset=0):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO login_table (LOGINID, EMPID, PASSWORD, LAST_RESET, FORCE_RESET)
            VALUES (?, ?, ?, ?, ?)
        ''', (loginid, empid, password, last_reset, force_reset))
        cls.commit()

    @classmethod
    def update_password(cls, empid, new_password, last_reset, force_reset=0):
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE login_table
            SET PASSWORD = ?, LAST_RESET = ?, FORCE_RESET = ?
            WHERE EMPID = ?
        ''', (new_password, last_reset, force_reset, empid))
        cls.commit()


# ======================
# 🔹 TimeEntry Queries
# ======================

    @classmethod
    def add_time_entry(cls, empid, projectid, start_time, stop_time, notes, manual_entry, total_minutes):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO time 
            (EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, TOTAL_MINUTES)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (empid, projectid, start_time, stop_time, notes, manual_entry, total_minutes))
        cls.commit()

    @classmethod
    def get_all_time_entries(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM time")
        return cursor.fetchall()
