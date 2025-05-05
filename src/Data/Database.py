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

    # ****************************
    # written on 5.4.2025 - EAB
    # ****************************

    @classmethod
    def update_employee_manager(cls, empid, new_mgr_empid):
        """
        Updates the manager (MGR_EMPID) for an employee.

        Args:
            empid: The ID of the employee to update
            new_mgr_empid: The new manager's employee ID (can be None to remove manager)
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE employee_table
            SET MGR_EMPID = ?
            WHERE EMPID = ?
        ''', (new_mgr_empid, empid))
        cls.commit()

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

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

    @classmethod
    def get_project_created_by(cls, projectid):
        cursor = cls.get_cursor()
        cursor.execute("SELECT CREATED_BY FROM projects WHERE PROJECTID = ?", (projectid,))
        result = cursor.fetchone()
        return result[0] if result else None


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

        if current_role == "project_manager":
            cursor.execute("SELECT EMPID, FIRST_NAME, LAST_NAME FROM employee_table WHERE EMP_ACTIVE = 1")
            return cursor.fetchall()

        return []

    @classmethod
    def get_project_ids_for_employee(cls, empid):
        cursor = cls.get_cursor()
        cursor.execute('''
            SELECT PROJECT_ID FROM employee_projects
            WHERE EMPID = ?
        ''', (empid,))
        return [row[0] for row in cursor.fetchall()]

    @classmethod
    def add_employee_to_project(cls, project_id, empid):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO employee_projects (PROJECT_ID, EMPID)
            VALUES (?, ?)
        ''', (project_id, empid))
        cls.commit()

    @classmethod
    def get_project_summary(cls, project_ids, start=None, end=None):
        if not project_ids:
            return []

        cursor = cls.get_cursor()
        placeholders = ','.join('?' for _ in project_ids)
        params = list(project_ids)

        query = f'''
            SELECT 
                p.PROJECT_NAME,
                p.PROJECTID,
                COUNT(DISTINCT t.EMPID) AS employee_count,
                SUM(t.TOTAL_MINUTES) AS total_minutes
            FROM time t
            JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE t.PROJECTID IN ({placeholders})
        '''

        if start:
            query += " AND t.START_TIME >= ?"
            params.append(start + " 00:00:00")
        if end:
            query += " AND t.STOP_TIME <= ?"
            params.append(end + " 23:59:59")

        query += " GROUP BY p.PROJECTID"

        cursor.execute(query, params)
        return cursor.fetchall()

    @classmethod
    def get_employees_assigned_to_project(cls, projectid):
        cursor = cls.get_cursor()
        cursor.execute('''
            SELECT EMPID FROM employee_projects
            WHERE PROJECT_ID = ?
        ''', (projectid,))
        return [row[0] for row in cursor.fetchall()]


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



    # ****************************
    # written on 5.4.2025 - EAB
    # ****************************

    @classmethod
    def deactivate_department(cls, dptid):
        """
        Deactivates a department by setting DPT_ACTIVE to 0.

        Args:
            dptid: The ID of the department to deactivate
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE departments
            SET DPT_ACTIVE = 0
            WHERE PROJECTID = ?
        ''', (dptid,))
        cls.commit()

    @classmethod
    def activate_department(cls, dptid):
        """
        Activates a department by setting DPT_ACTIVE to 1.

        Args:
            dptid: The ID of the department to activate
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE departments
            SET PROJECT_ACTIVE = 1
            WHERE PROJECTID = ?
        ''', (dptid,))
        cls.commit()

    @classmethod
    def update_manager_ID(cls, dptid, new_mgr_empid):
        """
        Updates the manager (MANAGERID) for an department.

        Args:
            dptid: The ID of the department to update
            new_mgr_empid: The new manager's employee ID (can be None to remove manager)
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE departments
            SET MANAGERID = ?
            WHERE DPTID = ?
        ''', (new_mgr_empid, dptid))
        cls.commit()

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************



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


    # test consolidated project reporting page below
    @classmethod
    def get_time_entries_filtered_by_projects(cls, project_ids, selected_project=None, start_date=None, end_date=None):
        cursor = cls.get_cursor()

        placeholders = ','.join('?' for _ in project_ids)
        query = f'''
            SELECT t.TIMEID, e.FIRST_NAME, e.LAST_NAME, p.PROJECT_NAME,
                   t.START_TIME, t.STOP_TIME, t.TOTAL_MINUTES, t.NOTES
            FROM time t
            JOIN employee_table e ON t.EMPID = e.EMPID
            JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE t.PROJECTID IN ({placeholders})
        '''
        params = list(project_ids)

        if selected_project:
            query += ' AND t.PROJECTID = ?'
            params.append(selected_project)

        if start_date:
            query += ' AND t.START_TIME >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND t.STOP_TIME <= ?'
            params.append(end_date)

        print("🔍 Project report query:", query)
        print("📦 Params:", params)

        cursor.execute(query, params)
        return cursor.fetchall()

    # ****************************
    # written on 4.29.25 - EAB
    # ****************************

    @classmethod
    def update_notes(cls, timeid, new_notes):
        """
        Updates the notes field for an existing time entry.

        Args:
            timeid: The ID of the time entry to update
            new_notes: The new notes text to set
        """
        cursor = cls.get_cursor()
        cursor.execute('''
                    UPDATE time_entries
                    SET NOTES = ?
                    WHERE TIMEID = ?
                ''', (new_notes, timeid))
        cls.commit()

    # ****************************
    # end of 4.29.25 update - EAB
    # ****************************

    # ****************************
    # written on 5.4.25 - EAB
    # ****************************

    @classmethod
    def update_projectid(cls, timeid, new_projectid):
        """
        Updates the PROJECTID field for an existing time entry.

        Args:
            timeid: The ID of the time entry to update
            projectid: The new PROJECTID
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE projects
            SET PROJECTID = ?
            WHERE TIMEID = ?
        ''', (new_projectid, timeid))
        cls.commit()


    @classmethod
    def manual_note_true(cls, timeid):
        """
        Indicates a manual note by setting MANUAL_ENTRY to 1.

        Args:
            timeid: The ID of the entry to update
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE departments
            SET MANUAL_ENTRY = 1
            WHERE TIMEID = ?
        ''', (timeid,))
        cls.commit()

    @classmethod
    def add_manual_time_entry(cls, empid, projectid, start_datetime, stop_datetime, notes=None):
        """
        Add a manual time entry to the database.

        Args:
            empid: Employee ID
            projectid: Project ID
            start_datetime: Start datetime in format 'YYYY-MM-DD HH:MM:SS'
            stop_datetime: Stop datetime in format 'YYYY-MM-DD HH:MM:SS'
            notes: Optional notes for the time entry

        Note: If seconds are not provided, they will default to :00
        """
        cursor = cls.get_cursor()

        # If the datetime doesn't include seconds, add :00
        if len(start_datetime.split(':')) == 2:
            start_datetime += ':00'
        if len(stop_datetime.split(':')) == 2:
            stop_datetime += ':00'

        # Calculate total minutes
        from datetime import datetime
        start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
        stop_dt = datetime.strptime(stop_datetime, '%Y-%m-%d %H:%M:%S')
        total_minutes = int((stop_dt - start_dt).total_seconds() / 60)

        # Insert the time entry with manual_entry flag set to 1
        cursor.execute('''
            INSERT INTO time 
            (EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, TOTAL_MINUTES)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (empid, projectid, start_datetime, stop_datetime, notes, total_minutes))
        cls.commit()

#                      *** EXAMPLES OF HOW TO USE ***
#                            Database.add_manual_time_entry(
#                                empid='E001',
#                                projectid='P001',
#                                start_date='2025-05-04',
#                                start_time='09:30',
#                                stop_date='2025-05-04',
#                                stop_time='17:45',
#                                notes='Manual entry for client meeting'
#                            )
#
#                        *** Or with a version that accepts full datetime strings
#                            Database.add_manual_time_entry(
#                                empid='E001',
#                                projectid='P001',
#                                start_datetime='2025-05-04 09:30',
#                                stop_datetime='2025-05-04 17:45',
#                                notes='Manual entry for client meeting'
#                            )

    # ****************************
    # end of 5.4.25 update - EAB
    # ****************************


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

        if start_date and end_date:
            query += " AND t.START_TIME BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        if empid:
            query += " AND t.EMPID = ?"
            params.append(empid)

        if empid:
            query += " AND t.EMPID = ?"
            params.append(empid)

        # Debug
        print("🔍 Query:", query)
        print("📦 Params:", params)

        cursor.execute(query, params)
        return cursor.fetchall()



# ======================
# 🔹 EmployeeProject Queries
# ======================

    # ****************************
    # written on 5.4.2025 - EAB
    # ****************************

    @classmethod
    def add_employee_project(cls, empid, project_id):
        """
        Add an employee-project relationship to the employee_projects junction table.

        Args:
            empid: The employee ID
            project_id: The project ID
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO employee_projects (EMPID, PROJECT_ID)
            VALUES (?, ?)
        ''', (empid, project_id))
        cls.commit()



    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

