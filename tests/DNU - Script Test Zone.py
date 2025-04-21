#!/usr/bin/env python3
"""
Script to add ROLEID column to employee_table
--------------------------------------------
This script connects to the MariaDB database and adds a ROLEID column
to the employee_table, placing it between DPTID and EMAIL_ADDRESS columns.
"""

import sys
import os
import mariadb
from typing import Dict, Any


def add_roleid_column() -> bool:
    """
    Add a ROLEID column to the employee_table, placing it
    between DPTID and EMAIL_ADDRESS columns.

    Returns:
        Boolean indicating success (True) or failure (False)
    """
    success = False

    try:
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )

        # Create a cursor from the connection
        cursor = conn.cursor()

        # Check if the column already exists to avoid errors
        check_query = """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = 'employee_table'
        AND column_name = 'ROLEID'
        """
        cursor.execute(check_query)
        column_exists = cursor.fetchone()[0]

        if column_exists:
            print("ROLEID column already exists in employee_table.")
        else:
            # Add the ROLEID column after DPTID
            alter_query = """
            ALTER TABLE employee_table
            ADD COLUMN ROLEID VARCHAR(20) NULL AFTER DPTID
            """
            cursor.execute(alter_query)
            conn.commit()
            print("ROLEID column added successfully between DPTID and EMAIL_ADDRESS in employee_table.")

            # Display the updated table structure
            cursor.execute("DESCRIBE employee_table")
            table_structure = cursor.fetchall()

            print("\nUpdated employee_table structure:")
            print("-" * 60)
            print(f"{'Column':<20} {'Type':<25} {'Null':<6} {'Key':<6}")
            print("-" * 60)
            for column in table_structure:
                print(f"{column[0]:<20} {column[1]:<25} {column[2]:<6} {column[3]:<6}")

            success = True

        # Close cursor and connection
        cursor.close()
        conn.close()

        return success

    except Exception as error:
        print(f"Error in add_roleid_column: {error}")
        # Attempt to rollback if there was an error
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            print("Transaction rolled back")
        return False


if __name__ == "__main__":
    print("\n=== Running Add ROLEID Column to employee_table ===")
    add_roleid_column()