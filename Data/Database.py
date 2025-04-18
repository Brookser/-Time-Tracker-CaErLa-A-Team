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
    def get_all_employees(cls):
        cls.connect()
        cursor = cls.__connection.cursor()
        cursor.execute("SELECT * FROM employee_table")
        return cursor.fetchall()

    @classmethod
    def get_all_projects(cls):
        cls.connect()
        cursor = cls.__connection.cursor()
        cursor.execute("SELECT * FROM projects")
        return cursor.fetchall()

    @classmethod
    def get_departments(cls):
        cls.connect()
        cursor = cls.__connection.cursor()
        cursor.execute("SELECT * FROM department")
        return cursor.fetchall()

    # Employees
    @classmethod
    def add_employee(cls, empid, first_name, last_name, dptid, email=None, mgr_empid=None, active=1):
        cls.connect()
        cursor = cls.__connection.cursor()
        query = '''
            INSERT INTO employee_table
            (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (empid, first_name, last_name, dptid, email, mgr_empid, active))
        cls.__connection.commit()

    @classmethod
    def get_active_employees(cls):
        cls.connect()
        cursor = cls.__connection.cursor()
        cursor.execute("SELECT * FROM employee_table WHERE EMP_ACTIVE = 1")
        return cursor.fetchall()

    # @classmethod
    # def log_time_entry(cls, employee_id, project_id, start_time, end_time, notes=""):
    #     cls.connect()
    #     cursor = cls.__connection.cursor()
    #     query = '''
    #         INSERT INTO time (employee_id, project_id, start_time, end_time, notes)
    #         VALUES (?, ?, ?, ?, ?)
    #     '''
    #     cursor.execute(query, (employee_id, project_id, start_time, end_time, notes))
    #     cls.__connection.commit()
    #
    # @classmethod
    # def get_login_info(cls, username):
    #     cls.connect()
    #     cursor = cls.__connection.cursor()
    #     query = "SELECT * FROM login_table WHERE username = ?"
    #     cursor.execute(query, (username,))
    #     return cursor.fetchone()
