# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Example: runs tests to:
#                   • count number of required password resets
#                   • retrieve inactive projects from the database
#                   • projects with a PRIOR_PROJECTID
#                   • projects with a 4/22/2025 start date
#                   • inactive employees
#                   • manual time entries
#                   • time summary by employee
#                   • project time summary
# UPDATES:
#           04.29.2025 - updated script to send results to database_report.txt in addition to showing in console.
#                           The script that simply shows results in console is still present, however it has been
#                           commented out of if __name__ == "__main__":
#                               To run console results only, change which function is called from if __name__ == "__main__":
#                      - Updated expected output values to align with updates made to Dummy Data

# Input:            none
# Output:           Expected results as follows:
#                   • Password Reset Required
#                          2096	Godfrey	Gaye

#                   • Inactive Projects (5 total)
#                         PROJECTID 	 PROJECT_NAME                   	 CREATED_BY
#                         P10005    	 Bustard                        	 E9010
#                         P10008    	 Brazilian tapir                	 E9023
#                         P10009    	 Dog, raccoon                   	 E9001
#                         P10014    	 Goose, andean                  	 E9021
#                         P10022    	 Squirrel, antelope ground      	 E9019

#                   •Projects with PRIOR_PROJECTID
#                         PROJECTID 	 PROJECT_NAME                   	 CREATED_BY 	 DATE_CREATED        	 PRIOR_PROJECTID
#                         P10015    	 Goose, greylag                 	 E9021      	 2025-04-15 00:00:00 	 P10014
#                         P10016    	 Greater adjutant stork         	 E9010      	 2025-04-15 00:00:00 	 P10005
#                         P10017    	 Javan gold-spotted mongoose    	 E9023      	 2025-04-15 00:00:00 	 P10008
#                         P10020    	 Dog                            	 E9001      	 2025-04-15 00:00:00 	 P10009
#                         P10021    	 Racoon                         	 E9001      	 2025-04-15 00:00:00 	 P10009
#                         P10025    	 Squirrel                       	 E9013      	 2025-04-15 00:00:00 	 P10022

#                   • Projects with 4/22/2025 start date
#                        PROJECTID 	 PROJECT_NAME                   	 CREATED_BY 	 DATE_CREATED        	 PRIOR_PROJECTID 	 PROJECT_ACTIVE
#                        P004      	 Client Onboarding Flow         	 E007       	 2025-04-22 14:30:00 	 None            	1

#                   • Inactive Employees (total 3)
#                         EMPID  	 FIRST_NAME 	 LAST_NAME    	 DPTID
#                         E9008  	 Aundrea    	 Abela        	 SVCS
#                         E9017  	 Kenny      	 Scardifeild  	 FIN
#                         E9020  	 Dane       	 Eynald       	 R&D

#                   • Active Department Status Count (active=1 vs. inactive=2; total count =10)
#                        Row Labels     Count of  DPT_ACTIVE
#                           0	            1
#                           1	            9
#                        Grand Total	    10

#                   • manual entries in time table = 30
#                        Manual Time Entries:
#                        ----------------------------------------
#                        TIMEID          EMPID           PROJECTID
#                        ----------------------------------------
#                        1               E001            P001
#                        2               E001            P001
#                        3               TEST01          P001
#                        4               E001            P002
#                        5               TEST01          P002
#                        6               E0009           P003
#                        7               E004            P003
#                        8               E0009           P001
#                        9               TEST01          P001
#                        10              E003            P001
#                        11              E003            P002
#                        12              E011            P001
#                        13              E012            P002
#                        14              E013            P003
#                        15              E014            P004
#                        16              E015            P001
#                        17              E016            P002
#                        19              E9003           P10003
#                        20              E9005           P10005
#                        22              E9005           P10005
#                        24              E9006           P10006
#                        27              E9007           P10009
#                        28              E9007           P10009
#                        29              E9011           P10010
#                        30              E9011           P10011
#                        32              E9014           P10014
#                        33              E9015           P10015
#                        35              E9017           P10017
#                        37              E9019           P10020
#                        38              E9021           P10021
#                        ----------------------------------------
#                        Total manual time entries: 30

#                   • Roll up for Multiple Time Entries: (total = 9)
#                        Row Labels	    Name	Count of  EMPID  	Sum of  TOTAL_MINUTES
#                         TEST01 	     Tess       	5	            360
#                         E9006  	     Godfrey    	4	            299
#                         E9007     	 Angelia    	3	            304
#                         E001   	     Casey      	3	            210
#                         E012      	 Tom        	3	            195
#                         E003      	 Yesac      	2	            165
#                         E9011     	 Gaby       	2	            160
#                         E0009     	 Liesl      	2	            150
#                        E9005      	 Othello    	2	            148

#                   • PROJECT_ID totals
#                        Row Labels	    Project Name	        Sum of  TOTAL_MINUTES
#                         P10014    	 Goose, andean                  	1539
#                        P10015      	 Goose, greylag                 	678
#                         P001      	 Time Tracker DB Testing        	660
#                         P002      	 Marketing Website Redesign     	375
#                         P10006    	 Boat-billed heron              	299
#                         P003      	 Internal Tooling Upgrade       	285
#                         P10009    	 Dog, raccoon                   	248
#                         P10005    	 Bustard                        	148
#                         P10018    	 Legaan, Monitor (unidentified) 	142
#                         P10021    	 Racoon                         	134
#                         P10001    	 Andean goose                   	129
#                         P10016    	 Greater adjutant stork         	126
#                         P004      	 Client Onboarding Flow         	120
#                         P10025    	 Squirrel                       	118
#                         P10011    	 Flamingo, greater              	98
#                         P10012    	 Frilled dragon                 	92
#                         P10020    	 Dog                            	91
#                         P10003    	 Argalis                        	74
#                         P10010    	 Dolphin, striped               	62
#                         P10017    	 Javan gold-spotted mongoose    	60
#                         P10007    	 Bottle-nose dolphin            	56
#                         P10024    	 Vulture, oriental white-backed 	45



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
import datetime

class CustomWriter:
    def __init__(self, file):
        self.file = file
        self.terminal = sys.stdout

    def write(self, message):
        self.file.write(message)
        self.terminal.write(message)

    def flush(self):
        self.file.flush()
        self.terminal.flush()

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


def get_projects_created_on_date(target_date: str = "2025-04-22") -> List[Dict[str, Any]]:
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


def save_results_to_txt():
    """
    Run all queries and save results to a single text file.
    """
    # Create a file to save all results
    with open('database_report.txt', 'w') as file:
        # Write a header for the report
        file.write("DATABASE QUERY RESULTS REPORT\n")
        file.write("============================\n\n")
        file.write(f"Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Redirect stdout to capture print output
        original_stdout = sys.stdout
        sys.stdout = CustomWriter(file)

        try:
            # Run each function
            file.write("\n=== Force Reset Logins ===\n")
            get_force_reset_logins()

            file.write("\n=== Inactive Projects ===\n")
            get_inactive_projects()

            file.write("\n=== Projects with Prior Versions ===\n")
            get_projects_with_prior()

            file.write("\n=== Projects Created on April 15, 2025 ===\n")
            get_projects_created_on_date()

            file.write("\n=== Inactive Employees ===\n")
            get_inactive_employees()

            file.write("\n=== Department Status Count ===\n")
            get_department_active_count()

            file.write("\n=== Manual Time Entries ===\n")
            get_manual_time_entries()

            file.write("\n=== Employee Time Summary ===\n")
            get_employee_time_summary()

            file.write("\n=== Project Time Summary ===\n")
            get_project_time_summary()

        finally:
            # Restore stdout
            sys.stdout = original_stdout

    print(f"All results have been saved to database_report.txt")

if __name__ == "__main__":   #use one or the other of the below statements; comment out the other
    # run_all_tests()
    save_results_to_txt()

# **********************************************************************************************************************
# **********************************************************************************************************************
