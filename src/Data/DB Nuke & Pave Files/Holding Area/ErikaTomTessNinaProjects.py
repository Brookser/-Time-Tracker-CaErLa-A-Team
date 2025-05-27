# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      script that queries for all projects assigned to employees Test01 (Tess) and E011 (Nina)
#                   that were created by users E004 (Erika) or E012 (Tom)
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter
#
# Change Log:       - 05.26.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

# !/usr/bin/env python3
"""
Script to find all projects that employees Test01 and E011 are assigned to
that were created by users E004 or E012.

This script uses the Database class methods to query the time_tracker database.
"""

from src.Data.Database import Database


def get_projects_for_employees_by_creators():
    """
    Returns all projects that EMPID Test01 and E011 are assigned to
    that belong to users with EMPID E004 or E012.

    Returns:
        list: List of tuples containing project information
    """

    # Target employees we're searching for
    target_employees = ['Test01', 'E011']

    # Target project creators
    target_creators = ['E004', 'E012']

    try:
        # Connect to the database
        Database.connect()
        cursor = Database.get_cursor()

        # SQL query to find projects assigned to target employees that were created by target creators
        query = """
            SELECT DISTINCT 
                p.PROJECTID,
                p.PROJECT_NAME,
                p.CREATED_BY,
                CONCAT(creator.FIRST_NAME, ' ', creator.LAST_NAME) as CREATOR_NAME,
                ep.EMPID as ASSIGNED_EMPLOYEE,
                CONCAT(assigned.FIRST_NAME, ' ', assigned.LAST_NAME) as EMPLOYEE_NAME,
                p.DATE_CREATED,
                p.PROJECT_ACTIVE
            FROM projects p
            INNER JOIN employee_projects ep ON p.PROJECTID = ep.PROJECT_ID
            INNER JOIN employee_table creator ON p.CREATED_BY = creator.EMPID
            INNER JOIN employee_table assigned ON ep.EMPID = assigned.EMPID
            WHERE ep.EMPID IN (?, ?)
            AND p.CREATED_BY IN (?, ?)
            ORDER BY p.PROJECT_NAME, ep.EMPID
        """

        # Execute the query
        cursor.execute(query, (*target_employees, *target_creators))
        results = cursor.fetchall()

        cursor.close()
        return results

    except Exception as e:
        print(f"Error executing query: {e}")
        return []


def format_results(results):
    """
    Format the query results for display.

    Args:
        results (list): List of tuples from the database query

    Returns:
        str: Formatted string representation of the results
    """
    if not results:
        return "No projects found matching the criteria."

    output = []
    output.append("Projects assigned to Test01 and E011 created by E004 or E012:")
    output.append("=" * 70)

    for row in results:
        projectid, project_name, created_by, creator_name, assigned_empid, employee_name, date_created, active = row

        status = "Active" if active else "Inactive"
        output.append(f"""
Project ID: {projectid}
Project Name: {project_name}
Created By: {created_by} ({creator_name})
Assigned To: {assigned_empid} ({employee_name})
Date Created: {date_created}
Status: {status}
{'-' * 50}""")

    return '\n'.join(output)


def main():
    """
    Main function to execute the query and display results.
    """
    print("Querying projects for employees Test01 and E011...")
    print("Looking for projects created by E004 or E012...")
    print()

    # Execute the query
    results = get_projects_for_employees_by_creators()

    # Format and display results
    formatted_output = format_results(results)
    print(formatted_output)

    # Additional summary information
    if results:
        unique_projects = set(row[0] for row in results)
        unique_employees = set(row[4] for row in results)
        unique_creators = set(row[2] for row in results)

        print(f"\nSummary:")
        print(f"Total project assignments found: {len(results)}")
        print(f"Unique projects: {len(unique_projects)}")
        print(f"Employees involved: {', '.join(sorted(unique_employees))}")
        print(f"Project creators involved: {', '.join(sorted(unique_creators))}")


def get_projects_summary():
    """
    Alternative method using existing Database class methods where possible.

    Returns:
        dict: Dictionary containing project assignments
    """
    try:
        results = {}
        target_employees = ['Test01', 'E011']
        target_creators = ['E004', 'E012']

        # For each target employee, get their projects and filter by creator
        for empid in target_employees:
            employee_projects = Database.get_projects_by_user(empid)

            # Filter projects created by target creators
            filtered_projects = []
            for project_id, project_name in employee_projects:
                creator = Database.get_project_created_by(project_id)
                if creator in target_creators:
                    filtered_projects.append({
                        'project_id': project_id,
                        'project_name': project_name,
                        'created_by': creator
                    })

            if filtered_projects:
                results[empid] = filtered_projects

        return results

    except Exception as e:
        print(f"Error in alternative method: {e}")
        return {}


if __name__ == "__main__":
    main()

    # Also demonstrate the alternative approach using existing methods
    print("\n" + "=" * 70)
    print("Alternative approach using existing Database methods:")
    print("=" * 70)

    summary = get_projects_summary()
    if summary:
        for empid, projects in summary.items():
            print(f"\nEmployee {empid}:")
            for project in projects:
                print(f"  - {project['project_name']} (ID: {project['project_id']}, Created by: {project['created_by']})")
    else:
        print("No matching projects found using alternative method.")

# **********************************************************************************************************************
# **********************************************************************************************************************
