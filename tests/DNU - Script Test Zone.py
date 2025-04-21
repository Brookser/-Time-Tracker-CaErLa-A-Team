#!/usr/bin/env python3
"""
Script to add ROLEID column to employee_table
--------------------------------------------
This script connects to the MariaDB database and adds a ROLEID column
to the employee_table, placing it between DPTID and EMAIL_ADDRESS columns.
"""
import os
import sys
import mariadb
from dotenv import load_dotenv
from tabulate import tabulate  # You may need to install this: pip install tabulate

# Load environment variables
load_dotenv()


def display_all_tables():
    """
    List all tables in the database and display their data in a visual grid.
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

        # Get list of all tables in the database
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """, (os.getenv("DB_NAME"),))

        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        print(f"Found {len(tables)} tables in the database:")
        for i, table in enumerate(tables):
            print(f"{i + 1}. {table[0]}")

        print("\nDisplaying data for all tables:\n")

        # Display data for each table
        for table in tables:
            table_name = table[0]
            print(f"\n{'=' * 80}")
            print(f"TABLE: {table_name}")
            print(f"{'=' * 80}")

            # Get column names
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]

            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if rows:
                # Display data in a formatted table
                print(tabulate(rows, headers=column_names, tablefmt="grid"))
                print(f"Total rows: {len(rows)}")
            else:
                print("No data in this table.")

        # Close cursor and connection
        cursor.close()
        conn.close()

    except mariadb.Error as error:
        print(f"Error displaying tables: {error}")
        sys.exit(1)


def get_table_count_summary():
    """
    Get a summary of row counts for each table.
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

        # Get list of all tables in the database
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """, (os.getenv("DB_NAME"),))

        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        # Collect row counts for each table
        table_counts = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_counts.append((table_name, count))

        # Display summary
        print("\nTable Row Count Summary:")
        print("=" * 40)
        print(tabulate(table_counts, headers=["Table Name", "Row Count"], tablefmt="grid"))

        # Close cursor and connection
        cursor.close()
        conn.close()

    except mariadb.Error as error:
        print(f"Error getting table count summary: {error}")
        sys.exit(1)


if __name__ == "__main__":
    print("Examining database tables and their contents...\n")
    get_table_count_summary()
    display_all_tables()