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
    def add_employee(cls, empid, first_name, last_name, dptid, email=None, mgr_empid=None, active=1, emp_role="User"):
        cursor = cls.get_cursor()
        query = '''
            INSERT INTO employee_table
            (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (empid, first_name, last_name, dptid, email, mgr_empid, active, emp_role))
        cls.commit()

    @classmethod
    def get_active_employees(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM employee_table WHERE EMP_ACTIVE = 1")
        return cursor.fetchall()

    @classmethod
    def get_employees_managed_by(cls, manager_id):
        cursor = cls.get_cursor()
        cursor.execute("SELECT EMPID FROM employee_table WHERE MGR_EMPID = ?", (manager_id,))
        return [row[0] for row in cursor.fetchall()]

    @classmethod
    def get_department_of_employee(cls, empid):
        cursor = cls.get_cursor()
        cursor.execute("SELECT DPTID FROM employee_table WHERE EMPID = ?", (empid,))
        result = cursor.fetchone()
        return result[0] if result else None

    @classmethod
    def get_employees_in_department(cls, dptid):
        cursor = cls.get_cursor()
        cursor.execute("SELECT EMPID FROM employee_table WHERE DPTID = ?", (dptid,))
        return [row[0] for row in cursor.fetchall()]

    @classmethod
    def get_visible_employees(cls, current_empid, current_role):
        cursor = cls.get_cursor()

        if current_role == "admin":
            cursor.execute("SELECT EMPID, FIRST_NAME, LAST_NAME FROM employee_table WHERE EMP_ACTIVE = 1")
            return cursor.fetchall()

        if current_role == "manager":
            query = '''
                SELECT EMPID, FIRST_NAME, LAST_NAME 
                FROM employee_table 
                WHERE EMP_ACTIVE = 1 AND (
                    MGR_EMPID = ? OR 
                    DPTID = (SELECT DPTID FROM employee_table WHERE EMPID = ?)
                )
            '''
            cursor.execute(query, (current_empid, current_empid))
            return cursor.fetchall()

        # Individual users don't need a dropdown
        return []

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

    @classmethod
    def add_department(cls, dptid, dpt_name, manager_id=None, active=1):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO department (DPTID, DPT_NAME, MANAGERID, DPT_ACTIVE)
            VALUES (?, ?, ?, ?)
        ''', (dptid, dpt_name, manager_id, active))
        cls.commit()

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

    @classmethod
    def get_login_by_email(cls, email):
        cursor = cls.get_cursor()
        cursor.execute('''
            SELECT l.LOGINID, l.EMPID, l.PASSWORD, l.LAST_RESET, l.FORCE_RESET, e.EMP_ROLE
            FROM login_table l
            JOIN employee_table e ON l.EMPID = e.EMPID
            WHERE e.EMAIL_ADDRESS = ?
        ''', (email,))
        return cursor.fetchone()

    @classmethod
    def get_employee_by_empid(cls, empid):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM employee_table WHERE EMPID = ?", (empid,))
        return cursor.fetchone()


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
        cursor.execute('''
            SELECT 
                t.EMPID,
                CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS employee_name,
                t.PROJECTID,
                p.PROJECT_NAME,
                t.START_TIME,
                t.STOP_TIME,
                t.TOTAL_MINUTES,
                t.NOTES
            FROM time t
            JOIN employee_table e ON t.EMPID = e.EMPID
            JOIN projects p ON t.PROJECTID = p.PROJECTID
        ''')
        return cursor.fetchall()

    @classmethod
    def get_time_entries_filtered_multiple_empids(cls, empids, start_date=None, end_date=None):
        cursor = cls.get_cursor()

        placeholders = ','.join('?' for _ in empids)
        query = f'''
            SELECT t.TIMEID, e.FIRST_NAME, e.LAST_NAME, p.PROJECT_NAME, 
                   t.START_TIME, t.STOP_TIME, t.NOTES, t.TOTAL_MINUTES
            FROM time t
            JOIN employee_table e ON t.EMPID = e.EMPID
            JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE t.EMPID IN ({placeholders})
        '''
        params = empids

        if start_date:
            query += " AND t.START_TIME >= ?"
            params.append(start_date)
        if end_date:
            query += " AND t.STOP_TIME <= ?"
            params.append(end_date)

        print("🔍 Manager Query:", query)
        print("📦 Params:", params)

        cursor.execute(query, params)
        return cursor.fetchall()

    @classmethod
    def get_time_entries_filtered(cls, start_date=None, end_date=None, empid=None):
        cursor = cls.get_cursor()

        query = '''
            SELECT t.TIMEID, e.FIRST_NAME, e.LAST_NAME, p.PROJECT_NAME, 
                   t.START_TIME, t.STOP_TIME, t.NOTES, t.TOTAL_MINUTES
            FROM time t
            JOIN employee_table e ON t.EMPID = e.EMPID
            JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE 1=1
        '''
        params = []

        # 🔽 Add each condition individually
        if start_date:
            query += " AND t.START_TIME >= ?"
            params.append(start_date)

        if end_date:
            query += " AND t.STOP_TIME <= ?"
            params.append(end_date)

        if empid:
            query += " AND t.EMPID = ?"
            params.append(empid)

        # Debug
        print("🔍 Query:", query)
        print("📦 Params:", params)

        cursor.execute(query, params)
        return cursor.fetchall()



