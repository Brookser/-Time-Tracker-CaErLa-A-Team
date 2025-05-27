# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      adds column to 'time' table to support manager 'flagged_for_review'
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter
#
# Change Log:       - 05.26.2025: Initial setup
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


def connect_to_database():
    """
    Establish connection to MariaDB database.
    """
    try:
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )
        return conn
    except mariadb.Error as error:
        print(f"Error connecting to database: {error}")
        sys.exit(1)


def check_current_time_table_structure():
    """
    Check the current structure of the time table to see what columns exist.
    """
    print("\n1. Checking current time table structure...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'time'
            ORDER BY ORDINAL_POSITION;
        """)

        columns = cursor.fetchall()

        if not columns:
            print("   ❌ Time table not found!")
            return False

        print(f"   ✅ Found time table with {len(columns)} columns")

        # Display current structure
        pt = PrettyTable()
        pt.field_names = ["Column Name", "Data Type", "Nullable", "Default", "Comment"]
        pt.align = 'l'

        review_flag_exists = False
        for col in columns:
            col_name, data_type, nullable, default, comment = col
            pt.add_row([col_name, data_type, nullable, str(default) if default else '', comment or ''])

            if col_name.upper() in ['FLAGGED_FOR_REVIEW', 'REVIEW_FLAG', 'FLAG_FOR_REVIEW']:
                review_flag_exists = True

        print("   Current table structure:")
        print(pt)

        if review_flag_exists:
            print("   ⚠️  A review flag column already exists")
            return False

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error checking table structure: {error}")
        return False
    finally:
        cursor.close()
        conn.close()


def add_review_flag_column():
    """
    Add the FLAGGED_FOR_REVIEW boolean column to the time table.
    """
    print("\n2. Adding FLAGGED_FOR_REVIEW column to time table...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Add the new column
        alter_sql = """
        ALTER TABLE time 
        ADD COLUMN FLAGGED_FOR_REVIEW TINYINT(1) DEFAULT 0 
        COMMENT 'Flag indicating if time entry needs manager review'
        """

        cursor.execute(alter_sql)
        conn.commit()

        print("   ✅ Successfully added FLAGGED_FOR_REVIEW column")
        print("   📋 Column details:")
        print("      - Name: FLAGGED_FOR_REVIEW")
        print("      - Type: TINYINT(1) (boolean)")
        print("      - Default: 0 (false/not flagged)")
        print("      - Nullable: No")
        print("      - Comment: Flag indicating if time entry needs manager review")

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error adding column: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def add_review_flag_index():
    """
    Add an index on the FLAGGED_FOR_REVIEW column for efficient queries.
    """
    print("\n3. Adding index for FLAGGED_FOR_REVIEW column...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Add index for efficient queries on flagged entries
        index_sql = """
        CREATE INDEX idx_flagged_for_review ON time (FLAGGED_FOR_REVIEW)
        """

        cursor.execute(index_sql)
        conn.commit()

        print("   ✅ Successfully added index idx_flagged_for_review")
        print("   📈 This will improve performance when querying flagged entries")

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error adding index: {error}")
        print("   ℹ️  Index may already exist or there was a database issue")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def verify_column_addition():
    """
    Verify that the column was added successfully and show updated structure.
    """
    print("\n4. Verifying column addition...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'time'
            AND COLUMN_NAME = 'FLAGGED_FOR_REVIEW';
        """)

        column_info = cursor.fetchone()

        if column_info:
            col_name, data_type, nullable, default, comment = column_info
            print("   ✅ Column successfully added")
            print(f"      Column: {col_name}")
            print(f"      Type: {data_type}")
            print(f"      Nullable: {nullable}")
            print(f"      Default: {default}")
            print(f"      Comment: {comment}")
        else:
            print("   ❌ Column not found after addition")
            return False

        # Get total count of time entries
        cursor.execute("SELECT COUNT(*) FROM time;")
        total_entries = cursor.fetchone()[0]

        # Check how many are flagged (should be 0 initially)
        cursor.execute("SELECT COUNT(*) FROM time WHERE FLAGGED_FOR_REVIEW = 1;")
        flagged_entries = cursor.fetchone()[0]

        print(f"\n   📊 Current time entry status:")
        print(f"      Total entries: {total_entries}")
        print(f"      Flagged for review: {flagged_entries}")
        print(f"      Not flagged: {total_entries - flagged_entries}")

        # Show sample of updated structure
        cursor.execute("""
            SELECT TIMEID, EMPID, PROJECTID, FLAGGED_FOR_REVIEW
            FROM time 
            ORDER BY TIMEID 
            LIMIT 5;
        """)

        sample_data = cursor.fetchall()

        if sample_data:
            print(f"\n   📋 Sample data showing new column:")
            pt = PrettyTable()
            pt.field_names = ["Time ID", "Employee ID", "Project ID", "Flagged for Review"]
            pt.align = 'l'

            for row in sample_data:
                flagged_status = "Yes" if row[3] == 1 else "No"
                pt.add_row([row[0], row[1], row[2], flagged_status])

            print(pt)

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error verifying column: {error}")
        return False
    finally:
        cursor.close()
        conn.close()


def show_usage_examples():
    """
    Show examples of how to use the new review flag functionality.
    """
    print("\n5. Usage examples for the new review flag...")

    print("   📝 SQL Examples:")
    print("   ================")

    print("\n   Flag a time entry for review:")
    print("   UPDATE time SET FLAGGED_FOR_REVIEW = 1 WHERE TIMEID = 'T_12345';")

    print("\n   Get all flagged time entries:")
    print("   SELECT * FROM time WHERE FLAGGED_FOR_REVIEW = 1;")

    print("\n   Get flagged entries for a specific employee:")
    print("   SELECT * FROM time WHERE EMPID = 'E001' AND FLAGGED_FOR_REVIEW = 1;")

    print("\n   Get flagged entries with employee details:")
    print("""   SELECT t.TIMEID, e.FIRST_NAME, e.LAST_NAME, t.START_TIME, t.STOP_TIME, t.NOTES
   FROM time t
   INNER JOIN employee_table e ON t.EMPID = e.EMPID
   WHERE t.FLAGGED_FOR_REVIEW = 1;""")

    print("\n   Clear review flag after review:")
    print("   UPDATE time SET FLAGGED_FOR_REVIEW = 0 WHERE TIMEID = 'T_12345';")

    print("\n   📊 Database.py Classmethod Examples:")
    print("   ====================================")

    print("""
   @classmethod
   def flag_time_entry_for_review(cls, timeid):
       cursor = cls.get_cursor()
       cursor.execute("UPDATE time SET FLAGGED_FOR_REVIEW = 1 WHERE TIMEID = ?", (timeid,))
       cls.commit()
       cursor.close()

   @classmethod
   def get_flagged_time_entries(cls, empid=None):
       cursor = cls.get_cursor()
       if empid:
           cursor.execute("SELECT * FROM time WHERE FLAGGED_FOR_REVIEW = 1 AND EMPID = ?", (empid,))
       else:
           cursor.execute("SELECT * FROM time WHERE FLAGGED_FOR_REVIEW = 1")
       result = cursor.fetchall()
       cursor.close()
       return result

   @classmethod
   def clear_review_flag(cls, timeid):
       cursor = cls.get_cursor()
       cursor.execute("UPDATE time SET FLAGGED_FOR_REVIEW = 0 WHERE TIMEID = ?", (timeid,))
       cls.commit()
       cursor.close()""")


def show_indexes_info():
    """
    Show information about indexes on the time table.
    """
    print("\n6. Current indexes on time table...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("SHOW INDEX FROM time;")
        indexes = cursor.fetchall()

        if indexes:
            print("   📑 Current indexes:")
            pt = PrettyTable()
            pt.field_names = ["Index Name", "Column", "Unique", "Type"]
            pt.align = 'l'

            for idx in indexes:
                # Index format: Table, Non_unique, Key_name, Seq_in_index, Column_name, ...
                key_name = idx[2]
                column_name = idx[4]
                is_unique = "Yes" if idx[1] == 0 else "No"
                index_type = idx[10] if len(idx) > 10 else "BTREE"

                pt.add_row([key_name, column_name, is_unique, index_type])

            print(pt)
        else:
            print("   ⚠️  No indexes found")

    except mariadb.Error as error:
        print(f"   ❌ Error getting index information: {error}")
    finally:
        cursor.close()
        conn.close()


def main():
    """
    Main function to add review flag functionality to time table.
    """
    print("=== Adding Review Flag to Time Table ===")
    print("This script will add a FLAGGED_FOR_REVIEW boolean column to the time table")
    print("to allow managers to flag time entries that need review.")

    try:
        # Step 1: Check current structure
        if not check_current_time_table_structure():
            print("\n❌ Cannot proceed with column addition.")
            response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Exiting.")
                return

        # Step 2: Add the column
        if not add_review_flag_column():
            print("\n❌ Failed to add review flag column. Exiting.")
            return

        # Step 3: Add index
        add_review_flag_index()  # Non-critical if it fails

        # Step 4: Verify addition
        if not verify_column_addition():
            print("\n❌ Column verification failed.")
            return

        # Step 5: Show usage examples
        show_usage_examples()

        # Step 6: Show index information
        show_indexes_info()

        print("\n=== Review Flag Addition Complete! ===")
        print("\n✅ Summary of changes:")
        print("• Added FLAGGED_FOR_REVIEW column to time table")
        print("• Column type: TINYINT(1) with default value 0")
        print("• Added index for efficient queries")
        print("• All existing time entries default to not flagged")
        print("• Ready for manager review workflow")

        print(f"\n📋 Next Steps:")
        print("• Update Database.py with review flag classmethods")
        print("• Implement manager review UI functionality")
        print("• Create reports for flagged time entries")
        print("• Set up notifications for managers")

    except Exception as error:
        print(f"\n❌ Error during execution: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
