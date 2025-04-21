# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Discovers existing tables in DB, drops all tables, creates tables, populates with data
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.20.2025: Initial setup of tests
#                   - 04.21.2025: Updated ROLE_NAME in role_names for ROLEID 4 & 5:
#                           • senior_manager --> vp_csuite
#                           • admin --> CEO
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

import os
import sys
import mariadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def drop_all_tables():
    """
    Check for existing tables in the database and drop them all.
    """
    try:
    # Connect to MariaDB
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )

        # Create a cursor
        cursor = conn.cursor()

        # First, disable foreign key checks to avoid constraint issues when dropping tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Get list of all tables in the database
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            """, (os.getenv("DB_NAME"),))

        tables = cursor.fetchall()

        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

        if tables:
            print("\nDropping tables...")

            # First drop any triggers
            cursor.execute("""
                SELECT TRIGGER_NAME
                FROM information_schema.TRIGGERS
                WHERE TRIGGER_SCHEMA = %s
                """, (os.getenv("DB_NAME"),))

            triggers = cursor.fetchall()

            for trigger in triggers:
                print(f"Dropping trigger: {trigger[0]}")
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger[0]}")

            # Now drop all tables
            for table in tables:
                table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            print("\nAll tables have been dropped successfully.")
        else:
            print("No tables found in the database.")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Commit changes
        conn.commit()

        # Close cursor and connection
        cursor.close()
        conn.close()

    except mariadb.Error as error:
        print(f"Error dropping tables: {error}")
        sys.exit(1)


def setup_database():
    """
    Create database schema for the employee project management system.
    """
    try:
        # Connect to MariaDB
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )

        # Create a cursor
        cursor = conn.cursor()

        # Add proper error handling for each step
        try:
            # Create department table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS department (
                    DPTID VARCHAR(20) PRIMARY KEY,
                    DPT_NAME VARCHAR(100) NOT NULL,
                    MANAGERID VARCHAR(20),
                    DPT_ACTIVE TINYINT(1) DEFAULT 1,
                    INDEX (MANAGERID)
                )
                """)
            print("Department table created successfully.")

            # Create employee_table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_table (
                    EMPID VARCHAR(20) PRIMARY KEY,
                    FIRST_NAME VARCHAR(50) NOT NULL,
                    LAST_NAME VARCHAR(50) NOT NULL,
                    DPTID VARCHAR(20) NOT NULL,
                    EMAIL_ADDRESS VARCHAR(100) UNIQUE NOT NULL,
                    MGR_EMPID VARCHAR(20),
                    EMP_ACTIVE TINYINT(1) DEFAULT 1,
                    EMP_ROLE VARCHAR(20) NOT NULL,
                    INDEX (DPTID),
                    INDEX (MGR_EMPID),
                    CONSTRAINT fk_employee_dept FOREIGN KEY (DPTID)
                        REFERENCES department(DPTID) ON UPDATE CASCADE,
                    CONSTRAINT fk_employee_manager FOREIGN KEY (MGR_EMPID)
                        REFERENCES employee_table(EMPID) ON UPDATE CASCADE
                )
                """)
            print("Employee table created successfully.")

            # Update department with foreign key to employee_table (now that employee_table exists)
            cursor.execute("""
                ALTER TABLE department
                ADD CONSTRAINT fk_dept_manager FOREIGN KEY (MANAGERID)
                    REFERENCES employee_table(EMPID) ON UPDATE CASCADE
                """)
            print("Department table altered successfully.")

            # Create login_table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_table (
                    LOGINID VARCHAR(50) PRIMARY KEY,
                    EMPID VARCHAR(20) NOT NULL,
                    PASSWORD VARCHAR(255) NOT NULL,
                    LAST_RESET DATETIME,
                    FORCE_RESET TINYINT(1) DEFAULT 0,
                    INDEX (EMPID),
                    CONSTRAINT fk_login_employee FOREIGN KEY (EMPID)
                        REFERENCES employee_table(EMPID) ON UPDATE CASCADE
                )
                """)
            print("Login table created successfully.")

            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    PROJECTID VARCHAR(20) PRIMARY KEY,
                    PROJECT_NAME VARCHAR(100) NOT NULL,
                    CREATED_BY VARCHAR(20) NOT NULL,
                    DATE_CREATED DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIOR_PROJECTID VARCHAR(20),
                    PROJECT_ACTIVE TINYINT(1) DEFAULT 1,
                    INDEX (CREATED_BY),
                    INDEX (PRIOR_PROJECTID),
                    CONSTRAINT fk_project_creator FOREIGN KEY (CREATED_BY)
                        REFERENCES employee_table(EMPID) ON UPDATE CASCADE,
                    CONSTRAINT fk_project_parent FOREIGN KEY (PRIOR_PROJECTID)
                        REFERENCES projects(PROJECTID) ON UPDATE CASCADE
                )
                """)
            print("Projects table created successfully.")

            # Create time table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time (
                    TIMEID VARCHAR(20) PRIMARY KEY,
                    EMPID VARCHAR(20) NOT NULL,
                    PROJECTID VARCHAR(20) NOT NULL,
                    START_TIME DATETIME NOT NULL,
                    STOP_TIME DATETIME NOT NULL,
                    NOTES TEXT,
                    MANUAL_ENTRY TINYINT(1) DEFAULT 0,
                    TOTAL_MINUTES INT GENERATED ALWAYS AS
                        (TIMESTAMPDIFF(MINUTE, START_TIME, STOP_TIME)) STORED,
                    INDEX (EMPID),
                    INDEX (PROJECTID),
                    INDEX (START_TIME),
                    INDEX (STOP_TIME),
                    CONSTRAINT fk_time_employee FOREIGN KEY (EMPID)
                        REFERENCES employee_table(EMPID) ON UPDATE CASCADE,
                    CONSTRAINT fk_time_project FOREIGN KEY (PROJECTID)
                        REFERENCES projects(PROJECTID) ON UPDATE CASCADE,
                    CONSTRAINT chk_time_valid CHECK (STOP_TIME > START_TIME)
                )
                """)
            print("Time table created successfully.")

            # Create triggers for custom auto-increment fields

            # Trigger for EMPID
            cursor.execute("""
                DROP TRIGGER IF EXISTS before_insert_employee;
                """)
            cursor.execute("""
                CREATE TRIGGER before_insert_employee
                BEFORE INSERT ON employee_table
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.EMPID IS NULL OR NEW.EMPID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(EMPID, 2) + 0), 1000) + 1
                                    FROM employee_table);
                        SET NEW.EMPID = CONCAT('E', next_id);
                    END IF;
                END;
                """)
            print("Employee ID trigger created successfully.")

            # Trigger for DPTID
            cursor.execute("""
                DROP TRIGGER IF EXISTS before_insert_department;
                """)
            cursor.execute("""
                CREATE TRIGGER before_insert_department
                BEFORE INSERT ON department
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.DPTID IS NULL OR NEW.DPTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(DPTID, 2) + 0), 1000) + 1
                                    FROM department);
                        SET NEW.DPTID = CONCAT('D', next_id);
                    END IF;
                END;
                """)
            print("Department ID trigger created successfully.")

            # Trigger for PROJECTID
            cursor.execute("""
                DROP TRIGGER IF EXISTS before_insert_project;
                """)
            cursor.execute("""
                CREATE TRIGGER before_insert_project
                BEFORE INSERT ON projects
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.PROJECTID IS NULL OR NEW.PROJECTID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(PROJECTID, 2) + 0), 10000) + 1
                                    FROM projects);
                        SET NEW.PROJECTID = CONCAT('P', next_id);
                    END IF;
                END;
                """)
            print("Project ID trigger created successfully.")

            # Trigger for time TIMEID
            cursor.execute("""
                DROP TRIGGER IF EXISTS before_insert_time;
                """)
            cursor.execute("""
                CREATE TRIGGER before_insert_time
                BEFORE INSERT ON time
                FOR EACH ROW
                BEGIN
                    DECLARE next_id INT;
                    IF NEW.TIMEID IS NULL OR NEW.TIMEID = '' THEN
                        SET next_id = (SELECT IFNULL(MAX(SUBSTRING(TIMEID, 2) + 0), 1000) + 1
                                    FROM time);
                        SET NEW.TIMEID = CONCAT('T', next_id);
                    END IF;
                END;
                """)
            print("Time ID trigger created successfully.")

            # Add a function to safely load initial data with circular foreign key references
            def load_initial_data():
                """
                Load initial data for the database, disabling foreign key checks temporarily.
                """
                try:
                    # Disable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

                    # Here you would insert your initial data
                    # For example:
                    # cursor.execute("INSERT INTO department (DPTID, DPT_NAME, DPT_ACTIVE) VALUES ('D1001', 'Administration', 1);")
                    # cursor.execute("INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, EMP_ACTIVE, EMP_ROLE) VALUES ('E1001', 'Admin', 'User', 'D1001', 'admin@example.com', 1, 'ADMIN');")
                    # cursor.execute("UPDATE department SET MANAGERID = 'E1001' WHERE DPTID = 'D1001';")

                    # Re-enable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
                    print("Initial data loaded successfully.")

                except mariadb.Error as error:
                    print(f"Error loading initial data: {error}")
                    raise

            # Uncomment this line to load initial data:
            # load_initial_data()

            # Commit changes
            conn.commit()
            print("Database setup completed successfully.")

        except mariadb.Error as error:
            # Rollback in case of any error
            conn.rollback()
            print(f"Error during setup: {error}")
            raise

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    except mariadb.Error as error:
        print(f"Error connecting to database: {error}")
        sys.exit(1)


import os
import sys
import mariadb
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


def insert_sample_data():
    """
    Insert sample data into the database tables.
    """
    try:
        # Connect to MariaDB
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )

        # Create a cursor
        cursor = conn.cursor()

        try:
            # Disable foreign key checks temporarily to handle circular references
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

            # Insert Department data
            print("Inserting department data...")
            departments = [
                ('D1001', 'Marketing', 'E1006', 1),
                ('D1002', 'Training', 'E1011', 1),
                ('D1003', 'Business Development', 'E1025', 1),
                ('D1004', 'Services', 'E1007', 1),
                ('D1005', 'Research and Development', 'E1025', 1),
                ('D1006', 'Legal', 'E1002', 1),
                ('D1007', 'Engineering', 'E1012', 1),
                ('D1008', 'Support', 'E1014', 1)
            ]

            cursor.execute("DELETE FROM department;")  # Clear existing data
            for dept in departments:
                cursor.execute("""
                    INSERT INTO department (DPTID, DPT_NAME, MANAGERID, DPT_ACTIVE)
                    VALUES (?, ?, ?, ?);
                """, dept)

            # Insert Employee data
            print("Inserting employee data...")
            employees = [
                ('E1001', 'Lane', 'Beere', 'D1006', 'lbeeree@rakuten.co.jp', 'E1002', 1, 'individual'),
                ('E1002', 'Bobina', 'Windless', 'D1006', 'bwindless8@census.gov', None, 1, 'manager'),
                ('E1003', 'Elwin', 'Klaggeman', 'D1001', 'eklaggemanc@furl.net', 'E1006', 1, 'individual'),
                ('E1004', 'Archibald', 'Benck', 'D1001', 'abenckj@amazonaws.com', 'E1006', 1, 'individual'),
                ('E1005', 'Othello', 'Beesey', 'D1001', 'obeeseym@plala.or.jp', 'E1006', 0, 'individual'),
                ('E1006', 'Godfrey', 'Gaye', 'D1001', 'ggaye7@mashable.com', None, 1, 'manager'),
                ('E1007', 'Angelia', 'Favell', 'D1004', 'afavella@hostgator.com', None, 1, 'manager'),
                ('E1008', 'Aundrea', 'Abela', 'D1004', 'aabelak@vimeo.com', 'E1007', 0, 'individual'),
                ('E1009', 'Gilles', 'Shaylor', 'D1004', 'gshaylort@ezinearticles.com', 'E1007', 1, 'individual'),
                ('E1010', 'Danny', 'Montgomery', 'D1002', 'dmontgomery6@stumbleupon.com', 'E1011', 1, 'individual'),
                ('E1011', 'Gaby', 'Phizaclea', 'D1002', 'gphizaclea9@prweb.com', None, 1, 'manager'),
                ('E1012', 'Doti', 'Le Moucheux', 'D1007', 'dlemoucheuxg@skype.com', None, 1, 'manager'),
                ('E1013', 'Freeman', 'Jobbins', 'D1002', 'fjobbinsd@icio.us', 'E1012', 1, 'manager'),
                ('E1014', 'Devy', 'Johann', 'D1008', 'djohann2@amazon.co.uk', None, 1, 'manager'),
                ('E1015', 'Peg', 'Hawkes', 'D1008', 'phawkes3@blinklist.com', 'E1014', 1, 'individual'),
                ('E1016', 'Christiane', 'Pullar', 'D1008', 'cpullarb@state.tx.us', 'E1014', 1, 'individual'),
                ('E1017', 'Kenny', 'Scardifieldh', 'D1002', 'kscardifeldh@amazon.co.jp', 'E1011', 0, 'individual'),
                ('E1018', 'Charlena', 'Drysdall', 'D1005', 'cdrysdalli@mapy.cz', 'E1025', 1, 'project_manager'),
                ('E1019', 'Hersh', 'Cleeo', 'D1003', 'hcleeo@google.it', 'E1025', 1, 'individual'),
                ('E1020', 'Dane', 'Eynald', 'D1005', 'deynaldf@ning.com', 'E1025', 0, 'project_manager'),
                ('E1021', 'Husein', 'Barker', 'D1003', 'hbarker4@tinypic.com', 'E1025', 1, 'individual'),
                ('E1022', 'Chantalle', 'Godsil', 'D1003', 'cgodsil1@dailymail.co.uk', 'E1025', 1, 'individual'),
                ('E1023', 'Hamid', 'Klouz', 'D1007', 'hklouz6@theatlantic.com', 'E1012', 1, 'individual'),
                ('E1024', 'Hilliard', 'Beedell', 'D1006', 'hbeedell0@wsj.com', 'E1002', 1, 'individual'),
                ('E1025', 'Bert', 'Warlock', 'D1006', 'bwarlockn@techcrunch.com', None, 1, 'manager')
            ]

            cursor.execute("DELETE FROM employee_table;")  # Clear existing data
            for emp in employees:
                cursor.execute("""
                    INSERT INTO employee_table 
                    (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE, EMP_ROLE)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, emp)

            # Insert Login data
            print("Inserting login data...")
            logins = [
                ('E1001', 'lbeeree', '$2a$04$EPyave8qMEQSh6fSymaCwOyBaJDFEM2SLeTsY5GuFOVCn0nRZkde', '4/15/2025', 0),
                ('E1002', 'bwindless8', '$2a$04$tLIhoeshQhhzVKANKsfcGOs1q9uULk0SwyvVo9MJTs7nbEGr.mYq', '4/15/2025', 0),
                ('E1003', 'eklaggemanc', '$2a$04$LOWPes5QJofFKMrHC6dRZJidkrv723T78RVyTmz5RuMWmW8I2', '4/15/2025', 0),
                ('E1004', 'abenckj', '$2a$04$T5po9lnqKOI6zqWbRbIVjOb8kP2kaihCYI1HVCImYE.e.PYEPwR0', '4/15/2025', 0),
                ('E1005', 'obeeseym', '$2a$04$QUTLYpmlSVw9X5EjE3aQ9sYiBeK00kYxbHLrfWsT./VYQ9RAaW', '4/15/2025', 0),
                ('E1006', 'ggaye7', '$2a$04$.Dqmfnqt2N2.XtyPo6KOotoYR2xHMkR0h4Z45CkJ/Vt6PIQj5q', '4/15/2025', 1),
                ('E1007', 'afavella', '$2a$04$5NktOozn4fywGv0oZTleXUfQ15dRGizrJnp52n5XKlNHsO', '4/15/2025', 0),
                ('E1008', 'aabelak', '$2a$04$ncN3s3vkFN/OnaxUJb8xvQsauuqy.SJvz3fF4sbuWQVwBFZqD7EC', '4/15/2025', 0),
                ('E1009', 'gshaylort', '$2a$04$WH6a1R0IQyqaEnhCD05veq9QuvdsLWfsZ6ZTcjleJX2379Lrv6', '4/15/2025', 0),
                ('E1010', 'dmontgomery6', '$2a$04$b2hPQJLph3x.6Fi8oKgufiBd/IuKhXtDAgfwDvOpofT/RwYcu', '4/15/2025', 0),
                ('E1011', 'gphizaclea9', '$2a$04$Rt9oFusIHF6rrHK/1kFSOTg9Cvnmk4iwtIFTX9qYWyKzmDro.C', '4/15/2025', 0),
                ('E1012', 'dlemoucheuxg', '$2a$04$7YawGsTWc2LiI0wPsE0UeaoeSaSlPTJ7JsEQDP7ZaPlaQdu6y5VLS', '4/15/2025',
                 0),
                ('E1013', 'fjobbinsd', '$2a$04$je81yH.1N0WL65dX9OMFfOkzB/Bxb9HdRNLP2sUBm0mZMFR78XO', '4/15/2025', 0),
                ('E1014', 'djohann2', '$2a$04$Ud9a4TM4phSu5MPWxFgCuAaT380K6bGYkqnlEz2cXU7nEwHcy', '4/15/2025', 0),
                ('E1015', 'phawkes3', '$2a$04$vqplo6hCIQ6LWBzSfdnyyO3.0rUe286OFEpjQPLm.ZnAmOXANBpu', '4/15/2025', 0),
                ('E1016', 'cpullarb', '$2a$04$7aRhzIoH6G1Wt8TfqxiChu85LOgPz6bZuITmmfdm2fvBrFswGi', '4/15/2025', 0),
                (
                'E1017', 'kscardifeldh', '$2a$04$dhkCCbmcX1w28k3NuInHXuuUQvt.6voHTHa5Gbl6kMRnmbw42BLg', '4/15/2025', 0),
                ('E1018', 'cdrysdalli', '$2a$04$i0zOZp6sPZ7xEjZkhok0aOSiVOPYfT89fGPg2xgXxn9bBXJt0huS', '4/15/2025', 0),
                ('E1019', 'hcleeo', '$2a$04$9LHUynLcH$fUoabmQwbaOnjSdykQtYS7jP6R/T5280xOxWZ04Nu', '4/15/2025', 0),
                ('E1020', 'deynaldf', '$2a$04$ok5hS66ZucBFBWxqGCL1Otdyzqe.PbqaH/Cond69H36p1aWWMrw2', '4/15/2025', 0),
                ('E1021', 'hbarker4', '$2a$04$hYY1yb3Gxph28ROPaInq33.Z/K3asTqG4h7ppDhAZyNrmPFlc3Ze', '4/15/2025', 0),
                ('E1022', 'cgodsil1', '$2a$04$DiZPbsZz5w8owBPMUqMWK..xV0IO1.kOwafuZcRdPgafxQNMBUET6', '4/15/2025', 0),
                ('E1023', 'hklouz6', '$2a$04$uOH1bfOJWunpuPAnRsssA.SQ21NESXFPdZRj6q.WD.elbRgF75ZjW', '4/15/2025', 0),
                ('E1024', 'hbeedell0', '$2a$04$PEa6t0ZaR/Q1eVO.AXpL8WiTRdH4PZmQBrNVUJzwe36QCQDjnu', '4/15/2025', 0),
                ('E1025', 'bwarlockn', '$2a$04$EvWr0AxhDGEcDVzvpn3fbe$jvLF0hFudaN3KKtmqfHbhAA4G276', '4/15/2025', 0)
            ]

            cursor.execute("DELETE FROM login_table;")  # Clear existing data
            for login in logins:
                cursor.execute("""
                    INSERT INTO login_table (LOGINID, EMPID, PASSWORD, LAST_RESET, FORCE_RESET)
                    VALUES (?, ?, ?, STR_TO_DATE(?, '%m/%d/%Y'), ?);
                """, login)

            # Insert Projects data
            print("Inserting projects data...")
            projects = [
                ('P10001', 'Andean goose', 'E1003', '4/1/2025', None, 1),
                ('P10002', 'Antelope, sable', 'E1013', '4/1/2025', None, 1),
                ('P10003', 'Argalis', 'E1003', '4/1/2025', None, 1),
                ('P10004', 'Bare-faced go away bird', 'E1003', '4/1/2025', None, 1),
                ('P10005', 'Blesbok', 'E1010', '4/1/2025', None, 0),
                ('P10006', 'Boat-billed heron', 'E1004', '4/1/2025', None, 1),
                ('P10007', 'Bottle-nose dolphin', 'E1004', '4/1/2025', None, 1),
                ('P10008', 'Brazilian tapir', 'E1023', '4/1/2025', None, 0),
                ('P10009', 'Dog, raccoon', 'E1001', '4/1/2025', None, 0),
                ('P10010', 'Dolphin, striped', 'E1005', '4/1/2025', None, 1),
                ('P10011', 'Flamingo, greater', 'E1005', '4/1/2025', None, 1),
                ('P10012', 'Frilled dragon', 'E1005', '4/1/2025', None, 1),
                ('P10013', 'Giant heron', 'E1005', '4/1/2025', None, 1),
                ('P10014', 'Goose, andean', 'E1021', '4/1/2025', None, 0),
                ('P10015', 'Goose, greylag', 'E1021', '4/15/2025', 'P10014', 1),
                ('P10016', 'Greater adjutant stork', 'E1010', '4/15/2025', 'P10005', 1),
                ('P10017', 'Javan gold-spotted mongoose', 'E1023', '4/15/2025', 'P10008', 1),
                ('P10018', 'Legaan, Monitor (unidentified)', 'E1019', '4/1/2025', None, 1),
                ('P10019', 'Lynx, african', 'E1019', '4/1/2025', None, 1),
                ('P10020', 'Dog', 'E1001', '4/15/2025', 'P10009', 1),
                ('P10021', 'Raccoon', 'E1001', '4/15/2025', 'P10009', 1),
                ('P10022', 'Squirrel, antelope ground', 'E1019', '4/1/2025', None, 0),
                ('P10023', 'Steenbuck', 'E1019', '4/1/2025', None, 1),
                ('P10024', 'Vulture, oriental white-backed', 'E1019', '4/1/2025', None, 1),
                ('P10025', 'Squirrel', 'E1013', '4/15/2025', 'P10022', 1)
            ]

            cursor.execute("DELETE FROM projects;")  # Clear existing data
            for project in projects:
                cursor.execute("""
                    INSERT INTO projects 
                    (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
                    VALUES (?, ?, ?, STR_TO_DATE(?, '%m/%d/%Y'), ?, ?);
                """, project)

            # Insert Time data
            print("Inserting time data...")
            times = [
                ('T1243', 'E1001', 'P10001', '4/5/2024 9:50', '4/5/2024 11:59', 'Integer ac', 0),
                ('T1610', 'E1003', 'P10003', '12/9/2024 16:47', '12/9/2024 18:01', 'Vestibulu', 0),
                ('T1488', 'E1005', 'P10005', '4/14/2025 4:01', '4/14/2025 5:17', 'Suspendis', 1),
                ('T2088', 'E1005', 'P10005', '1/8/2025 20:09', '1/8/2025 21:05', 'Mauris en', 0),
                ('T9730', 'E1005', 'P10005', '3/11/2025 9:51', '3/11/2025 11:03', 'Sed sagit', 0),
                ('T2307', 'E1006', 'P10006', '1/24/2025 3:11', '1/24/2025 4:21', 'Cras non ', 0),
                ('T2505', 'E1006', 'P10006', '5/29/2024 7:58', '5/29/2024 9:56', 'Donec di', 0),
                ('T9874', 'E1006', 'P10006', '1/16/2025 14:46', '1/16/2025 15:41', 'Phasellus', 0),
                ('T5576', 'E1007', 'P10007', '6/23/2024 22:07', '6/23/2024 22:51', 'Duis bibe', 1),
                ('T2096', 'E1007', 'P10009', '3/10/2024 19:27', '3/10/2024 20:39', 'Sed sagit', 1),
                ('T4446', 'E1007', 'P10009', '6/22/2024 8:15', '6/22/2024 9:11', 'In sagitt', 1),
                ('T7638', 'E1010', 'P10010', '1/23/2025 1:01', '1/23/2025 2:03', 'Duis aliqu', 0),
                ('T5018', 'E1011', 'P10011', '2/13/2025 4:19', '2/13/2025 5:57', 'In congue', 1),
                ('T8012', 'E1012', 'P10012', '6/15/2024 19:12', '6/15/2024 20:44', 'Maecenas ', 0),
                ('T1094', 'E1014', 'P10014', '4/6/2025 9:30', '4/6/2025 11:09', 'Pellentes', 1),
                ('T6718', 'E1015', 'P10015', '8/7/2024 8:32', '8/7/2024 10:50', 'Nulla ut ', 0),
                ('T8334', 'E1016', 'P10016', '2/4/2025 8:28', '2/4/2025 10:34', 'Praesent ', 0),
                ('T9229', 'E1017', 'P10017', '3/31/2025 13:09', '3/31/2025 14:09', 'Quisque a', 0),
                ('T1610', 'E1018', 'P10018', '2/5/2025 5:09', '2/5/2025 5:12', 'Vestibulu', 0),
                ('T2505', 'E1019', 'P10020', '10/9/2024 13:38', '10/9/2024 15:09', 'Fusce po', 1),
                ('T9229', 'E1021', 'P10021', '3/26/2024 3:58', '3/26/2024 6:12', 'In quis ju', 0),
                ('T1094', 'E1024', 'P10024', '10/30/2024 11:36', '10/30/2024 11:45', 'Maecenas ', 0),
                ('T2505', 'E1025', 'P10025', '4/7/2025 3:24', '4/7/2025 5:22', 'Donec di', 0)
            ]

            cursor.execute("DELETE FROM time;")  # Clear existing data
            for time_entry in times:
                # Parse datetime strings
                start_time = datetime.strptime(time_entry[3], '%m/%d/%Y %H:%M')
                stop_time = datetime.strptime(time_entry[4], '%m/%d/%Y %H:%M')

                cursor.execute("""
                    INSERT INTO time 
                    (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (time_entry[0], time_entry[1], time_entry[2], start_time, stop_time, time_entry[5], time_entry[6]))

            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

            # Commit changes
            conn.commit()
            print("Sample data insertion completed successfully.")

        except mariadb.Error as error:
            # Rollback in case of any error
            conn.rollback()
            print(f"Error during data insertion: {error}")
            raise

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    except mariadb.Error as error:
        print(f"Error connecting to database: {error}")
        sys.exit(1)


if __name__ == "__main__":
    print("=== Inserting sample data into the database tables… ===")
    insert_sample_data()
    print("=== Sample data insertion complete! ===")


if __name__ == "__main__":
    print("=== Checking for existing tables and dropping them… ===")
    drop_all_tables()

    print("=== Database is now empty and ready for setup. ===")

    print("=== Setting up the database tables… ===")
    setup_database()

    print("=== Database table setup complete! ===")

    print("=== Inserting Dummy Data… ===")
    insert_sample_data()

    print("=== Dummy Data setup complete! ===")


# **********************************************************************************************************************
# **********************************************************************************************************************
