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

    # Create tables
    # Note: Order is important due to foreign key constraints

    # Create department table
    cursor.execute("""
    	CREATE TABLE IF NOT EXISTS department (
        	DPTID VARCHAR(20) PRIMARY KEY,
        	DPT_NAME VARCHAR(100) NOT NULL,
        	MANAGERID VARCHAR(20),
        	DPT_ACTIVE TINYINT(1) DEFAULT 1
    	)
    	""")

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
        	CONSTRAINT fk_employee_dept FOREIGN KEY (DPTID)
            	REFERENCES department(DPTID) ON UPDATE CASCADE,
        	CONSTRAINT fk_employee_manager FOREIGN KEY (MGR_EMPID)
            	REFERENCES employee_table(EMPID) ON UPDATE CASCADE
    	)
    	""")

    # Update department with foreign key to employee_table (now that employee_table exists)
    cursor.execute("""
    	ALTER TABLE department
    	ADD CONSTRAINT fk_dept_manager FOREIGN KEY (MANAGERID)
        	REFERENCES employee_table(EMPID) ON UPDATE CASCADE
    	""")

    # Create login_table
    cursor.execute("""
    	CREATE TABLE IF NOT EXISTS login_table (
        	LOGINID VARCHAR(50) PRIMARY KEY,
        	EMPID VARCHAR(20) NOT NULL,
        	PASSWORD VARCHAR(255) NOT NULL,
        	LAST_RESET DATETIME,
        	FORCE_RESET TINYINT(1) DEFAULT 0,
        	CONSTRAINT fk_login_employee FOREIGN KEY (EMPID)
            	REFERENCES employee_table(EMPID) ON UPDATE CASCADE
    	)
    	""")

    # Create role_names table
    cursor.execute("""
    	CREATE TABLE IF NOT EXISTS role_names (
        	ROLEID VARCHAR(20) PRIMARY KEY,
        	ROLE_NAME VARCHAR(100) UNIQUE NOT NULL
    	)
    	""")

    # Create employee_roles table
    cursor.execute("""
    	CREATE TABLE IF NOT EXISTS employee_roles (
        	EMP_ROLE_ID VARCHAR(20) PRIMARY KEY,
        	EMPID VARCHAR(20) NOT NULL,
        	ROLEID VARCHAR(20) NOT NULL,
        	CONSTRAINT fk_emprole_employee FOREIGN KEY (EMPID)
            	REFERENCES employee_table(EMPID) ON UPDATE CASCADE,
        	CONSTRAINT fk_emprole_role FOREIGN KEY (ROLEID)
            	REFERENCES role_names(ROLEID) ON UPDATE CASCADE,
        	CONSTRAINT uk_employee_role UNIQUE (EMPID, ROLEID)
    	)
    	""")

    # Create projects table
    cursor.execute("""
    	CREATE TABLE IF NOT EXISTS projects (
        	PROJECTID VARCHAR(20) PRIMARY KEY,
        	PROJECT_NAME VARCHAR(100) NOT NULL,
        	CREATED_BY VARCHAR(20) NOT NULL,
        	DATE_CREATED DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        	PRIOR_PROJECTID VARCHAR(20),
        	PROJECT_ACTIVE TINYINT(1) DEFAULT 1,
        	CONSTRAINT fk_project_creator FOREIGN KEY (CREATED_BY)
            	REFERENCES employee_table(EMPID) ON UPDATE CASCADE,
        	CONSTRAINT fk_project_parent FOREIGN KEY (PRIOR_PROJECTID)
            	REFERENCES projects(PROJECTID) ON UPDATE CASCADE
    	)
    	""")

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
        	CONSTRAINT fk_time_employee FOREIGN KEY (EMPID)
            	REFERENCES employee_table(EMPID) ON UPDATE CASCADE,
        	CONSTRAINT fk_time_project FOREIGN KEY (PROJECTID)
            	REFERENCES projects(PROJECTID) ON UPDATE CASCADE,
        	CONSTRAINT chk_time_valid CHECK (STOP_TIME > START_TIME)
    	)
    	""")

    # Create triggers for custom auto-increment fields

    # Trigger for employee_roles EMP_ROLE_ID
    cursor.execute("""
    	DROP TRIGGER IF EXISTS before_insert_emp_role;
    	""")

    cursor.execute("""
    	CREATE TRIGGER before_insert_emp_role
    	BEFORE INSERT ON employee_roles
    	FOR EACH ROW
    	BEGIN
        	DECLARE next_id INT;
        	SET next_id = (SELECT IFNULL(MAX(SUBSTRING(EMP_ROLE_ID, 2) + 0), 100) + 1
                    	FROM employee_roles);
        	SET NEW.EMP_ROLE_ID = CONCAT('E', next_id);
    	END;
    	""")

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
        	SET next_id = (SELECT IFNULL(MAX(SUBSTRING(TIMEID, 2) + 0), 1000) + 1
                    	FROM time);
        	SET NEW.TIMEID = CONCAT('T', next_id);
    	END;
    	""")

    # Commit changes
    conn.commit()

    print("Database setup completed successfully.")

    # Close cursor and connection
    cursor.close()
    conn.close()

    except mariadb.Error as error:
    print(f"Error setting up database: {error}")
    sys.exit(1)


def insert_sample_data():
    """
    Insert data from the provided file into the database.
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

    # Insert department data
    departments = [
        ('559', 'Legal', '1243', 1),
        ('207', 'Marketing', '2096', 1),
        ('443', 'Services', '2307', 1),
        ('277', 'Training', '3981', 1),
        ('604', 'Engineering', '4235', 1),
        ('813', 'Support', '4730', 1),
        ('221', 'Human Resources', '9616', 1),
        ('556', 'Research and Development', '9888', 1),
        ('343', 'Business Development', '9888', 1),
        ('895', 'SeniorManagement', '9888', 1),
        ('962', 'CEO', '9888', 1)
    ]

    cursor.executemany("""
    	INSERT INTO department (DPTID, DPT_NAME, MANAGERID, DPT_ACTIVE)
    	VALUES (?, ?, ?, ?)
    	""", departments)

    # Insert employee data
    employees = [
        ('1094', 'Lane', 'Beere', '559', 'lbeeree@rakuten.co.jp', '1243', 1),
        ('1243', 'Bobina', 'Windless', '559', 'bwindless8@census.gov', '9730', 1),
        ('1488', 'Elwin', 'Klaggeman', '207', 'eklaggemanc@free.fr', '2096', 1),
        ('1610', 'Archibald', 'Benck', '207', 'abenckj@amazonaws.com', '2096', 1),
        ('2088', 'Othello', 'Beesey', '207', 'obeeseym@plala.or.jp', '2096', 0),
        ('2096', 'Godfrey', 'Gaye', '207', 'ggaye7@mashable.com', '9730', 1),
        ('2307', 'Angelia', 'Favell', '443', 'afavella@hostgator.com', '9874', 1),
        ('2505', 'Aundrea', 'Abela', '443', 'aabelak@vimeo.com', '2307', 0),
        ('2764', 'Gilles', 'Shaylor', '443', 'gshaylorl@ezinearticles.com', '2307', 1),
        ('3838', 'Dannie', 'Montgomery', '277', 'dmontgomery5@craigslist.org', '3981', 1),
        ('3981', 'Gaby', 'Phizaclea', '277', 'gphizaclea9@prweb.com', '9874', 1),
        ('4235', 'Doti', 'Le Moucheux', '604', 'dlemoucheuxg@skype.com', '9730', 1),
        ('4446', 'Freeman', 'Jobbins', '604', 'fjobbinsd@xing.com', '4235', 1),
        ('4730', 'Devy', 'Johann', '813', 'djohann2@amazon.co.uk', '9730', 1),
        ('5018', 'Peg', 'Hawkes', '813', 'phawkes3@blinklist.com', '4730', 1),
        ('5576', 'Christiane', 'Pullar', '813', 'cpullarb@state.tx.us', '4730', 1),
        ('6539', 'Kenny', 'Scardifeild', '221', 'kscardifeildh@ameblo.jp', '9616', 0),
        ('7638', 'Charlena', 'Drysdall', '556', 'cdrysdalli@mapy.cz', '8334', 1),
        ('8012', 'Hersh', 'Clee', '343', 'hcleeo@google.it', '9874', 1),
        ('8334', 'Dane', 'Eynald', '556', 'deynaldf@ning.com', '9874', 0),
        ('9229', 'Husein', 'Barker', '221', 'hbarker4@tinypic.com', '9616', 1),
        ('9616', 'Chantalle', 'Godsil', '221', 'cgodsil1@dailymail.co.uk', '9874', 1),
        ('9730', 'Hamid', 'Klouz', '895', 'hklouz6@theatlantic.com', '9888', 1),
        ('9874', 'Hilliard', 'Beedell', '895', 'hbeedell0@wsj.com', '9888', 1),
        ('9888', 'Bert', 'Warlock', '962', 'bwarlockn@techcrunch.com', '9888', 1)
    ]

    cursor.executemany("""
    	INSERT INTO employee_table (EMPID, FIRST_NAME, LAST_NAME, DPTID, EMAIL_ADDRESS, MGR_EMPID, EMP_ACTIVE)
    	VALUES (?, ?, ?, ?, ?, ?, ?)
    	""", employees)

    # Insert login data
    logins = [
        ('9874', 'hbeedell0', '$2a$04$PEat6lDZaR/Q1eYO.AXpL.BWlTRdlMPZml5BrNVUx2we36QCObjnu', '2025-04-15', 0),
        ('9616', 'cgodsil1', '$2a$04$DIzPbsZzSw8owBPMUqMWK..xV0iO1.kOwafuZcRdPgafxQNMBUET6', '2025-04-15', 0),
        ('4730', 'djohann2', '$2a$04$Ud9a4TM4pbPu5MPWx3FpOuAaT380KGbGtYk4njlEz2uXU7nEwHgAy', '2025-04-15', 0),
        ('5018', 'phawkes3', '$2a$04$vqplo6hClQ6LWBzSfdhyyO3.0rUe28GwDEFpjQPLm.ZmAmOXANBpu', '2025-04-15', 0),
        ('9229', 'hbarker4', '$2a$04$RY1YpIx9SmGQf9PeInq33.Z/K3asToGtDQ4mQ7hbAZyNrmPFUe3Ze', '2025-04-15', 0),
        ('3838', 'dmontgomery5', '$2a$04$b2hP03I.mb3z.6Fj8qkFquHif8dj/Iui9Gy/spvByQpqfT/RyVrcu', '2025-04-15', 0),
        ('9730', 'hklouz6', '$2a$04$uOH1bfOJWunpuPAnRsssA.SQ21NESXFPdZRj6q.WD.elBrgF79ZjW', '2025-04-15', 0),
        ('2096', 'ggaye7', '$2a$04$.Dqmfnqt2N2.Xf.yF0s6KOotoYR2xHMktR0h4Z45Ck/JVfCPIQj5q', '2025-04-15', 1),
        ('1243', 'bwindless8', '$2a$04$tLIhoeahQhhzVKANKsicGOs1q9uULK0SvryVt/9MJTs7nbEGr.mYq', '2025-04-15', 0),
        ('3981', 'gphizaclea9', '$2a$04$Rtl9oFusiHF6rrHK/1kFSOTg9CFrxmk4iwdIFTX9qYYVyKzmDro.C', '2025-04-15', 0),
        ('2307', 'afavella', '$2a$04$5NktOozni47ggvCvboZTIeXiFkWnLZvObu5FV3Fun0s2nEXKlNHsO', '2025-04-15', 0),
        ('5576', 'cpullarb', '$2a$04$7aRhz1oH6G1Wr8TRqxiChu85L.6OgPebrZulTnmrfdm2ivHrEswGi', '2025-04-15', 0),
        ('1488', 'eklaggemanc', '$2a$04$LOWPe6S/OJoFkMkHCGdRZ.Jj4utYjZx/u1Y7RRVyTmz5RuMWmW8l2', '2025-04-15', 0),
        ('4446', 'fjobbinsd', '$2a$04$je81vH.1N0WLG5dXSOMFfOkZB/BxD9HdRNLP2sUBm0mZ/tMFR78XO', '2025-04-15', 0),
        ('1094', 'lbeeree', '$2a$04$EPyave8qMEQSh6fSymaCwOyBaJDFEMf2SLeTsY5GuFOVCn0nRZkde', '2025-04-15', 0),
        ('8334', 'deynaldf', '$2a$04$ok5hSE6ZucBFBWxxqGCL1Otdyzqe.PbqaH/Cond69H36p1aMWMiw2', '2025-04-15', 0),
        ('4235', 'dlemoucheuxg', '$2a$04$7YawGsTWo2LiU9wPsEU0eexaSzIPT/dJsEQDP7ZaPlaQdu6yf5VLS', '2025-04-15', 0),
        ('6539', 'kscardifeildh', '$2a$04$dbkCC5mX1vy3Bk3NnlpHXuuUQYdVMqqnCTHg5Gbl6kMRmmx42BI1q', '2025-04-15', 0),
        ('7638', 'cdrysdalli', '$2a$04$t0zOZp6sPZ7xEjZkhok0aOSiVOPYYTSR9IGPg2xy0Xn9bBXJL0huS', '2025-04-15', 0),
        ('1610', 'abenckj', '$2a$04$T5po9lnqKOI6zqWbRblVjOb8kP2kaihCYI1HVClmYE.e.PYEPwf0.', '2025-04-15', 0),
        ('2505', 'aabelak', '$2a$04$ncN3s3vkFN/OnaxUJb8xvOsauuqy.SUvz3FIF4sbuWQVwBFZqD7EC', '2025-04-15', 0),
        ('2764', 'gshaylorl', '$2a$04$WHt6a1R0lQyqaGhhCD05VeqP8QuvdsLWfa2GZTcjleJX237/9LrV6', '2025-04-15', 0),
        ('2088', 'obeeseym', '$2a$04$QLUTLYpmISVw9X5EjJE3aOX9sYIBeK00kYxbHLrfWsT./VYQ9RAaW', '2025-04-15', 0),
        ('9888', 'bwarlockn', '$2a$04$EwVr0AxhDGEcDVzwpn3fbeSiyLF0JtiFudaN3KKImqjHbhAA4G276', '2025-04-15', 0),
        ('8012', 'hcleeo', '$2a$04$9LtHUytu8HSfUoabmQwbaOnjSdylxQtYS7jP6R/T5280xOxWZ04Nu', '2025-04-15', 0)
    ]

    cursor.executemany("""
    	INSERT INTO login_table (LOGINID, EMPID, PASSWORD, LAST_RESET, FORCE_RESET)
    	VALUES (?, ?, ?, ?, ?)
    	""", logins)

    # Insert role_names data
    roles = [
        ('1', 'individual_user'),
        ('2', 'manager'),
        ('3', 'project_manager'),
        ('4', 'senior manager'),
        ('5', 'admin')
    ]

    cursor.executemany("""
    	INSERT INTO role_names (ROLEID, ROLE_NAME)
    	VALUES (?, ?)
    	""", roles)

    # Insert employee_roles data
    employee_roles = [
        (None, '1094', '1'),
        (None, '1243', '2'),
        (None, '1488', '1'),
        (None, '1610', '1'),
        (None, '2088', '1'),
        (None, '2096', '2'),
        (None, '2307', '2'),
        (None, '2505', '1'),
        (None, '2764', '1'),
        (None, '3838', '1'),
        (None, '3981', '2'),
        (None, '4235', '2'),
        (None, '4446', '1'),
        (None, '4730', '2'),
        (None, '5018', '1'),
        (None, '5576', '1'),
        (None, '6539', '1'),
        (None, '7638', '1'),
        (None, '8012', '3'),
        (None, '8334', '3'),
        (None, '9229', '1'),
        (None, '9616', '3'),
        (None, '9730', '4'),
        (None, '9874', '4'),
        (None, '9888', '5')
    ]

    cursor.executemany("""
    	INSERT INTO employee_roles (EMP_ROLE_ID, EMPID, ROLEID)
    	VALUES (?, ?, ?)
    	""", employee_roles)

    # Insert projects data
    projects = [
        ('10001', 'Andean goose', '1488', '2025-04-01', None, 1),
        ('10002', 'Antelope, sable', '4446', '2025-04-01', None, 1),
        ('10003', 'Argalis', '1488', '2025-04-01', None, 1),
        ('10004', 'Bare-faced go away bird', '1488', '2025-04-01', None, 1),
        ('10005', 'Blesbok', '3838', '2025-04-01', None, 0),
        ('10006', 'Boat-billed heron', '1610', '2025-04-01', None, 1),
        ('10007', 'Bottle-nose dolphin', '1610', '2025-04-01', None, 1),
        ('10008', 'Brazilian tapir', '9730', '2025-04-01', None, 0),
        ('10009', 'Dog, raccoon', '1094', '2025-04-01', None, 0),
        ('10010', 'Dolphin, striped', '2088', '2025-04-01', None, 1),
        ('10011', 'Flamingo, greater', '2088', '2025-04-01', None, 1),
        ('10012', 'Frilled dragon', '2088', '2025-04-01', None, 1),
        ('10013', 'Giant heron', '2088', '2025-04-01', None, 1),
        ('10014', 'Goose, andean', '9229', '2025-04-01', None, 0),
        ('10015', 'Goose, greylag', '9229', '2025-04-15', '10014', 1),
        ('10016', 'Greater adjutant stork', '3838', '2025-04-15', '10005', 1),
        ('10017', 'Javan gold-spotted mongoose', '9730', '2025-04-15', '10008', 1),
        ('10018', 'Legaan, Monitor (unidentified)', '8012', '2025-04-01', None, 1),
        ('10019', 'Lynx, african', '8012', '2025-04-01', None, 1),
        ('10020', 'Dog', '1094', '2025-04-15', '10009', 1),
        ('10021', 'Racoon', '1094', '2025-04-15', '10009', 1),
        ('10022', 'Squirrel, antelope ground', '8012', '2025-04-01', None, 0),
        ('10023', 'Steenbuck', '8012', '2025-04-01', None, 1),
        ('10024', 'Vulture, oriental white-backed', '8012', '2025-04-01', None, 1),
        ('10025', 'Squirrel', '4446', '2025-04-15', '10022', 1)
    ]

    cursor.executemany("""
    	INSERT INTO projects (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
    	VALUES (?, ?, ?, ?, ?, ?)
    	""", projects)

    # Insert time data with correct datetime format
    time_entries = [
        (None, '1243', '10001', '2024-04-05 09:50:00', '2024-04-05 11:59:00',
         'Integer ac leo. Pellentesque ultrices mattis odio. Donec vitae nisi.', 0),
        (None, '1488', '10003', '2024-12-09 16:47:00', '2024-12-09 18:01:00',
         'Vestibulum quam sapien, varius ut, blandit non, interdum in, ante. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Duis faucibus accumsan odio. Curabitur convallis.',
         1),
        (None, '1610', '10003', '2024-04-17 04:40:00', '2024-04-17 05:35:00',
         'Duis aliquam convallis nunc. Proin at turpis a pede posuere nonummy. Integer non velit.', 0),
        (None, '1488', '10005', '2025-04-14 04:01:00', '2025-04-14 05:17:00',
         'Suspendisse potenti. In eleifend quam a odio. In hac habitasse platea dictumst.', 1),
        (None, '2088', '10005', '2025-01-08 20:09:00', '2025-01-08 21:05:00',
         'Mauris enim leo, rhoncus sed, vestibulum sit amet, cursus id, turpis. Integer aliquet, massa id lobortis convallis, tortor risus dapibus augue, vel accumsan tellus nisi eu orci. Mauris lacinia sapien quis libero.',
         0),
        (None, '9730', '10005', '2025-03-11 09:51:00', '2025-03-11 11:03:00',
         'Sed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci. Nullam molestie nibh in lectus.',
         0),
        (None, '2088', '10006', '2025-01-24 03:11:00', '2025-01-24 04:21:00',
         'Cras non velit nec nisi vulputate nonummy. Maecenas tincidunt lacus at velit. Vivamus vel nulla eget eros elementum pellentesque.',
         0),
        (None, '2505', '10006', '2024-05-29 07:58:00', '2024-05-29 09:56:00',
         'Donec diam neque, vestibulum eget, vulputate ut, ultrices vel, augue. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec pharetra, magna vestibulum aliquet ultrices, erat tortor sollicitudin mi, sit amet lobortis sapien sapien non mi. Integer ac neque.',
         0),
        (None, '9874', '10006', '2025-01-16 14:46:00', '2025-01-16 15:41:00',
         'Phasellus in felis. Donec semper sapien a libero. Nam dui.', 0),
        (None, '5576', '10007', '2024-06-23 21:55:00', '2024-06-23 22:51:00',
         'Duis bibendum, felis sed interdum venenatis, turpis enim blandit mi, in porttitor pede justo eu massa. Donec dapibus. Duis at velit eu est congue elementum.',
         0),
        (None, '2096', '10009', '2024-03-10 19:27:00', '2024-03-10 20:39:00',
         'Sed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci. Nullam molestie nibh in lectus.',
         1),
        (None, '2505', '10009', '2024-06-22 08:15:00', '2024-06-22 09:11:00',
         'In sagittis dui vel nisl. Duis ac nibh. Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus.',
         1),
        (None, '2307', '10010', '2025-01-23 01:01:00', '2025-01-23 02:03:00',
         'Duis aliquam convallis nunc. Proin at turpis a pede posuere nonummy. Integer non velit.', 1),
        (None, '4446', '10010', '2025-03-07 11:42:00', '2025-03-07 13:36:00',
         'Vestibulum ac est lacinia nisi venenatis tristique. Fusce congue, diam id ornare imperdiet, sapien urna pretium nisl, ut volutpat sapien arcu sed augue. Aliquam erat volutpat.',
         0),
        (None, '7638', '10011', '2025-02-13 04:19:00', '2025-02-13 05:57:00',
         'In congue. Etiam justo. Etiam pretium iaculis justo.', 1),
        (None, '5018', '10012', '2024-06-15 19:12:00', '2024-06-15 20:44:00',
         'Maecenas tristique, est et tempus semper, est quam pharetra magna, ac consequat metus sapien ut nunc. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Mauris viverra diam vitae quam. Suspendisse potenti.',
         0),
        (None, '8012', '10014', '2025-04-06 09:30:00', '2025-04-06 11:09:00',
         'Pellentesque at nulla. Suspendisse potenti. Cras in purus eu magna vulputate luctus.', 1),
        (None, '1094', '10015', '2024-08-07 08:32:00', '2024-08-07 10:50:00',
         'Nulla ut erat id mauris vulputate elementum. Nullam varius. Nulla facilisi.', 0),
        (None, '1094', '10016', '2025-02-04 08:28:00', '2025-02-04 10:34:00',
         'Praesent id massa id nisl venenatis lacinia. Aenean sit amet justo. Morbi ut odio.', 0),
        (None, '1610', '10017', '2025-03-31 13:09:00', '2025-03-31 14:09:00',
         'Quisque porta volutpat erat. Quisque erat eros, viverra eget, congue eget, semper rutrum, nulla. Nunc purus.',
         0),
        (None, '8334', '10018', '2025-02-05 02:50:00', '2025-02-05 05:12:00',
         'Vestibulum quam sapien, varius ut, blandit non, interdum in, ante. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Duis faucibus accumsan odio. Curabitur convallis.',
         0),
        (None, '1610', '10020', '2024-10-09 13:38:00', '2024-10-09 15:09:00',
         'Fusce posuere felis sed lacus. Morbi sem mauris, laoreet ut, rhoncus aliquet, pulvinar sed, nisl. Nunc rhoncus dui vel sem.',
         1),
        (None, '2505', '10021', '2024-03-26 03:58:00', '2024-03-26 06:12:00',
         'In quis justo. Maecenas rhoncus aliquam lacus. Morbi quis tortor id nulla ultrices aliquet.', 0),
        (None, '9229', '10024', '2024-10-30 11:00:00', '2024-10-30 11:45:00',
         'Maecenas tristique, est et tempus semper, est quam pharetra magna, ac consequat metus sapien ut nunc. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Mauris viverra diam vitae quam. Suspendisse potenti.',
         0),
        (None, '2505', '10025', '2025-04-07 03:24:00', '2025-04-07 05:22:00',
         'Donec diam neque, vestibulum eget, vulputate ut, ultrices vel, augue. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec pharetra, magna vestibulum aliquet ultrices, erat tortor sollicitudin mi, sit amet lobortis sapien sapien non mi. Integer ac neque.',
         0)
    ]

    cursor.executemany("""
    	INSERT INTO time (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
    	VALUES (?, ?, ?, ?, ?, ?, ?)
    	""", time_entries)

    # Commit changes
    conn.commit()

    print("Sample data inserted successfully.")

    # Close cursor and connection
    cursor.close()
    conn.close()

    except mariadb.Error as error:
    print(f"Error inserting sample data: {error}")
    sys.exit(1)


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
