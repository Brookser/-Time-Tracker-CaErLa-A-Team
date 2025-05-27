# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      script that adds employees and time entries to projects owned
#                       by Erika and Tim to more accurately showcase program features
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
Script to:
1. Assign 5-15 individual employees to the identified projects
2. Generate time entries for newly assigned employees from 5/20/2025 through 5/26/2025

Projects to assign to:
- P19241 (MarketingWebsite) - Inactive
- P99006 (MarketingWebsite 2) - Active
- P13724 (TestingID) - Inactive
- P99005 (TestingID 2) - Active
- P27260 (TestProj to Add employees) - Active
"""

import random
from datetime import datetime, timedelta
from src.Data.Database import Database
import uuid

# Available individual employees from the provided list
AVAILABLE_EMPLOYEES = [
    'E001', 'E009', 'E011', 'E013', 'E015', 'E9001', 'E9003', 'E9004',
    'E9005', 'E9008', 'E9010', 'E9013', 'E9015', 'E9016', 'E9017',
    'E9019', 'E9021', 'E9022', 'E9023', 'E9024', 'TEST01'
]

# Target projects for assignment
TARGET_PROJECTS = {
    'P19241': {'name': 'MarketingWebsite', 'active': False, 'creator': 'E004'},
    'P99006': {'name': 'MarketingWebsite 2', 'active': True, 'creator': 'E004'},
    'P13724': {'name': 'TestingID', 'active': False, 'creator': 'E012'},
    'P99005': {'name': 'TestingID 2', 'active': True, 'creator': 'E012'},
    'P27260': {'name': 'TestProj to Add employees', 'active': True, 'creator': 'E012'}
}

# Employees already assigned to these projects (updated with previous assignments)
ALREADY_ASSIGNED = {
    'P19241': ['E004', 'E015', 'E016', 'E001', 'E9003', 'E012', 'E003', 'TEST01', 'E9013', 'E9021'],
    'P99006': ['E004', 'E015', 'E016', 'E001', 'E9003', 'E012', 'E003', 'TEST01', 'E009', 'E9010', 'E9015', 'E9024'],
    'P13724': ['E012', 'TEST01', 'E9013', 'E9023'],
    'P99005': ['E012', 'TEST01', 'E9001', 'E011', 'E9010', 'E9017'],
    'P27260': ['E9013', 'E013', 'E012', 'E011', 'E9010', 'E9022', 'E9023', 'E9024']
}

# Work notes templates
WORK_NOTES_TEMPLATES = {
    'MarketingWebsite': [
        "Updated website homepage layout",
        "Implemented responsive design changes",
        "Optimized images for web performance",
        "Testing cross-browser compatibility",
        "Updated content management system",
        "Fixed navigation menu issues",
        "Reviewed SEO optimization",
        "Updated marketing copy",
        "Testing mobile responsiveness",
        "Implemented analytics tracking"
    ],
    'MarketingWebsite 2': [
        "Migrated content to new platform",
        "Testing updated UI components",
        "Implemented new feature requests",
        "Updated branding elements",
        "Optimized conversion funnels",
        "Testing A/B variations",
        "Updated landing page content",
        "Implemented security updates",
        "Testing payment integration",
        "Updated email templates"
    ],
    'TestingID': [
        "Conducted unit testing",
        "Performed integration testing",
        "Updated test documentation",
        "Fixed failing test cases",
        "Implemented automated tests",
        "Testing edge cases",
        "Updated testing framework",
        "Performed regression testing",
        "Testing API endpoints",
        "Updated test data sets"
    ],
    'TestingID 2': [
        "Enhanced test coverage",
        "Implemented new test scenarios",
        "Updated testing protocols",
        "Testing performance metrics",
        "Automated test reporting",
        "Updated test environments",
        "Testing user workflows",
        "Implemented stress testing",
        "Testing data validation",
        "Updated test automation"
    ],
    'TestProj to Add employees': [
        "Onboarding new team members",
        "Updated project documentation",
        "Conducted team training sessions",
        "Implemented role assignments",
        "Updated access permissions",
        "Conducted skills assessment",
        "Organized team meetings",
        "Updated project timelines",
        "Implemented resource allocation",
        "Conducted performance reviews"
    ]
}


def select_employees_for_assignment(num_to_assign=None):
    """Select employees, avoiding those already heavily assigned."""
    if num_to_assign is None:
        num_to_assign = random.randint(8, 12)  # Slightly smaller range for better management

    # Count current assignments for each available employee
    assignment_counts = {}
    for emp in AVAILABLE_EMPLOYEES:
        count = 0
        for project_assignments in ALREADY_ASSIGNED.values():
            if emp in project_assignments:
                count += 1
        assignment_counts[emp] = count

    # Sort by assignment count and select primarily from less assigned employees
    sorted_employees = sorted(AVAILABLE_EMPLOYEES, key=lambda x: assignment_counts[x])

    # Select with bias toward less assigned employees
    selected = []
    low_assigned = [emp for emp in sorted_employees if assignment_counts[emp] <= 1]

    if len(low_assigned) >= num_to_assign:
        selected = random.sample(low_assigned, num_to_assign)
    else:
        selected.extend(low_assigned)
        remaining_needed = num_to_assign - len(selected)
        remaining_employees = [emp for emp in sorted_employees if emp not in selected]
        selected.extend(random.sample(remaining_employees, min(remaining_needed, len(remaining_employees))))

    return selected[:num_to_assign]


def assign_employees_to_projects(selected_employees):
    """Assign selected employees to projects, avoiding duplicates."""
    assignments = {project_id: [] for project_id in TARGET_PROJECTS.keys()}

    for emp in selected_employees:
        # Each employee gets assigned to 1-2 projects (reduced from 1-3)
        num_projects = random.choices([1, 2], weights=[0.6, 0.4])[0]

        # Get available projects for this employee (not already assigned)
        available_projects = []
        for project_id in TARGET_PROJECTS.keys():
            if emp not in ALREADY_ASSIGNED[project_id]:
                available_projects.append(project_id)

        if not available_projects:
            continue  # Skip if employee is already assigned to all projects

        # Weight active projects higher
        project_weights = []
        for project_id in available_projects:
            if TARGET_PROJECTS[project_id]['active']:
                project_weights.append(0.8)  # Higher weight for active projects
            else:
                project_weights.append(0.2)  # Lower weight for inactive projects

        # Select projects ensuring no duplicates
        num_to_select = min(num_projects, len(available_projects))
        if num_to_select > 0:
            selected_projects = random.choices(available_projects, weights=project_weights, k=num_to_select)

            # Remove duplicates while preserving some randomness
            unique_projects = list(set(selected_projects))
            for project_id in unique_projects:
                assignments[project_id].append(emp)

    return assignments


def generate_time_id():
    """Generate a unique time ID in the format used by the system."""
    return f"t-{uuid.uuid4().hex[:8]}"


def generate_work_notes(project_name):
    """Generate realistic work notes for a project."""
    base_notes = WORK_NOTES_TEMPLATES.get(project_name, [
        "Working on project tasks",
        "Implementing new features",
        "Testing functionality",
        "Code review and debugging",
        "Documentation updates"
    ])

    # 15% chance of empty notes
    if random.random() < 0.15:
        return ""

    # 75% chance of using template, 25% chance of simple notes
    if random.random() < 0.75:
        return random.choice(base_notes)
    else:
        simple_notes = ["testing", "working on updates", "bug fixes", "feature implementation", "code review"]
        return random.choice(simple_notes)


def generate_time_entries_for_date_range(assignments, start_date=None, end_date=None):
    """Generate time entries for assigned employees for specified date range."""
    if start_date is None:
        start_date = datetime(2025, 5, 20)
    if end_date is None:
        end_date = datetime(2025, 5, 26)

    time_entries = []

    # Create employee-project pairs
    employee_project_pairs = []
    for project_id, employees in assignments.items():
        for emp_id in employees:
            employee_project_pairs.append((emp_id, project_id))

    # Generate entries for each day
    current_date = start_date
    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5

        for emp_id, project_id in employee_project_pairs:
            # Work probability: 85% weekdays, 15% weekends
            work_probability = 0.15 if is_weekend else 0.85

            if random.random() < work_probability:
                # 1-2 entries per day (reduced from 1-3)
                num_entries = random.choices([1, 2], weights=[0.7, 0.3])[0]

                for _ in range(num_entries):
                    entry = generate_single_time_entry(emp_id, project_id, current_date)
                    if entry:
                        time_entries.append(entry)

        current_date += timedelta(days=1)

    return time_entries


def generate_single_time_entry(emp_id, project_id, date):
    """Generate a single time entry for an employee on a specific date."""
    # Normal work hours bias
    if random.random() < 0.88:  # 88% during normal hours
        start_hour = random.randint(8, 17)
    else:  # 12% outside normal hours
        start_hour = random.choice([7, 18, 19, 20])

    start_minute = random.choice([0, 15, 30, 45])
    start_time = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)

    # Duration distribution (biased toward longer, meaningful work sessions)
    duration_weights = {
        range(5, 10): 0.08,  # 8% very short (5-9 min)
        range(10, 30): 0.22,  # 22% short (10-29 min)
        range(30, 60): 0.45,  # 45% medium (30-59 min)
        range(60, 91): 0.25  # 25% long (60-90 min)
    }

    duration_range = random.choices(
        list(duration_weights.keys()),
        weights=list(duration_weights.values())
    )[0]

    duration_minutes = random.choice(list(duration_range))
    stop_time = start_time + timedelta(minutes=duration_minutes)

    # Generate notes
    project_name = TARGET_PROJECTS[project_id]['name']
    notes = generate_work_notes(project_name)

    return {
        'timeid': generate_time_id(),
        'empid': emp_id,
        'project_id': project_id,
        'start_time': start_time,
        'stop_time': stop_time,
        'notes': notes,
        'manual_entry': 0,
        'total_minutes': duration_minutes
    }


def insert_time_entries_new_method(time_entries):
    """
    Insert time entries using the new Database method.

    Args:
        time_entries (list): List of time entry dictionaries

    Returns:
        int: Number of entries inserted successfully
    """
    success_count = 0

    for entry in time_entries:
        try:
            result = Database.add_time_entry_with_timeid(
                timeid=entry['timeid'],
                empid=entry['empid'],
                projectid=entry['project_id'],
                start_time=entry['start_time'],
                stop_time=entry['stop_time'],
                notes=entry['notes'],
                manual_entry=entry['manual_entry']
            )

            if result:
                success_count += 1
                print(f"✓ Added time entry {entry['timeid']} for {entry['empid']} on {entry['start_time'].date()}")

        except Exception as e:
            print(f"✗ Failed to add time entry {entry['timeid']}: {e}")
            continue

    return success_count


def insert_employee_project_assignments(assignments):
    """Insert employee-project assignments, avoiding duplicates."""
    count = 0
    for project_id, employees in assignments.items():
        for emp_id in employees:
            try:
                Database.add_employee_to_project(project_id, emp_id)
                print(f"✓ Assigned {emp_id} to project {project_id}")
                count += 1
            except Exception as e:
                if "Duplicate entry" in str(e):
                    print(f"⚠ {emp_id} already assigned to {project_id} - skipping")
                else:
                    print(f"✗ Failed to assign {emp_id} to {project_id}: {e}")
    return count


def display_assignment_summary(assignments):
    """Display a summary of planned assignments."""
    print("\n" + "=" * 80)
    print("PLANNED EMPLOYEE-PROJECT ASSIGNMENTS")
    print("=" * 80)

    total_assignments = 0
    for project_id, employees in assignments.items():
        if employees:
            project_info = TARGET_PROJECTS[project_id]
            status = "Active" if project_info['active'] else "Inactive"
            print(f"\nProject: {project_info['name']} (ID: {project_id}) - {status}")
            print(f"Created by: {project_info['creator']}")
            print(f"New assignments ({len(employees)}):")
            for emp in employees:
                print(f"  • {emp}")
            total_assignments += len(employees)

    print(f"\nTotal new assignments: {total_assignments}")


def display_time_entry_summary(time_entries):
    """Display a summary of generated time entries."""
    print("\n" + "=" * 80)
    print("GENERATED TIME ENTRIES SUMMARY")
    print("=" * 80)

    entries_by_employee = {}
    total_minutes = 0

    for entry in time_entries:
        emp_id = entry['empid']
        if emp_id not in entries_by_employee:
            entries_by_employee[emp_id] = []
        entries_by_employee[emp_id].append(entry)
        total_minutes += entry['total_minutes']

    print(f"Total time entries generated: {len(time_entries)}")
    print(f"Total time logged: {total_minutes} minutes ({total_minutes / 60:.1f} hours)")
    print(f"Employees with entries: {len(entries_by_employee)}")
    print(f"Date range: 2025-05-20 to 2025-05-26")

    print(f"\nBreakdown by employee:")
    for emp_id in sorted(entries_by_employee.keys()):
        entries = entries_by_employee[emp_id]
        emp_total_minutes = sum(entry['total_minutes'] for entry in entries)
        projects = set(entry['project_id'] for entry in entries)
        print(f"  {emp_id}: {len(entries)} entries, {emp_total_minutes} min ({emp_total_minutes / 60:.1f}h), {len(projects)} projects")


def main():
    """Main execution function."""
    print("EMPLOYEE ASSIGNMENT AND TIME ENTRY GENERATION - WEEK 2 (5/20-5/26)")
    print("=" * 75)

    # Step 1: Select employees
    print("\n1. Selecting NEW employees for assignment (avoiding those already assigned)...")
    selected_employees = select_employees_for_assignment(random.randint(5, 15))  # Random 5-15 as requested
    print(f"Selected {len(selected_employees)} employees: {', '.join(selected_employees)}")

    # Step 2: Assign to projects
    print("\n2. Assigning employees to projects...")
    assignments = assign_employees_to_projects(selected_employees)
    display_assignment_summary(assignments)

    # Step 3: Generate time entries
    print("\n3. Generating time entries for date range 5/20/2025 - 5/26/2025...")
    time_entries = generate_time_entries_for_date_range(assignments,
                                                        datetime(2025, 5, 20),
                                                        datetime(2025, 5, 26))
    display_time_entry_summary(time_entries)

    # Step 4: Confirm before inserting
    total_assignments = sum(len(employees) for employees in assignments.values())
    print(f"\n4. Ready to insert into database:")
    print(f"   - {total_assignments} new project assignments")
    print(f"   - {len(time_entries)} time entries")

    confirm = input("\nProceed with database insertion? (y/N): ").strip().lower()

    if confirm == 'y':
        print("\n5. Inserting data into database...")

        # Insert project assignments
        print("\nInserting project assignments...")
        assignments_inserted = insert_employee_project_assignments(assignments)

        # Insert time entries using new method
        print(f"\nInserting time entries using new Database method...")
        entries_inserted = insert_time_entries_new_method(time_entries)

        print(f"\n✅ DATABASE INSERTION COMPLETE")
        print(f"   - Project assignments inserted: {assignments_inserted}")
        print(f"   - Time entries inserted: {entries_inserted}")
    else:
        print("\n❌ Database insertion cancelled.")


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
