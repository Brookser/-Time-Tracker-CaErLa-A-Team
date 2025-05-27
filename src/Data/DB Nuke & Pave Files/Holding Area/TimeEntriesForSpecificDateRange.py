# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      script that finds time entries for 05/20/2025-06/02/2025
#
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
Script to query all time entries between 05/20/2025 and 06/02/2025.
Returns results in
    • a clean grid/table format sorted by employee from oldest to newest, and
    • a clean grid/table format sorted from oldest to newest
"""

from src.Data.Database import Database
from datetime import datetime


def get_time_entries_date_range(start_date, end_date):
    """
    Get all time entries between specified dates with employee and project names.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        list: List of tuples containing time entry information
    """
    try:
        Database.connect()
        cursor = Database.get_cursor()

        query = '''
            SELECT 
                t.TIMEID,
                t.EMPID,
                CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS EMPLOYEE_NAME,
                t.PROJECTID,
                p.PROJECT_NAME,
                t.START_TIME,
                t.STOP_TIME,
                t.TOTAL_MINUTES,
                t.NOTES,
                t.MANUAL_ENTRY,
                t.FLAGGED_FOR_REVIEW
            FROM time t
            INNER JOIN employee_table e ON t.EMPID = e.EMPID
            INNER JOIN projects p ON t.PROJECTID = p.PROJECTID
            WHERE t.START_TIME >= ? AND t.START_TIME <= ?
            ORDER BY t.EMPID ASC, t.START_TIME ASC
        '''

        # Format dates for SQL query
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"

        cursor.execute(query, (start_datetime, end_datetime))
        results = cursor.fetchall()

        cursor.close()
        return results

    except Exception as e:
        print(f"Error executing query: {e}")
        return []


def format_table_row(values, widths):
    """
    Format a single row for the table with proper column widths.

    Args:
        values (list): List of values for the row
        widths (list): List of column widths

    Returns:
        str: Formatted row string
    """
    formatted_values = []
    for i, value in enumerate(values):
        str_value = str(value) if value is not None else ""
        # Truncate if too long
        if len(str_value) > widths[i]:
            str_value = str_value[:widths[i] - 3] + "..."
        formatted_values.append(str_value.ljust(widths[i]))

    return "| " + " | ".join(formatted_values) + " |"


def create_table_separator(widths):
    """
    Create a separator line for the table.

    Args:
        widths (list): List of column widths

    Returns:
        str: Separator line
    """
    return "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"


def display_time_entries_table(time_entries, start_date, end_date):
    """
    Display time entries in a clean table format sorted by EMPID then start time.

    Args:
        time_entries (list): List of time entry tuples
        start_date (str): Start date for the query
        end_date (str): End date for the query
    """
    if not time_entries:
        print(f"No time entries found between {start_date} and {end_date}.")
        return

    print(f"\nTIME ENTRIES: {start_date} to {end_date}")
    print(f"Total entries: {len(time_entries)} | Sorted: By Employee ID, then Oldest to Newest")
    print("=" * 120)

    # Define column headers and widths
    headers = [
        "Time ID", "Emp ID", "Employee Name", "Project ID", "Project Name",
        "Start Date", "Start Time", "Duration", "Notes", "Type"
    ]

    # Column widths (adjust as needed)
    widths = [12, 8, 16, 10, 20, 10, 8, 8, 25, 6]

    # Print table header
    separator = create_table_separator(widths)
    print(separator)
    print(format_table_row(headers, widths))
    print(separator)

    # Print each row
    for entry in time_entries:
        (timeid, empid, employee_name, projectid, project_name,
         start_time, stop_time, total_minutes, notes, manual_entry, flagged) = entry

        # Format data for display
        start_date_str = start_time.strftime('%m/%d/%Y') if start_time else ""
        start_time_str = start_time.strftime('%H:%M') if start_time else ""
        duration_str = f"{total_minutes}m" if total_minutes else "0m"
        notes_str = notes.replace('\n', ' ').replace('\r', ' ') if notes else ""
        entry_type = "Manual" if manual_entry == 1 else "Timer"

        row_data = [
            timeid, empid, employee_name, projectid, project_name,
            start_date_str, start_time_str, duration_str, notes_str, entry_type
        ]

        print(format_table_row(row_data, widths))

    print(separator)


def display_time_entries_chronological_table(time_entries, start_date, end_date):
    """
    Display time entries in chronological order (sorted by start time only).

    Args:
        time_entries (list): List of time entry tuples
        start_date (str): Start date for the query
        end_date (str): End date for the query
    """
    if not time_entries:
        print(f"No time entries found between {start_date} and {end_date}.")
        return

    # Sort entries chronologically by start time
    chronological_entries = sorted(time_entries, key=lambda x: x[5])  # x[5] is START_TIME

    print(f"\nTIME ENTRIES: {start_date} to {end_date} (CHRONOLOGICAL ORDER)")
    print(f"Total entries: {len(chronological_entries)} | Sorted: Oldest to Newest (All Employees)")
    print("=" * 120)

    # Define column headers and widths
    headers = [
        "Time ID", "Emp ID", "Employee Name", "Project ID", "Project Name",
        "Start Date", "Start Time", "Duration", "Notes", "Type"
    ]

    # Column widths (adjust as needed)
    widths = [12, 8, 16, 10, 20, 10, 8, 8, 25, 6]

    # Print table header
    separator = create_table_separator(widths)
    print(separator)
    print(format_table_row(headers, widths))
    print(separator)

    # Print each row
    for entry in chronological_entries:
        (timeid, empid, employee_name, projectid, project_name,
         start_time, stop_time, total_minutes, notes, manual_entry, flagged) = entry

        # Format data for display
        start_date_str = start_time.strftime('%m/%d/%Y') if start_time else ""
        start_time_str = start_time.strftime('%H:%M') if start_time else ""
        duration_str = f"{total_minutes}m" if total_minutes else "0m"
        notes_str = notes.replace('\n', ' ').replace('\r', ' ') if notes else ""
        entry_type = "Manual" if manual_entry == 1 else "Timer"

        row_data = [
            timeid, empid, employee_name, projectid, project_name,
            start_date_str, start_time_str, duration_str, notes_str, entry_type
        ]

        print(format_table_row(row_data, widths))

    print(separator)


def display_summary_table(time_entries):
    """
    Display summary statistics in a table format.

    Args:
        time_entries (list): List of time entry tuples
    """
    if not time_entries:
        return

    # Calculate statistics
    employees = set()
    projects = set()
    total_minutes = 0
    manual_entries = 0
    flagged_entries = 0
    dates = set()

    for entry in time_entries:
        (timeid, empid, employee_name, projectid, project_name,
         start_time, stop_time, minutes, notes, manual_entry, flagged) = entry

        employees.add(empid)
        projects.add(projectid)
        total_minutes += minutes if minutes else 0

        if manual_entry == 1:
            manual_entries += 1
        if flagged == 1:
            flagged_entries += 1
        if start_time:
            dates.add(start_time.date())

    timer_entries = len(time_entries) - manual_entries
    total_hours = total_minutes / 60.0
    avg_minutes = total_minutes / len(time_entries) if time_entries else 0

    print(f"\nSUMMARY STATISTICS")
    print("=" * 60)

    # Summary in table format
    summary_data = [
        ["Total Entries", len(time_entries)],
        ["Unique Employees", len(employees)],
        ["Unique Projects", len(projects)],
        ["Date Range", f"{len(dates)} days"],
        ["Total Time", f"{total_minutes} minutes ({total_hours:.1f} hours)"],
        ["Average Entry", f"{avg_minutes:.1f} minutes"],
        ["Timer Entries", timer_entries],
        ["Manual Entries", manual_entries],
        ["Flagged Entries", flagged_entries]
    ]

    # Print summary table
    summary_widths = [20, 25]
    summary_separator = create_table_separator(summary_widths)

    print(summary_separator)
    print(format_table_row(["Metric", "Value"], summary_widths))
    print(summary_separator)

    for metric, value in summary_data:
        print(format_table_row([metric, str(value)], summary_widths))

    print(summary_separator)


def display_employee_breakdown(time_entries):
    """
    Display a breakdown by employee in table format.

    Args:
        time_entries (list): List of time entry tuples
    """
    if not time_entries:
        return

    # Group by employee
    employee_stats = {}

    for entry in time_entries:
        (timeid, empid, employee_name, projectid, project_name,
         start_time, stop_time, minutes, notes, manual_entry, flagged) = entry

        if empid not in employee_stats:
            employee_stats[empid] = {
                'name': employee_name,
                'entries': 0,
                'minutes': 0,
                'projects': set()
            }

        employee_stats[empid]['entries'] += 1
        employee_stats[empid]['minutes'] += minutes if minutes else 0
        employee_stats[empid]['projects'].add(projectid)

    print(f"\nBREAKDOWN BY EMPLOYEE")
    print("=" * 80)

    # Employee breakdown table
    emp_headers = ["Emp ID", "Employee Name", "Entries", "Total Hours", "Projects"]
    emp_widths = [8, 18, 8, 12, 10]

    emp_separator = create_table_separator(emp_widths)
    print(emp_separator)
    print(format_table_row(emp_headers, emp_widths))
    print(emp_separator)

    # Sort by EMPID and then by total hours (descending) for consistent display
    sorted_employees = sorted(employee_stats.items(),
                              key=lambda x: (x[0], -x[1]['minutes']))

    for empid, stats in sorted_employees:
        hours = stats['minutes'] / 60.0
        row_data = [
            empid,
            stats['name'],
            str(stats['entries']),
            f"{hours:.1f}h",
            str(len(stats['projects']))
        ]
        print(format_table_row(row_data, emp_widths))

    print(emp_separator)


def display_project_breakdown(time_entries):
    """
    Display a breakdown by project in table format.

    Args:
        time_entries (list): List of time entry tuples
    """
    if not time_entries:
        return

    # Group by project
    project_stats = {}

    for entry in time_entries:
        (timeid, empid, employee_name, projectid, project_name,
         start_time, stop_time, minutes, notes, manual_entry, flagged) = entry

        if projectid not in project_stats:
            project_stats[projectid] = {
                'name': project_name,
                'entries': 0,
                'minutes': 0,
                'employees': set()
            }

        project_stats[projectid]['entries'] += 1
        project_stats[projectid]['minutes'] += minutes if minutes else 0
        project_stats[projectid]['employees'].add(empid)

    print(f"\nBREAKDOWN BY PROJECT")
    print("=" * 80)

    # Project breakdown table
    proj_headers = ["Project ID", "Project Name", "Entries", "Total Hours", "Employees"]
    proj_widths = [12, 22, 8, 12, 10]

    proj_separator = create_table_separator(proj_widths)
    print(proj_separator)
    print(format_table_row(proj_headers, proj_widths))
    print(proj_separator)

    # Sort by total hours (descending)
    sorted_projects = sorted(project_stats.items(),
                             key=lambda x: x[1]['minutes'], reverse=True)

    for projectid, stats in sorted_projects:
        hours = stats['minutes'] / 60.0
        row_data = [
            projectid,
            stats['name'],
            str(stats['entries']),
            f"{hours:.1f}h",
            str(len(stats['employees']))
        ]
        print(format_table_row(row_data, proj_widths))

    print(proj_separator)


def export_table_to_file(time_entries, start_date, end_date, filename=None):
    """
    Export the table format to a text file.

    Args:
        time_entries (list): List of time entry tuples
        start_date (str): Start date for the query
        end_date (str): End date for the query
        filename (str, optional): Output filename
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"time_entries_table_{start_date.replace('-', '')}_{end_date.replace('-', '')}_{timestamp}.txt"

    try:
        import sys
        from io import StringIO

        # Capture print output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        # Generate all the tables
        display_time_entries_table(time_entries, start_date, end_date)
        display_time_entries_chronological_table(time_entries, start_date, end_date)
        display_summary_table(time_entries)
        display_employee_breakdown(time_entries)
        display_project_breakdown(time_entries)

        # Restore stdout
        sys.stdout = old_stdout

        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(captured_output.getvalue())

        print(f"\n✅ Table exported to: {filename}")

    except Exception as e:
        print(f"✗ Error exporting table: {e}")


def main():
    """Main execution function."""
    print("TIME ENTRIES QUERY - TABLE FORMAT")
    print("=" * 50)

    # Define date range
    start_date = "2025-05-20"
    end_date = "2025-06-02"

    print(f"Querying time entries from {start_date} to {end_date}...")
    print("Results will be sorted by Employee ID, then by start time (oldest to newest)")

    # Execute the query
    time_entries = get_time_entries_date_range(start_date, end_date)

    if not time_entries:
        print(f"\nNo time entries found between {start_date} and {end_date}.")
        return

    # Display main table (sorted by EMPID, then start time)
    display_time_entries_table(time_entries, start_date, end_date)

    # Display chronological table (sorted by start time only)
    display_time_entries_chronological_table(time_entries, start_date, end_date)

    # Display summary tables
    display_summary_table(time_entries)
    display_employee_breakdown(time_entries)
    display_project_breakdown(time_entries)

    # Ask if user wants to export to file
    export_choice = input(f"\nExport table to file? (y/N): ").strip().lower()
    if export_choice == 'y':
        export_table_to_file(time_entries, start_date, end_date)

    print(f"\n✅ Query complete. Displayed {len(time_entries)} time entries in table format.")


def custom_date_query():
    """Query with custom date ranges in table format."""
    print("CUSTOM DATE RANGE QUERY - TABLE FORMAT")
    print("=" * 50)

    try:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()

        # Validate date format
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        time_entries = get_time_entries_date_range(start_date, end_date)

        if time_entries:
            display_time_entries_table(time_entries, start_date, end_date)
            display_time_entries_chronological_table(time_entries, start_date, end_date)
            display_summary_table(time_entries)
            display_employee_breakdown(time_entries)
            display_project_breakdown(time_entries)
        else:
            print(f"\nNo time entries found between {start_date} and {end_date}.")

    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD format.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--custom":
        custom_date_query()
    else:
        main()

# **********************************************************************************************************************
# **********************************************************************************************************************
