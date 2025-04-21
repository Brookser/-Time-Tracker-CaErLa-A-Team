# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Discovers existing tables in DB, then drops all tables
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


if __name__ == "__main__":
    print("=== Checking for existing tables and dropping them… ===")
    drop_all_tables()

    print("=== Database is now empty and ready for setup. ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
