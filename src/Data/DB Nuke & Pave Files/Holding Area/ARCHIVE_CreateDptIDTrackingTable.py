# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.22.2025
# Description:      creates and then populates table so employee department
#                       changes can be tracked
#
#                     1. Table Creation
#                     Creates employee_department_history table with proper structure:
#                     HISTORY_ID: Auto-increment primary key
#                     EMPID: Employee ID (foreign key to employee_table)
#                     DPTID: Department ID (foreign key to department)
#                     ASSIGNMENT_DATE: Date assigned to department
#                     CREATED_TIMESTAMP: When record was created
#
#                     2. Proper Database Design
#                     Foreign key constraints to maintain data integrity
#                     Indexes on EMPID, DPTID, and ASSIGNMENT_DATE for performance
#                     UTF8MB4 charset for consistency with existing tables
#
#                     3. Data Population
#                     Pulls ALL current employee-department assignments from employee_table
#                     Includes both active and inactive employees as requested
#                     Includes both active and inactive departments
#                     Uses 2025-05-20 as the assignment date for all records
#
#                     4. Comprehensive Verification
#                     Shows department distribution summary
#                     Displays sample records with employee/department names
#                     Verifies foreign key constraints are working
#                     Provides summary statistics
#
#                     5. Safety Features
#                     Checks if table already exists and asks before dropping
#                     Uses transactions with rollback on errors
#                     Detailed error handling and status reporting
#                     Follows your established style guide
#
#                     What Gets Populated:
#                     The script will populate the table with entries for all 40
#                           employees currently in the database, including:#
#                     Active employees in active departments
#                     Active employees in inactive departments (like D001)
#                     Inactive employees (like E9008, E9017, E9020)
#                     All with assignment date of 2025-05-20
#
#
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter
#
# Change Log:       - 05.22.2025: Initial setup
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


def create_department_history_table():
    """
    Create the employee_department_history table to track department changes.
    """
    print("\n1. Creating employee_department_history table...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'employee_department_history';
        """)

        table_exists = cursor.fetchone()[0] > 0

        if table_exists:
            print("   ⚠️  Table employee_department_history already exists")

            # Ask user what to do
            response = input("   Do you want to drop and recreate it? (y/N): ").strip().lower()
            if response == 'y':
                cursor.execute("DROP TABLE employee_department_history;")
                print("   🗑️  Dropped existing table")
            else:
                print("   ℹ️  Keeping existing table structure")
                cursor.close()
                conn.close()
                return False

        # Create the table
        create_table_sql = """
        CREATE TABLE employee_department_history (
            HISTORY_ID INT AUTO_INCREMENT PRIMARY KEY,
            EMPID VARCHAR(20) NOT NULL,
            DPTID VARCHAR(20) NOT NULL,
            ASSIGNMENT_DATE DATE NOT NULL,
            CREATED_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_empid (EMPID),
            INDEX idx_dptid (DPTID),
            INDEX idx_assignment_date (ASSIGNMENT_DATE),
            CONSTRAINT fk_emp_dept_hist_employee 
                FOREIGN KEY (EMPID) REFERENCES employee_table(EMPID) 
                ON UPDATE CASCADE,
            CONSTRAINT fk_emp_dept_hist_department 
                FOREIGN KEY (DPTID) REFERENCES department(DPTID) 
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """

        cursor.execute(create_table_sql)
        conn.commit()

        print("   ✅ Successfully created employee_department_history table")
        print("   📋 Table structure:")
        print("      - HISTORY_ID: Auto-increment primary key")
        print("      - EMPID: Employee ID (foreign key)")
        print("      - DPTID: Department ID (foreign key)")
        print("      - ASSIGNMENT_DATE: Date assigned to department")
        print("      - CREATED_TIMESTAMP: Record creation timestamp")
        print("      - Indexes on EMPID, DPTID, and ASSIGNMENT_DATE")

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error creating table: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_current_employee_departments():
    """
    Retrieve all current employee-department assignments from employee_table.
    """
    print("\n2. Retrieving current employee-department assignments...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                e.EMPID,
                e.FIRST_NAME,
                e.LAST_NAME,
                e.DPTID,
                d.DPT_NAME,
                e.EMP_ACTIVE,
                d.DPT_ACTIVE
            FROM employee_table e
            INNER JOIN department d ON e.DPTID = d.DPTID
            ORDER BY e.EMPID;
        """)

        employees = cursor.fetchall()

        print(f"   Found {len(employees)} employees with department assignments")

        # Display summary by department
        dept_summary = {}
        active_count = 0
        inactive_count = 0

        for emp_data in employees:
            empid, first_name, last_name, dptid, dept_name, emp_active, dept_active = emp_data

            if dptid not in dept_summary:
                dept_summary[dptid] = {
                    'dept_name': dept_name,
                    'dept_active': dept_active,
                    'employees': []
                }

            dept_summary[dptid]['employees'].append({
                'empid': empid,
                'name': f"{first_name} {last_name}",
                'active': emp_active
            })

            if emp_active:
                active_count += 1
            else:
                inactive_count += 1

        # Display department summary
        print(f"   Employee status: {active_count} active, {inactive_count} inactive")
        print("   Department distribution:")

        pt = PrettyTable()
        pt.field_names = ["Dept ID", "Department Name", "Active", "Employee Count"]

        for dptid, info in sorted(dept_summary.items()):
            pt.add_row([
                dptid,
                info['dept_name'][:20],  # Truncate long names
                "Yes" if info['dept_active'] else "No",
                len(info['employees'])
            ])

        print(pt)

        return employees

    except mariadb.Error as error:
        print(f"   ❌ Error retrieving employee departments: {error}")
        return []
    finally:
        cursor.close()
        conn.close()


def populate_department_history(employees, assignment_date="2025-05-20"):
    """
    Populate the employee_department_history table with current assignments.
    """
    print(f"\n3. Populating department history with assignment date {assignment_date}...")

    if not employees:
        print("   ⚠️  No employee data provided")
        return

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Parse the assignment date
        date_obj = datetime.datetime.strptime(assignment_date, "%Y-%m-%d").date()

        insert_sql = """
            INSERT INTO employee_department_history (EMPID, DPTID, ASSIGNMENT_DATE)
            VALUES (?, ?, ?);
        """

        success_count = 0
        error_count = 0

        print(f"   Inserting {len(employees)} department history records...")

        for emp_data in employees:
            empid, first_name, last_name, dptid, dept_name, emp_active, dept_active = emp_data

            try:
                cursor.execute(insert_sql, (empid, dptid, date_obj))
                success_count += 1

            except mariadb.Error as error:
                print(f"   ⚠️  Error inserting {empid} -> {dptid}: {error}")
                error_count += 1

        conn.commit()

        print(f"   ✅ Successfully inserted {success_count} records")
        if error_count > 0:
            print(f"   ⚠️  {error_count} records failed to insert")

        # Verify the data was inserted
        cursor.execute("SELECT COUNT(*) FROM employee_department_history;")
        total_records = cursor.fetchone()[0]
        print(f"   📊 Total records in employee_department_history: {total_records}")

    except ValueError as error:
        print(f"   ❌ Invalid date format: {error}")
        print("   Expected format: YYYY-MM-DD")
    except mariadb.Error as error:
        print(f"   ❌ Error populating history: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def display_department_history_sample():
    """
    Display a sample of the department history data.
    """
    print("\n4. Displaying sample department history data...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Get sample data with employee names and department names
        cursor.execute("""
            SELECT 
                edh.HISTORY_ID,
                edh.EMPID,
                CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as EMPLOYEE_NAME,
                edh.DPTID,
                d.DPT_NAME,
                edh.ASSIGNMENT_DATE,
                CASE WHEN e.EMP_ACTIVE = 1 THEN 'Active' ELSE 'Inactive' END as EMP_STATUS,
                CASE WHEN d.DPT_ACTIVE = 1 THEN 'Active' ELSE 'Inactive' END as DEPT_STATUS,
                edh.CREATED_TIMESTAMP
            FROM employee_department_history edh
            INNER JOIN employee_table e ON edh.EMPID = e.EMPID
            INNER JOIN department d ON edh.DPTID = d.DPTID
            ORDER BY edh.EMPID
            LIMIT 15;
        """)

        sample_data = cursor.fetchall()

        if sample_data:
            pt = PrettyTable()
            pt.field_names = [
                "History ID", "Emp ID", "Employee Name", "Dept ID",
                "Department", "Assignment Date", "Emp Status", "Dept Status"
            ]
            pt.max_width = 15
            pt.align = 'l'

            for row in sample_data:
                pt.add_row([
                    row[0], row[1], row[2][:15], row[3],
                    row[4][:12], str(row[5]), row[6], row[7]
                ])

            print(pt)
            print(f"   (Showing first 15 records)")
        else:
            print("   ⚠️  No data found in employee_department_history table")

        # Show summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT EMPID) as unique_employees,
                COUNT(DISTINCT DPTID) as unique_departments,
                MIN(ASSIGNMENT_DATE) as earliest_date,
                MAX(ASSIGNMENT_DATE) as latest_date
            FROM employee_department_history;
        """)

        stats = cursor.fetchone()

        print(f"\n   📈 Summary Statistics:")
        print(f"      Total Records: {stats[0]}")
        print(f"      Unique Employees: {stats[1]}")
        print(f"      Unique Departments: {stats[2]}")
        print(f"      Date Range: {stats[3]} to {stats[4]}")

    except mariadb.Error as error:
        print(f"   ❌ Error displaying sample data: {error}")
    finally:
        cursor.close()
        conn.close()


def verify_table_constraints():
    """
    Verify the foreign key constraints are working properly.
    """
    print("\n5. Verifying table constraints and relationships...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check for any orphaned records (shouldn't be any with proper FKs)
        cursor.execute("""
            SELECT 'Orphaned Employees' as check_type, COUNT(*) as count
            FROM employee_department_history edh
            LEFT JOIN employee_table e ON edh.EMPID = e.EMPID
            WHERE e.EMPID IS NULL

            UNION ALL

            SELECT 'Orphaned Departments' as check_type, COUNT(*) as count
            FROM employee_department_history edh
            LEFT JOIN department d ON edh.DPTID = d.DPTID
            WHERE d.DPTID IS NULL;
        """)

        constraint_checks = cursor.fetchall()

        pt = PrettyTable()
        pt.field_names = ["Constraint Check", "Count"]

        all_good = True
        for check_type, count in constraint_checks:
            status = "✅" if count == 0 else "❌"
            pt.add_row([f"{status} {check_type}", count])
            if count > 0:
                all_good = False

        print(pt)

        if all_good:
            print("   ✅ All foreign key constraints are working properly")
        else:
            print("   ⚠️  Some constraint violations found")

        # Show table indexes
        cursor.execute("""
            SHOW INDEX FROM employee_department_history;
        """)

        indexes = cursor.fetchall()
        print(f"\n   📑 Table has {len(indexes)} indexes for optimal performance")

    except mariadb.Error as error:
        print(f"   ❌ Error verifying constraints: {error}")
    finally:
        cursor.close()
        conn.close()


def main():
    """
    Main function to create department history table and populate it.
    """
    print("=== Employee Department History Table Setup ===")
    print("This script will create a new table to track employee department changes")
    print("and populate it with current employee-department assignments.")

    try:
        # Step 1: Create the table
        table_created = create_department_history_table()

        if not table_created:
            print("\n❌ Table creation failed or was skipped. Exiting.")
            return

        # Step 2: Get current employee-department assignments
        employees = get_current_employee_departments()

        if not employees:
            print("\n❌ No employee data found. Exiting.")
            return

        # Step 3: Populate the history table
        assignment_date = "2025-05-20"  # As specified
        populate_department_history(employees, assignment_date)

        # Step 4: Display sample data
        display_department_history_sample()

        # Step 5: Verify constraints
        verify_table_constraints()

        print("\n=== Department History Table Setup Complete! ===")
        print("\n✅ Summary of what was created:")
        print("• New table: employee_department_history")
        print("• Tracks: Employee ID, Department ID, Assignment Date")
        print("• Populated with current assignments dated 2025-05-20")
        print("• Includes both active and inactive employees/departments")
        print("• Proper foreign key constraints and indexes added")
        print("• Ready to track future department changes")

        print(f"\n📝 Usage Examples:")
        print("• Track when employees change departments")
        print("• Generate department history reports")
        print("• Audit employee movements between departments")
        print("• Analyze department staffing changes over time")

    except Exception as error:
        print(f"\n❌ Error during execution: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
