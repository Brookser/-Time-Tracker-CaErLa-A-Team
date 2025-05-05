# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.30.2025
# Description:      Dummy Data setup script to include employee_projects
# Input:            none
# Output:           confirmation message

#
# Change Log:       - 04.30.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

import os
import sys
import mariadb
import datetime
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


# Custom writer class to capture print statements
class CustomWriter:
    def __init__(self, file):
        self.file = file

    def write(self, text):
        self.file.write(text)

    def flush(self):
        self.file.flush()


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

        # Step 1: Insert departments (from image 1)
        print("\nPopulating department table...")
        departments = [
            ('D001', 'General', None, 0),
            ('DEV', 'BusinessDevelopment', 'E9025', 1),
            ('ENG', 'Engineering', 'E003', 1),
            ('FIN', 'Finance', 'TEST01', 1),
            ('HR', 'HumanResources', 'E001', 1),
            ('LEG', 'Legal', 'E9005', 1),
            ('MKT', 'Marketing', None, 1),
            ('R&D', 'ResearchandDevelopment', 'E9025', 1),
            ('SUP', 'Support', 'E9014', 1),
            ('SVCS', 'Services', 'E9007', 1)
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
            ('E9009', 'Lisa', 'Hill', 'ENG', 'lisah@wou.edu', None, 1, 'manager'),
            ('E001', 'Casey', 'Hill', 'D001', 'casey.hill@example.com', None, 1, 'individual'),
            ('E003', 'Yesac', 'Llih', 'D001', 'YesacLlih@email.com', None, 1, 'manager'),
            ('E004', 'Erika', 'Brooks', 'ENG', 'eb@email.com', None, 1, 'project_manager'),
            ('E006', 'Frankie', 'Hill', 'ENG', 'frankie@wou.edu', None, 1, 'user'),
            ('E007', 'Jack', 'White', 'ENG', 'jw@wou.edu', None, 1, 'project_manager'),
            ('E008', 'Ivy', 'Nguyen', 'ENG', 'ivy@company.com', None, 1, 'manager'),
            ('E009', 'Milo', 'Patel', 'MKT', 'milo@company.com', 'E008', 1, 'individual'),
            ('E010', 'Test', 'LoginAccount', 'ENG', 'anotherTestEmail@gmail.com', None, 1, 'manager'),
            ('E011', 'Nina', 'Smith', 'FIN', 'nina@wou.edu', 'E010', 1, 'individual'),
            ('E012', 'Tom', 'Lee', 'FIN', 'tom@wou.edu', 'E011', 1, 'manager'),
            ('E013', 'Sara', 'Kim', 'HR', 'sara@wou.edu', 'E012', 1, 'individual'),
            ('E014', 'Alex', 'Brown', 'HR', 'alex@wou.edu', 'E013', 1, 'manager'),
            ('E015', 'Jamie', 'Fox', 'MKT', 'jamie@wou.edu', 'E014', 1, 'individual'),
            ('E016', 'Taylor', 'Green', 'MKT', 'taylor@wou.edu', 'E015', 1, 'manager'),
            ('E9001', 'Lane', 'Beere', 'LEG', 'lbeere@rakuten.co.jp', 'E9002', 1, 'individual'),
            ('E9002', 'Bobina', 'Windless', 'LEG', 'bwindless8@census.gov', None, 1, 'manager'),
            ('E9003', 'Elwin', 'Klagseman', 'FIN', 'eklagseman@free.fr', 'E9005', 1, 'individual'),
            ('E9004', 'Archibald', 'Bemet', 'HR', 'abemet@jamaizone.com', 'E9006', 1, 'individual'),
            ('E9005', 'Othello', 'Bessey', 'HR', 'obessey@jdjakla.ca', 'E9006', 1, 'individual'),
            ('E9006', 'Godfrey', 'Gaye', 'HR', 'ggaye7@mashable.com', None, 1, 'manager'),
            ('E9007', 'Angelia', 'Favell', 'SVCS', 'afavella@hostgator.com', None, 1, 'manager'),
            ('E9008', 'Aundrea', 'Abela', 'SVCS', 'aabelak@lycos.com', 'E9007', 0, 'individual'),
            ('E9010', 'Dannie', 'Montgomery', 'FIN', 'dmontgomery5@acgmail.org', 'E9011', 1, 'individual'),
            ('E9011', 'Gaby', 'Pfilzaclea', 'FIN', 'gpfilzaclea9@prweb.com', None, 1, 'manager'),
            ('E9012', 'Doti', 'Le Moucheux', 'FIN', 'dlemoucheux@skype.com', None, 1, 'manager'),
            ('E9013', 'Freeman', 'Jobbins', 'FIN', 'fjobbins@ning.com', 'E9012', 1, 'individual'),
            ('E9014', 'Devy', 'Johanni', 'SUP', 'djohanni2@amazon.co.uk', None, 1, 'manager'),
            ('E9015', 'Peg', 'Hawkes', 'SUP', 'phawkes3@blinkist.com', 'E9014', 1, 'individual'),
            ('E9016', 'Christine', 'Pullar', 'SUP', 'cpullarb@state.tx.us', 'E9014', 1, 'individual'),
            ('E9017', 'Kenny', 'Scardifeild', 'FIN', 'kscardifeild@umekis.jp', 'E0911', 0, 'individual'),
            ('E9018', 'Charlena', 'Drydell', 'R&D', 'cdrydall@mapyx.cz', 'E9025', 1, 'project_manager'),
            ('E9019', 'Heran', 'Clee', 'DEV', 'hcleee@google.it', 'E9025', 1, 'individual'),
            ('E9020', 'Dane', 'Eynald', 'R&D', 'deynald@ning.com', 'E9025', 0, 'project_manager'),
            ('E9021', 'Husein', 'Barker', 'DEV', 'hbarker4@tmyiplc.com', 'E9025', 1, 'individual'),
            ('E9022', 'Chantalle', 'Godall', 'DEV', 'cgodall1@eahymail.co.uk', 'E9025', 1, 'individual'),
            ('E9023', 'Hamid', 'Klouz', 'FIN', 'hklouz5@nifeatlantiic.com', 'E9012', 1, 'individual'),
            ('E9024', 'Hilliard', 'Bredell', 'LEG', 'hbredell@aol.com', 'E9002', 1, 'individual'),
            ('E9025', 'Bert', 'Wartock', 'LEG', 'bwartockn@techcrunch.com', None, 1, 'manager'),
            ('TEST01', 'Tess', 'Tester', 'D001', 'tess@example.com', None, 1, 'individual')
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

        # Step 3: Insert login data (from image 3)
        print("\nPopulating login_table...")
        logins = [
            ('aabelak', 'E9008', '123', '2025-04-15 00:00:00', 0),
            ('abemet', 'E9004', '123', '2025-04-15 00:00:00', 0),
            ('afavella', 'E9007', '123', '2025-04-15 00:00:00', 0),
            ('bwartockn', 'E9025', '123', '2025-04-15 00:00:00', 0),
            ('bwindless8', 'E9002', '123', '2025-04-15 00:00:00', 0),
            ('cdrydall', 'E9018', '123', '2025-04-15 00:00:00', 0),
            ('cgodall1', 'E9022', '123', '2025-04-15 00:00:00', 0),
            ('cpullarb', 'E9016', '123', '2025-04-15 00:00:00', 0),
            ('deynaldf', 'E9020', '123', '2025-04-15 00:00:00', 0),
            ('djohanni2', 'E9014', '123', '2025-04-15 00:00:00', 0),
            ('dlemoucheuxs', 'E9012', '123', '2025-04-15 00:00:00', 0),
            ('dmontgomery5', 'E9010', '123', '2025-04-15 00:00:00', 0),
            ('eklagsemano', 'E9003', '123', '2025-04-15 00:00:00', 0),
            ('fjobbinsd', 'E9013', '123', '2025-04-15 00:00:00', 0),
            ('ggaye7', 'E9006', '123', '2025-04-15 00:00:00', 1),
            ('gpfilzaclea9', 'E9011', '123', '2025-04-15 00:00:00', 0),
            ('gshaylorl', 'E9009', '123', '2025-04-15 00:00:00', 0),
            ('hbarker4', 'E9021', '123', '2025-04-15 00:00:00', 0),
            ('hbredell0', 'E9024', '123', '2025-04-15 00:00:00', 0),
            ('hcleee', 'E9019', '123', '2025-04-15 00:00:00', 0),
            ('hklouz5', 'E9023', '123', '2025-04-15 00:00:00', 0),
            ('kscardifeild', 'E9017', '123', '2025-04-15 00:00:00', 0),
            ('lbeere', 'E9001', '123', '2025-04-15 00:00:00', 0),
            ('login_casey', 'E001', 'secret123', '2025-04-17 20:27:26', 0),
            ('login_E009', 'E009', 'cfhillskhdjhe', '2025-04-21 19:40:30', 0),
            ('login_E003', 'E003', '123', '2025-04-21 01:05:24', 0),
            ('login_E004', 'E004', '123', '2025-04-21 18:09:59', 0),
            ('login_E006', 'E006', '123', '2025-04-21 19:19:47', 0),
            ('login_E007', 'E007', 'pass1', '2025-04-21 18:46:58', 0),
            ('login_E008', 'E008', '1', '2025-04-20 10:05', 0),
            ('login_E010', 'E010', '12312312312312', '2025-04-23 12:59:27', 0),
            ('login_E011', 'E011', 'pass3', '2025-04-20 10:05', 0),
            ('login_E012', 'E012', 'pass4', '2025-04-20 10:05', 0),
            ('login_E013', 'E013', 'pass5', '2025-04-20 10:05', 0),
            ('login_E014', 'E014', 'pass6', '2025-04-20 10:05', 0),
            ('login_E015', 'E015', 'pass7', '2025-04-20 10:05', 0),
            ('login_E016', 'E016', 'pass8', '2025-04-20 10:05', 0),
            ('login_TEST02', 'TEST01', 'password123', '2025-04-23 12:46:21', 0),
            ('obesseym', 'E9005', '123', '2025-04-15 00:00:00', 0),
            ('phawkes3', 'E9015', '123', '2025-04-15 00:00:00', 0)
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

        # Step 4: Insert projects (from image 4)
        print("\nPopulating projects table...")
        projects = [
            ('P001', 'TimeTrackerDBTest', 'E001', '2025-04-19 21:44:34', None, 1),
            ('P002', 'MarketingWebsite', 'E004', '2025-04-20 10:00:00', None, 1),
            ('P003', 'InternalTooling', 'E9009', '2025-04-21 09:00:00', None, 1),
            ('P004', 'ClientOnboarding', 'E007', '2025-04-22 14:30:00', None, 1),
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

        # Step 5: Insert employee_projects assignments (from image 6)
        print("\nPopulating employee_projects junction table...")
        employee_projects = [
            ('E001', 'P001'),
            ('E001', 'P002'),
            ('TEST01', 'P001'),
            ('TEST01', 'P002'),
            ('E9009', 'P003'),
            ('E004', 'P003'),
            ('E9009', 'P001'),
            ('E003', 'P002'),
            ('E011', 'P001'),
            ('E012', 'P002'),
            ('E013', 'P003'),
            ('E007', 'P004'),
            ('E015', 'P001'),
            ('E016', 'P002'),
            ('E9001', 'P10001'),
            ('E9003', 'P10003'),
            ('E9005', 'P10005'),
            ('E9006', 'P10006'),
            ('E9008', 'P10006'),
            ('E9007', 'P10007'),
            ('E9007', 'P10009'),
            ('E9011', 'P10010'),
            ('E9011', 'P10011'),
            ('E9012', 'P10012'),
            ('E9014', 'P10014'),
            ('E9015', 'P10015'),
            ('E9016', 'P10016'),
            ('E9017', 'P10017'),
            ('E9018', 'P10018'),
            ('E9019', 'P10019'),
            ('E9021', 'P10021'),
            ('E9024', 'P10024'),
            ('E012', 'P004')
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

        # Step 6: Insert time entries (from image 5)
        print("\nPopulating time table...")
        time_entries = [
            ('1', 'E001', 'P001', '2025-04-1920:58:08', '2025-04-1921:58:08', 'Worked on initial setup', '1'),
            ('2', 'E001', 'P001', '2025-04-2009:30:00', '2025-04-2011:00:00', 'Entered start/stop manually', '1'),
            ('3', 'TEST01', 'P001', '2025-04-2110:00:00', '2025-04-2111:30:00', 'Manual entry for testing', '1'),
            ('4', 'E001', 'P002', '2025-04-2213:00:00', '2025-04-2214:00:00', 'Casey: project planning', '1'),
            ('5', 'TEST01', 'P002', '2025-04-2215:00:00', '2025-04-2216:00:00', 'Tess: wireframing', '1'),
            ('6', 'E0009', 'P003', '2025-04-2309:00:00', '2025-04-2310:30:00', 'Liesl: team check-ins and', '1'),
            ('7', 'E004', 'P003', '2025-04-2311:00:00', '2025-04-2312:00:00', 'documentation', '1'),
            ('8', 'E0009', 'P001', '2025-04-2404:52:06', '2025-04-2405:52:06', 'Erika: stakeholder meeting', '1'),
            ('9', 'TEST01', 'P001', '2025-04-2403:52:06', '2025-04-2404:52:06', 'Liesl: debugging session', '1'),
            ('10', 'E003', 'P001', '2025-04-2309:00:00', '2025-04-2310:30:00', 'Tess: finished documentation', '1'),
            ('11', 'E003', 'P002', '2025-04-2413:00:00', '2025-04-2414:15:00', 'Yesac: planning meeting', '1'),
            ('12', 'E011', 'P001', '2025-04-2409:00:00', '2025-04-2410:00:00', 'Yesac: reviewed reports', '1'),
            ('13', 'E012', 'P002', '2025-04-2410:00:00', '2025-04-2411:00:00', 'Nina: daily task', '1'),
            ('14', 'E013', 'P003', '2025-04-2411:00:00', '2025-04-2412:00:00', 'Tom: daily task', '1'),
            ('15', 'E014', 'P004', '2025-04-2412:00:00', '2025-04-2413:00:00', 'Sara: daily task', '1'),
            ('16', 'E015', 'P001', '2025-04-2413:00:00', '2025-04-2414:00:00', 'Alex: daily task', '1'),
            ('17', 'E016', 'P002', '2025-04-2414:00:00', '2025-04-2415:00:00', 'Jamie: daily task', '1'),
            ('18', 'E9001', 'P10001', '2024-04-0509:50:00', '2024-04-0511:59:00', 'Taylor: daily task', '0'),
            ('19', 'E9003', 'P10003', '2024-12-0916:47:00', '2024-12-0918:01:00', 'Integer ac', '1'),
            ('20', 'E9005', 'P10005', '2024-04-1404:01:00', '2024-04-1405:17:00', 'Vestibulum', '1'),
            ('21', 'E9006', 'P10006', '2025-01-0820:09:00', '2025-01-0821:05:00', 'Suspendisse', '0'),
            ('22', 'E9005', 'P10005', '2025-03-1109:51:00', '2025-03-1111:03:00', 'Mauris enim', '1'),
            ('23', 'E9006', 'P10006', '2025-01-2403:11:00', '2025-01-2404:21:00', 'Sed sagittis', '0'),
            ('24', 'E9006', 'P10006', '2024-05-2907:58:00', '2024-05-2909:56:00', 'Cras non tortor', '1'),
            ('25', 'E9006', 'P10006', '2025-01-1614:46:00', '2025-01-1615:41:00', 'Donec diam', '0'),
            ('26', 'E9007', 'P10007', '2024-06-2321:55:00', '2024-06-2322:51:00', 'Phasellus in', '0'),
            ('27', 'E9007', 'P10009', '2024-03-1019:27:00', '2024-03-1020:39:00', 'Duis bibendum', '1'),
            ('28', 'E9007', 'P10009', '2024-06-2206:15:00', '2024-06-2209:11:00', 'Sed sagittis', '1'),
            ('29', 'E9011', 'P10010', '2025-01-2301:01:00', '2025-01-2302:03:00', 'In sagittis', '1'),
            ('30', 'E9011', 'P10011', '2025-02-1304:19:00', '2025-02-1305:57:00', 'Duis aliquam', '1'),
            ('31', 'E9012', 'P10012', '2024-06-1519:12:00', '2024-06-1520:44:00', 'In congue', '0'),
            ('32', 'E9014', 'P10014', '2025-04-0509:30:00', '2025-04-0611:09:00', 'Maecenas ut', '1'),
            ('33', 'E9015', 'P10015', '2024-08-0708:32:00', '2024-08-0719:50:00', 'Pellentesque', '1'),
            ('34', 'E9016', 'P10016', '2025-02-0408:28:00', '2025-02-0410:34:00', 'Nulla ute', '0'),
            ('35', 'E9017', 'P10017', '2025-03-3113:09:00', '2025-03-3114:09:00', 'Praesent id', '1'),
            ('36', 'E9018', 'P10018', '2025-02-0502:50:00', '2025-02-0505:12:00', 'Quisque posuere', '0'),
            ('37', 'E9019', 'P10020', '2024-10-0913:38:00', '2024-10-0915:09:00', 'Vestibulum', '1'),
            ('38', 'E9021', 'P10021', '2024-03-2603:58:00', '2024-03-2606:12:00', 'Fusce posuere', '1'),
            ('39', 'E9024', 'P10024', '2024-10-3011:00:00', '2024-10-3011:45:00', 'In quis justo', '0'),
            ('40', 'E9025', 'P10025', '2025-04-0703:24:00', '2025-04-0705:22:00', 'Maecenas ut', '0'),
            ('41', 'TEST01', 'P001', '2025-04-2509:00:00', '2025-04-2510:30:00', 'Tess: completed documentation updates', '0'),
            ('42', 'TEST01', 'P002', '2025-04-2511:00:00', '2025-04-2512:00:00', 'Tess: meeting with project team', '0'),
            ('43', 'E012', 'P003', '2025-04-2508:00:00', '2025-04-2509:15:00', 'Tom: sprint review session', '0'),
            ('44', 'E012', 'P004', '2025-04-2513:00:00', '2025-04-2514:00:00', 'Tom: system update prep', '0')
        ]

        for entry in time_entries:
            try:
                # Parse dates for calculation of TOTAL_MINUTES
                start_time = datetime.strptime(entry[2], "%Y-%m-%d %H:%M:%S")
                stop_time = datetime.strptime(entry[3], "%Y-%m-%d %H:%M:%S")

                # Calculate minutes
                minutes_diff = int((stop_time - start_time).total_seconds() / 60)

                cursor.execute("""
                            INSERT INTO time (TIMEID, EMPID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
                print(f"  Added time entry for {entry[1]}, duration: {minutes_diff} minutes")
            except mariadb.Error as e:
                print(f"  Error adding time entry for {entry[1]}: {e}")

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
