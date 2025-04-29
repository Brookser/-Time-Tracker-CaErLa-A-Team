# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Sets up dummy data in the DB
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.20.2025: Initial setup of tests
#                   - 04.21.2025: Updated ROLE_NAME in role_names for ROLEID 4 & 5:
#                           • senior_manager --> vp_csuite
#                           • admin --> CEO
#                   - 4.24.2025: Changes to datapoints made in order to align with the schema
#                           Casey created
#
# **********************************************************************************************************************
# **********************************************************************************************************************  
#!/usr/bin/env python3
"""
MariaDB Additional Data Insertion Script

This script inserts additional data into a MariaDB database for the time tracker application.
It handles the data shown in the provided images and calculates the TOTAL_MINUTES field.
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


def calculate_minutes(start_time, stop_time):
    """
    Calculate the time difference in minutes between start_time and stop_time
    """
    format_str = "%Y-%m-%d %H:%M:%S"
    start_dt = datetime.strptime(start_time, format_str)
    stop_dt = datetime.strptime(stop_time, format_str)

    # Calculate the difference in minutes
    diff_minutes = int((stop_dt - start_dt).total_seconds() / 60)
    return diff_minutes


def populate_additional_data():
    """
    Function to populate the database with the additional data from the images
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Temporarily disable foreign key checks
        print("Temporarily disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Start transaction
        conn.autocommit = False

        # Step 1: Insert departments (from image 2)
        print("\nPopulating department table...")
        departments = [
            ('FIN', 'Training', 'E9001', 1),
            ('DEV', 'Business Development', 'E9025', 1),
            ('SVCS', 'Services', 'E9007', 1),
            ('R&D', 'Research and Development', 'E9025', 1),
            ('LEG', 'Legal', 'E9005', 1),
            ('SUP', 'Support', 'E9014', 1)
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

        # Step 2: Insert employees (from image 2)
        print("\nPopulating employee_table...")
        employees = [
            ('E9003', 'Elwin', 'Klagseman', 'FIN', 'eklagseman@free.fr', 'E9005', 1, 'individual'),
            ('E9004', 'Archibald', 'Bemet', 'HR', 'abemet@jamaizone.com', 'E9006', 1, 'individual'),
            ('E9005', 'Othello', 'Bessey', 'HR', 'obessey@jdjakla.ca', 'E9006', 1, 'individual'),
            ('E9006', 'Godfrey', 'Gaye', 'HR', 'ggaye7@mashable.com', 'NULL', 1, 'manager'),
            ('E9010', 'Dannie', 'Montgomery', 'FIN', 'dmontgomery5@acgmail.org', 'E9011', 1, 'individual'),
            ('E9011', 'Gaby', 'Pfilzaclea', 'FIN', 'gpfilzaclea9@prweb.com', 'NULL', 1, 'manager'),
            ('E9017', 'Kenny', 'Scardifeild', 'FIN', 'kscardifeild@umekis.jp', 'E0911', 0, 'individual'),
            ('E9019', 'Heran', 'Clee', 'DEV', 'hcleee@google.it', 'E9025', 1, 'individual'),
            ('E9021', 'Husein', 'Barker', 'DEV', 'hbarker4@tmyiplc.com', 'E9025', 1, 'individual'),
            ('E9022', 'Chantalle', 'Godall', 'DEV', 'cgodall1@eahymail.co.uk', 'E9025', 1, 'individual'),
            ('E9007', 'Angelia', 'Favell', 'SVCS', 'afavella@hostgator.com', 'NULL', 1, 'manager'),
            ('E9008', 'Aundrea', 'Abela', 'SVCS', 'aabelak@lycos.com', 'E9007', 0, 'individual'),
            ('E9009', 'Gilles', 'Shaylor', 'SVCS', 'gshaylorl@ezinearticles.com', 'E9007', 1, 'individual'),
            ('E9018', 'Charlena', 'Drydell', 'R&D', 'cdrydall@mapyx.cz', 'E9025', 1, 'project_manager'),
            ('E9020', 'Dane', 'Eynald', 'R&D', 'deynald@ning.com', 'E9025', 0, 'project_manager'),
            ('E9001', 'Lane', 'Beere', 'LEG', 'lbeere@rakuten.co.jp', 'E9002', 1, 'individual'),
            ('E9002', 'Bobina', 'Windless', 'LEG', 'bwindless8@census.gov', 'NULL', 1, 'manager'),
            ('E9024', 'Hilliard', 'Bredell', 'LEG', 'hbredell@aol.com', 'E9002', 1, 'individual'),
            ('E9025', 'Bert', 'Wartock', 'LEG', 'bwartockn@techcrunch.com', 'NULL', 1, 'manager'),
            ('E9012', 'Doti', 'Le Moucheux', 'FIN', 'dlemoucheux@skype.com', 'NULL', 1, 'manager'),
            ('E9013', 'Freeman', 'Jobbins', 'FIN', 'fjobbins@ning.com', 'E9012', 1, 'individual'),
            ('E9023', 'Hamid', 'Klouz', 'FIN', 'hklouz5@nifeatlantiic.com', 'E9012', 1, 'individual'),
            ('E9014', 'Devy', 'Johanni', 'SUP', 'djohanni2@amazon.co.uk', 'NULL', 1, 'manager'),
            ('E9015', 'Peg', 'Hawkes', 'SUP', 'phawkes3@blinkist.com', 'E9014', 1, 'individual'),
            ('E9016', 'Christine', 'Pullar', 'SUP', 'cpullarb@state.tx.us', 'E9014', 1, 'individual')
        ]

        for emp in employees:
            try:
                # Replace 'NULL' string with actual None value
                emp_values = list(emp)
                if emp_values[5] == 'NULL':
                    emp_values[5] = None

                cursor.execute("""
                    INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, emp_values)
                print(f"  Added employee: {emp[0]} - {emp[1]} {emp[2]}")
            except mariadb.Error as e:
                print(f"  Error adding employee {emp[0]}: {e}")

        # Step 3: Insert login data (from image 1)
        print("\nPopulating login_table...")
        # Convert the date format from MM/DD/YYYY to YYYY-MM-DD HH:MM:SS
        logins = [
            ('lbeere', 'E9001', '123', '2025-04-15 00:00:00', 0),
            ('bwindless8', 'E9002', '123', '2025-04-15 00:00:00', 0),
            ('eklagsemano', 'E9003', '123', '2025-04-15 00:00:00', 0),
            ('abemet', 'E9004', '123', '2025-04-15 00:00:00', 0),
            ('obesseym', 'E9005', '123', '2025-04-15 00:00:00', 0),
            ('ggaye7', 'E9006', '123', '2025-04-15 00:00:00', 1),
            ('afavella', 'E9007', '123', '2025-04-15 00:00:00', 0),
            ('aabelak', 'E9008', '123', '2025-04-15 00:00:00', 0),
            ('gshaylorl', 'E9009', '123', '2025-04-15 00:00:00', 0),
            ('dmontgomery5', 'E9010', '123', '2025-04-15 00:00:00', 0),
            ('gpfilzaclea9', 'E9011', '123', '2025-04-15 00:00:00', 0),
            ('dlemoucheuxs', 'E9012', '123', '2025-04-15 00:00:00', 0),
            ('fjobbinsd', 'E9013', '123', '2025-04-15 00:00:00', 0),
            ('djohanni2', 'E9014', '123', '2025-04-15 00:00:00', 0),
            ('phawkes3', 'E9015', '123', '2025-04-15 00:00:00', 0),
            ('cpullarb', 'E9016', '123', '2025-04-15 00:00:00', 0),
            ('kscardifeild', 'E9017', '123', '2025-04-15 00:00:00', 0),
            ('cdrydall', 'E9018', '123', '2025-04-15 00:00:00', 0),
            ('hcleee', 'E9019', '123', '2025-04-15 00:00:00', 0),
            ('deynaldf', 'E9020', '123', '2025-04-15 00:00:00', 0),
            ('hbarker4', 'E9021', '123', '2025-04-15 00:00:00', 0),
            ('cgodall1', 'E9022', '123', '2025-04-15 00:00:00', 0),
            ('hklouz5', 'E9023', '123', '2025-04-15 00:00:00', 0),
            ('hbredell0', 'E9024', '123', '2025-04-15 00:00:00', 0),
            ('bwartockn', 'E9025', '123', '2025-04-15 00:00:00', 0)
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

        # Step 4: Insert projects (from image 1)
        print("\nPopulating projects table...")
        # Convert date format from MM/DD/YYYY to YYYY-MM-DD
        projects = [
            ('P10001', 'Andean goose', 'E9003', '2025-04-01 00:00:00', None, 1),
            ('P10002', 'Antelope, sable', 'E9013', '2025-04-01 00:00:00', None, 1),
            ('P10003', 'Argalis', 'E9003', '2025-04-01 00:00:00', None, 1),
            ('P10004', 'Bare-faced go away bird', 'E9003', '2025-04-01 00:00:00', None, 1),
            ('P10005', 'Bustard', 'E9010', '2025-04-01 00:00:00', None, 0),
            ('P10006', 'Boat-billed heron', 'E9004', '2025-04-01 00:00:00', None, 1),
            ('P10007', 'Bottle-nose dolphin', 'E9004', '2025-04-01 00:00:00', None, 1),
            ('P10008', 'Brazilian tapir', 'E9023', '2025-04-01 00:00:00', None, 0),
            ('P10009', 'Dog, raccoon', 'E9001', '2025-04-01 00:00:00', None, 0),
            ('P10010', 'Dolphin, striped', 'E9005', '2025-04-01 00:00:00', None, 1),
            ('P10011', 'Flamingo, greater', 'E9005', '2025-04-01 00:00:00', None, 1),
            ('P10012', 'Frilled dragon', 'E9005', '2025-04-01 00:00:00', None, 1),
            ('P10013', 'Giant heron', 'E9005', '2025-04-01 00:00:00', None, 1),
            ('P10014', 'Goose, andean', 'E9021', '2025-04-01 00:00:00', None, 0),
            ('P10015', 'Goose, greylag', 'E9021', '2025-04-15 00:00:00', 'P10014', 1),
            ('P10016', 'Greater adjutant stork', 'E9010', '2025-04-15 00:00:00', 'P10005', 1),
            ('P10017', 'Javan gold-spotted mongoose', 'E9023', '2025-04-15 00:00:00', 'P10008', 1),
            ('P10018', 'Legaan, Monitor (unidentified)', 'E9013', '2025-04-01 00:00:00', None, 1),
            ('P10019', 'Lynx, african', 'E9019', '2025-04-01 00:00:00', None, 1),
            ('P10020', 'Dog', 'E9001', '2025-04-15 00:00:00', 'P10009', 1),
            ('P10021', 'Racoon', 'E9001', '2025-04-15 00:00:00', 'P10009', 1),
            ('P10022', 'Squirrel, antelope ground', 'E9019', '2025-04-01 00:00:00', None, 0),
            ('P10023', 'Serin', 'E9019', '2025-04-01 00:00:00', None, 1),
            ('P10024', 'Vulture, oriental white-backed', 'E9019', '2025-04-01 00:00:00', None, 1),
            ('P10025', 'Squirrel', 'E9013', '2025-04-15 00:00:00', 'P10022', 1)
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

        # Step 5: Insert time entries and calculate TOTAL_MINUTES (from image 2)
        print("\nPopulating time table...")
        time_entries = [
            ('E9001', 'P10001', '2024-04-05 09:50:00', '2024-04-05 11:59:00', 'Integer ac', 0),
            ('E9003', 'P10003', '2024-12-09 16:47:00', '2024-12-09 18:01:00', 'Vestibulum', 1),
            ('E9005', 'P10005', '2024-04-14 04:01:00', '2024-04-14 05:17:00', 'Suspendisse', 1),
            ('E9006', 'P10006', '2025-01-08 20:09:00', '2025-01-08 21:05:00', 'Mauris enim', 0),
            ('E9005', 'P10005', '2025-03-11 09:51:00', '2025-03-11 11:03:00', 'Sed sagittis', 1),
            ('E9006', 'P10006', '2025-01-24 03:11:00', '2025-01-24 04:21:00', 'Cras non tortor', 0),
            ('E9006', 'P10006', '2024-05-29 07:58:00', '2024-05-29 09:56:00', 'Donec diam', 1),
            ('E9006', 'P10006', '2025-01-16 14:46:00', '2025-01-16 15:41:00', 'Phasellus in', 0),
            ('E9007', 'P10007', '2024-06-23 21:55:00', '2024-06-23 22:51:00', 'Duis bibendum', 0),
            ('E9007', 'P10009', '2024-03-10 19:27:00', '2024-03-10 20:39:00', 'Sed sagittis', 1),
            ('E9007', 'P10009', '2024-06-22 06:15:00', '2024-06-22 09:11:00', 'In sagittis', 1),
            ('E9011', 'P10010', '2025-01-23 01:01:00', '2025-01-23 02:03:00', 'Duis aliquam', 1),
            ('E9011', 'P10011', '2025-02-13 04:19:00', '2025-02-13 05:57:00', 'In congue', 1),
            ('E9012', 'P10012', '2024-06-15 19:12:00', '2024-06-15 20:44:00', 'Maecenas ut', 0),
            ('E9014', 'P10014', '2025-04-05 09:30:00', '2025-04-06 11:09:00', 'Pellentesque', 1),
            ('E9015', 'P10015', '2024-08-07 08:32:00', '2024-08-07 19:50:00', 'Nulla ute', 1),
            ('E9016', 'P10016', '2025-02-04 08:28:00', '2025-02-04 10:34:00', 'Praesent id', 0),
            ('E9017', 'P10017', '2025-03-31 13:09:00', '2025-03-31 14:09:00', 'Quisque posuere', 1),
            ('E9018', 'P10018', '2025-02-05 02:50:00', '2025-02-05 05:12:00', 'Vestibulum', 0),
            ('E9019', 'P10020', '2024-10-09 13:38:00', '2024-10-09 15:09:00', 'Fusce posuere', 1),
            ('E9021', 'P10021', '2024-03-26 03:58:00', '2024-03-26 06:12:00', 'In quis justo', 1),
            ('E9024', 'P10024', '2024-10-30 11:00:00', '2024-10-30 11:45:00', 'Maecenas ut', 0),
            ('E9025', 'P10025', '2025-04-07 03:24:00', '2025-04-07 05:22:00', 'Donec diam', 0),
            ('TEST01', 'P001', '2025-04-25 09:00:00', '2025-04-25 10:30:00', 'Tess: completed documentation updates', 0),
            ('TEST01', 'P002', '2025-04-25 11:00:00', '2025-04-25 12:00:00', 'Tess: meeting with project team', 0),
            ('E012', 'P003', '2025-04-25 08:00:00', '2025-04-25 09:15:00', 'Tom: sprint review session', 0),
            ('E012', 'P004', '2025-04-25 13:00:00', '2025-04-25 14:00:00', 'Tom: system update prep ', 0)
        ]

        for entry in time_entries:
            try:
                # Parse dates for calculation of TOTAL_MINUTES
                start_time = datetime.strptime(entry[2], "%Y-%m-%d %H:%M:%S")
                stop_time = datetime.strptime(entry[3], "%Y-%m-%d %H:%M:%S")

                # Calculate minutes
                minutes_diff = int((stop_time - start_time).total_seconds() / 60)

                cursor.execute("""
                    INSERT INTO time (EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, TOTAL_MINUTES)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], minutes_diff))
                print(f"  Added time entry for {entry[0]} on project {entry[1]}, duration: {minutes_diff} minutes")
            except mariadb.Error as e:
                print(f"  Error adding time entry for {entry[0]} on project {entry[1]}: {e}")

        # Re-enable foreign key checks
        print("\nRe-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Commit the transaction
        conn.commit()
        print("\nAll additional data has been successfully inserted!")

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
    print("=== MariaDB Additional Data Insertion Tool ===")
    populate_additional_data()
    print("=== Additional data insertion complete! ===")


# **********************************************************************************************************************
# **********************************************************************************************************************
