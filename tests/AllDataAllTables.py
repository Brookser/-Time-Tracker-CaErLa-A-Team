# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Discovers existing tables in DB
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
import datetime
from dotenv import load_dotenv
from prettytable import PrettyTable

# Load environment variables
load_dotenv()


def display_all_tables():
    """
    Discover all tables in the database and display their contents in a visual grid.
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
            # Get list of all tables in the database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            tables = cursor.fetchall()
            print(f"Found {len(tables)} tables in the database")

            # For each table, display its contents
            for table in tables:
                table_name = table[0]
                print(f"\n\n{'=' * 80}")
                print(f"Table: {table_name}")
                print(f"{'=' * 80}")

                # Get column information
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
                    ORDER BY ORDINAL_POSITION;
                """)

                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]

                # Get table data
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()

                # Create a pretty table
                pt = PrettyTable()
                pt.field_names = column_names

                # Add rows to the table
                for row in rows:
                    # Format datetime values for better display
                    formatted_row = []
                    for value in row:
                        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date) or isinstance(value,
                                                                                                                  datetime.time):
                            formatted_row.append(str(value))
                        else:
                            formatted_row.append(value)
                    pt.add_row(formatted_row)

                # Set max width for all columns to prevent wide tables
                pt.max_width = 30
                pt.align = 'l'  # Left align text

                # Print the pretty table
                print(pt)
                print(f"Total rows: {len(rows)}")

        except mariadb.Error as error:
            print(f"Error querying database: {error}")
            raise

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    except mariadb.Error as error:
        print(f"Error connecting to database: {error}")
        sys.exit(1)


if __name__ == "__main__":
    print("=== Displaying all tables in the database ===")
    display_all_tables()
    print("\n=== Display complete! ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
