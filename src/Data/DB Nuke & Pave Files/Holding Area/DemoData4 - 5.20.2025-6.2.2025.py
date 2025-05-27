# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.26.2025
# Description:      script that adds time entries for TEST01 (Tess) and E011 (Nina) for date range
#                       5/20/2025 - 6/2/2025
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
Script to add more time entries for TEST01 and E011 for date range 05/20/2025-06/02/2025.
Ensures no overlapping start/stop times with existing entries for these employees.
"""

from src.Data.Database import Database
from datetime import datetime, timedelta
import uuid
import random

# Target employees
TARGET_EMPLOYEES = ['TEST01', 'E011']

# Projects these employees are assigned to
EMPLOYEE_PROJECTS = {
    'TEST01': ['P19241', 'P99006', 'P13724', 'P99005'],  # From previous query results
    'E011': ['P27260', 'P99005']  # From previous query results
}

# Existing time entries for TEST01 and E011 (from the pasted data)
EXISTING_ENTRIES = {
    'TEST01': [
        {'date': '2025-05-24', 'start': '02:39', 'stop': '02:40', 'duration': 1},  # 02:39-02:40
        {'date': '2025-05-24', 'start': '03:15', 'stop': '03:16', 'duration': 1},  # 03:15-03:16
        {'date': '2025-05-24', 'start': '06:38', 'stop': '06:38', 'duration': 0},  # 06:38
        {'date': '2025-05-24', 'start': '20:31', 'stop': '20:31', 'duration': 0},  # 20:31
        {'date': '2025-05-24', 'start': '22:02', 'stop': '22:05', 'duration': 3},  # 22:02-22:05
        {'date': '2025-05-26', 'start': '23:24', 'stop': '23:45', 'duration': 21},  # 23:24-23:45
        {'date': '2025-05-26', 'start': '23:46', 'stop': '23:46', 'duration': 0},  # 23:46
    ],
    'E011': [
        {'date': '2025-05-26', 'start': '23:57', 'stop': '23:57', 'duration': 0},  # 23:57
    ]
}

# Work notes templates for projects
WORK_NOTES_BY_PROJECT = {
    'P19241': [  # MarketingWebsite
        "Updated website homepage layout",
        "Implemented responsive design changes",
        "Fixed navigation menu issues",
        "Reviewed SEO optimization",
        "Updated marketing copy",
        "Testing mobile responsiveness",
        "Fixed broken links",
        "Optimized page load speeds"
    ],
    'P99006': [  # MarketingWebsite 2
        "Migrated content to new platform",
        "Testing updated UI components",
        "Updated branding elements",
        "Testing A/B variations",
        "Updated landing page content",
        "Testing payment integration",
        "Fixed CSS styling issues",
        "Updated API integrations"
    ],
    'P13724': [  # TestingID
        "Conducted unit testing",
        "Performed integration testing",
        "Fixed failing test cases",
        "Testing edge cases",
        "Performed regression testing",
        "Testing API endpoints",
        "Updated test data sets",
        "Testing error handling"
    ],
    'P99005': [  # TestingID 2
        "Enhanced test coverage",
        "Implemented new test scenarios",
        "Testing performance metrics",
        "Updated test environments",
        "Testing user workflows",
        "Testing data validation",
        "Updated test automation",
        "Testing deployment processes"
    ],
    'P27260': [  # TestProj to Add employees
        "Onboarding new team members",
        "Updated project documentation",
        "Conducted team training sessions",
        "Updated access permissions",
        "Organized team meetings",
        "Updated project timelines",
        "Conducted performance reviews",
        "Updated team structure"
    ]
}


def get_existing_entries_from_db(empid, start_date, end_date):
    """
    Get existing time entries for an employee from the database.

    Args:
        empid (str): Employee ID
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        list: List of existing time entries
    """
    try:
        Database.connect()
        cursor = Database.get_cursor()

        query = '''
            SELECT START_TIME, STOP_TIME, TOTAL_MINUTES
            FROM time
            WHERE EMPID = ? AND START_TIME >= ? AND START_TIME <= ?
            ORDER BY START_TIME
        '''

        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"

        cursor.execute(query, (empid, start_datetime, end_datetime))
        results = cursor.fetchall()

        cursor.close()

        # Convert to our format
        existing_entries = []
        for start_time, stop_time, minutes in results:
            if start_time:
                entry = {
                    'date': start_time.strftime('%Y-%m-%d'),
                    'start': start_time.strftime('%H:%M'),
                    'stop': stop_time.strftime('%H:%M') if stop_time else start_time.strftime('%H:%M'),
                    'duration': minutes if minutes else 0
                }
                existing_entries.append(entry)

        return existing_entries

    except Exception as e:
        print(f"Error getting existing entries for {empid}: {e}")
        return []


def time_to_minutes(time_str):
    """Convert HH:MM to minutes since midnight."""
    hour, minute = map(int, time_str.split(':'))
    return hour * 60 + minute


def minutes_to_time(minutes):
    """Convert minutes since midnight to HH:MM."""
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def find_available_time_slots(existing_entries, date_str, min_duration=15):
    """
    Find available time slots for a given date, avoiding existing entries.

    Args:
        existing_entries (list): List of existing time entries
        date_str (str): Date in 'YYYY-MM-DD' format
        min_duration (int): Minimum duration in minutes for a slot

    Returns:
        list: List of available time slots as (start_minutes, end_minutes) tuples
    """
    # Get existing entries for this specific date
    date_entries = [entry for entry in existing_entries if entry['date'] == date_str]

    # Convert to minutes and create occupied periods
    occupied_periods = []
    for entry in date_entries:
        start_mins = time_to_minutes(entry['start'])
        stop_mins = time_to_minutes(entry['stop'])

        # Add 5-minute buffer around each entry to avoid close overlaps
        buffer_start = max(0, start_mins - 5)
        buffer_stop = min(1439, stop_mins + 5)  # 1439 = 23:59

        occupied_periods.append((buffer_start, buffer_stop))

    # Sort occupied periods
    occupied_periods.sort()

    # Merge overlapping periods
    merged_periods = []
    for start, end in occupied_periods:
        if merged_periods and start <= merged_periods[-1][1]:
            merged_periods[-1] = (merged_periods[-1][0], max(merged_periods[-1][1], end))
        else:
            merged_periods.append((start, end))

    # Find available slots (work hours: 7 AM to 10 PM = 420 to 1320 minutes)
    work_start = 7 * 60  # 7:00 AM
    work_end = 22 * 60  # 10:00 PM

    available_slots = []
    current_time = work_start

    for occupied_start, occupied_end in merged_periods:
        # Add slot before this occupied period
        if current_time < occupied_start:
            slot_duration = occupied_start - current_time
            if slot_duration >= min_duration:
                available_slots.append((current_time, occupied_start))

        current_time = max(current_time, occupied_end)

    # Add final slot after all occupied periods
    if current_time < work_end:
        slot_duration = work_end - current_time
        if slot_duration >= min_duration:
            available_slots.append((current_time, work_end))

    return available_slots


def generate_time_id():
    """Generate a unique time ID."""
    return f"t-{uuid.uuid4().hex[:8]}"


def generate_work_notes(project_id):
    """Generate work notes for a project."""
    notes_list = WORK_NOTES_BY_PROJECT.get(project_id, ["Working on project tasks"])

    # 20% chance of empty notes
    if random.random() < 0.2:
        return ""

    return random.choice(notes_list)


def generate_new_time_entries(empid, start_date, end_date):
    """
    Generate new time entries for an employee without overlapping existing ones.

    Args:
        empid (str): Employee ID
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        list: List of new time entry dictionaries
    """
    # Get existing entries from database
    existing_entries = get_existing_entries_from_db(empid, start_date, end_date)

    print(f"Found {len(existing_entries)} existing entries for {empid}")

    new_entries = []
    projects = EMPLOYEE_PROJECTS.get(empid, [])

    if not projects:
        print(f"No projects found for {empid}")
        return []

    # Generate entries for each day in the range
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    while current_date <= end_date_obj:
        date_str = current_date.strftime('%Y-%m-%d')
        is_weekend = current_date.weekday() >= 5

        # Number of entries per day: 2-4 on weekdays, 0-2 on weekends
        if is_weekend:
            if random.random() < 0.3:  # 30% chance of working on weekends
                num_entries = random.randint(1, 2)
            else:
                num_entries = 0
        else:
            num_entries = random.randint(2, 4)

        if num_entries > 0:
            # Find available time slots for this day
            available_slots = find_available_time_slots(existing_entries, date_str)

            if available_slots:
                # Generate entries for available slots
                for _ in range(min(num_entries, len(available_slots))):
                    if not available_slots:
                        break

                    # Pick a random available slot
                    slot_idx = random.randint(0, len(available_slots) - 1)
                    slot_start, slot_end = available_slots.pop(slot_idx)

                    # Generate entry within this slot
                    entry = generate_single_entry(empid, date_str, slot_start, slot_end, projects)
                    if entry:
                        new_entries.append(entry)

                        # Update existing entries to include this new one for conflict checking
                        existing_entries.append({
                            'date': date_str,
                            'start': entry['start_time'].strftime('%H:%M'),
                            'stop': entry['stop_time'].strftime('%H:%M'),
                            'duration': entry['total_minutes']
                        })

        current_date += timedelta(days=1)

    return new_entries


def generate_single_entry(empid, date_str, slot_start_mins, slot_end_mins, projects):
    """
    Generate a single time entry within an available time slot.

    Args:
        empid (str): Employee ID
        date_str (str): Date in 'YYYY-MM-DD' format
        slot_start_mins (int): Slot start time in minutes since midnight
        slot_end_mins (int): Slot end time in minutes since midnight
        projects (list): List of available projects

    Returns:
        dict: Time entry dictionary
    """
    slot_duration = slot_end_mins - slot_start_mins

    # Entry duration: 15 minutes to 2 hours, but not exceeding slot duration
    max_duration = min(120, slot_duration - 10)  # Leave 10 min buffer
    min_duration = min(15, max_duration)

    if max_duration < min_duration:
        return None

    # Duration distribution
    if max_duration >= 60:
        # Bias toward longer entries
        duration = random.choices(
            range(min_duration, max_duration + 1),
            weights=[1 if d < 30 else 3 if d < 60 else 2 for d in range(min_duration, max_duration + 1)]
        )[0]
    else:
        duration = random.randint(min_duration, max_duration)

    # Random start time within the slot (leaving room for duration)
    latest_start = slot_end_mins - duration
    start_mins = random.randint(slot_start_mins, latest_start)
    stop_mins = start_mins + duration

    # Convert back to datetime
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    start_time = date_obj + timedelta(minutes=start_mins)
    stop_time = date_obj + timedelta(minutes=stop_mins)

    # Random project
    project_id = random.choice(projects)

    # Generate notes
    notes = generate_work_notes(project_id)

    return {
        'timeid': generate_time_id(),
        'empid': empid,
        'project_id': project_id,
        'start_time': start_time,
        'stop_time': stop_time,
        'notes': notes,
        'manual_entry': 0,
        'total_minutes': duration
    }


def insert_time_entries(time_entries):
    """Insert time entries using the Database method."""
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
                print(f"✓ Added {entry['timeid']} for {entry['empid']} on {entry['start_time'].strftime('%m/%d %H:%M')}-{entry['stop_time'].strftime('%H:%M')} ({entry['total_minutes']}m)")

        except Exception as e:
            print(f"✗ Failed to add entry {entry['timeid']}: {e}")
            continue

    return success_count


def display_summary(entries_by_employee):
    """Display a summary of generated entries."""
    print(f"\nSUMMARY OF NEW TIME ENTRIES")
    print("=" * 50)

    total_entries = 0
    total_minutes = 0

    for empid, entries in entries_by_employee.items():
        if entries:
            emp_minutes = sum(entry['total_minutes'] for entry in entries)
            emp_hours = emp_minutes / 60.0

            projects = set(entry['project_id'] for entry in entries)

            print(f"{empid}: {len(entries)} entries, {emp_minutes} min ({emp_hours:.1f}h), {len(projects)} projects")

            total_entries += len(entries)
            total_minutes += emp_minutes

    total_hours = total_minutes / 60.0
    print(f"\nTotal: {total_entries} entries, {total_minutes} minutes ({total_hours:.1f} hours)")


def main():
    """Main execution function."""
    print("ADD NON-OVERLAPPING TIME ENTRIES FOR TEST01 AND E011")
    print("=" * 60)

    start_date = "2025-05-20"
    end_date = "2025-06-02"

    print(f"Date range: {start_date} to {end_date}")
    print(f"Target employees: {', '.join(TARGET_EMPLOYEES)}")

    # Generate entries for each employee
    all_entries = {}

    for empid in TARGET_EMPLOYEES:
        print(f"\nGenerating entries for {empid}...")
        entries = generate_new_time_entries(empid, start_date, end_date)
        all_entries[empid] = entries
        print(f"Generated {len(entries)} new entries for {empid}")

    # Display summary
    display_summary(all_entries)

    # Flatten entries for insertion
    all_entries_list = []
    for entries in all_entries.values():
        all_entries_list.extend(entries)

    if not all_entries_list:
        print("\nNo new entries generated.")
        return

    # Confirm before inserting
    print(f"\nReady to insert {len(all_entries_list)} new time entries into database.")
    confirm = input("Proceed with insertion? (y/N): ").strip().lower()

    if confirm == 'y':
        print("\nInserting time entries...")
        success_count = insert_time_entries(all_entries_list)
        print(f"\n✅ Successfully inserted {success_count} out of {len(all_entries_list)} time entries.")
    else:
        print("\n❌ Insertion cancelled.")


if __name__ == "__main__":
    main()

# **********************************************************************************************************************
# **********************************************************************************************************************
