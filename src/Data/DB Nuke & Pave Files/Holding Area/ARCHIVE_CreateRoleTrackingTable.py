# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.24.2025
# Description:      creates and then populates table so employee role
#                       changes can be tracked
#
#                     1. Table Creation: employee_role_history
#                     ROLE_HISTORY_ID: Auto-increment primary key
#                     EMPID: Employee ID (foreign key to employee_table)
#                     EMP_ROLE: Employee role (individual, manager, project_manager, user)
#                     ROLE_ASSIGNMENT_DATE: Date assigned to role
#                     CREATED_TIMESTAMP: Record creation timestamp
#
#                     2. Proper Database Design
#                     Foreign key constraint to employee_table
#                     Indexes on EMPID, ROLE_ASSIGNMENT_DATE, and EMP_ROLE for performance
#                     Same charset/collation as existing tables
#
#                     3. Current Role Analysis
#                     Shows role distribution across the organization
#                     Displays active vs inactive employees by role
#                     Provides detailed breakdown of who has what role
#
#                     4. Data Population
#                     Populates with all current employee roles from employee_table
#                     Uses 2025-05-20 as assignment date (consistent with department history)
#                     Includes both active and inactive employees
#                     Shows summary of records inserted by role type
#
#                     5. Data Verification
#                     Validates foreign key constraints
#                     Checks for standard vs non-standard role values
#                     Provides summary statistics and role distribution
#                     Shows sample data with employee names and departments
#
#                     What Gets Tracked:
#                     Based on your current data, the script will track these roles:#
#                     individual: Regular employees
#                     manager: Department/team managers
#                     project_manager: Project managers
#                     user: Basic users
#
#
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter
#
# Change Log:       - 05.24.2025: Initial setup
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


def create_role_history_table():
    """
    Create the employee_role_history table to track role changes.
    """
    print("\n1. Creating employee_role_history table...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'employee_role_history';
        """)

        table_exists = cursor.fetchone()[0] > 0

        if table_exists:
            print("   ⚠️  Table employee_role_history already exists")

            # Ask user what to do
            response = input("   Do you want to drop and recreate it? (y/N): ").strip().lower()
            if response == 'y':
                cursor.execute("DROP TABLE employee_role_history;")
                print("   🗑️  Dropped existing table")
            else:
                print("   ℹ️  Keeping existing table structure")
                cursor.close()
                conn.close()
                return False

        # Create the table
        create_table_sql = """
        CREATE TABLE employee_role_history (
            ROLE_HISTORY_ID INT AUTO_INCREMENT PRIMARY KEY,
            EMPID VARCHAR(20) NOT NULL,
            EMP_ROLE VARCHAR(20) NOT NULL,
            ROLE_ASSIGNMENT_DATE DATE NOT NULL,
            CREATED_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_role_empid (EMPID),
            INDEX idx_role_assignment_date (ROLE_ASSIGNMENT_DATE),
            INDEX idx_emp_role (EMP_ROLE),
            CONSTRAINT fk_emp_role_hist_employee 
                FOREIGN KEY (EMPID) REFERENCES employee_table(EMPID) 
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """

        cursor.execute(create_table_sql)
        conn.commit()

        print("   ✅ Successfully created employee_role_history table")
        print("   📋 Table structure:")
        print("      - ROLE_HISTORY_ID: Auto-increment primary key")
        print("      - EMPID: Employee ID (foreign key)")
        print("      - EMP_ROLE: Employee role (individual, manager, project_manager, user)")
        print("      - ROLE_ASSIGNMENT_DATE: Date assigned to role")
        print("      - CREATED_TIMESTAMP: Record creation timestamp")
        print("      - Indexes on EMPID, ROLE_ASSIGNMENT_DATE, and EMP_ROLE")

        return True

    except mariadb.Error as error:
        print(f"   ❌ Error creating table: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_current_employee_roles():
    """
    Retrieve all current employee role assignments from employee_table.
    """
    print("\n2. Retrieving current employee role assignments...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                e.EMPID,
                e.FIRST_NAME,
                e.LAST_NAME,
                e.EMP_ROLE,
                e.DPTID,
                d.DPT_NAME,
                e.EMP_ACTIVE
            FROM employee_table e
            INNER JOIN department d ON e.DPTID = d.DPTID
            ORDER BY e.EMP_ROLE, e.EMPID;
        """)

        employees = cursor.fetchall()

        print(f"   Found {len(employees)} employees with role assignments")

        # Display summary by role
        role_summary = {}
        active_count = 0
        inactive_count = 0

        for emp_data in employees:
            empid, first_name, last_name, emp_role, dptid, dept_name, emp_active = emp_data

            if emp_role not in role_summary:
                role_summary[emp_role] = {
                    'employees': [],
                    'active_count': 0,
                    'inactive_count': 0
                }

            role_summary[emp_role]['employees'].append({
                'empid': empid,
                'name': f"{first_name} {last_name}",
                'dept': dptid,
                'active': emp_active
            })

            if emp_active:
                role_summary[emp_role]['active_count'] += 1
                active_count += 1
            else:
                role_summary[emp_role]['inactive_count'] += 1
                inactive_count += 1

        # Display role summary
        print(f"   Employee status: {active_count} active, {inactive_count} inactive")
        print("   Role distribution:")

        pt = PrettyTable()
        pt.field_names = ["Role", "Active Employees", "Inactive Employees", "Total"]

        for role, info in sorted(role_summary.items()):
            pt.add_row([
                role,
                info['active_count'],
                info['inactive_count'],
                len(info['employees'])
            ])

        print(pt)

        # Show detailed breakdown
        print("\n   Detailed role assignments:")
        for role, info in sorted(role_summary.items()):
            print(f"   📋 {role}: {len(info['employees'])} employees")
            for emp in info['employees'][:5]:  # Show first 5
                status = "Active" if emp['active'] else "Inactive"
                print(f"      - {emp['empid']} ({emp['name'][:20]}) - {emp['dept']} - {status}")
            if len(info['employees']) > 5:
                print(f"      ... and {len(info['employees']) - 5} more")

        return employees

    except mariadb.Error as error:
        print(f"   ❌ Error retrieving employee roles: {error}")
        return []
    finally:
        cursor.close()
        conn.close()


def populate_role_history(employees, assignment_date="2025-05-20"):
    """
    Populate the employee_role_history table with current role assignments.
    """
    print(f"\n3. Populating role history with assignment date {assignment_date}...")

    if not employees:
        print("   ⚠️  No employee data provided")
        return

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Parse the assignment date
        date_obj = datetime.datetime.strptime(assignment_date, "%Y-%m-%d").date()

        insert_sql = """
            INSERT INTO employee_role_history (EMPID, EMP_ROLE, ROLE_ASSIGNMENT_DATE)
            VALUES (?, ?, ?);
        """

        success_count = 0
        error_count = 0
        role_counts = {}

        print(f"   Inserting {len(employees)} role history records...")

        for emp_data in employees:
            empid, first_name, last_name, emp_role, dptid, dept_name, emp_active = emp_data

            try:
                cursor.execute(insert_sql, (empid, emp_role, date_obj))
                success_count += 1

                # Count roles for summary
                role_counts[emp_role] = role_counts.get(emp_role, 0) + 1

            except mariadb.Error as error:
                print(f"   ⚠️  Error inserting {empid} -> {emp_role}: {error}")
                error_count += 1

        conn.commit()

        print(f"   ✅ Successfully inserted {success_count} records")
        if error_count > 0:
            print(f"   ⚠️  {error_count} records failed to insert")

        # Show insertion summary by role
        print(f"   📊 Records inserted by role:")
        for role, count in sorted(role_counts.items()):
            print(f"      {role}: {count} records")

        # Verify the data was inserted
        cursor.execute("SELECT COUNT(*) FROM employee_role_history;")
        total_records = cursor.fetchone()[0]
        print(f"   📈 Total records in employee_role_history: {total_records}")

    except ValueError as error:
        print(f"   ❌ Invalid date format: {error}")
        print("   Expected format: YYYY-MM-DD")
    except mariadb.Error as error:
        print(f"   ❌ Error populating role history: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def display_role_history_sample():
    """
    Display a sample of the role history data.
    """
    print("\n4. Displaying sample role history data...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Get sample data with employee names and department info
        cursor.execute("""
            SELECT 
                erh.ROLE_HISTORY_ID,
                erh.EMPID,
                CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as EMPLOYEE_NAME,
                erh.EMP_ROLE,
                e.DPTID,
                d.DPT_NAME,
                erh.ROLE_ASSIGNMENT_DATE,
                CASE WHEN e.EMP_ACTIVE = 1 THEN 'Active' ELSE 'Inactive' END as EMP_STATUS,
                erh.CREATED_TIMESTAMP
            FROM employee_role_history erh
            INNER JOIN employee_table e ON erh.EMPID = e.EMPID
            INNER JOIN department d ON e.DPTID = d.DPTID
            ORDER BY erh.EMP_ROLE, erh.EMPID
            LIMIT 15;
        """)

        sample_data = cursor.fetchall()

        if sample_data:
            pt = PrettyTable()
            pt.field_names = [
                "History ID", "Emp ID", "Employee Name", "Role",
                "Dept", "Department", "Assignment Date", "Status"
            ]
            pt.max_width = 15
            pt.align = 'l'

            for row in sample_data:
                pt.add_row([
                    row[0], row[1], row[2][:15], row[3],
                    row[4], row[5][:12], str(row[6]), row[7]
                ])

            print(pt)
            print(f"   (Showing first 15 records)")
        else:
            print("   ⚠️  No data found in employee_role_history table")

        # Show summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT EMPID) as unique_employees,
                COUNT(DISTINCT EMP_ROLE) as unique_roles,
                MIN(ROLE_ASSIGNMENT_DATE) as earliest_date,
                MAX(ROLE_ASSIGNMENT_DATE) as latest_date
            FROM employee_role_history;
        """)

        stats = cursor.fetchone()

        # Show role distribution
        cursor.execute("""
            SELECT EMP_ROLE, COUNT(*) as count
            FROM employee_role_history
            GROUP BY EMP_ROLE
            ORDER BY count DESC;
        """)

        role_dist = cursor.fetchall()

        print(f"\n   📈 Summary Statistics:")
        print(f"      Total Records: {stats[0]}")
        print(f"      Unique Employees: {stats[1]}")
        print(f"      Unique Roles: {stats[2]}")
        print(f"      Date Range: {stats[3]} to {stats[4]}")

        print(f"\n   📊 Role Distribution:")
        for role, count in role_dist:
            print(f"      {role}: {count} employees")

    except mariadb.Error as error:
        print(f"   ❌ Error displaying sample data: {error}")
    finally:
        cursor.close()
        conn.close()


def verify_role_table_constraints():
    """
    Verify the foreign key constraints and data integrity.
    """
    print("\n5. Verifying table constraints and data integrity...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check for orphaned records and validate role values
        cursor.execute("""
            SELECT 'Orphaned Employees' as check_type, COUNT(*) as count
            FROM employee_role_history erh
            LEFT JOIN employee_table e ON erh.EMPID = e.EMPID
            WHERE e.EMPID IS NULL

            UNION ALL

            SELECT 'Valid Role Values' as check_type, COUNT(DISTINCT EMP_ROLE) as count
            FROM employee_role_history
            WHERE EMP_ROLE IN ('individual', 'manager', 'project_manager', 'user')

            UNION ALL

            SELECT 'Total Unique Roles' as check_type, COUNT(DISTINCT EMP_ROLE) as count
            FROM employee_role_history;
        """)

        constraint_checks = cursor.fetchall()

        pt = PrettyTable()
        pt.field_names = ["Constraint Check", "Count"]

        for check_type, count in constraint_checks:
            if "Orphaned" in check_type:
                status = "✅" if count == 0 else "❌"
            else:
                status = "ℹ️"
            pt.add_row([f"{status} {check_type}", count])

        print(pt)

        # Check for any unusual role values
        cursor.execute("""
            SELECT EMP_ROLE, COUNT(*) as count
            FROM employee_role_history
            WHERE EMP_ROLE NOT IN ('individual', 'manager', 'project_manager', 'user')
            GROUP BY EMP_ROLE;
        """)

        unusual_roles = cursor.fetchall()
        if unusual_roles:
            print(f"\n   ⚠️  Non-standard role values found:")
            for role, count in unusual_roles:
                print(f"      '{role}': {count} employees")
        else:
            print(f"\n   ✅ All role values are standard")

        # Show table indexes
        cursor.execute("""
            SHOW INDEX FROM employee_role_history;
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
    Main function to create role history table and populate it.
    """
    print("=== Employee Role History Table Setup ===")
    print("This script will create a new table to track employee role changes")
    print("and populate it with current employee role assignments.")

    try:
        # Step 1: Create the table
        table_created = create_role_history_table()

        if not table_created:
            print("\n❌ Table creation failed or was skipped. Exiting.")
            return

        # Step 2: Get current employee role assignments
        employees = get_current_employee_roles()

        if not employees:
            print("\n❌ No employee data found. Exiting.")
            return

        # Step 3: Populate the history table
        assignment_date = "2025-05-20"  # Same date as department history
        populate_role_history(employees, assignment_date)

        # Step 4: Display sample data
        display_role_history_sample()

        # Step 5: Verify constraints
        verify_role_table_constraints()

        print("\n=== Role History Table Setup Complete! ===")
        print("\n✅ Summary of what was created:")
        print("• New table: employee_role_history")
        print("• Tracks: Employee ID, Role, Assignment Date")
        print("• Populated with current role assignments dated 2025-05-20")
        print("• Includes both active and inactive employees")
        print("• Proper foreign key constraints and indexes added")
        print("• Ready to track future role changes")

        print(f"\n📝 Usage Examples:")
        print("• Track when employees get promoted/demoted")
        print("• Generate role change audit reports")
        print("• Analyze career progression patterns")
        print("• Monitor management structure changes")
        print("• Compliance reporting for role assignments")

    except Exception as error:
        print(f"\n❌ Error during execution: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
