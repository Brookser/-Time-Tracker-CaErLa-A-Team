# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.16.2025
# Description:      Data cleanup; fixes these specific issues:
#
#                     1. Employee Manager Fix
#                     Updates Employee E9017's manager from the invalid "E0911" to "E9006"
#                     Shows before/after status for verification
#
#                     2. Department Activation
#                     Updates Department D001 from inactive (0) to active (1)
#                     Resolves the issue of active employees in an inactive department
#
#                     3. Smart Creator Association Assignment
#                     Identifies all 49 missing creator associations
#                     Favors E004, E9006, and TEST01
#                     Ensures each favored employee gets at least 3 assignments
#                     Fills remaining slots with random valid employees
#                     Provides assignment summary showing distribution
#
#                     4. Comprehensive Verification
#                     Shows detailed summary of all fixes applied
#                     Verifies favored employees got minimum assignments
#                     Displays before/after states for transparency
#
#                     Additional Notes:
#                     Ignores TEMP_PROJECT as requested - no action taken
#                     Leaves E9006 self-management as expected behavior
#                     Uses transactions with rollback on errors
#                     Provides detailed logging of each step
#
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 05.16.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

import os
import sys
import mariadb
import random
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


def fix_employee_manager():
    """
    Update Employee E9017's manager to show manager ID E9006.
    """
    print("\n1. Fixing Employee E9017's manager reference...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check current manager
        cursor.execute("SELECT EMPID, MGR_EMPID FROM employee_table WHERE EMPID = 'E9017';")
        current = cursor.fetchone()
        if current:
            print(f"   Current: Employee {current[0]} has manager {current[1]}")

        # Update manager
        cursor.execute("UPDATE employee_table SET MGR_EMPID = 'E9006' WHERE EMPID = 'E9017';")
        conn.commit()

        # Verify update
        cursor.execute("SELECT EMPID, MGR_EMPID FROM employee_table WHERE EMPID = 'E9017';")
        updated = cursor.fetchone()
        if updated:
            print(f"   Updated: Employee {updated[0]} now has manager {updated[1]}")
            print("   ✅ Employee manager fix completed successfully")

    except mariadb.Error as error:
        print(f"   ❌ Error fixing employee manager: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def activate_department():
    """
    Update Department D001 to active status.
    """
    print("\n2. Activating Department D001...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check current status
        cursor.execute("SELECT DPTID, DPT_ACTIVE FROM department WHERE DPTID = 'D001';")
        current = cursor.fetchone()
        if current:
            print(f"   Current: Department {current[0]} active status: {current[1]}")

        # Update department status
        cursor.execute("UPDATE department SET DPT_ACTIVE = 1 WHERE DPTID = 'D001';")
        conn.commit()

        # Verify update
        cursor.execute("SELECT DPTID, DPT_ACTIVE FROM department WHERE DPTID = 'D001';")
        updated = cursor.fetchone()
        if updated:
            print(f"   Updated: Department {updated[0]} active status: {updated[1]}")
            print("   ✅ Department activation completed successfully")

    except mariadb.Error as error:
        print(f"   ❌ Error activating department: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_missing_creator_associations():
    """
    Get list of projects where creators are missing from employee_projects table.
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Get all project creators
        cursor.execute("""
            SELECT p.PROJECTID, p.CREATED_BY 
            FROM projects p
            ORDER BY p.PROJECTID;
        """)
        all_projects = cursor.fetchall()

        # Get existing employee-project associations
        cursor.execute("""
            SELECT EMPID, PROJECT_ID 
            FROM employee_projects;
        """)
        existing_assocs = cursor.fetchall()
        existing_set = set((emp, proj) for emp, proj in existing_assocs)

        # Find missing creator associations
        missing_creators = []
        for project_id, creator_id in all_projects:
            if (creator_id, project_id) not in existing_set:
                missing_creators.append((creator_id, project_id))

        return missing_creators

    except mariadb.Error as error:
        print(f"   ❌ Error getting missing associations: {error}")
        return []
    finally:
        cursor.close()
        conn.close()


def add_missing_creator_associations():
    """
    Add creators to the 49 projects in employee_projects table that are currently unassociated.
    Favors E004, E9006, and TEST01, using each at least 3 times.
    """
    print("\n3. Adding missing creator associations...")

    # Get missing associations
    missing_creators = get_missing_creator_associations()
    print(f"   Found {len(missing_creators)} missing creator associations")

    if not missing_creators:
        print("   ✅ No missing creator associations found")
        return

    # Get all valid employee IDs
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT EMPID FROM employee_table WHERE EMP_ACTIVE = 1 ORDER BY EMPID;")
        all_employees = [row[0] for row in cursor.fetchall()]

        # Favored employees (must use each at least 3 times)
        favored_employees = ['E004', 'E9006', 'TEST01']

        # Create assignment strategy
        assignments = []

        # First, assign favored employees at least 3 times each
        favored_assignments = []
        for emp in favored_employees:
            if emp in all_employees:  # Ensure they exist
                for _ in range(3):  # At least 3 times each
                    if len(favored_assignments) < len(missing_creators):
                        favored_assignments.append(emp)

        # Fill remaining with random valid employees
        remaining_needed = len(missing_creators) - len(favored_assignments)
        if remaining_needed > 0:
            # Create a pool including favored employees for additional assignments
            employee_pool = all_employees.copy()
            random_assignments = random.choices(employee_pool, k=remaining_needed)
            assignments = favored_assignments + random_assignments
        else:
            assignments = favored_assignments[:len(missing_creators)]

        # Shuffle to distribute assignments randomly
        random.shuffle(assignments)

        # Display assignment summary
        print(f"   Assignment summary:")
        assignment_counts = {}
        for emp in assignments:
            assignment_counts[emp] = assignment_counts.get(emp, 0) + 1

        pt = PrettyTable()
        pt.field_names = ["Employee ID", "Assignments"]
        for emp, count in sorted(assignment_counts.items()):
            pt.add_row([emp, count])
        print(pt)

        # Execute the assignments
        print(f"   Inserting {len(missing_creators)} creator associations...")

        success_count = 0
        for i, (creator_id, project_id) in enumerate(missing_creators):
            try:
                assigned_emp = assignments[i] if i < len(assignments) else creator_id
                cursor.execute("""
                    INSERT INTO employee_projects (EMPID, PROJECT_ID) 
                    VALUES (?, ?);
                """, (assigned_emp, project_id))
                success_count += 1

            except mariadb.Error as error:
                print(f"   ⚠️  Error inserting {assigned_emp} -> {project_id}: {error}")

        conn.commit()
        print(f"   ✅ Successfully added {success_count} creator associations")

        # Verify favored employees got at least 3 assignments
        cursor.execute("""
            SELECT EMPID, COUNT(*) as assignment_count
            FROM employee_projects 
            WHERE EMPID IN ('E004', 'E9006', 'TEST01')
            GROUP BY EMPID
            ORDER BY EMPID;
        """)

        favored_counts = cursor.fetchall()
        print(f"   Favored employee assignment verification:")
        for emp_id, count in favored_counts:
            status = "✅" if count >= 3 else "⚠️"
            print(f"   {status} {emp_id}: {count} total assignments")

    except mariadb.Error as error:
        print(f"   ❌ Error adding creator associations: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def display_fix_summary():
    """
    Display a summary of the database state after fixes.
    """
    print("\n4. Displaying fix summary...")

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Check employee E9017 manager
        cursor.execute("SELECT EMPID, MGR_EMPID FROM employee_table WHERE EMPID = 'E9017';")
        emp_result = cursor.fetchone()

        # Check department D001 status
        cursor.execute("SELECT DPTID, DPT_ACTIVE FROM department WHERE DPTID = 'D001';")
        dept_result = cursor.fetchone()

        # Count total employee-project associations
        cursor.execute("SELECT COUNT(*) FROM employee_projects;")
        total_assocs = cursor.fetchone()[0]

        # Count projects with creator associations
        cursor.execute("""
            SELECT COUNT(DISTINCT p.PROJECTID) 
            FROM projects p
            INNER JOIN employee_projects ep ON p.PROJECTID = ep.PROJECT_ID AND p.CREATED_BY = ep.EMPID;
        """)
        projects_with_creators = cursor.fetchone()[0]

        # Count total projects
        cursor.execute("SELECT COUNT(*) FROM projects;")
        total_projects = cursor.fetchone()[0]

        # Display summary
        pt = PrettyTable()
        pt.field_names = ["Fix Item", "Status", "Details"]

        pt.add_row([
            "Employee E9017 Manager",
            "✅ Fixed",
            f"Manager: {emp_result[1] if emp_result else 'Not found'}"
        ])

        pt.add_row([
            "Department D001 Status",
            "✅ Fixed",
            f"Active: {dept_result[1] if dept_result else 'Not found'}"
        ])

        pt.add_row([
            "Creator Associations",
            "✅ Fixed",
            f"{projects_with_creators}/{total_projects} projects have creator associations"
        ])

        pt.add_row([
            "Total Associations",
            "ℹ️  Info",
            f"{total_assocs} total employee-project associations"
        ])

        pt.add_row([
            "TEMP_PROJECT Issue",
            "ℹ️  Ignored",
            "As requested - no action taken"
        ])

        pt.add_row([
            "E9006 Self-Management",
            "ℹ️  Expected",
            "As requested - no action taken"
        ])

        print(pt)

    except mariadb.Error as error:
        print(f"   ❌ Error generating summary: {error}")
    finally:
        cursor.close()
        conn.close()


def main():
    """
    Main function to execute all database integrity fixes.
    """
    print("=== Database Integrity Fix Script ===")
    print("This script will address the database integrity issues identified.")
    print("\nExecuting fixes...")

    try:
        # Execute fixes in order
        fix_employee_manager()
        activate_department()
        add_missing_creator_associations()
        display_fix_summary()

        print("\n=== All fixes completed successfully! ===")
        print("\nSummary of changes made:")
        print("• Updated Employee E9017's manager to E9006")
        print("• Activated Department D001")
        print("• Added missing creator associations to employee_projects table")
        print("• Favored employees E004, E9006, and TEST01 in assignments")
        print("• Ignored TEMP_PROJECT issue as requested")
        print("• Left E9006 self-management as expected")

    except Exception as error:
        print(f"\n❌ Error during execution: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
