# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Example: runs tests to:
#                   • count number of required password resets
#                   • retrieve inactive projects from the database
#                   • projects with a PRIOR_PROJECTID
#                   • projects with a 4/15/2025 start date
#                   • inactive employees
#                   • manual time entries
#                   • time summary by employee
#                   • project time summary
# Input:            none
# Output:           Expected results as follows:
#                   • expected resets: 2096	Godfrey	Gaye
#                   • Inactive Projects
#                          10005 Blesbok
#                          10008 Brazilian tapir
#                          10009 Dog, raccoon
#                          10014 Goose, andean
#                          10022 Squirrel, antelope ground
#                   •Projects with PRIOR_PROJECTID
#                          10015 Goose, greylag
#                          10016 Greater adjutant stork
#                          10017 Javan gold-spotted mongoose
#                          10020 Dog
#                          10021 Racoon
#                          10025 Squirrel
#                   • Projects with 4/15/2025 start date
#                          10015 Goose, greylag
#                          10016 Greater adjutant stork
#                          10017 Javan gold-spotted mongoose
#                          10020 Dog
#                          10021 Racoon
#                          10025 Squirrel
#                   • Inactive Employees
#                          2088 Othello Beesey
#                          2505 Aundrea Abela
#                          6539 Kenny Scardifeild
#                          8334 Dane Eynald
#                   • manual entries = 8
#                   • EmployeeID	num of entries	Expected Minute Totals
#                         1094	2	264.96
#                         1488	2	149.76
#                         1610	3	205.92
#                         2088	2	126.72
#                         2505	4	426.24
#                   • PROJECT_ID totals
#                         10001	128.16
#                         10003	128.16
#                         10005	204.48
#                         10006	243.36
#                         10007	56.16
#                         10009	128.16
#                         10010	175.68
#                         10011	97.92
#                         10012	92.16
#                         10014	99.36
#                         10015	138.24
#                         10016	126.72
#                         10017	60.48
#                         10018	142.56
#                         10020	90.72
#                         10021	133.92
#                         10024	44.64
#                         10025	118.08

# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.20.2025: Initial setup of tests
#
# **********************************************************************************************************************
# **********************************************************************************************************************
# !/usr/bin/env python3
"""
Database utility script
-----------------------
This script provides functions to:
1. Retrieve login IDs where FORCE_RESET is set to true
2. Retrieve inactive projects from the database
"""

import sys
import os
import logging
from typing import List, Dict, Any
import mariadb
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_utils.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("database_utils_script")

# Load environment variables
load_dotenv()


def get_force_reset_logins():
    """
    Retrieve login IDs where FORCE_RESET is set to true
    using the existing Database class for connection.
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

        # Create a cursor from the connection
        cursor = conn.cursor()

        # Query to find logins with FORCE_RESET enabled
        query = "SELECT LOGINID FROM login_table WHERE FORCE_RESET = 1"
        cursor.execute(query)

        # Fetch all matching login IDs
        logins = cursor.fetchall()

        if not logins:
            print("No accounts with FORCE_RESET enabled were found.")
        else:
            print("Accounts requiring password reset:")
            print("----------------------------------")
            for login in logins:
                print(login[0])

        # Close cursor (connection will be handled by Database class)
        cursor.close()
        conn.close()

        return [login[0] for login in logins]

    except Exception as error:
        logger.error(f"Error in get_force_reset_logins: {error}")
        return []


def get_inactive_projects() -> List[Dict[str, Any]]:
    """
    Retrieve all projects that have PROJECT_ACTIVE set to false
    using environment variables for connection details.
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to find projects with PROJECT_ACTIVE = false
        query = """
        SELECT p.PROJECTID, p.PROJECT_NAME, p.CREATED_BY, 
               DATE_FORMAT(p.DATE_CREATED, '%Y-%m-%d %H:%i:%s') AS DATE_CREATED,
               CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS CREATOR_NAME,
               p.PRIOR_PROJECTID
        FROM projects p
        JOIN employee_table e ON p.CREATED_BY = e.EMPID
        WHERE p.PROJECT_ACTIVE = FALSE
        ORDER BY p.PROJECT_NAME
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # If there are prior projects, get their names
        if results:
            for project in results:
                if project['PRIOR_PROJECTID']:
                    prior_query = """
                    SELECT PROJECT_NAME
                    FROM projects
                    WHERE PROJECTID = %s
                    """
                    cursor.execute(prior_query, (project['PRIOR_PROJECTID'],))
                    prior_result = cursor.fetchone()
                    if prior_result:
                        project['PRIOR_PROJECT_NAME'] = prior_result['PROJECT_NAME']
                    else:
                        project['PRIOR_PROJECT_NAME'] = "Unknown"
                else:
                    project['PRIOR_PROJECT_NAME'] = None

        # Print results
        if not results:
            print("No inactive projects found (PROJECT_ACTIVE = FALSE)")
        else:
            print("\nInactive Projects:")
            print("-" * 100)
            print(f"{'PROJECT ID':<15} {'PROJECT NAME':<40} {'CREATED BY':<30} {'DATE CREATED':<20}")
            print("-" * 100)

            for project in results:
                print(
                    f"{project['PROJECTID']:<15} {project['PROJECT_NAME']:<40} {project['CREATOR_NAME']:<30} {project['DATE_CREATED']:<20}")

                # If project has a prior version, print it with indentation
                if project['PRIOR_PROJECTID']:
                    print(f"    Previous version: {project['PRIOR_PROJECTID']} - {project['PRIOR_PROJECT_NAME']}")

            print("-" * 100)

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        logger.error(f"Error in get_inactive_projects: {error}")
        return []


def get_projects_with_prior() -> List[Dict[str, Any]]:
    """
    Retrieve all projects that have a PRIOR_PROJECTID value,
    indicating they are newer versions of existing projects.
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to find projects with a PRIOR_PROJECTID
        query = """
        SELECT
            p.PROJECTID,
            p.PROJECT_NAME,
            p.PRIOR_PROJECTID,
            prior.PROJECT_NAME AS PRIOR_PROJECT_NAME,
            p.CREATED_BY,
            CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS CREATOR_NAME,
            DATE_FORMAT(p.DATE_CREATED, '%Y-%m-%d %H:%i:%s') AS DATE_CREATED,
            p.PROJECT_ACTIVE
        FROM projects p
        JOIN employee_table e ON p.CREATED_BY = e.EMPID
        LEFT JOIN projects prior ON p.PRIOR_PROJECTID = prior.PROJECTID
        WHERE p.PRIOR_PROJECTID IS NOT NULL
        ORDER BY p.DATE_CREATED DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # Print results
        if not results:
            print("No projects found with prior versions")
        else:
            print("\nProjects with Prior Versions:")
            print("-" * 110)
            print(f"{'PROJECT ID':<15} {'PROJECT NAME':<35} {'PRIOR PROJECT ID':<15} {'PRIOR PROJECT NAME':<35}")
            print("-" * 110)

            for project in results:
                print(f"{project['PROJECTID']:<15} {project['PROJECT_NAME']:<35} " +
                      f"{project['PRIOR_PROJECTID']:<15} {project['PRIOR_PROJECT_NAME']:<35}")

                # Print additional information
                status = "Active" if project['PROJECT_ACTIVE'] else "Inactive"
                print(f"    Created by: {project['CREATOR_NAME']} | Date: {project['DATE_CREATED']} | Status: {status}")
                print("-" * 110)

            print(f"Total projects with prior versions: {len(results)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        print(f"Error in get_projects_with_prior: {error}")
        return []


def get_projects_created_on_date(target_date: str = "2025-04-15") -> List[Dict[str, Any]]:
    """
    Retrieve all projects created on the specified date.

    Args:
        target_date: Date in format 'YYYY-MM-DD' to search for

    Returns:
        List of dictionaries containing project information
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to find projects created on target date
        # MariaDB DATE() function extracts the date part from a datetime
        query = """
        SELECT
            p.PROJECTID,
            p.PROJECT_NAME,
            p.CREATED_BY,
            DATE_FORMAT(p.DATE_CREATED, '%Y-%m-%d %H:%i:%s') AS DATE_CREATED,
            CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS CREATOR_NAME,
            p.PROJECT_ACTIVE
        FROM projects p
        JOIN employee_table e ON p.CREATED_BY = e.EMPID
        WHERE DATE(p.DATE_CREATED) = %s
        ORDER BY p.DATE_CREATED
        """

        cursor.execute(query, (target_date,))
        results = cursor.fetchall()

        # Print results
        if not results:
            print(f"No projects found created on {target_date}")
        else:
            print(f"\nProjects created on {target_date}:")
            print("-" * 100)
            print(f"{'PROJECT ID':<15} {'PROJECT NAME':<40} {'CREATED BY':<30} {'TIME CREATED':<20}")
            print("-" * 100)

            for project in results:
                print(f"{project['PROJECTID']:<15} {project['PROJECT_NAME']:<40} " +
                      f"{project['CREATOR_NAME']:<30} {project['DATE_CREATED']:<20}")

            print("-" * 100)
            print(f"Total projects created on {target_date}: {len(results)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        print(f"Error in get_projects_created_on_date: {error}")
        return []


def get_inactive_employees() -> List[Dict[str, Any]]:
    """
    Retrieve all employees where EMP_ACTIVE is not true
    (which includes both false and null values).

    Returns:
        List of dictionaries containing inactive employee information
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to find employees where EMP_ACTIVE is not true
        # This covers both FALSE and NULL values
        query = """
        SELECT
            e.EMPID,
            e.FIRST_NAME,
            e.LAST_NAME,
            e.EMAIL_ADDRESS,
            d.DPTID,
            d.DPT_NAME,
            CASE
                WHEN e.MGR_EMPID IS NOT NULL THEN CONCAT(m.FIRST_NAME, ' ', m.LAST_NAME)
                ELSE 'None'
            END AS MANAGER_NAME
        FROM employee_table e
        LEFT JOIN department d ON e.DPTID = d.DPTID
        LEFT JOIN employee_table m ON e.MGR_EMPID = m.EMPID
        WHERE e.EMP_ACTIVE IS NOT TRUE
        ORDER BY e.LAST_NAME, e.FIRST_NAME
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # Print results
        if not results:
            print("No inactive employees found")
        else:
            print("\nInactive Employees:")
            print("-" * 100)
            print(f"{'EMPLOYEE ID':<15} {'NAME':<30} {'EMAIL':<35} {'DEPARTMENT':<20}")
            print("-" * 100)

            for employee in results:
                full_name = f"{employee['FIRST_NAME']} {employee['LAST_NAME']}"
                print(f"{employee['EMPID']:<15} {full_name:<30} " +
                      f"{employee['EMAIL_ADDRESS'] or 'N/A':<35} {employee['DPT_NAME']:<20}")
                if employee['MANAGER_NAME'] != 'None':
                    print(f"    Manager: {employee['MANAGER_NAME']}")

            print("-" * 100)
            print(f"Total inactive employees: {len(results)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        print(f"Error in get_inactive_employees: {error}")
        return []


def get_department_active_count() -> Dict[str, int]:
    """
    Count departments by DPT_ACTIVE status.

    Returns:
        Dictionary with counts of active, inactive, and null status departments
    """
    counts = {
        'active': 0,
        'inactive': 0,
        'null': 0,
        'total': 0
    }

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
        cursor = conn.cursor(dictionary=True)

        # Query to count departments by DPT_ACTIVE status
        query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN DPT_ACTIVE = TRUE THEN 1 ELSE 0 END) AS active_count,
            SUM(CASE WHEN DPT_ACTIVE = FALSE THEN 1 ELSE 0 END) AS inactive_count,
            SUM(CASE WHEN DPT_ACTIVE IS NULL THEN 1 ELSE 0 END) AS null_count
        FROM department
        """

        cursor.execute(query)
        result = cursor.fetchone()

        counts['total'] = result['total'] or 0
        counts['active'] = result['active_count'] or 0
        counts['inactive'] = result['inactive_count'] or 0
        counts['null'] = result['null_count'] or 0

        # Print results
        print("Department Status Summary:")
        print("-" * 50)
        print(f"Total departments: {counts['total']}")
        print(f"Active departments (DPT_ACTIVE = TRUE): {counts['active']}")
        print(f"Inactive departments (DPT_ACTIVE = FALSE): {counts['inactive']}")
        print(f"Null status departments (DPT_ACTIVE = NULL): {counts['null']}")
        print("-" * 50)

        # Close cursor and connection
        cursor.close()
        conn.close()

        return counts

    except Exception as error:
        print(f"Error in get_department_active_count: {error}")
        return counts


def get_manual_time_entries() -> List[tuple[Any, Any, Any]]:
    """
    Retrieve time entries where MANUAL_ENTRY is set to true (1).

    Returns:
        List of tuples containing (TIMEID, EMPID, PROJECTID)
    """
    manual_entries = []

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

        # Query to get time entries where MANUAL_ENTRY is true (1)
        query = "SELECT TIMEID, EMPID, PROJECTID FROM time WHERE MANUAL_ENTRY = 1"
        cursor.execute(query)

        # Fetch all results
        manual_entries = cursor.fetchall()

        # Print results
        if not manual_entries:
            print("No manual time entries found.")
        else:
            print("Manual Time Entries:")
            print("-" * 40)
            print(f"{'TIMEID':<15} {'EMPID':<15} {'PROJECTID':<15}")
            print("-" * 40)

            for entry in manual_entries:
                print(f"{entry[0]:<15} {entry[1]:<15} {entry[2]:<15}")

            print("-" * 40)
            print(f"Total manual time entries: {len(manual_entries)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return manual_entries

    except Exception as error:
        print(f"Error in get_manual_time_entries: {error}")
        return []


def get_employee_time_summary() -> List[Dict[str, Any]]:
    """
    Retrieve employees with multiple time entries, along with entry count
    and total minutes.

    Returns:
        List of dictionaries containing employee time summary information
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to get employees with multiple time entries
        query = """
        SELECT
            t.EMPID,
            CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS EMPLOYEE_NAME,
            COUNT(t.TIMEID) AS ENTRY_COUNT,
            SUM(t.TOTAL_MINUTES) AS TOTAL_MINUTES,
            MIN(t.START_TIME) AS FIRST_ENTRY,
            MAX(t.START_TIME) AS LAST_ENTRY
        FROM time t
        JOIN employee_table e ON t.EMPID = e.EMPID
        GROUP BY t.EMPID
        HAVING COUNT(t.TIMEID) > 1
        ORDER BY COUNT(t.TIMEID) DESC, SUM(t.TOTAL_MINUTES) DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # For each employee, get details about their projects
        if results:
            for employee in results:
                project_query = """
                SELECT
                    p.PROJECTID,
                    p.PROJECT_NAME,
                    COUNT(t.TIMEID) AS ENTRY_COUNT,
                    SUM(t.TOTAL_MINUTES) AS PROJECT_MINUTES,
                    ROUND(SUM(t.TOTAL_MINUTES) / %s * 100, 2) AS PERCENTAGE
                FROM time t
                JOIN projects p ON t.PROJECTID = p.PROJECTID
                WHERE t.EMPID = %s
                GROUP BY t.PROJECTID
                ORDER BY SUM(t.TOTAL_MINUTES) DESC
                """

                cursor.execute(project_query, (employee['TOTAL_MINUTES'], employee['EMPID']))
                employee['projects'] = cursor.fetchall()

                # Format dates for better readability
                if employee['FIRST_ENTRY']:
                    employee['FIRST_ENTRY'] = employee['FIRST_ENTRY'].strftime("%Y-%m-%d %H:%M:%S")
                if employee['LAST_ENTRY']:
                    employee['LAST_ENTRY'] = employee['LAST_ENTRY'].strftime("%Y-%m-%d %H:%M:%S")

        # Print results
        if not results:
            print("No employees found with multiple time entries")
        else:
            print("Employees with Multiple Time Entries:")
            print("-" * 100)
            print(f"{'EMPLOYEE ID':<15} {'EMPLOYEE NAME':<30} {'ENTRIES':<10} {'TOTAL MINUTES':<15} {'HOURS':<10}")
            print("-" * 100)

            for employee in results:
                hours = round(employee['TOTAL_MINUTES'] / 60, 2) if employee['TOTAL_MINUTES'] else 0
                print(f"{employee['EMPID']:<15} {employee['EMPLOYEE_NAME']:<30} " +
                      f"{employee['ENTRY_COUNT']:<10} {employee['TOTAL_MINUTES']:<15} {hours:<10}")

                # Print date range
                print(f"    First entry: {employee['FIRST_ENTRY']} | Last entry: {employee['LAST_ENTRY']}")

                # Print project breakdown if available
                if employee.get('projects'):
                    print(f"    Project breakdown:")
                    for project in employee['projects']:
                        proj_hours = round(project['PROJECT_MINUTES'] / 60, 2) if project['PROJECT_MINUTES'] else 0
                        print(f"    - {project['PROJECT_NAME']:<40}: {project['ENTRY_COUNT']} entries, " +
                              f"{project['PROJECT_MINUTES']} mins ({proj_hours} hrs), {project['PERCENTAGE']}%")

                print("-" * 100)

            print(f"Total employees with multiple entries: {len(results)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        print(f"Error in get_employee_time_summary: {error}")
        return []


def get_project_time_summary() -> List[Dict[str, Any]]:
    """
    Retrieve all projects with aggregated time data.

    Returns:
        List of dictionaries containing project time summary information
    """
    results = []

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
        cursor = conn.cursor(dictionary=True)

        # Execute query to aggregate time by project
        query = """
        SELECT
            t.PROJECTID,
            p.PROJECT_NAME,
            COUNT(t.TIMEID) AS ENTRY_COUNT,
            SUM(t.TOTAL_MINUTES) AS TOTAL_MINUTES,
            ROUND(SUM(t.TOTAL_MINUTES) / 60, 2) AS TOTAL_HOURS,
            MIN(t.START_TIME) AS FIRST_ENTRY,
            MAX(t.START_TIME) AS LAST_ENTRY,
            COUNT(DISTINCT t.EMPID) AS EMPLOYEE_COUNT
        FROM time t
        JOIN projects p ON t.PROJECTID = p.PROJECTID
        GROUP BY t.PROJECTID
        ORDER BY SUM(t.TOTAL_MINUTES) DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # Format date fields for better readability
        if results:
            for project in results:
                if project['FIRST_ENTRY']:
                    project['FIRST_ENTRY'] = project['FIRST_ENTRY'].strftime("%Y-%m-%d %H:%M:%S")
                if project['LAST_ENTRY']:
                    project['LAST_ENTRY'] = project['LAST_ENTRY'].strftime("%Y-%m-%d %H:%M:%S")

        # Print results
        if not results:
            print("No time entries found in the database")
        else:
            print("Project Time Summary:")
            print("-" * 100)
            print(f"{'PROJECT ID':<15} {'PROJECT NAME':<40} {'ENTRIES':<10} {'TOTAL MINUTES':<15} {'HOURS':<10}")
            print("-" * 100)

            # Track total time across all projects
            total_minutes = 0
            total_entries = 0

            for project in results:
                total_minutes += project['TOTAL_MINUTES'] or 0
                total_entries += project['ENTRY_COUNT'] or 0

                print(f"{project['PROJECTID']:<15} {project['PROJECT_NAME']:<40} " +
                      f"{project['ENTRY_COUNT']:<10} {project['TOTAL_MINUTES']:<15} {project['TOTAL_HOURS']:<10}")

                # Print additional information
                print(f"    Date range: {project['FIRST_ENTRY']} to {project['LAST_ENTRY']}")
                print(f"    Employees involved: {project['EMPLOYEE_COUNT']}")
                print("-" * 100)

            # Print summary totals
            total_hours = round(total_minutes / 60, 2)
            print(f"Total time across all projects: {total_minutes} minutes ({total_hours} hours)")
            print(f"Total number of time entries: {total_entries}")
            print(f"Total number of projects with time entries: {len(results)}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        return results

    except Exception as error:
        print(f"Error in get_project_time_summary: {error}")
        return []







# *************************************
# *************************************

def run_all_tests():
    """
    Execute all database query functions
    """
    print("\n=== Running Force Reset Logins Query ===")
    get_force_reset_logins()

    print("\n=== Running Inactive Projects Query ===")
    get_inactive_projects()

    print("\n=== Running Projects with Prior Versions Query ===")
    get_projects_with_prior()

    print("\n=== Running Projects Created on April 15, 2025 Query ===")
    get_projects_created_on_date()

    print("\n=== Running Inactive Employees Query ===")
    get_inactive_employees()

    print("\n=== Running Department Status Count Query ===")
    get_department_active_count()

    print("\n=== Running Manual Time Entries Query ===")
    get_manual_time_entries()

    print("\n=== Running Employee Time Summary Query ===")
    get_employee_time_summary()

    print("\n=== Running Project Time Summary Query ===")
    get_project_time_summary()


if __name__ == "__main__":
    run_all_tests()

# **********************************************************************************************************************
# **********************************************************************************************************************
