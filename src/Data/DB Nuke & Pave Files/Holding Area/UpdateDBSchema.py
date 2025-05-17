# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.16.2025
# Description:      updates DB Schema present on 5.16.2025
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 05.16.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

# !/usr/bin/env python3
"""
Time Tracker Database Schema Update Script

This script modifies the time_tracker database by:
1. Adding an ASSIGNMENT_DATE column to the employee_projects table
2. Creating a new department_history table to track employee department changes

Prerequisites:
- MySQL Connector for Python: pip install mysql-connector-python
- Database credentials with ALTER and CREATE privileges on the time_tracker database
"""

import mysql.connector
from mysql.connector import Error
import getpass
import datetime


def connect_to_database():
    """Connect to the MySQL/MariaDB database using user input credentials."""
    try:
        # Get connection details from user
        host = input("Enter database host (default: localhost): ") or "localhost"
        port = input("Enter database port (default: 3306): ") or "3306"
        database = input("Enter database name (default: time_tracker): ") or "time_tracker"
        user = input("Enter database username: ")
        password = getpass.getpass("Enter database password: ")

        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL/MariaDB Server version {db_info}")
            return connection

    except Error as e:
        print(f"Error connecting to MySQL/MariaDB: {e}")
        return None


def add_assignment_date_to_employee_projects(connection):
    """Add ASSIGNMENT_DATE column to employee_projects table."""
    try:
        cursor = connection.cursor()

        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'time_tracker'
            AND TABLE_NAME = 'employee_projects'
            AND COLUMN_NAME = 'ASSIGNMENT_DATE'
        """)
        column_exists = cursor.fetchone()[0] > 0

        if column_exists:
            print("ASSIGNMENT_DATE column already exists in employee_projects table.")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE employee_projects
                ADD COLUMN ASSIGNMENT_DATE datetime DEFAULT CURRENT_TIMESTAMP
            """)

            # Populate existing rows with current date
            current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"""
                UPDATE employee_projects
                SET ASSIGNMENT_DATE = '{current_date}'
                WHERE ASSIGNMENT_DATE IS NULL
            """)

            connection.commit()
            print("Added ASSIGNMENT_DATE column to employee_projects table.")

        cursor.close()
        return True

    except Error as e:
        print(f"Error modifying employee_projects table: {e}")
        return False


def create_department_history_table(connection):
    """Create the department_history table."""
    try:
        cursor = connection.cursor()

        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'time_tracker'
            AND TABLE_NAME = 'department_history'
        """)
        table_exists = cursor.fetchone()[0] > 0

        if table_exists:
            print("department_history table already exists.")
        else:
            # Create the department_history table
            cursor.execute("""
                CREATE TABLE department_history (
                    HISTORY_ID varchar(36) NOT NULL,
                    EMPID varchar(20) NOT NULL,
                    DPTID varchar(20) NOT NULL,
                    CHANGE_DATE datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHANGED_BY varchar(20) NOT NULL,
                    NOTES text DEFAULT NULL,
                    PRIMARY KEY (HISTORY_ID),
                    KEY EMPID (EMPID),
                    KEY DPTID (DPTID),
                    KEY CHANGED_BY (CHANGED_BY),
                    CONSTRAINT fk_dpt_history_employee FOREIGN KEY (EMPID) REFERENCES employee_table (EMPID) ON UPDATE CASCADE,
                    CONSTRAINT fk_dpt_history_department FOREIGN KEY (DPTID) REFERENCES department (DPTID) ON UPDATE CASCADE,
                    CONSTRAINT fk_dpt_history_changer FOREIGN KEY (CHANGED_BY) REFERENCES employee_table (EMPID) ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
            """)

            # Create a trigger to automatically record department changes
            cursor.execute("""
                DELIMITER $$
                DROP TRIGGER IF EXISTS trg_department_history $$
                CREATE TRIGGER trg_department_history
                AFTER UPDATE ON employee_table
                FOR EACH ROW
                BEGIN
                    IF OLD.DPTID <> NEW.DPTID THEN
                        INSERT INTO department_history (
                            HISTORY_ID,
                            EMPID,
                            DPTID,
                            CHANGE_DATE,
                            CHANGED_BY,
                            NOTES
                        ) VALUES (
                            UUID(),
                            NEW.EMPID,
                            NEW.DPTID,
                            CURRENT_TIMESTAMP,
                            NEW.EMPID,  -- Default to self-change, should be overridden by application
                            CONCAT('Changed from ', OLD.DPTID, ' to ', NEW.DPTID)
                        );
                    END IF;
                END $$
                DELIMITER ;
            """)

            connection.commit()
            print("Created department_history table and associated trigger.")

        cursor.close()
        return True

    except Error as e:
        print(f"Error creating department_history table: {e}")
        return False


def handle_trigger_creation_separately(connection):
    """Handle trigger creation separately due to DELIMITER issues."""
    try:
        cursor = connection.cursor()

        # Check if trigger already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = 'time_tracker'
            AND TRIGGER_NAME = 'trg_department_history'
        """)
        trigger_exists = cursor.fetchone()[0] > 0

        if trigger_exists:
            print("trg_department_history trigger already exists.")
        else:
            # Drop trigger if it exists (just to be safe)
            cursor.execute("DROP TRIGGER IF EXISTS trg_department_history")

            # Create trigger without DELIMITER statements (they're not needed in programmatic execution)
            cursor.execute("""
                CREATE TRIGGER trg_department_history
                AFTER UPDATE ON employee_table
                FOR EACH ROW
                BEGIN
                    IF OLD.DPTID <> NEW.DPTID THEN
                        INSERT INTO department_history (
                            HISTORY_ID,
                            EMPID,
                            DPTID,
                            CHANGE_DATE,
                            CHANGED_BY,
                            NOTES
                        ) VALUES (
                            UUID(),
                            NEW.EMPID,
                            NEW.DPTID,
                            CURRENT_TIMESTAMP,
                            NEW.EMPID,
                            CONCAT('Changed from ', OLD.DPTID, ' to ', NEW.DPTID)
                        );
                    END IF;
                END
            """)

            connection.commit()
            print("Created trg_department_history trigger.")

        cursor.close()
        return True

    except Error as e:
        print(f"Error creating trigger: {e}")
        return False


def main():
    """Main function to coordinate database updates."""
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database. Exiting.")
        return

    try:
        # Start a transaction
        connection.start_transaction()

        # Implement changes
        success1 = add_assignment_date_to_employee_projects(connection)
        success2 = create_department_history_table(connection)

        # Handle trigger separately (due to DELIMITER issues)
        success3 = handle_trigger_creation_separately(connection)

        if success1 and success2 and success3:
            connection.commit()
            print("\nDatabase schema updated successfully!")
        else:
            connection.rollback()
            print("\nDatabase update failed. Rolling back changes.")

    except Error as e:
        connection.rollback()
        print(f"Error during database update: {e}")
        print("Changes rolled back.")

    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    print("Time Tracker Database Schema Update Script")
    print("=========================================")
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
