import mariadb
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime, timezone

local_tz = pytz.timezone("America/Los_Angeles")  # adjust if needed

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

    @classmethod
    def fetch_one(cls, query, params=None):
        cursor = cls.get_cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        return result

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

    # @classmethod
    # def get_visible_employees(cls, current_empid, current_role):
    #     cursor = cls.get_cursor()
    #
    #     if current_role == "admin":
    #         cursor.execute("SELECT EMPID, FIRST_NAME, LAST_NAME FROM employee_table WHERE EMP_ACTIVE = 1")
    #         return cursor.fetchall()
    #
    #     if current_role == "manager":
    #         query = '''
    #             SELECT EMPID, FIRST_NAME, LAST_NAME
    #             FROM employee_table
    #             WHERE EMP_ACTIVE = 1 AND (
    #                 MGR_EMPID = ? OR
    #                 DPTID = (SELECT DPTID FROM employee_table WHERE EMPID = ?)
    #             )
    #         '''
    #         cursor.execute(query, (current_empid, current_empid))
    #         return cursor.fetchall()
    #
    #     # Individual users don't need a dropdown
    #     return []

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

    # ****************************
    # written on 5.12.2025 - EAB
    # ****************************

    @classmethod
    def activate_emp(cls, empid):
        """
        Activates an employee by setting EMP_ACTIVE to 1.

        Args:
            empid: The employee ID to activate

        Returns:
            Boolean indicating whether the activation was successful

        Raises:
            Exception: If there was a database error during the update
        """
        try:
            # First check if the employee exists
            cursor = cls.get_cursor()
            cursor.execute("SELECT COUNT(*) FROM employee_table WHERE EMPID = ?", (empid,))
            if cursor.fetchone()[0] == 0:
                print(f"Employee ID {empid} not found")
                return False

            cursor.execute('''
                UPDATE employee_table
                SET EMP_ACTIVE = 1
                WHERE EMPID = ?
            ''', (empid,))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error activating employee: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

    @classmethod
    def deactivate_emp(cls, empid):
        """
        Deactivates an employee by setting EMP_ACTIVE to 0.

        Args:
            empid: The employee ID to deactivate

        Returns:
            Boolean indicating whether the deactivation was successful

        Raises:
            Exception: If there was a database error during the update
        """
        try:
            # First check if the employee exists
            cursor = cls.get_cursor()
            cursor.execute("SELECT COUNT(*) FROM employee_table WHERE EMPID = ?", (empid,))
            if cursor.fetchone()[0] == 0:
                print(f"Employee ID {empid} not found")
                return False

            cursor.execute('''
                UPDATE employee_table
                SET EMP_ACTIVE = 0
                WHERE EMPID = ?
            ''', (empid,))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error deactivating employee: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

    # ****************************
    # end of 5.12.2025 update - EAB
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

    @classmethod
    def get_projects_by_user(cls, empid):
        cursor = cls.get_cursor()
        query = """
            SELECT DISTINCT p.PROJECTID, p.PROJECT_NAME
            FROM projects p
            LEFT JOIN employee_projects ep ON p.PROJECTID = ep.PROJECT_ID
            WHERE p.PROJECT_ACTIVE = 1
              AND (p.CREATED_BY = ? OR ep.EMPID = ?)
        """
        cursor.execute(query, (empid, empid))
        return cursor.fetchall()

    # *******************************
    # written on 5.4.2025 - EAB
    # *******************************

    @classmethod
    def deactivate_project(cls, projectid):
        """
        Deactivates a project by setting PROJECT_ACTIVE to 0.

        Args:
            projectid: The ID of the project to deactivate
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE projects
            SET PROJECT_ACTIVE = 0
            WHERE PROJECTID = ?
        ''', (projectid,))
        cls.commit()

    @classmethod
    def activate_project(cls, projectid):
        """
        Activates a project by setting PROJECT_ACTIVE to 1.

        Args:
            projectid: The ID of the project to activate
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE projects
            SET PROJECT_ACTIVE = 1
            WHERE PROJECTID = ?
        ''', (projectid,))
        cls.commit()

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

    # ****************************
    # written on 5.12.2025 - EAB
    # ****************************

    @classmethod
    def change_project_name(cls, current_projectid, new_project_name, created_by):
        """
        Creates a new project as a renamed version of an existing project.
        This method performs the following operations:
        1. Creates a new project record with the new name
        2. Sets the current project as inactive
        3. Links the new project to the old one
        4. Updates references in employee_projects and time tables

        Args:
            current_projectid: The ID of the current project to be renamed
            new_project_name: The new name for the project
            created_by: The employee ID of the user making the change

        Returns:
            dict: A dictionary containing 'success' (bool) and 'new_projectid' (if successful)

        Raises:
            Exception: If there was a database error during the process
        """
        try:
            cursor = cls.get_cursor()

            # 1. Check if the current project exists
            cursor.execute("SELECT COUNT(*) FROM projects WHERE PROJECTID = ?", (current_projectid,))
            if cursor.fetchone()[0] == 0:
                print(f"Project ID {current_projectid} not found")
                return {'success': False, 'error': 'Project not found'}

            # 2. Begin transaction
            cls.__connection.autocommit = False

            # 3. Generate a new project ID
            # Note: We don't actually need to generate it manually because
            # there's a trigger that will handle this if we provide an empty PROJECTID
            new_projectid = None  # The trigger will fill this in

            # 4. Create new project with current project as PRIOR_PROJECTID
            date_created = datetime.now(timezone.utc)
            cursor.execute('''
                INSERT INTO projects 
                (PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
                VALUES (?, ?, ?, ?, 1)
            ''', (new_project_name, created_by, date_created, current_projectid))

            # 5. Get the new project ID that was generated by the trigger
            # cursor.execute("SELECT LAST_INSERT_ID()")
            cursor.execute('''
                SELECT PROJECTID FROM projects 
                WHERE PROJECT_NAME = ? AND CREATED_BY = ? AND PRIOR_PROJECTID = ?
                ORDER BY DATE_CREATED DESC
                LIMIT 1
            ''', (new_project_name, created_by, current_projectid))
            new_projectid = cursor.fetchone()[0]

            # If that doesn't work because the database doesn't support LAST_INSERT_ID()
            # Then try to get the new project ID by querying for it
            if not new_projectid:
                cursor.execute('''
                    SELECT PROJECTID FROM projects 
                    WHERE PROJECT_NAME = ? AND CREATED_BY = ? AND DATE_CREATED = ? AND PRIOR_PROJECTID = ?
                ''', (new_project_name, created_by, date_created, current_projectid))
                result = cursor.fetchone()
                if result:
                    new_projectid = result[0]
                else:
                    raise Exception("Failed to retrieve the newly created project ID")

            # 6. Set the current project as inactive
            cursor.execute('''
                UPDATE projects
                SET PROJECT_ACTIVE = 0
                WHERE PROJECTID = ?
            ''', (current_projectid,))

            # 7. Update employee_projects table to reference the new project
            cursor.execute('''
                INSERT INTO employee_projects (EMPID, PROJECT_ID)
                SELECT EMPID, ? 
                FROM employee_projects
                WHERE PROJECT_ID = ?
            ''', (new_projectid, current_projectid))

            # 8. Update ALL time table entries to reference the new project
            # Updated to include all entries regardless of STOP_TIME
            cursor.execute('''
                UPDATE time
                SET PROJECTID = ?
                WHERE PROJECTID = ?
            ''', (new_projectid, current_projectid))

            # 9. Commit the transaction
            cls.commit()

            return {'success': True, 'new_projectid': new_projectid}

        except Exception as e:
            print(f"Error changing project name: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            return {'success': False, 'error': str(e)}

    # ****************************
    # end of 5.12.2025 update - EAB
    # ****************************

# ======================
# 🔹 Department Queries
# ======================

    @classmethod
    def get_departments(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM department")
        return cursor.fetchall()

    @classmethod   # updated on 5.12.2025
    def add_department(cls, dptid, dpt_name, manager_id=None, active=1):
        """
        Adds a new department to the database.

        Args:
            dptid: The department ID (can be empty - auto-generated by trigger)
            dpt_name: The department name
            manager_id: Optional manager ID (can be None)
            active: Department active flag (defaults to 1)
        """
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

    # ****************************
    # written on 5.12.2025 - EAB
    # ****************************

    @classmethod
    def update_department_name(cls, dptid, new_dpt_name):
        """
        Updates the department name (DPT_NAME) for an existing department.

        Args:
            dptid: The ID of the department to update
            new_dpt_name: The new department name to set
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE department
            SET DPT_NAME = ?
            WHERE DPTID = ?
        ''', (new_dpt_name, dptid))
        cls.commit()



    # ****************************
    # end of 5.12.2025 update - EAB
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

    # *******************************
    # written on 5.12.2025 - EAB
    # *******************************

    @classmethod
    def force_password_reset(cls, loginid):
        """
        Forces a password reset by setting FORCE_RESET to 1.

        Args:
            loginid: The ID of the user whose password is being reset
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE login_table
            SET FORCE_RESET = 1
            WHERE LOGINID = ?
        ''', (loginid,))
        cls.commit()

    @classmethod
    def no_force_reset(cls, loginid):
        """
        Negates a forced password reset by setting FORCE_RESET to 0.

        Args:
            loginid: The ID of the user needing a negation of force reset
        """
        cursor = cls.get_cursor()
        cursor.execute('''
            UPDATE login_table
            SET FORCE_RESET = 0
            WHERE LOGINID = ?
        ''', (loginid,))
        cls.commit()

    @classmethod
    def password_reset(cls, loginid, new_password):
        """
        Updates a user's password, sets the reset date to current time, and turns off the force reset flag.

        Args:
            loginid: The login ID of the user
            new_password: The new (already hashed) password to set

        Returns:
            Boolean indicating whether the update was successful

        Raises:
            Exception: If there was a database error during the update
        """
        try:
            # First check if the loginid exists
            cursor = cls.get_cursor()
            cursor.execute("SELECT COUNT(*) FROM login_table WHERE LOGINID = ?", (loginid,))
            if cursor.fetchone()[0] == 0:
                print(f"Login ID {loginid} not found")
                return False

            current_time = datetime.now(timezone.utc)

            cursor.execute('''
                UPDATE login_table
                SET PASSWORD = ?, LAST_RESET = ?, FORCE_RESET = 0
                WHERE LOGINID = ?
            ''', (new_password, current_time, loginid))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error resetting password: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

    # ****************************
    # end of 5.12.2025 update - EAB
    # ****************************

# ======================
# 🔹 TimeEntry Queries
# ======================

    @staticmethod
    def get_timer_by_timeid(timeid):
        query = """
            SELECT t.TIMEID, t.START_TIME, t.STOP_TIME, t.NOTES, t.PROJECTID
            FROM time t
            WHERE t.TIMEID = ? AND t.STOP_TIME IS NULL
        """
        result = Database.fetch_one(query, (timeid,))
        return result

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

        query += " ORDER BY t.STOP_TIME IS NOT NULL, t.STOP_TIME DESC"

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

        query += " ORDER BY t.STOP_TIME IS NOT NULL, t.STOP_TIME DESC"

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

        query += " ORDER BY t.STOP_TIME IS NOT NULL, t.STOP_TIME DESC"

        cursor.execute(query, params)
        return cursor.fetchall()

    @classmethod
    def get_active_timer_for_user(cls, empid):
        cursor = cls.get_cursor()
        cursor.execute('''
            SELECT t.TIMEID, p.PROJECT_NAME, t.START_TIME, t.NOTES
            FROM time t
            JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE t.EMPID = ? AND t.STOP_TIME IS NULL AND t.MANUAL_ENTRY = 0
            ORDER BY t.START_TIME DESC
            LIMIT 1
        ''', (empid,))
        return cursor.fetchone()

    @classmethod
    def start_time_entry(cls, timeid, empid, projectid, start_time, notes):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO time (TIMEID, EMPID, PROJECTID, START_TIME, NOTES, MANUAL_ENTRY)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (timeid, empid, projectid, datetime.now(timezone.utc), notes))
        cls.commit()

    @classmethod
    def stop_time_entry(cls, empid):
        cursor = cls.get_cursor()
        stop_time = datetime.now(timezone.utc)
        cursor.execute('''
            UPDATE time
            SET STOP_TIME = ?
            WHERE EMPID = ? AND STOP_TIME IS NULL
        ''', (stop_time, empid))

        cls.commit()

    # *******************************
    # written on 5.4.2025 - EAB
    # *******************************

    # so DemoData.py can run correctly
    @classmethod
    def erikas_add_time_entry(cls, empid, projectid, start_time, stop_time, notes, manual_entry):
        cursor = cls.get_cursor()

        # Try a simple insert first
        try:
            cursor.execute('''
                INSERT INTO time (EMPID, PROJECTID, START_TIME, STOP_TIME, MANUAL_ENTRY)
                VALUES (%s, %s, %s, %s, %s)
            ''', (empid, projectid, start_time, stop_time, manual_entry))
            cls.commit()
            print("Simple insert successful!")
        except Exception as e:
            print(f"Simple insert failed: {e}")

        # Now try with notes
        try:
            cursor.execute('''
                INSERT INTO time (EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (empid, projectid, start_time, stop_time, notes, manual_entry))
            cls.commit()
            print("Full insert successful!")
        except Exception as e:
            print(f"Full insert failed: {e}")

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

    # ****************************
    # written on 5.12.2025 - EAB
    # ****************************

    @classmethod
    def update_time_entry_both_times(cls, timeid, new_start_time, new_stop_time):
        """
        Updates both START_TIME and STOP_TIME for a time entry.

        Args:
            timeid: The ID of the time entry to update
            new_start_time: The new start time (datetime format)
            new_stop_time: The new stop time (datetime format)

        Returns:
            Boolean indicating whether the update was successful

        Raises:
            Exception: If there was a database error or if stop time is not after start time
        """
        try:
            # Parse the datetime objects if they're strings
            if isinstance(new_start_time, str):
                new_start_time = datetime.strptime(new_start_time, '%Y-%m-%d %H:%M:%S')
            if isinstance(new_stop_time, str):
                new_stop_time = datetime.strptime(new_stop_time, '%Y-%m-%d %H:%M:%S')

            # Validate that stop time is after start time
            if new_stop_time <= new_start_time:
                raise ValueError("Stop time must be after start time")

            # First check if the time entry exists
            cursor = cls.get_cursor()
            cursor.execute("SELECT COUNT(*) FROM time WHERE TIMEID = ?", (timeid,))
            if cursor.fetchone()[0] == 0:
                print(f"Time entry ID {timeid} not found")
                return False

            # Update the time entry
            cursor.execute('''
                UPDATE time
                SET START_TIME = ?, STOP_TIME = ?, MANUAL_ENTRY = 1
                WHERE TIMEID = ?
            ''', (new_start_time, new_stop_time, timeid))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error updating time entry: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

    @classmethod
    def update_time_entry_start(cls, timeid, new_start_time):
        """
        Updates only the START_TIME for a time entry.

        Args:
            timeid: The ID of the time entry to update
            new_start_time: The new start time (datetime format)

        Returns:
            Boolean indicating whether the update was successful

        Raises:
            Exception: If there was a database error or if the new start time is after the existing stop time
        """
        try:
            # Parse the datetime object if it's a string
            if isinstance(new_start_time, str):
                new_start_time = datetime.strptime(new_start_time, '%Y-%m-%d %H:%M:%S')

            # First check if the time entry exists and get the current stop time
            cursor = cls.get_cursor()
            cursor.execute("SELECT STOP_TIME FROM time WHERE TIMEID = ?", (timeid,))
            result = cursor.fetchone()
            if not result:
                print(f"Time entry ID {timeid} not found")
                return False

            # Check if there's a stop time and if so, validate that the new start time is before it
            stop_time = result[0]
            if stop_time and new_start_time >= stop_time:
                raise ValueError("Start time must be before stop time")

            # Update the time entry
            cursor.execute('''
                UPDATE time
                SET START_TIME = ?, MANUAL_ENTRY = 1
                WHERE TIMEID = ?
            ''', (new_start_time, timeid))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error updating start time: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

    @classmethod
    def update_time_entry_stop(cls, timeid, new_stop_time):
        """
        Updates only the STOP_TIME for a time entry.

        Args:
            timeid: The ID of the time entry to update
            new_stop_time: The new stop time (datetime format)

        Returns:
            Boolean indicating whether the update was successful

        Raises:
            Exception: If there was a database error or if the new stop time is before the existing start time
        """
        try:
            # Parse the datetime object if it's a string
            if isinstance(new_stop_time, str):
                new_stop_time = datetime.strptime(new_stop_time, '%Y-%m-%d %H:%M:%S')

            # First check if the time entry exists and get the current start time
            cursor = cls.get_cursor()
            cursor.execute("SELECT START_TIME FROM time WHERE TIMEID = ?", (timeid,))
            result = cursor.fetchone()
            if not result:
                print(f"Time entry ID {timeid} not found")
                return False

            # Validate that the new stop time is after the start time
            start_time = result[0]
            if new_stop_time <= start_time:
                raise ValueError("Stop time must be after start time")

            # Update the time entry
            cursor.execute('''
                UPDATE time
                SET STOP_TIME = ?, MANUAL_ENTRY = 1
                WHERE TIMEID = ?
            ''', (new_stop_time, timeid))
            cls.commit()

            # Return true if at least one row was updated
            rows_updated = cursor.rowcount
            return rows_updated > 0

        except Exception as e:
            print(f"Error updating stop time: {e}")
            cls.__connection.rollback()  # Rollback the transaction in case of error
            raise  # Re-raise the exception for the caller to handle

#   ***** This class method exists for an extreme edge case. Please carefully consider if this
#           action is appropriate before proceeding *****
    @classmethod
    def revert_to_automated(cls, timeid):
        """
        Marks a time entry as non-manual by setting MANUAL_ENTRY to 0.
        This should only be used in specific cases where an entry should
        no longer be considered manually edited.

        Args:
            timeid: The ID of the time entry to update

        Returns:
            Boolean indicating whether the update was successful
        """
        try:
            cursor = cls.get_cursor()
            cursor.execute("SELECT COUNT(*) FROM time WHERE TIMEID = ?", (timeid,))
            if cursor.fetchone()[0] == 0:
                print(f"Time entry ID {timeid} not found")
                return False

            cursor.execute('''
                UPDATE time
                SET MANUAL_ENTRY = 0
                WHERE TIMEID = ?
            ''', (timeid,))
            cls.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error reverting manual entry flag: {e}")
            cls.__connection.rollback()
            raise

    # ****************************
    # end of 5.12.2025 update - EAB
    # ****************************

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
