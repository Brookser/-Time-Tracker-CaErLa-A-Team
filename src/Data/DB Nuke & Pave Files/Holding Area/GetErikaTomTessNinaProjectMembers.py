# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      script that queries employees for all projects assigned to employees Test01 (Tess) and E011 (Nina)
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
Script to get all employees assigned to the projects identified in the previous query results.

Projects identified:
- P19241 (MarketingWebsite)
- P99006 (MarketingWebsite 2)
- P13724 (TestingID)
- P99005 (TestingID 2)
- P27260 (TestProj to Add employees)

This script will find ALL employees assigned to these projects, not just Test01 and E011.
"""

from src.Data.Database import Database


def get_all_employees_for_projects():
    """
    Get all employees assigned to the identified projects.

    Returns:
        dict: Dictionary with project IDs as keys and employee lists as values
    """

    # Project IDs from the previous query results
    target_projects = ['P19241', 'P99006', 'P13724', 'P99005', 'P27260']

    try:
        Database.connect()
        cursor = Database.get_cursor()

        # Query to get all employees assigned to these projects with detailed info
        placeholders = ','.join('?' for _ in target_projects)
        query = f"""
            SELECT 
                p.PROJECTID,
                p.PROJECT_NAME,
                p.CREATED_BY,
                CONCAT(creator.FIRST_NAME, ' ', creator.LAST_NAME) as CREATOR_NAME,
                p.PROJECT_ACTIVE,
                ep.EMPID as ASSIGNED_EMPLOYEE,
                CONCAT(assigned.FIRST_NAME, ' ', assigned.LAST_NAME) as EMPLOYEE_NAME,
                assigned.EMAIL_ADDRESS,
                assigned.DPTID,
                d.DPT_NAME,
                assigned.EMP_ROLE,
                assigned.EMP_ACTIVE
            FROM projects p
            INNER JOIN employee_projects ep ON p.PROJECTID = ep.PROJECT_ID
            INNER JOIN employee_table assigned ON ep.EMPID = assigned.EMPID
            INNER JOIN employee_table creator ON p.CREATED_BY = creator.EMPID
            LEFT JOIN department d ON assigned.DPTID = d.DPTID
            WHERE p.PROJECTID IN ({placeholders})
            ORDER BY p.PROJECTID, assigned.LAST_NAME, assigned.FIRST_NAME
        """

        cursor.execute(query, target_projects)
        results = cursor.fetchall()

        cursor.close()
        return results

    except Exception as e:
        print(f"Error executing query: {e}")
        return []


def organize_results_by_project(results):
    """
    Organize the query results by project.

    Args:
        results (list): List of tuples from the database query

    Returns:
        dict: Dictionary organized by project ID
    """
    projects = {}

    for row in results:
        (projectid, project_name, created_by, creator_name, project_active,
         empid, employee_name, email, dptid, dept_name, emp_role, emp_active) = row

        if projectid not in projects:
            projects[projectid] = {
                'project_name': project_name,
                'created_by': created_by,
                'creator_name': creator_name,
                'project_active': project_active,
                'employees': []
            }

        projects[projectid]['employees'].append({
            'empid': empid,
            'name': employee_name,
            'email': email,
            'department_id': dptid,
            'department_name': dept_name,
            'role': emp_role,
            'active': emp_active
        })

    return projects


def get_all_unique_employees(results):
    """
    Get a unique list of all employees across all projects.

    Args:
        results (list): List of tuples from the database query

    Returns:
        dict: Dictionary of unique employees with their details
    """
    unique_employees = {}

    for row in results:
        empid = row[5]  # ASSIGNED_EMPLOYEE

        if empid not in unique_employees:
            unique_employees[empid] = {
                'name': row[6],  # EMPLOYEE_NAME
                'email': row[7],  # EMAIL_ADDRESS
                'department_id': row[8],  # DPTID
                'department_name': row[9],  # DPT_NAME
                'role': row[10],  # EMP_ROLE
                'active': row[11],  # EMP_ACTIVE
                'projects': []
            }

        # Add project to employee's project list
        unique_employees[empid]['projects'].append({
            'project_id': row[0],
            'project_name': row[1]
        })

    return unique_employees


def format_results_by_project(projects):
    """
    Format results organized by project.

    Args:
        projects (dict): Dictionary of projects and their employees

    Returns:
        str: Formatted string representation
    """
    output = []
    output.append("ALL EMPLOYEES ASSIGNED TO IDENTIFIED PROJECTS")
    output.append("=" * 80)

    for projectid, project_info in projects.items():
        status = "Active" if project_info['project_active'] else "Inactive"
        output.append(f"""
PROJECT: {project_info['project_name']} (ID: {projectid})
Created by: {project_info['created_by']} ({project_info['creator_name']})
Status: {status}
Assigned Employees ({len(project_info['employees'])}):""")

        for emp in project_info['employees']:
            emp_status = "Active" if emp['active'] else "Inactive"
            dept_info = f" ({emp['department_name']})" if emp['department_name'] else ""
            output.append(f"  • {emp['empid']} - {emp['name']}")
            output.append(f"    Email: {emp['email']}")
            output.append(f"    Department: {emp['department_id']}{dept_info}")
            output.append(f"    Role: {emp['role']} | Status: {emp_status}")
            output.append("")

        output.append("-" * 60)

    return '\n'.join(output)


def format_results_by_employee(unique_employees):
    """
    Format results organized by employee.

    Args:
        unique_employees (dict): Dictionary of unique employees

    Returns:
        str: Formatted string representation
    """
    output = []
    output.append("\nALL UNIQUE EMPLOYEES (organized by employee)")
    output.append("=" * 80)

    # Sort employees by name for better readability
    sorted_employees = sorted(unique_employees.items(),
                              key=lambda x: x[1]['name'])

    for empid, emp_info in sorted_employees:
        emp_status = "Active" if emp_info['active'] else "Inactive"
        dept_info = f" ({emp_info['department_name']})" if emp_info['department_name'] else ""

        output.append(f"""
EMPLOYEE: {emp_info['name']} (ID: {empid})
Email: {emp_info['email']}
Department: {emp_info['department_id']}{dept_info}
Role: {emp_info['role']} | Status: {emp_status}
Assigned to {len(emp_info['projects'])} project(s):""")

        for project in emp_info['projects']:
            output.append(f"  • {project['project_id']} - {project['project_name']}")

        output.append("-" * 50)

    return '\n'.join(output)


def generate_summary_statistics(projects, unique_employees):
    """
    Generate summary statistics.

    Args:
        projects (dict): Dictionary of projects
        unique_employees (dict): Dictionary of unique employees

    Returns:
        str: Formatted summary statistics
    """
    total_assignments = sum(len(p['employees']) for p in projects.values())
    active_employees = sum(1 for emp in unique_employees.values() if emp['active'])
    active_projects = sum(1 for p in projects.values() if p['project_active'])

    # Count employees by role
    role_counts = {}
    for emp in unique_employees.values():
        role = emp['role']
        role_counts[role] = role_counts.get(role, 0) + 1

    # Count employees by department
    dept_counts = {}
    for emp in unique_employees.values():
        dept = emp['department_name'] or "No Department"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    output = []
    output.append("\nSUMMARY STATISTICS")
    output.append("=" * 50)
    output.append(f"Total projects analyzed: {len(projects)}")
    output.append(f"Active projects: {active_projects}")
    output.append(f"Total unique employees: {len(unique_employees)}")
    output.append(f"Active employees: {active_employees}")
    output.append(f"Total project assignments: {total_assignments}")
    output.append("")
    output.append("Employees by Role:")
    for role, count in sorted(role_counts.items()):
        output.append(f"  • {role}: {count}")
    output.append("")
    output.append("Employees by Department:")
    for dept, count in sorted(dept_counts.items()):
        output.append(f"  • {dept}: {count}")

    return '\n'.join(output)


def main():
    """
    Main function to execute the query and display results.
    """
    print("Getting all employees assigned to the identified projects...")
    print("Target Projects: P19241, P99006, P13724, P99005, P27260")
    print()

    # Execute the query
    results = get_all_employees_for_projects()

    if not results:
        print("No employees found for the specified projects.")
        return

    # Organize results
    projects = organize_results_by_project(results)
    unique_employees = get_all_unique_employees(results)

    # Display results organized by project
    print(format_results_by_project(projects))

    # Display results organized by employee
    print(format_results_by_employee(unique_employees))

    # Display summary statistics
    print(generate_summary_statistics(projects, unique_employees))


def get_employees_using_existing_methods():
    """
    Alternative approach using existing Database class methods.

    Returns:
        dict: Dictionary of employees by project
    """
    target_projects = ['P19241', 'P99006', 'P13724', 'P99005', 'P27260']

    employees_by_project = {}

    try:
        for project_id in target_projects:
            employees = Database.get_employees_assigned_to_project(project_id)
            if employees:
                employees_by_project[project_id] = employees

    except Exception as e:
        print(f"Error using existing methods: {e}")

    return employees_by_project


if __name__ == "__main__":
    main()

    # Also demonstrate the alternative approach
    print("\n" + "=" * 80)
    print("ALTERNATIVE APPROACH (using existing Database methods)")
    print("=" * 80)

    alt_results = get_employees_using_existing_methods()
    if alt_results:
        for project_id, employees in alt_results.items():
            print(f"\nProject {project_id}:")
            for empid in employees:
                print(f"  - {empid}")
    else:
        print("No results from alternative method.")

# **********************************************************************************************************************
# **********************************************************************************************************************
