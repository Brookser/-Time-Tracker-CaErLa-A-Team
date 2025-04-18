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
    def get_all_projects(cls):
        cursor = cls.get_cursor()
        cursor.execute("SELECT * FROM projects")
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
    # 🔹 Login
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
