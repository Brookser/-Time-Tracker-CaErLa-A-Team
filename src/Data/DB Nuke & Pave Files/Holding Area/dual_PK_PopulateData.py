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
#                   - 05.05.2025: changes made directly to DB via console script;
#                         scripts rewritten in order to conform to new structure
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


def populate_additional_data():
    """
    Function to populate the database with the additional data based on SQL dump
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Temporarily disable foreign key checks
        print("Temporarily disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Start transaction
        conn.autocommit = False

        # Step 1: Insert departments (updated to match SQL dump)
        print("\nPopulating department table...")
        departments = [
            ('D001', 'General', None, 0),
            ('D002', 'Sales', 'E9003', 1),
            ('D003', 'Popcorn Making', 'E9006', 1),
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

        # Step 2: Insert employees (updated to match SQL dump)
        print("\nPopulating employee_table...")
        employees = [
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
            ('E015', 'Jamie', 'Fox', 'MKT', 'jamie@wou.edu', 'E9006', 1, 'individual'),
            ('E016', 'Taylor', 'Green', 'MKT', 'taylor@wou.edu', 'E015', 1, 'manager'),
            ('E9001', 'Lane', 'Beere', 'LEG', 'lbeere@rakuten.co.jp', 'E9006', 1, 'individual'),
            ('E9002', 'Bobina', 'Windless', 'LEG', 'bwindless8@census.gov', None, 1, 'manager'),
            ('E9003', 'Elwin', 'Klagseman', 'FIN', 'eklagseman@free.fr', 'E9006', 1, 'individual'),
            ('E9004', 'Archibald', 'Bemet', 'HR', 'abemet@jamaizone.com', 'E9006', 1, 'individual'),
            ('E9005', 'Othello', 'Bessey', 'HR', 'obessey@jdjakla.ca', 'E9006', 1, 'individual'),
            ('E9006', 'Godfrey', 'Gaye', 'HR', 'ggaye7@mashable.com', 'E9006', 1, 'manager'),
            ('E9007', 'Angelia', 'Favell', 'SVCS', 'afavella@hostgator.com', None, 1, 'manager'),
            ('E9008', 'Aundrea', 'Abela', 'SVCS', 'aabelak@lycos.com', 'E9007', 0, 'individual'),
            ('E9009', 'Lisa', 'Hill', 'ENG', 'lisah@wou.edu', None, 1, 'manager'),
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
                cursor.execute("""
                    INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)
                print(f"  Added employee: {emp[0]} - {emp[1]} {emp[2]}")
            except mariadb.Error as e:
                print(f"  Error adding employee {emp[0]}: {e}")

        # Step 3: Insert login data (from SQL dump)
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
            ('login_E003', 'E003', '123', '2025-04-21 01:05:24', 0),
            ('login_E004', 'E004', '123', '2025-04-21 18:09:59', 0),
            ('login_E006', 'E006', '123', '2025-04-21 19:19:47', 0),
            ('login_E007', 'E007', 'pass1', '2025-04-21 18:46:58', 0),
            ('login_E008', 'E008', '1', '2025-04-20 10:05:00', 0),
            ('login_E009', 'E009', 'cfhillskhdjhe', '2025-04-21 19:40:30', 0),
            ('login_E010', 'E010', '12312312312312', '2025-04-23 12:59:27', 0),
            ('login_E011', 'E011', 'pass3', '2025-04-20 10:05:00', 0),
            ('login_E012', 'E012', 'pass4', '2025-04-20 10:05:00', 0),
            ('login_E013', 'E013', 'pass5', '2025-04-20 10:05:00', 0),
            ('login_E014', 'E014', 'pass6', '2025-04-20 10:05:00', 0),
            ('login_E015', 'E015', 'pass7', '2025-04-20 10:05:00', 0),
            ('login_E016', 'E016', 'pass8', '2025-04-20 10:05:00', 0),
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

        # Step 4: Insert projects
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
            ('P10025', 'Squirrel', 'E9013', '2025-04-15 00:00:00', 'P10022', 1),
            ('P10026','Recipes','E015','2025-05-04 00:00:00',None,0),
            ('P10027','Fish','E9001','2025-05-04 00:00:00',None,0),
            ('P10028','Birds','E9003','2025-05-04 00:00:00',None,0),
            ('P10029','Plants','E9004','2025-05-04 00:00:00',None,0),
            ('P10030','Games','E9006','2025-05-04 00:00:00',None,0),
            ('P10031','Exercise','E004','2025-05-04 00:00:00',None,0),
            ('P10032','Languages','E004','2025-05-04 00:00:00',None,0),
            ('P10033','Recipes','E015','2025-05-04 00:00:00',None,0),
            ('P10034','Fish','E9001','2025-05-04 00:00:00',None,0),
            ('P10035','Birds','E9003','2025-05-04 00:00:00',None,0),
            ('P10036','Plants','E9004','2025-05-04 00:00:00',None,0),
            ('P10037','Games','E9006','2025-05-04 00:00:00',None,0),
            ('P10038','Exercise','E004','2025-05-04 00:00:00',None,0),
            ('P10039','Languages','E004','2025-05-04 00:00:00',None,0),
            ('P10040','Recipes','E015','2025-05-04 00:00:00',None,0),
            ('P10041','Fish','E9001','2025-05-04 00:00:00',None,0),
            ('P10042','Birds','E9003','2025-05-04 00:00:00',None,0),
            ('P10043','Plants','E9004','2025-05-04 00:00:00',None,0),
            ('P10044','Games','E9006','2025-05-04 00:00:00',None,0),
            ('P10045','Exercise','E004','2025-05-04 00:00:00',None,0),
            ('P10046','Languages','E004','2025-05-04 00:00:00',None,0),
            ('P10047','Recipes','E015','2025-05-04 00:00:00',None,1),
            ('P10048','Fish','E9001','2025-05-04 00:00:00',None,1),
            ('P10049','Birds','E9003','2025-05-04 00:00:00',None,1),
            ('P10050','Plants','E9004','2025-05-04 00:00:00',None,1),
            ('P10051','Games','E9006','2025-05-04 00:00:00',None,1),
            ('P10052','Exercise','E004','2025-05-04 00:00:00',None,1),
            ('P10053','Languages','E004','2025-05-04 00:00:00',None,1),
            ('P_0ebcc5d2','FY25Q2 QBR','E012','2025-05-02 00:01:20',None,1),
            ('P_1c846c27','TestProj to Add employees','E012','2025-04-30 21:22:04',None,1),
            ('P_214b1665','TestProj to Add employees','E012','2025-04-30 21:21:01',None,1),
            ('P_39442928','Sprint 5','E9006','2025-05-01 22:58:09',None,1),
            ('P_5b0ea510','Prepare for Stakeholder meeting','E9006','2025-05-01 22:57:43',None,1),
            ('P_64d9b214','Marketing Website Q1 Refresh','E012','2025-05-02 00:05:00',None,1),
            ('P_831b5a2f','Personal Project 1','E013','2025-05-01 19:57:31',None,1),
            ('P_9991a15c','TestProj2 Via Web UI','E012','2025-04-30 20:49:45',None,1),
            ('P_9febc212','TestProj3 via UI post DB adjust','E012','2025-04-30 23:12:42',None,1),
            ('P_ALPHA1','Quarterly Marketing Revamp','E012','2025-05-01 03:39:18',None,1),
            ('P_ALPHA2','Website Redesign Sprint','E012','2025-05-01 03:39:18',None,1),
            ('P_dc6125b5','TessTestPRoj','TEST01','2025-05-01 10:35:28',None,1),
            ('P_ece415c0','TestProj4 via PM UI','E004','2025-05-01 09:58:25',None,1),
            ('P_f505695e','Project 8','E004','2025-05-01 19:49:04',None,1),
            ('P_f7b57295','Project 7','E9006','2025-05-01 19:47:53',None,1),
            ('SD0001','Special Development 1','E015','2025-05-04 00:00:00',None,1),
            ('SD0002','Special Development 2','E015','2025-05-04 00:00:00',None,1),
            ('SD0004','Special Development 4','E015','2025-05-04 00:00:00',None,1),
            ('SD0005','Special Development 5','E015','2025-05-04 00:00:00',None,1),
            ('SD0006','Special Development 6','E015','2025-05-04 00:00:00',None,1),
            ('SD0007','Special Development 7','E015','2025-05-04 00:00:00',None,1)
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

        # Step 5: Insert employee_projects assignments (same as original script)
        print("\nPopulating employee_projects junction table...")
        employee_projects = [
            ('E001', 'P001'),
            ('E001', 'P002'),
            ('E001', 'P_ece415c0'),
            ('E001', 'P_f505695e'),
            ('E003', 'P002'),
            ('E004', 'P001'),
            ('E004', 'P002'),
            ('E004', 'P003'),
            ('E004', 'P_ece415c0'),
            ('E004', 'P_f505695e'),
            ('E004', 'SD0001'),
            ('E004', 'SD0002'),
            ('E004', 'SD0005'),
            ('E004', 'SD0007'),
            ('E007', 'P004'),
            ('E011', 'P001'),
            ('E011', 'P_1c846c27'),
            ('E012', 'P002'),
            ('E012', 'P004'),
            ('E012', 'P_0ebcc5d2'),
            ('E012', 'P_1c846c27'),
            ('E012', 'P_64d9b214'),
            ('E012', 'P_9febc212'),
            ('E013', 'P003'),
            ('E013', 'P_1c846c27'),
            ('E013', 'P_39442928'),
            ('E013', 'P_64d9b214'),
            ('E013', 'P_831b5a2f'),
            ('E013', 'P_ece415c0'),
            ('E013', 'P_f7b57295'),
            ('E014', 'P_39442928'),
            ('E014', 'P_ece415c0'),
            ('E014', 'P_f7b57295'),
            ('E015', 'P001'),
            ('E015', 'P002'),
            ('E015', 'SD0001'),
            ('E015', 'SD0004'),
            ('E015', 'SD0006'),
            ('E015', 'SD0007'),
            ('E016', 'P002'),
            ('E9001', 'P10001'),
            ('E9001', 'P10007'),
            ('E9001', 'SD0002'),
            ('E9001', 'SD0004'),
            ('E9001', 'SD0005'),
            ('E9001', 'SD0007'),
            ('E9003', 'P001'),
            ('E9003', 'P002'),
            ('E9003', 'P10001'),
            ('E9003', 'P10003'),
            ('E9003', 'SD0002'),
            ('E9003', 'SD0005'),
            ('E9004', 'P10001'),
            ('E9004', 'P_39442928'),
            ('E9004', 'SD0001'),
            ('E9004', 'SD0004'),
            ('E9004', 'SD0005'),
            ('E9004', 'SD0007'),
            ('E9005', 'P10005'),
            ('E9006', 'P001'),
            ('E9006', 'P10006'),
            ('E9006', 'P_39442928'),
            ('E9006', 'P_5b0ea510'),
            ('E9006', 'P_f7b57295'),
            ('E9006', 'SD0004'),
            ('E9007', 'P10007'),
            ('E9007', 'P10009'),
            ('E9008', 'P10006'),
            ('E9009', 'P001'),
            ('E9009', 'P003'),
            ('E9011', 'P10010'),
            ('E9011', 'P10011'),
            ('E9011', 'P_9febc212'),
            ('E9012', 'P10012'),
            ('E9012', 'P_64d9b214'),
            ('E9013', 'P_1c846c27'),
            ('E9013', 'P_9febc212'),
            ('E9014', 'P10014'),
            ('E9015', 'P10015'),
            ('E9016', 'P10016'),
            ('E9017', 'P10017'),
            ('E9018', 'P10018'),
            ('E9019', 'P10019'),
            ('E9021', 'P10021'),
            ('E9023', 'P_9febc212'),
            ('E9024', 'P10024'),
            ('TEST01', 'P001'),
            ('TEST01', 'P002'),
            ('TEST01', 'P_dc6125b5')
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

        # Step 6: Insert time entries
        print("\nPopulating time table...")
        # Corrected time entries - note the updated schema with PROJECTID column
        time_entries = [
            ('1', 'E001', '2025-04-19 20:58:08', '2025-04-19 21:58:08', 'Worked on initial setup', 1, 'P001'),
            ('2', 'E001', '2025-04-20 09:30:00', '2025-04-20 11:00:00', 'Entered start/stop manually', 1, 'P002'),
            ('3', 'TEST01', '2025-04-21 10:00:00', '2025-04-21 11:30:00', 'Manualentry/testing', 1, 'P001'),
            ('4', 'E001', '2025-04-22 13:00:00', '2025-04-22 14:00:00', 'Caseyjprojectplanning', 1, 'P001'),
            ('5', 'TEST01', '2025-04-22 15:00:00', '2025-04-22 16:00:00', 'Tessjwritinmg', 1, 'P001'),
            ('6', 'E9009', '2025-04-23 09:00:00', '2025-04-23 10:30:00', 'Lisajteamcheck-inandocumentation', 1, 'P003'),
            ('7', 'E004', '2025-04-23 11:00:00', '2025-04-23 12:00:00', 'Erikajstakeholdermeeting', 1, 'P003'),
            ('8', 'E9009', '2025-04-24 04:52:06', '2025-04-24 05:52:06', 'Lisajdebuggsession', 1, 'P003'),
            ('9', 'TEST01', '2025-04-24 03:52:06', '2025-04-24 04:52:06', 'Tessfinisheddocumentation', 1, 'P001'),
            ('10', 'E003', '2025-04-23 09:00:00', '2025-04-23 10:30:00', 'Yesacjplanningmeeting', 1, 'P002'),
            ('11', 'E011', '2025-04-24 09:00:00', '2025-04-24 10:00:00', 'Ninajdailytask', 1, 'P_1c846c27'),
            ('12', 'E012', '2025-04-24 10:00:00', '2025-04-24 11:00:00', 'Tomjdailytask', 1, 'P002'),
            ('13', 'E013', '2025-04-24 11:00:00', '2025-04-24 12:00:00', 'Sarajdailytask', 1, 'P003'),
            ('14', 'E014', '2025-04-24 12:00:00', '2025-04-24 13:00:00', 'Alexjdailytask', 1, 'P004'),
            ('15', 'E015', '2025-04-24 13:00:00', '2025-04-24 14:00:00', 'Jamiejdailytask', 1, 'P001'),
            ('16', 'E016', '2025-04-24 14:00:00', '2025-04-24 15:00:00', 'Taylorjdailytask', 1, 'P002'),
            ('17', 'E016', '2025-04-24 14:00:00', '2025-04-24 15:00:00', 'Taylorjdailytask', 1, 'P002'),
            ('18', 'E9001', '2024-04-05 09:50:00', '2024-04-05 11:59:00', 'Integer ac', 0, 'P10001'),
            ('19', 'E9003', '2024-12-09 16:47:00', '2024-12-09 18:01:00', 'Vestibulum', 1, 'P10003'),
            ('20', 'E9005', '2024-04-14 04:01:00', '2024-04-14 05:17:00', 'Suspendisse', 1, 'P10005'),
            ('21', 'E9006', '2025-01-08 20:09:00', '2025-01-08 21:05:00', 'Mauris enim', 0, 'P10006'),
            ('22', 'E9005', '2025-03-11 09:51:00', '2025-03-11 11:03:00', 'Sed sagittis', 1, 'P10005'),
            ('23', 'E9006', '2025-01-24 03:11:00', '2025-01-24 04:21:00', 'Cras non tortor', 0, 'P10006'),
            ('24', 'E9006', '2024-05-29 07:58:00', '2024-05-29 09:56:00', 'Donec diam', 1, 'P10006'),
            ('25', 'E9006', '2025-01-16 14:46:00', '2025-01-16 15:41:00', 'Phasellus in', 0, 'P10006'),
            ('26', 'E9007', '2024-06-23 21:55:00', '2024-06-23 22:51:00', 'Duis bibendum', 0, 'P10007'),
            ('27', 'E9007', '2024-03-10 19:27:00', '2024-03-10 20:39:00', 'Sed sagittis', 1, 'P10007'),
            ('28', 'E9007', '2024-06-22 06:15:00', '2024-06-22 09:11:00', 'In sagittis', 1, 'P10007'),
            ('29', 'E9011', '2025-01-23 01:01:00', '2025-01-23 02:03:00', 'Duis aliquam', 1, 'P10010'),
            ('30', 'E9011', '2025-02-13 04:19:00', '2025-02-13 05:57:00', 'In congue', 1, 'P10011'),
            ('31', 'E9012', '2024-06-15 19:12:00', '2024-06-15 20:44:00', 'Maecenas ut', 0, 'P10012'),
            ('32', 'E9014', '2025-04-05 09:30:00', '2025-04-06 11:09:00', 'Pellentesque', 1, 'P10014'),
            ('33', 'E9015', '2024-08-07 08:32:00', '2024-08-07 19:50:00', 'Nulla ute', 1, 'P10015'),
            ('34', 'E9016', '2025-02-04 08:28:00', '2025-02-04 10:34:00', 'Praesent id', 0, 'P10016'),
            ('35', 'E9017', '2025-03-31 13:09:00', '2025-03-31 14:09:00', 'Quisque posuere', 1, 'P10017'),
            ('36', 'E9018', '2025-02-05 02:50:00', '2025-02-05 05:12:00', 'Vestibulum', 0, 'P10018'),
            ('37', 'E9019', '2024-10-09 13:38:00', '2024-10-09 15:09:00', 'Fusce posuere', 1, 'P10019'),
            ('38', 'E9021', '2024-03-26 03:58:00', '2024-03-26 06:12:00', 'In quis justo', 1, 'P10021'),
            ('39', 'E9024', '2024-10-30 11:00:00', '2024-10-30 11:45:00', 'Maecenas ut', 0, 'P10024'),
            ('40', 'E9025', '2025-04-07 03:24:00', '2025-04-07 05:22:00', 'Donec diam', 0, 'P10024'),
            ('41', 'TEST01', '2025-04-25 09:00:00', '2025-04-25 10:30:00', 'Tess:completed documentation', 0, 'P002'),
            ('42', 'TEST01', '2025-04-25 11:00:00', '2025-04-25 12:00:00', 'Tess:meeting with project team', 0, 'P002'),
            ('43', 'E012', '2025-04-25 08:00:00', '2025-04-25 09:15:00', 'Tom:sprint review session', 0, 'P004'),
            ('44', 'E012', '2025-04-25 13:00:00', '2025-04-25 14:00:00', 'Tom:system update prep', 0, 'P_1c846c27'),
            ('DD5001', 'E004', '2025-05-04 11:53:00', '2025-05-04 13:35:00', 'Organic local groupware', 0, 'SD0001'),
            ('DD5002', 'E004', '2025-05-04 10:01:00', '2025-05-04 10:35:00', 'Managed optimizing contingency', 0, 'SD0002'),
            ('DD5003', 'E004', '2025-05-04 10:54:00', '2025-05-04 11:08:00', 'Mandatory contextually-based paradigm', 0, 'SD0005'),
            ('DD5004', 'E015', '2025-05-04 11:55:00', '2025-05-04 12:26:00', 'Cross-platform asynchronous open architecture', 0, 'SD0001'),
            ('DD5005', 'E015', '2025-05-04 11:14:00', '2025-05-04 12:09:00', 'Optimized systemic monitoring', 0, 'SD0004'),
            ('DD5006', 'E015', '2025-05-04 08:57:00', '2025-05-04 12:02:00', 'Sharable bifurcated analyzer', 0, 'P002'),
            ('DD5007', 'E015', '2025-05-04 10:11:00', '2025-05-04 11:58:00', 'Business-focused 5th generation software', 0, 'SD0007'),
            ('DD5008', 'E9001', '2025-05-04 11:27:00', '2025-05-04 12:39:00', 'User-friendly directional complexity', 0, 'SD0002'),
            ('DD5009', 'E9001', '2025-05-04 11:57:00', '2025-05-04 12:56:00', 'Future-proofed multi-tasking ability', 0, 'SD0005'),
            ('DD5010', 'E9001', '2025-05-04 10:52:00', '2025-05-04 11:35:00', 'Optional encompassing throughput', 0, 'SD0004'),
            ('DD5011', 'E9001', '2025-05-04 11:00:00', '2025-05-04 11:33:00', 'Function-based 24 hour Graphical User Interface', 0, 'P10007'),
            ('DD5012', 'E9003', '2025-05-04 10:03:00', '2025-05-04 13:14:00', 'Profit-focused zero administration complexity', 0, 'P10001'),
            ('DD5013', 'E9003', '2025-05-04 10:04:00', '2025-05-04 11:27:00', 'Multi-layered scalable benchmark', 0, 'SD0002'),
            ('DD5014', 'E9003', '2025-05-04 10:37:00', '2025-05-04 12:49:00', 'Realigned background extranet', 0, 'SD0005'),
            ('DD5015', 'E9003', '2025-05-04 10:39:00', '2025-05-04 12:18:00', 'Profit-focused hybrid flexibility', 0, 'P002'),
            ('DD5016', 'E9004', '2025-05-04 11:58:00', '2025-05-04 12:56:00', 'Multi-layered user-facing middleware', 0, 'SD0004'),
            ('DD5017', 'E9004', '2025-05-04 10:06:00', '2025-05-04 11:45:00', 'Reverse-engineered intangible intranet', 0, 'SD0005'),
            ('DD5018', 'E9004', '2025-05-04 11:48:00', '2025-05-04 13:17:00', 'Persistent coherent functionalities', 0, 'SD0007'),
            ('DD5019', 'E9004', '2025-05-04 10:12:00', '2025-05-04 12:07:00', 'Synchronized zero tolerance migration', 0, 'SD0001'),
            ('DD5020', 'E9005', '2025-05-04 09:53:00', '2025-05-04 11:52:00', 'Streamlined national toolset', 0, 'SD0001'),
            ('DD5021', 'E004', '2025-05-04 10:03:00', '2025-05-04 10:53:00', 'Cloned stable flexibility', 0, 'P002'),
            ('DD5022', 'E015', '2025-05-04 12:05:00', '2025-05-04 12:49:00', 'Fully-configurable directional access', 0, 'SD0002'),
            ('DD5023', 'E9001', '2025-05-04 10:16:00', '2025-05-04 11:39:00', 'Ameliorated system-worthy conglomeration', 0, 'SD0007'),
            ('DD5024', 'E9003', '2025-05-04 11:43:00', '2025-05-04 12:56:00', 'Distributed multimedia strategy', 0, 'P001'),
            ('DD5025', 'E9004', '2025-05-04 12:04:00', '2025-05-04 13:11:00', 'Future-proofed transitional archive', 0, 'P10001'),
            ('DD5026', 'E9006', '2025-05-04 10:19:00', '2025-05-04 10:37:00', 'Multi-lateral interactive process improvement', 0, 'P001'),
            ('DD5027', 'E004', '2025-05-04 10:31:00', '2025-05-04 12:14:00', 'Optimized bifurcated challenge', 0, 'SD0007'),
            ('DD5028', 'E004', '2025-05-04 10:06:00', '2025-05-04 12:07:00', 'Sharable asynchronous customer loyalty', 0, 'P001'),
            ('DD5029', 'E004', '2025-05-04 10:08:00', '2025-05-04 11:47:00', 'Team-oriented directional time-frame', 0, 'SD0001'),
            ('DD5030', 'E004', '2025-05-04 09:51:00', '2025-05-04 10:49:00', 'Multi-layered actuating internet service-desk', 0, 'SD0002'),
            ('DD5031', 'E004', '2025-05-04 10:06:00', '2025-05-04 10:20:00', 'Diverse content-based initiative', 0, 'SD0005'),
            ('DD5032', 'E015', '2025-05-04 11:08:00', '2025-05-04 12:09:00', 'Balanced 24 hour productivity', 0, 'SD0001'),
            ('DD5033', 'E015', '2025-05-04 12:03:00', '2025-05-04 12:58:00', 'Object-based web-enabled implementation', 0, 'SD0004'),
            ('DD5034', 'E015', '2025-05-04 10:34:00', '2025-05-04 12:39:00', 'Synergized leading edge alliance', 0, 'P002'),
            ('DD5035', 'E015', '2025-05-04 09:51:00', '2025-05-04 11:38:00', 'Re-engineered web-enabled productivity', 0, 'SD0007'),
            ('DD5036', 'E9001', '2025-05-04 11:34:00', '2025-05-04 12:46:00', 'Profound disintermediate synergy', 0, 'SD0002'),
            ('DD5037', 'E9001', '2025-05-04 11:54:00', '2025-05-04 13:13:00', 'Optional explicit intranet', 0, 'SD0005'),
            ('DD5038', 'E9001', '2025-05-04 09:59:00', '2025-05-04 10:42:00', 'Robust analyzing customer loyalty', 0, 'SD0004'),
            ('DD5039', 'E9001', '2025-05-04 10:04:00', '2025-05-04 11:33:00', 'Extended intangible interface', 0, 'P10007'),
            ('DD5040', 'E9003', '2025-05-04 12:03:00', '2025-05-04 13:14:00', 'Reduced radical strategy', 0, 'P10001'),
            ('DD5041', 'E9003', '2025-05-04 10:27:00', '2025-05-04 11:50:00', 'Decentralized stable flexibility', 0, 'SD0002'),
            ('DD5042', 'E9003', '2025-05-04 10:06:00', '2025-05-04 12:18:00', 'Sharable client-server open architecture', 0, 'SD0005'),
            ('DD5043', 'E9003', '2025-05-04 10:17:00', '2025-05-04 11:59:00', 'Managed full-range emulation', 0, 'P002'),
            ('DD5044', 'E9004', '2025-05-04 11:16:00', '2025-05-04 11:50:00', 'Progressive object-oriented portal', 0, 'SD0004'),
            ('DD5045', 'E9004', '2025-05-04 11:35:00', '2025-05-04 11:49:00', 'Centralized contextually-based portal', 0, 'SD0005'),
            ('DD5046', 'E9004', '2025-05-04 10:43:00', '2025-05-04 11:44:00', 'Digitized optimizing parallelism', 0, 'SD0007'),
            ('DD5047', 'E9004', '2025-05-04 11:43:00', '2025-05-04 12:38:00', 'Fundamental secondary customer loyalty', 0, 'SD0001'),
            ('DD5048', 'E9006', '2025-05-04 09:52:00', '2025-05-04 11:52:00', 'Down-sized actuating superstructure', 0, 'SD0004'),
            ('DD5049', 'E004', '2025-05-04 10:42:00', '2025-05-04 12:29:00', 'Organized motivating implementation', 0, 'P002'),
            ('DD5050', 'E015', '2025-05-04 10:45:00', '2025-05-04 11:57:00', 'Decentralized leading definition', 0, 'SD0006'),
            ('DD5051', 'E9001', '2025-05-04 09:57:00', '2025-05-04 11:16:00', 'Organized content-based focus group', 0, 'SD0007'),
            ('DD5052', 'E9003', '2025-05-04 11:17:00', '2025-05-04 12:20:00', 'Networked 3rd generation time-frame', 0, 'P001'),
            ('DD5053', 'E9004', '2025-05-04 10:24:00', '2025-05-04 10:57:00', 'Right-sized context-sensitive architecture', 0, 'P10001'),
            ('DD5054', 'E9006', '2025-05-04 11:07:00', '2025-05-04 12:18:00', 'Object-based demand-driven challenge', 0, 'P001'),
            ('DD5055', 'E004', '2025-05-04 11:31:00', '2025-05-04 12:54:00', 'Proactive fault-tolerant capacity', 0, 'SD0007'),
            ('DD5056', 'E004', '2025-05-04 10:04:00', '2025-05-04 12:16:00', 'Expanded value-added open architecture', 0, 'P001'),
            ('t-517a15c6', 'E004', '2025-05-05 01:03:02', '2025-05-05 08:03:06', 'This is a time entry test via start/stop button', 0, 'P001'),
            ('t-a3e03c41', 'E004', '2025-05-05 00:55:42', '2025-05-05 08:02:23', '', 0, 'P001'),
            ('T50001', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:32:00', 'Organic local groupware', 0, 'SD0001'),
            ('T50002', 'E9001', '2025-05-04 09:50:00', '2025-05-04 10:24:00', 'Extended optimizing contingency', 0, 'SD0005'),
            ('T50003', 'E004', '2025-05-04 09:50:00', '2025-05-04 10:04:00', 'Mandatory contextually-based paradigm', 0, 'SD0005'),
            ('T50004', 'E015', '2025-05-04 09:50:00', '2025-05-04 10:51:00', 'Cross-platform asynchronous open architecture', 0, 'SD0001'),
            ('T50005', 'E015', '2025-05-04 09:50:00', '2025-05-04 10:45:00', 'Optimized systemic monitoring', 0, 'SD0004'),
            ('T50006', 'E015', '2025-05-04 09:50:00', '2025-05-04 11:55:00', 'Sharable bifurcated analyzer', 0, 'P002'),
            ('T50007', 'E015', '2025-05-04 09:50:00', '2025-05-04 11:37:00', 'Business-focused 5th generation software', 0, 'SD0007'),
            ('T50008', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:02:00', 'User-friendly directional complexity', 0, 'SD0002'),
            ('T50009', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:09:00', 'Future-proofed multi-tasking ability', 0, 'SD0005'),
            ('T50010', 'E9001', '2025-05-04 09:50:00', '2025-05-04 10:33:00', 'Optional encompassing throughput', 0, 'SD0004'),
            ('T50011', 'E9001', '2025-05-04 09:50:00', '2025-05-04 10:23:00', 'Function-based 24 hour Graphical User Interface', 0, 'P10007'),
            ('T50012', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:01:00', 'Profit-focused zero administration complexity', 0, 'P10001'),
            ('T50013', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:13:00', 'Multi-layered scalable benchmark', 0, 'SD0002'),
            ('T50014', 'E9003', '2025-05-04 09:50:00', '2025-05-04 12:02:00', 'Realigned background extranet', 0, 'SD0005'),
            ('T50015', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:32:00', 'Profit-focused hybrid flexibility', 0, 'P002'),
            ('T50016', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:24:00', 'Multi-layered user-facing middleware', 0, 'SD0004'),
            ('T50017', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:04:00', 'Reverse-engineered intangible intranet', 0, 'SD0005'),
            ('T50018', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:51:00', 'Persistent coherent functionalities', 0, 'SD0007'),
            ('T50019', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:45:00', 'Synchronized zero tolerance migration', 0, 'SD0001'),
            ('T50020', 'E9005', '2025-05-04 09:50:00', '2025-05-04 11:55:00', 'Streamlined national toolset', 0, 'SD0001'),
            ('T50021', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:37:00', 'Cloned stable flexibility', 0, 'P002'),
            ('T50022', 'E015', '2025-05-04 09:50:00', '2025-05-04 11:02:00', 'Fully-configurable directional access', 0, 'SD0002'),
            ('T50023', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:09:00', 'Ameliorated system-worthy conglomeration', 0, 'SD0007'),
            ('T50024', 'E9003', '2025-05-04 09:50:00', '2025-05-04 10:33:00', 'Distributed multimedia strategy', 0, 'P001'),
            ('T50025', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:23:00', 'Future-proofed transitional archive', 0, 'P10001'),
            ('T50026', 'E9006', '2025-05-04 09:50:00', '2025-05-04 11:01:00', 'Multi-lateral interactive process improvement', 0, 'P001'),
            ('T50027', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:13:00', 'Optimized bifurcated challenge', 0, 'SD0007'),
            ('T50028', 'E004', '2025-05-04 09:50:00', '2025-05-04 12:02:00', 'Sharable asynchronous customer loyalty', 0, 'P001'),
            ('T50029', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:29:00', 'Team-oriented directional time-frame', 0, 'SD0001'),
            ('T50030', 'E004', '2025-05-04 09:50:00', '2025-05-04 10:48:00', 'Multi-layered actuating internet service-desk', 0, 'SD0002'),
            ('T50031', 'E004', '2025-05-04 09:50:00', '2025-05-04 10:04:00', 'Diverse content-based initiative', 0, 'SD0005'),
            ('T50032', 'E015', '2025-05-04 09:50:00', '2025-05-04 10:51:00', 'Balanced 24 hour productivity', 0, 'SD0001'),
            ('T50033', 'E015', '2025-05-04 09:50:00', '2025-05-04 10:45:00', 'Object-based web-enabled implementation', 0, 'SD0004'),
            ('T50034', 'E015', '2025-05-04 09:50:00', '2025-05-04 11:55:00', 'Synergized leading edge alliance', 0, 'P002'),
            ('T50035', 'E015', '2025-05-04 09:50:00', '2025-05-04 11:37:00', 'Re-engineered web-enabled productivity', 0, 'SD0007'),
            ('T50036', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:02:00', 'Profound disintermediate synergy', 0, 'SD0002'),
            ('T50037', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:09:00', 'Optional explicit intranet', 0, 'SD0005'),
            ('T50038', 'E9001', '2025-05-04 09:50:00', '2025-05-04 10:33:00', 'Robust analyzing customer loyalty', 0, 'SD0004'),
            ('T50039', 'E9001', '2025-05-04 09:50:00', '2025-05-04 10:23:00', 'Extended intangible interface', 0, 'P10007'),
            ('T50040', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:01:00', 'Reduced radical strategy', 0, 'P10001'),
            ('T50041', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:13:00', 'Decentralized stable flexibility', 0, 'SD0002'),
            ('T50042', 'E9003', '2025-05-04 09:50:00', '2025-05-04 12:02:00', 'Sharable client-server open architecture', 0, 'SD0005'),
            ('T50043', 'E9003', '2025-05-04 09:50:00', '2025-05-04 11:29:00', 'Managed full-range emulation', 0, 'P002'),
            ('T50044', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:48:00', 'Progressive object-oriented portal', 0, 'SD0004'),
            ('T50045', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:04:00', 'Centralized contextually-based portal', 0, 'SD0005'),
            ('T50046', 'E9004', '2025-05-04 09:50:00', '2025-05-04 11:19:00', 'Digitized optimizing parallelism', 0, 'SD0007'),
            ('T50047', 'E9004', '2025-05-04 09:50:00', '2025-05-04 11:45:00', 'Fundamental secondary customer loyalty', 0, 'SD0001'),
            ('T50048', 'E9006', '2025-05-04 09:50:00', '2025-05-04 11:49:00', 'Down-sized actuating superstructure', 0, 'SD0004'),
            ('T50049', 'E004', '2025-05-04 09:50:00', '2025-05-04 10:40:00', 'Organized motivating implementation', 0, 'P002'),
            ('T50050', 'E015', '2025-05-04 09:50:00', '2025-05-04 10:34:00', 'Decentralized leading definition', 0, 'SD0006'),
            ('T50051', 'E9001', '2025-05-04 09:50:00', '2025-05-04 11:13:00', 'Organized content-based focus group', 0, 'SD0007'),
            ('T50052', 'E9003', '2025-05-04 09:50:00', '2025-05-04 12:03:00', 'Networked 3rd generation time-frame', 0, 'P001'),
            ('T50053', 'E9004', '2025-05-04 09:50:00', '2025-05-04 10:57:00', 'Right-sized context-sensitive architecture', 0, 'P10001'),
            ('T50054', 'E9006', '2025-05-04 09:50:00', '2025-05-04 10:08:00', 'Object-based demand-driven challenge', 0, 'P001'),
            ('T50055', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:33:00', 'Proactive fault-tolerant capacity', 0, 'SD0007'),
            ('T50056', 'E004', '2025-05-04 09:50:00', '2025-05-04 11:51:00', 'Expanded value-added open architecture', 0, 'P001'),
            ('T9001', 'E001', '2025-05-01 09:00:00', '2025-05-01 10:00:00', 'Worked on PM project', 1, 'P_ece415c0'),
            ('T9002', 'E009', '2025-05-01 10:30:00', '2025-05-01 11:15:00', 'Drafted assets', 1, 'P_ece415c0'),
            ('T9003', 'E013', '2025-05-01 14:00:00', '2025-05-01 15:30:00', 'Reviewed updates', 1, 'P_ece415c0'),
            ('T900401', 'E9004', '2025-05-01 22:11:58', '2025-05-01 23:11:58', 'Morning task 1', 1, 'P10006'),
            ('T900402', 'E9004', '2025-05-02 00:11:58', '2025-05-02 01:11:58', 'Afternoon task 2', 1, 'P10006'),
            ('T900501', 'E9005', '2025-05-01 20:12:07', '2025-05-01 21:12:07', 'Morning task 1', 1, 'P10006'),
            ('T900502', 'E9005', '2025-05-02 00:12:07', '2025-05-02 01:12:07', 'Afternoon task 2', 1, 'P10006')
        ]

        for entry in time_entries:
            try:
                cursor.execute("""
                            INSERT INTO time (TIMEID, EMPID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY, PROJECTID)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, entry)
                print(f"  Added time entry for {entry[1]}, project {entry[6]}")
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
