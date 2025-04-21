# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      creates tables as per the ERD
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


if __name__ == "__main__":
    print("=== Setting up the database tables… ===")
    setup_database()

    print("=== Database table setup complete! ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
