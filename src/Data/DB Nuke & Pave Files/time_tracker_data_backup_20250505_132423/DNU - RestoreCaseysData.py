# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.24.2025
# Description:      Restores Casey's initial data
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.24.2025: Initial setup of tests
#                   - 05.05.2025: updated to align with changes made directly to DB via console script
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

#!/usr/bin/env python3
"""
MariaDB Data Population Script

This script populates a MariaDB database with sample data for the time tracker application.
It handles foreign key constraints by inserting data in the correct order.
"""
import os
import sys
import mariadb
import datetime
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


def connect_to_database():
    """
    Establish connection to MariaDB using environment variables with proper error handling
    """
    # Check if required environment variables are set
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: The following required environment variables are not set: {', '.join(missing_vars)}")
        print("Please set these environment variables in your .env file before running the script.")
        sys.exit(1)

    # Handle DB_PORT with default value if not set
    db_port = os.getenv("DB_PORT")
    if db_port is None:
        db_port = 3306  # Default MariaDB port
        print(f"Warning: DB_PORT not set, using default port {db_port}")
    else:
        try:
            db_port = int(db_port)
        except ValueError:
            print(f"Error: DB_PORT value '{db_port}' is not a valid integer")
            sys.exit(1)

    try:
        # Connect to MariaDB
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=db_port,
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )
        print(f"Successfully connected to {os.getenv('DB_NAME')} database")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)


def populate_data():
    """
    Main function to populate the database with sample data
    Handles foreign key constraints by inserting data in the correct order
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Temporarily disable foreign key checks
        print("Temporarily disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Start transaction
        conn.autocommit = False

        # Step 1: Create departments without managers first
        print("\nPopulating department table (step 1 - without managers)...")
        departments = [
            ('ENG', 'Engineering', None, 1),
            ('FIN', 'Finance', None, 1),
            ('HR', 'Human Resources', None, 1),
            ('MKT', 'Marketing', None, 1),
            ('D001', 'General', None, 0)  # Adding D001 as it's used by employees
        ]

        for dept in departments:
            try:
                cursor.execute("""
                    INSERT INTO department (DPTID, DPT_NAME, MANAGERID, DPT_ACTIVE)
                    VALUES (?, ?, ?, ?)
                """, dept)
                print(f"  Added department: {dept[0]} - {dept[1]}")
            except mariadb.Error as e:
                print(f"  Error adding department {dept[0]}: {e}")

        # Step 2: Create employees without managers
        print("\nPopulating employee_table (step 1 - without managers)...")
        employees_without_managers = [
            ('E9009', 'Lisa', 'Hill', 'ENG', 'lisah@wou.edu', None, 1, 'manager'),  # Changed from E0009 to E9009 to match schema
            ('E001', 'Casey', 'Hill', 'D001', 'casey.hill@example.com', None, 1, 'individual'),
            ('E003', 'Yesac', 'Llih', 'D001', 'YesacLlih@email.com', None, 1, 'manager'),
            ('E004', 'Erika', 'Brooks', 'ENG', 'eb@email.com', None, 1, 'project_manager'),
            ('E006', 'Frankie', 'Hill', 'ENG', 'frankie@wou.edu', None, 1, 'user'),
            ('E007', 'Jack', 'White', 'ENG', 'jw@wou.edu', None, 1, 'project_manager'),
            ('E008', 'Ivy', 'Nguyen', 'ENG', 'ivy@company.com', None, 1, 'manager'),  # Changed MKT to ENG to match schema
            ('E010', 'Test', 'LoginAccount', 'ENG', 'anotherTestEmail@gmail.com', None, 1, 'manager'),
            ('TEST01', 'Tess', 'Tester', 'D001', 'tess@example.com', None, 1, 'individual')
        ]

        for emp in employees_without_managers:
            try:
                cursor.execute("""
                    INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)
                print(f"  Added employee: {emp[0]} - {emp[1]} {emp[2]}")
            except mariadb.Error as e:
                print(f"  Error adding employee {emp[0]}: {e}")

        # Step 3: Update department managers now that employees exist
        print("\nUpdating department managers...")
        department_managers = [
            ('ENG', 'E003'),
            ('FIN', 'TEST01'),
            ('HR', 'E001'),
            ('MKT', None)
        ]

        for dept_id, manager_id in department_managers:
            try:
                cursor.execute("""
                    UPDATE department 
                    SET MANAGERID = ? 
                    WHERE DPTID = ?
                """, (manager_id, dept_id))
                print(f"  Updated manager for department {dept_id}: {manager_id}")
            except mariadb.Error as e:
                print(f"  Error updating manager for department {dept_id}: {e}")

        # Step 4: Create employees with managers
        print("\nPopulating employee_table (step 2 - with managers)...")
        employees_with_managers = [
            ('E009', 'Milo', 'Patel', 'MKT', 'milo@company.com', 'E008', 1, 'individual'),  # Changed from 'user' to 'individual' to match schema
            ('E011', 'Nina', 'Smith', 'FIN', 'nina@wou.edu', 'E010', 1, 'individual'),
            ('E012', 'Tom', 'Lee', 'FIN', 'tom@wou.edu', 'E011', 1, 'manager'),
            ('E013', 'Sara', 'Kim', 'HR', 'sara@wou.edu', 'E012', 1, 'individual'),
            ('E014', 'Alex', 'Brown', 'HR', 'alex@wou.edu', 'E013', 1, 'manager'),
            ('E015', 'Jamie', 'Fox', 'MKT', 'jamie@wou.edu', 'E9006', 1, 'individual'),  # Changed manager to E9006 to match schema
            ('E016', 'Taylor', 'Green', 'MKT', 'taylor@wou.edu', 'E015', 1, 'manager')
        ]

        for emp in employees_with_managers:
            try:
                cursor.execute("""
                    INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)
                print(f"  Added employee: {emp[0]} - {emp[1]} {emp[2]}")
            except mariadb.Error as e:
                print(f"  Error adding employee {emp[0]}: {e}")

        # Step 5: Create login records
        print("\nPopulating login_table...")
        logins = [
            ('login_casey', 'E001', 'secret123', '2025-04-17 20:27:26', 0),
            ('login_E009', 'E009', 'cfhillskhdjhe', '2025-04-21 19:40:30', 0),  # Updated time to match schema
            ('login_E003', 'E003', '123', '2025-04-21 01:05:24', 0),
            ('login_E004', 'E004', '123', '2025-04-21 18:09:59', 0),  # Updated time to match schema
            ('login_E006', 'E006', '123', '2025-04-21 19:19:47', 0),  # Updated time to match schema
            ('login_E007', 'E007', 'pass1', '2025-04-21 18:46:58', 0),  # Updated password to match schema
            ('login_E008', 'E008', '1', '2025-04-20 10:05:00', 0),  # Updated password and time to match schema
            ('login_E010', 'E010', '12312312312312', '2025-04-23 12:59:27', 0),  # Updated password to match schema
            ('login_E011', 'E011', 'pass3', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_E012', 'E012', 'pass4', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_E013', 'E013', 'pass5', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_E014', 'E014', 'pass6', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_E015', 'E015', 'pass7', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_E016', 'E016', 'pass8', '2025-04-20 10:05:00', 0),  # Updated time to match schema
            ('login_TEST02', 'TEST01', 'password123', '2025-04-23 12:46:21', 0)
        ]

        for login in logins:
            try:
                cursor.execute("""
                    INSERT INTO login_table (LOGINID, EMPID, PASSWORD, LAST_RESET, FORCE_RESET)
                    VALUES (?, ?, ?, ?, ?)
                """, login)
                print(f"  Added login: {login[0]} for employee {login[1]}")
            except mariadb.Error as e:
                print(f"  Error adding login {login[0]}: {e}")

        # Step 6: Create projects
        print("\nPopulating projects table...")
        projects = [
            ('P001', 'TimeTrackerDBTest', 'E001', '2025-04-19 21:44:34', None, 1),  # Updated name to match schema
            ('P002', 'MarketingWebsite', 'E004', '2025-04-20 10:00:00', None, 1),  # Updated name to match schema
            ('P003', 'InternalTooling', 'E9009', '2025-04-21 09:00:00', None, 1),  # Updated creator and name to match schema
            ('P004', 'ClientOnboarding', 'E007', '2025-04-22 14:30:00', None, 1)  # Updated name to match schema
        ]

        for project in projects:
            try:
                cursor.execute("""
                    INSERT INTO projects (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, project)
                print(f"  Added project: {project[0]} - {project[1]}")
            except mariadb.Error as e:
                print(f"  Error adding project {project[0]}: {e}")

        # Step 7: Add employee-project assignments
        print("\nPopulating employee_projects junction table...")
        employee_projects = [
            ('E001', 'P001'),
            ('E001', 'P002'),
            ('E003', 'P002'),
            ('E004', 'P001'),
            ('E004', 'P002'),
            ('E004', 'P003'),
            ('E007', 'P004'),
            ('E011', 'P001'),
            ('E012', 'P002'),
            ('E012', 'P004'),
            ('E013', 'P003'),
            ('E015', 'P001'),
            ('E015', 'P002'),
            ('E016', 'P002'),
            ('E9009', 'P001'),
            ('E9009', 'P003'),
            ('TEST01', 'P001'),
            ('TEST01', 'P002')
        ]

        for emp_proj in employee_projects:
            try:
                cursor.execute("""
                    INSERT INTO employee_projects (EMPID, PROJECT_ID)
                    VALUES (?, ?)
                """, emp_proj)
                print(f"  Added employee-project assignment: {emp_proj[0]} - {emp_proj[1]}")
            except mariadb.Error as e:
                print(f"  Error adding employee-project assignment {emp_proj[0]} - {emp_proj[1]}: {e}")

        # Step 8: Create time entries
        print("\nPopulating time table...")
        # Modified for new schema: (TIMEID, EMPID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, PROJECTID)
        time_entries = [
            ('1', 'E001', '2025-04-19 20:58:08', '2025-04-19 21:58:08', 'Worked on initial setup', 1, 'P001'),
            ('2', 'E001', '2025-04-20 09:30:00', '2025-04-20 11:00:00', 'Entered start/stop manually', 1, 'P002'),
            ('3', 'TEST01', '2025-04-21 10:00:00', '2025-04-21 11:30:00', 'Manualentry/testing', 1, 'P001'),  # Updated notes to match schema
            ('4', 'E001', '2025-04-22 13:00:00', '2025-04-22 14:00:00', 'Caseyjprojectplanning', 1, 'P001'),  # Updated notes and project to match schema
            ('5', 'TEST01', '2025-04-22 15:00:00', '2025-04-22 16:00:00', 'Tessjwritinmg', 1, 'P001'),  # Updated notes and project to match schema
            ('6', 'E9009', '2025-04-23 09:00:00', '2025-04-23 10:30:00', 'Lisajteamcheck-inandocumentation', 1, 'P003'),  # Updated notes to match schema
            ('7', 'E004', '2025-04-23 11:00:00', '2025-04-23 12:00:00', 'Erikajstakeholdermeeting', 1, 'P003'),  # Updated notes to match schema
            ('8', 'E9009', '2025-04-24 04:52:06', '2025-04-24 05:52:06', 'Lisajdebuggsession', 1, 'P003'),  # Updated notes to match schema
            ('9', 'TEST01', '2025-04-24 03:52:06', '2025-04-24 04:52:06', 'Tessfinisheddocumentation', 1, 'P001'),  # Updated notes to match schema
            ('10', 'E003', '2025-04-23 09:00:00', '2025-04-23 10:30:00', 'Yesacjplanningmeeting', 1, 'P002'),  # Updated notes to match schema
            ('11', 'E003', '2025-04-24 13:00:00', '2025-04-24 14:15:00', 'Yesacjreviewedreports', 1, 'P002'),  # Updated notes to match schema
            ('12', 'E011', '2025-04-24 09:00:00', '2025-04-24 10:00:00', 'Ninajdailytask', 1, 'P001'),  # Updated notes to match schema
            ('13', 'E012', '2025-04-24 10:00:00', '2025-04-24 11:00:00', 'Tomjdailytask', 1, 'P002'),  # Updated notes to match schema
            ('14', 'E013', '2025-04-24 11:00:00', '2025-04-24 12:00:00', 'Sarajdailytask', 1, 'P003'),  # Updated notes to match schema
            ('15', 'E014', '2025-04-24 12:00:00', '2025-04-24 13:00:00', 'Alexjdailytask', 1, 'P004'),  # Updated notes to match schema
            ('16', 'E015', '2025-04-24 13:00:00', '2025-04-24 14:00:00', 'Jamiejdailytask', 1, 'P001'),  # Updated notes to match schema
            ('17', 'E016', '2025-04-24 14:00:00', '2025-04-24 15:00:00', 'Taylorjdailytask', 1, 'P002')  # Updated notes to match schema
        ]

        for entry in time_entries:
            try:
                cursor.execute("""
                    INSERT INTO time (TIMEID, EMPID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, PROJECTID)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, entry)
                print(f"  Added time entry: ID {entry[0]} for {entry[1]} on project {entry[6]}")
            except mariadb.Error as e:
                print(f"  Error adding time entry {entry[0]}: {e}")

        # Re-enable foreign key checks
        print("\nRe-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Commit the transaction
        conn.commit()
        print("\nAll data has been successfully inserted!")

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error during database population: {e}")
        print("All changes have been rolled back")
        sys.exit(1)
    finally:
        # Make sure foreign key checks are re-enabled even if an error occurs
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except:
            pass

        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=== MariaDB Data Population Tool ===")
    populate_data()
    print("=== Data population complete! ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
