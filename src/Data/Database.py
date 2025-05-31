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
    def add_time_entry(cls,
                       timeid,
                       empid,
                       projectid,
                       start_time,
                       stop_time,
                       notes,
                       manual_entry,
                       total_minutes):
        cursor = cls.get_cursor()
        cursor.execute('''
            INSERT INTO time 
            (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timeid, empid, projectid, start_time, stop_time, notes, manual_entry))
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
    def remove_time_entry(cls, timeid):
        """
        Removes a time entry from the database.

        Args:
            timeid: The ID of the time entry to remove

        Returns:
            dict: A dictionary containing 'success' (bool) and additional information

        Raises:
            Exception: If there was a database error during the deletion
        """
        try:
            # First check if the time entry exists and get some details for logging
            cursor = cls.get_cursor()
            cursor.execute("""
                SELECT t.EMPID, e.FIRST_NAME, e.LAST_NAME, t.PROJECTID, p.PROJECT_NAME, 
                       t.START_TIME, t.STOP_TIME 
                FROM time t
                JOIN employee_table e ON t.EMPID = e.EMPID
                JOIN projects p ON t.PROJECTID = p.PROJECTID
                WHERE t.TIMEID = ?
            """, (timeid,))

            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': f"Time entry ID {timeid} not found"}

            # Store details for return information
            empid, first_name, last_name, projectid, project_name, start_time, stop_time = result

            # Begin transaction
            cls.__connection.autocommit = False

            # Delete the time entry
            cursor.execute("DELETE FROM time WHERE TIMEID = ?", (timeid,))

            # Check if any rows were affected
            rows_deleted = cursor.rowcount
            if rows_deleted == 0:
                cls.__connection.rollback()
                return {'success': False, 'error': f"No time entry found with ID {timeid}"}

            # Commit the transaction
            cls.commit()

            # Return success with details of the deleted entry
            return {
                'success': True,
                'deleted_entry': {
                    'timeid': timeid,
                    'empid': empid,
                    'employee_name': f"{first_name} {last_name}",
                    'projectid': projectid,
                    'project_name': project_name,
                    'start_time': start_time,
                    'stop_time': stop_time
                }
            }

        except Exception as e:
            print(f"Error removing time entry: {e}")
            # Ensure we rollback in case of error
            if hasattr(cls, '__connection') and cls.__connection:
                cls.__connection.rollback()
            return {'success': False, 'error': str(e)}

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

    @classmethod
    def get_time_entry_notes(cls, timeid):
        """
        Get the notes for a specific time entry.

        Args:
            timeid (str): Time entry ID to get notes for

        Returns:
            str: Notes text, or None if time entry doesn't exist
        """
        cursor = cls.get_cursor()
        query = "SELECT NOTES FROM time WHERE TIMEID = ?"
        cursor.execute(query, (timeid,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    @classmethod
    def get_all_time_entry_notes(cls, empid=None, projectid=None):
        """
        Get notes for multiple time entries with optional filtering.

        Args:
            empid (str, optional): Filter by employee ID
            projectid (str, optional): Filter by project ID

        Returns:
            list: List of tuples containing (TIMEID, EMPID, PROJECTID, START_TIME, NOTES)
        """
        cursor = cls.get_cursor()

        base_query = """
               SELECT TIMEID, EMPID, PROJECTID, START_TIME, NOTES 
               FROM time 
               WHERE NOTES IS NOT NULL AND NOTES != ''
           """
        params = []

        if empid:
            base_query += " AND EMPID = ?"
            params.append(empid)

        if projectid:
            base_query += " AND PROJECTID = ?"
            params.append(projectid)

        base_query += " ORDER BY START_TIME DESC"

        cursor.execute(base_query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def get_all_time_entry_notes(cls, empid=None, projectid=None):
        """
        Get notes for multiple time entries with optional filtering.

        Args:
            empid (str, optional): Filter by employee ID
            projectid (str, optional): Filter by project ID

        Returns:
            list: List of tuples containing (TIMEID, EMPID, PROJECTID, START_TIME, NOTES)
        """
        cursor = cls.get_cursor()

        base_query = """
               SELECT TIMEID, EMPID, PROJECTID, START_TIME, NOTES 
               FROM time 
               WHERE NOTES IS NOT NULL AND NOTES != ''
           """
        params = []

        if empid:
            base_query += " AND EMPID = ?"
            params.append(empid)

        if projectid:
            base_query += " AND PROJECTID = ?"
            params.append(projectid)

        base_query += " ORDER BY START_TIME DESC"

        cursor.execute(base_query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def get_flagged_time_entries(cls, empid=None, include_employee_details=False):
        """
        Get all time entries that are flagged for review.

        Args:
            empid (str, optional): Filter by specific employee ID
            include_employee_details (bool): Whether to include employee name and department info

        Returns:
            list: List of tuples containing time entry information
        """
        cursor = cls.get_cursor()

        if include_employee_details:
            query = """
                    SELECT 
                        t.TIMEID, 
                        t.EMPID, 
                        CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as EMPLOYEE_NAME,
                        e.DPTID,
                        t.PROJECTID, 
                        t.START_TIME, 
                        t.STOP_TIME, 
                        t.TOTAL_MINUTES,
                        t.NOTES, 
                        t.MANUAL_ENTRY,
                        t.FLAGGED_FOR_REVIEW
                    FROM time t
                    INNER JOIN employee_table e ON t.EMPID = e.EMPID
                    WHERE t.FLAGGED_FOR_REVIEW = 1
                """
        else:
            query = """
                    SELECT TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, 
                           TOTAL_MINUTES, NOTES, MANUAL_ENTRY, FLAGGED_FOR_REVIEW
                    FROM time 
                    WHERE FLAGGED_FOR_REVIEW = 1
                """

        if empid:
            query += " AND t.EMPID = ?" if include_employee_details else " AND EMPID = ?"

        query += " ORDER BY START_TIME DESC"

        cursor.execute(query, (empid,) if empid else ())
        result = cursor.fetchall()
        cursor.close()

    @classmethod
    def get_flagged_entries_by_manager(cls, manager_empid):
        """
        Get all flagged time entries for employees managed by a specific manager.

        Args:
            manager_empid (str): Manager's employee ID

        Returns:
            list: List of tuples containing flagged entries for managed employees
        """
        cursor = cls.get_cursor()
        query = """
               SELECT 
                   t.TIMEID, 
                   t.EMPID, 
                   CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as EMPLOYEE_NAME,
                   e.DPTID,
                   t.PROJECTID, 
                   t.START_TIME, 
                   t.STOP_TIME, 
                   t.TOTAL_MINUTES,
                   t.NOTES, 
                   t.FLAGGED_FOR_REVIEW
               FROM time t
               INNER JOIN employee_table e ON t.EMPID = e.EMPID
               WHERE t.FLAGGED_FOR_REVIEW = 1 
               AND e.MGR_EMPID = ?
               ORDER BY t.START_TIME DESC
           """
        cursor.execute(query, (manager_empid,))
        result = cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def flag_time_entry_for_review(cls, timeid):
        """
        Flag a time entry for manager review.

        Args:
            timeid (str): Time entry ID to flag

        Returns:
            bool: True if successful, False if time entry doesn't exist

        Raises:
            Exception: If database error occurs
        """
        cursor = cls.get_cursor()

        try:
            # Check if time entry exists
            cursor.execute("SELECT TIMEID FROM time WHERE TIMEID = ?", (timeid,))
            if not cursor.fetchone():
                return False

            # Flag the entry for review
            cursor.execute("UPDATE time SET FLAGGED_FOR_REVIEW = 1 WHERE TIMEID = ?", (timeid,))
            cls.commit()
            return True

        except Exception as e:
            cls.__connection.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def unflag_time_entry(cls, timeid):
        """
        Remove review flag from a time entry (mark as reviewed/approved).

        Args:
            timeid (str): Time entry ID to unflag

        Returns:
            bool: True if successful, False if time entry doesn't exist

        Raises:
            Exception: If database error occurs
        """
        cursor = cls.get_cursor()

        try:
            # Check if time entry exists
            cursor.execute("SELECT TIMEID FROM time WHERE TIMEID = ?", (timeid,))
            if not cursor.fetchone():
                return False

            # Remove the review flag
            cursor.execute("UPDATE time SET FLAGGED_FOR_REVIEW = 0 WHERE TIMEID = ?", (timeid,))
            cls.commit()
            return True

        except Exception as e:
            cls.__connection.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def toggle_review_flag(cls, timeid):
        """
        Toggle the review flag status of a time entry.

        Args:
            timeid (str): Time entry ID to toggle

        Returns:
            bool: New flag status (True if now flagged, False if now unflagged), or None if entry doesn't exist

        Raises:
            Exception: If database error occurs
        """
        cursor = cls.get_cursor()

        try:
            # Get current flag status
            cursor.execute("SELECT FLAGGED_FOR_REVIEW FROM time WHERE TIMEID = ?", (timeid,))
            result = cursor.fetchone()

            if not result:
                return None

            current_flag = result[0]
            new_flag = 0 if current_flag else 1

            # Update the flag
            cursor.execute("UPDATE time SET FLAGGED_FOR_REVIEW = ? WHERE TIMEID = ?", (new_flag, timeid))
            cls.commit()
            return bool(new_flag)

        except Exception as e:
            cls.__connection.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def bulk_unflag_time_entries(cls, timeid_list):
        """
        Remove review flags from multiple time entries at once.

        Args:
            timeid_list (list): List of time entry IDs to unflag

        Returns:
            int: Number of entries successfully unflagged

        Raises:
            Exception: If database error occurs
        """
        cursor = cls.get_cursor()

        try:
            if not timeid_list:
                return 0

            # Create placeholders for the IN clause
            placeholders = ','.join(['?' for _ in timeid_list])
            query = f"UPDATE time SET FLAGGED_FOR_REVIEW = 0 WHERE TIMEID IN ({placeholders})"

            cursor.execute(query, timeid_list)
            affected_rows = cursor.rowcount
            cls.commit()
            return affected_rows

        except Exception as e:
            cls.__connection.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def get_flagged_entries_summary(cls):
        """
        Get a summary of flagged time entries by employee and department.

        Returns:
            dict: Dictionary containing summary statistics
        """
        cursor = cls.get_cursor()

        try:
            # Get total flagged entries
            cursor.execute("SELECT COUNT(*) FROM time WHERE FLAGGED_FOR_REVIEW = 1")
            total_flagged = cursor.fetchone()[0]

            # Get flagged entries by employee
            cursor.execute("""
                   SELECT 
                       e.EMPID, 
                       CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as EMPLOYEE_NAME,
                       e.DPTID,
                       COUNT(*) as FLAGGED_COUNT
                   FROM time t
                   INNER JOIN employee_table e ON t.EMPID = e.EMPID
                   WHERE t.FLAGGED_FOR_REVIEW = 1
                   GROUP BY e.EMPID, e.FIRST_NAME, e.LAST_NAME, e.DPTID
                   ORDER BY FLAGGED_COUNT DESC
               """)
            by_employee = cursor.fetchall()

            # Get flagged entries by department
            cursor.execute("""
                   SELECT 
                       e.DPTID,
                       d.DPT_NAME,
                       COUNT(*) as FLAGGED_COUNT
                   FROM time t
                   INNER JOIN employee_table e ON t.EMPID = e.EMPID
                   INNER JOIN department d ON e.DPTID = d.DPTID
                   WHERE t.FLAGGED_FOR_REVIEW = 1
                   GROUP BY e.DPTID, d.DPT_NAME
                   ORDER BY FLAGGED_COUNT DESC
               """)
            by_department = cursor.fetchall()

            # Get flagged entries by project
            cursor.execute("""
                   SELECT 
                       t.PROJECTID,
                       p.PROJECT_NAME,
                       COUNT(*) as FLAGGED_COUNT
                   FROM time t
                   INNER JOIN projects p ON t.PROJECTID = p.PROJECTID
                   WHERE t.FLAGGED_FOR_REVIEW = 1
                   GROUP BY t.PROJECTID, p.PROJECT_NAME
                   ORDER BY FLAGGED_COUNT DESC
               """)
            by_project = cursor.fetchall()

            return {
                'total_flagged': total_flagged,
                'by_employee': by_employee,
                'by_department': by_department,
                'by_project': by_project
            }

        finally:
            cursor.close()

    @classmethod
    def get_time_entries_needing_attention(cls, manager_empid=None, days_back=30):
        """
        Get time entries that might need attention (flagged, missing notes on long entries, etc.).

        Args:
            manager_empid (str, optional): Filter to employees managed by this manager
            days_back (int): How many days back to look (default 30)

        Returns:
            dict: Dictionary with different categories of entries needing attention
        """
        cursor = cls.get_cursor()

        try:
            base_where = f"WHERE t.START_TIME >= DATE_SUB(NOW(), INTERVAL {days_back} DAY)"

            if manager_empid:
                base_where += " AND e.MGR_EMPID = ?"
                params = (manager_empid,)
            else:
                params = ()

            # Get flagged entries
            flagged_query = f"""
                   SELECT t.TIMEID, t.EMPID, CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as NAME,
                          t.PROJECTID, t.START_TIME, t.TOTAL_MINUTES, 'Flagged for Review' as REASON
                   FROM time t
                   INNER JOIN employee_table e ON t.EMPID = e.EMPID
                   {base_where} AND t.FLAGGED_FOR_REVIEW = 1
                   ORDER BY t.START_TIME DESC
               """
            cursor.execute(flagged_query, params)
            flagged_entries = cursor.fetchall()

            # Get long entries without notes
            long_no_notes_query = f"""
                   SELECT t.TIMEID, t.EMPID, CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as NAME,
                          t.PROJECTID, t.START_TIME, t.TOTAL_MINUTES, 'Long entry without notes' as REASON
                   FROM time t
                   INNER JOIN employee_table e ON t.EMPID = e.EMPID
                   {base_where} AND t.TOTAL_MINUTES > 480 
                   AND (t.NOTES IS NULL OR t.NOTES = '')
                   ORDER BY t.TOTAL_MINUTES DESC
               """
            cursor.execute(long_no_notes_query, params)
            long_no_notes = cursor.fetchall()

            # Get unusual hours (very early/late entries)
            unusual_hours_query = f"""
                   SELECT t.TIMEID, t.EMPID, CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as NAME,
                          t.PROJECTID, t.START_TIME, t.TOTAL_MINUTES, 'Unusual hours' as REASON
                   FROM time t
                   INNER JOIN employee_table e ON t.EMPID = e.EMPID
                   {base_where} AND (
                       HOUR(t.START_TIME) < 6 OR HOUR(t.START_TIME) > 22 OR
                       HOUR(t.STOP_TIME) < 6 OR HOUR(t.STOP_TIME) > 22
                   )
                   ORDER BY t.START_TIME DESC
               """
            cursor.execute(unusual_hours_query, params)
            unusual_hours = cursor.fetchall()

            return {
                'flagged_entries': flagged_entries,
                'long_entries_no_notes': long_no_notes,
                'unusual_hours': unusual_hours,
                'total_needing_attention': len(flagged_entries) + len(long_no_notes) + len(unusual_hours)
            }

        finally:
            cursor.close()

    @classmethod
    def add_time_entry_with_timeid(cls, timeid, empid, projectid, start_time, stop_time, notes=None, manual_entry=0):
        """
        Add a time entry with a specific TIMEID - designed for bulk import operations.

        Args:
            timeid (str): Unique time entry ID
            empid (str): Employee ID
            projectid (str): Project ID
            start_time (datetime): Start datetime
            stop_time (datetime): Stop datetime
            notes (str, optional): Notes for the time entry
            manual_entry (int): Manual entry flag (0 for timer, 1 for manual)

        Returns:
            bool: True if successful, False if failed

        Raises:
            Exception: If there was a database error during insertion
        """
        try:
            cursor = cls.get_cursor()

            # Validate that stop_time is after start_time
            if stop_time <= start_time:
                raise ValueError("Stop time must be after start time")

            cursor.execute('''
                INSERT INTO time (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timeid, empid, projectid, start_time, stop_time, notes, manual_entry))

            cls.commit()
            return True

        except Exception as e:
            print(f"Error inserting time entry {timeid}: {e}")
            cls.__connection.rollback() if hasattr(cls, '_Database__connection') and cls.__connection else None
            raise

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

# ======================
# 🔹 Department History Queries
# ======================

    @classmethod
    def update_employee_department(cls, empid, new_dptid, assignment_date=None):
        """
        Update an employee's department assignment and record the change in history.

        Args:
            empid (str): Employee ID to update
            new_dptid (str): New department ID to assign
            assignment_date (datetime.date, optional): Date of assignment.
                                                     Defaults to current date if not provided.

        Returns:
            bool: True if update was successful, False otherwise

        Raises:
            Exception: If employee doesn't exist, department doesn't exist, or database error occurs
        """
        cursor = cls.get_cursor()

        try:
            # Verify employee exists
            cursor.execute("SELECT EMPID, DPTID FROM employee_table WHERE EMPID = ?", (empid,))
            employee_result = cursor.fetchone()
            if not employee_result:
                raise Exception(f"Employee {empid} not found")

            current_dptid = employee_result[1]

            # Check if already assigned to this department
            if current_dptid == new_dptid:
                return True  # No change needed

            # Verify new department exists
            cursor.execute("SELECT DPTID FROM department WHERE DPTID = ?", (new_dptid,))
            dept_result = cursor.fetchone()
            if not dept_result:
                raise Exception(f"Department {new_dptid} not found")

            # Use current date if assignment_date not provided
            if assignment_date is None:
                assignment_date = datetime.now(local_tz).date()

            # Update employee's department in employee_table
            cursor.execute(
                "UPDATE employee_table SET DPTID = ? WHERE EMPID = ?",
                (new_dptid, empid)
            )

            # Add record to department history table
            cursor.execute(
                "INSERT INTO employee_department_history (EMPID, DPTID, ASSIGNMENT_DATE) VALUES (?, ?, ?)",
                (empid, new_dptid, assignment_date)
            )

            cls.commit()
            return True

        except Exception as e:
            cls.__connection.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def get_employee_department_history(cls, empid):
        """
        Get the department assignment history for a specific employee.

        Args:
            empid (str): Employee ID to get history for

        Returns:
            list: List of tuples containing (DPTID, DPT_NAME, ASSIGNMENT_DATE) ordered by date
        """
        cursor = cls.get_cursor()
        query = '''
                SELECT edh.DPTID, d.DPT_NAME, edh.ASSIGNMENT_DATE
                FROM employee_department_history edh
                INNER JOIN department d ON edh.DPTID = d.DPTID
                WHERE edh.EMPID = ?
                ORDER BY edh.ASSIGNMENT_DATE DESC
            '''
        cursor.execute(query, (empid,))
        result = cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def get_current_department_employees(cls, dptid):
        """
        Get all employees currently assigned to a specific department.

        Args:
            dptid (str): Department ID

        Returns:
            list: List of tuples containing employee information for current department members
        """
        cursor = cls.get_cursor()
        query = '''
                SELECT EMPID, FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, EMP_ACTIVE, EMP_ROLE
                FROM employee_table
                WHERE DPTID = ?
                ORDER BY LAST_NAME, FIRST_NAME
            '''
        cursor.execute(query, (dptid,))
        result = cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def get_department_changes_since_date(cls, since_date):
        """
        Get all department changes that occurred since a specific date.

        Args:
            since_date (datetime.date): Date to check changes since

        Returns:
            list: List of tuples containing (EMPID, FIRST_NAME, LAST_NAME, DPTID, DPT_NAME, ASSIGNMENT_DATE)
        """
        cursor = cls.get_cursor()
        query = '''
                SELECT edh.EMPID, e.FIRST_NAME, e.LAST_NAME, edh.DPTID, d.DPT_NAME, edh.ASSIGNMENT_DATE
                FROM employee_department_history edh
                INNER JOIN employee_table e ON edh.EMPID = e.EMPID
                INNER JOIN department d ON edh.DPTID = d.DPTID
                WHERE edh.ASSIGNMENT_DATE >= ?
                ORDER BY edh.ASSIGNMENT_DATE DESC, e.LAST_NAME
            '''
        cursor.execute(query, (since_date,))
        result = cursor.fetchall()
        cursor.close()
        return result


# ======================
# 🔹 Role History Queries
# ======================

@classmethod
def update_employee_role(cls, empid, new_role, assignment_date=None):
    """
    Update an employee's role and record the change in history.

    Args:
        empid (str): Employee ID to update
        new_role (str): New role to assign (individual, manager, project_manager, user)
        assignment_date (datetime.date, optional): Date of role assignment.
                                                 Defaults to current date if not provided.

    Returns:
        bool: True if update was successful, False otherwise

    Raises:
        Exception: If employee doesn't exist, invalid role, or database error occurs
    """
    cursor = cls.get_cursor()

    try:
        # Define valid roles
        valid_roles = ['individual', 'manager', 'project_manager', 'user']

        # Validate role
        if new_role not in valid_roles:
            raise Exception(f"Invalid role '{new_role}'. Valid roles: {', '.join(valid_roles)}")

        # Verify employee exists and get current role
        cursor.execute("SELECT EMPID, EMP_ROLE FROM employee_table WHERE EMPID = ?", (empid,))
        employee_result = cursor.fetchone()
        if not employee_result:
            raise Exception(f"Employee {empid} not found")

        current_role = employee_result[1]

        # Check if already assigned to this role
        if current_role == new_role:
            return True  # No change needed

        # Use current date if assignment_date not provided
        if assignment_date is None:
            assignment_date = datetime.now(local_tz).date()

        # Update employee's role in employee_table
        cursor.execute(
            "UPDATE employee_table SET EMP_ROLE = ? WHERE EMPID = ?",
            (new_role, empid)
        )

        # Add record to role history table
        cursor.execute(
            "INSERT INTO employee_role_history (EMPID, EMP_ROLE, ROLE_ASSIGNMENT_DATE) VALUES (?, ?, ?)",
            (empid, new_role, assignment_date)
        )

        cls.commit()
        return True

    except Exception as e:
        cls.__connection.rollback()
        raise e
    finally:
        cursor.close()


@classmethod
def get_employee_role_history(cls, empid):
    """
    Get the role assignment history for a specific employee.

    Args:
        empid (str): Employee ID to get history for

    Returns:
        list: List of tuples containing (EMP_ROLE, ROLE_ASSIGNMENT_DATE) ordered by date desc
    """
    cursor = cls.get_cursor()
    query = '''
            SELECT EMP_ROLE, ROLE_ASSIGNMENT_DATE
            FROM employee_role_history
            WHERE EMPID = ?
            ORDER BY ROLE_ASSIGNMENT_DATE DESC
        '''
    cursor.execute(query, (empid,))
    result = cursor.fetchall()
    cursor.close()
    return result


@classmethod
def get_employees_by_role(cls, role, include_inactive=False):
    """
    Get all employees currently assigned to a specific role.

    Args:
        role (str): Role to filter by (individual, manager, project_manager, user)
        include_inactive (bool): Whether to include inactive employees

    Returns:
        list: List of tuples containing employee information for current role holders
    """
    cursor = cls.get_cursor()

    active_filter = "" if include_inactive else "AND EMP_ACTIVE = 1"

    query = f'''
            SELECT EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, EMP_ACTIVE
            FROM employee_table
            WHERE EMP_ROLE = ? {active_filter}
            ORDER BY LAST_NAME, FIRST_NAME
        '''
    cursor.execute(query, (role,))
    result = cursor.fetchall()
    cursor.close()
    return result


@classmethod
def get_role_changes_since_date(cls, since_date):
    """
    Get all role changes that occurred since a specific date.

    Args:
        since_date (datetime.date): Date to check changes since

    Returns:
        list: List of tuples containing (EMPID, FIRST_NAME, LAST_NAME, EMP_ROLE, ROLE_ASSIGNMENT_DATE)
    """
    cursor = cls.get_cursor()
    query = '''
            SELECT erh.EMPID, e.FIRST_NAME, e.LAST_NAME, erh.EMP_ROLE, erh.ROLE_ASSIGNMENT_DATE
            FROM employee_role_history erh
            INNER JOIN employee_table e ON erh.EMPID = e.EMPID
            WHERE erh.ROLE_ASSIGNMENT_DATE >= ?
            ORDER BY erh.ROLE_ASSIGNMENT_DATE DESC, e.LAST_NAME
        '''
    cursor.execute(query, (since_date,))
    result = cursor.fetchall()
    cursor.close()
    return result


@classmethod
def get_employee_career_progression(cls, empid):
    """
    Get detailed career progression for an employee including both role and department history.

    Args:
        empid (str): Employee ID to get career progression for

    Returns:
        dict: Dictionary containing role_history and department_history lists
    """
    cursor = cls.get_cursor()

    try:
        # Get role history
        cursor.execute('''
                SELECT EMP_ROLE, ROLE_ASSIGNMENT_DATE, 'role_change' as change_type
                FROM employee_role_history
                WHERE EMPID = ?
                ORDER BY ROLE_ASSIGNMENT_DATE DESC
            ''', (empid,))
        role_history = cursor.fetchall()

        # Get department history
        cursor.execute('''
                SELECT edh.DPTID, d.DPT_NAME, edh.ASSIGNMENT_DATE, 'dept_change' as change_type
                FROM employee_department_history edh
                INNER JOIN department d ON edh.DPTID = d.DPTID
                WHERE edh.EMPID = ?
                ORDER BY edh.ASSIGNMENT_DATE DESC
            ''', (empid,))
        dept_history = cursor.fetchall()

        return {
            'role_history': role_history,
            'department_history': dept_history
        }

    finally:
        cursor.close()


@classmethod
def get_current_managers(cls):
    """
    Get all employees currently in manager or project_manager roles.

    Returns:
        list: List of tuples containing manager information grouped by role
    """
    cursor = cls.get_cursor()
    query = '''
            SELECT EMPID, FIRST_NAME, LAST_NAME, EMP_ROLE, DPTID, EMAIL_ADDRESS
            FROM employee_table
            WHERE EMP_ROLE IN ('manager', 'project_manager') 
            AND EMP_ACTIVE = 1
            ORDER BY EMP_ROLE, LAST_NAME, FIRST_NAME
        '''
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result


@classmethod
def promote_employee_to_manager(cls, empid, manager_type='manager', assignment_date=None):
    """
    Promote an employee to a manager role with validation.

    Args:
        empid (str): Employee ID to promote
        manager_type (str): Type of manager ('manager' or 'project_manager')
        assignment_date (datetime.date, optional): Date of promotion

    Returns:
        bool: True if promotion was successful

    Raises:
        Exception: If employee doesn't exist, invalid manager type, or employee is inactive
    """
    cursor = cls.get_cursor()

    try:
        # Validate manager type
        if manager_type not in ['manager', 'project_manager']:
            raise Exception(f"Invalid manager type '{manager_type}'. Use 'manager' or 'project_manager'")

        # Verify employee exists and is active
        cursor.execute("SELECT EMPID, EMP_ROLE, EMP_ACTIVE FROM employee_table WHERE EMPID = ?", (empid,))
        employee_result = cursor.fetchone()
        if not employee_result:
            raise Exception(f"Employee {empid} not found")

        current_role, emp_active = employee_result[1], employee_result[2]

        if not emp_active:
            raise Exception(f"Cannot promote inactive employee {empid}")

        if current_role in ['manager', 'project_manager']:
            raise Exception(f"Employee {empid} is already in a management role ({current_role})")

        # Use the update_employee_role method to handle the promotion
        return cls.update_employee_role(empid, manager_type, assignment_date)

    except Exception as e:
        raise e
    finally:
        cursor.close()


@classmethod
def demote_manager_to_individual(cls, empid, assignment_date=None):
    """
    Demote a manager back to individual contributor role.

    Args:
        empid (str): Employee ID to demote
        assignment_date (datetime.date, optional): Date of demotion

    Returns:
        bool: True if demotion was successful

    Raises:
        Exception: If employee doesn't exist or is not currently a manager
    """
    cursor = cls.get_cursor()

    try:
        # Verify employee exists and is currently a manager
        cursor.execute("SELECT EMPID, EMP_ROLE FROM employee_table WHERE EMPID = ?", (empid,))
        employee_result = cursor.fetchone()
        if not employee_result:
            raise Exception(f"Employee {empid} not found")

        current_role = employee_result[1]

        if current_role not in ['manager', 'project_manager']:
            raise Exception(f"Employee {empid} is not currently in a management role (current: {current_role})")

        # Use the update_employee_role method to handle the demotion
        return cls.update_employee_role(empid, 'individual', assignment_date)

    except Exception as e:
        raise e
    finally:
        cursor.close()


@classmethod
def get_org_chart_by_role(cls):
    """
    Get organizational structure organized by roles for reporting.

    Returns:
        dict: Dictionary with roles as keys and employee lists as values
    """
    cursor = cls.get_cursor()
    query = '''
            SELECT 
                e.EMP_ROLE,
                e.EMPID, 
                CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as FULL_NAME,
                e.DPTID,
                d.DPT_NAME,
                e.EMAIL_ADDRESS,
                e.EMP_ACTIVE
            FROM employee_table e
            INNER JOIN department d ON e.DPTID = d.DPTID
            WHERE e.EMP_ACTIVE = 1
            ORDER BY e.EMP_ROLE, d.DPT_NAME, e.LAST_NAME, e.FIRST_NAME
        '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    # Organize by role
    org_chart = {}
    for row in results:
        role = row[0]
        if role not in org_chart:
            org_chart[role] = []

        org_chart[role].append({
            'empid': row[1],
            'name': row[2],
            'dept_id': row[3],
            'dept_name': row[4],
            'email': row[5],
            'active': row[6]
        })

    return org_chart


@classmethod
def validate_role_consistency(cls):
    """
    Validate that role assignments are consistent across the system.

    Returns:
        dict: Dictionary containing validation results and any issues found
    """
    cursor = cls.get_cursor()

    try:
        # Check for employees with roles but no role history
        cursor.execute('''
                SELECT e.EMPID, e.EMP_ROLE
                FROM employee_table e
                LEFT JOIN employee_role_history erh ON e.EMPID = erh.EMPID AND e.EMP_ROLE = erh.EMP_ROLE
                WHERE erh.EMPID IS NULL
            ''')
        missing_history = cursor.fetchall()

        # Check for invalid role values
        cursor.execute('''
                SELECT EMPID, EMP_ROLE
                FROM employee_table
                WHERE EMP_ROLE NOT IN ('individual', 'manager', 'project_manager', 'user')
            ''')
        invalid_roles = cursor.fetchall()

        # Get role distribution
        cursor.execute('''
                SELECT EMP_ROLE, COUNT(*) as count
                FROM employee_table
                WHERE EMP_ACTIVE = 1
                GROUP BY EMP_ROLE
                ORDER BY count DESC
            ''')
        role_distribution = cursor.fetchall()

        return {
            'missing_history': missing_history,
            'invalid_roles': invalid_roles,
            'role_distribution': role_distribution,
            'validation_passed': len(missing_history) == 0 and len(invalid_roles) == 0
        }

    finally:
        cursor.close()
