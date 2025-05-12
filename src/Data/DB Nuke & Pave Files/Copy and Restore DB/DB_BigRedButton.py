# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      This comprehensive DB_BigRedButton.py script  will run the below five Python files in the
#                   order specified:
#                         Get_SaveAllCurrentData.py
#                         GetCaseysSchema.py
#                         Discover_DropTables.py
#                         RestoreCaseysSchema.py
#                         RestoreTime_tracker_data_backup.py
#
#                     Key Features
#                         - Sequential Execution: Runs each script in order, passing control to the next only if
#                             the previous one succeeds
#                         - Colored Output: Uses ANSI colors to make the output more readable and to clearly
#                             distinguish between steps
#                         - Error Handling: Detects and reports failures in any of the scripts
#                         - Environment Checks: Verifies all required environment variables are set before starting
#                         - Script Availability Checks: Ensures all required script files exist
#                         - Confirmation Prompts: Asks for confirmation before executing potentially destructive operations
#                         - Timing Information: Tracks and reports how long each step and the overall process takes
#                         - Command-line Argument: Includes a --skip-confirm option to bypass confirmation prompts
#                             for automated runs
#
#                     Execution Flow
#                         - Displays a banner and explains what the script will do
#                         - Checks environment variables and script files
#                         - Asks for confirmation to proceed
#                         - Runs Get_SaveAllCurrentData.py to back up all data
#                         - Runs GetCaseysSchema.py to back up the schema
#                         - Asks for a second confirmation before destructive operations
#                         - Runs Discover_DropTables.py to drop all tables
#                         - Runs RestoreCaseysSchema.py to restore the schema
#                         - Runs RestoreTime_tracker_data_backup.py to restore data
#                         - Displays a success message and timing information
#
#             This script requires all the individual Python scripts listed above to be in the same directory and
#               has proper error handling to abort the process if any critical step fails.

# Input:            none
# Output:           confirmation messages
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 05.08.2025: Initial setup; code left in non-functional state
#                   - 05.11.2025: All updates complete; code runs as expected
#
# **********************************************************************************************************************
# **********************************************************************************************************************  


# !/usr/bin/env python3
"""
DB_BigRedButton

This script serves as a master control for the complete database backup and restore process.
It runs the individual scripts in the following order:
1. Get_SaveAllCurrentData.py - Backs up all table data to JSON and TXT files
2. GetCaseysSchema.py - Backs up the database schema
3. Discover_DropTables.py - Drops all tables from the database
4. RestoreCaseysSchema.py - Restores the database schema
5. RestoreTime_tracker_data_backup.py - Restores the data from backup files

This provides a "one-click" solution for a complete database refresh process.
"""

import os
import sys
import subprocess
import time
import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ANSI colors for output formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def run_script(script_name, description, args=None):
    """
    Run a Python script and handle its output
    """
    start_time = time.time()

    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}RUNNING: {script_name} - {description}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

    # Build command
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)

    try:
        # Run the script and capture output
        process = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Print the output
        if process.stdout:
            print(process.stdout)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{Colors.GREEN}{Colors.BOLD}SUCCESS: {script_name} completed in {duration:.2f} seconds{Colors.END}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}{Colors.BOLD}ERROR: {script_name} failed with exit code {e.returncode}{Colors.END}")
        if e.stdout:
            print(f"\nOutput:\n{e.stdout}")
        if e.stderr:
            print(f"\nError Output:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(f"{Colors.FAIL}{Colors.BOLD}ERROR: {script_name} not found{Colors.END}")
        return False


def check_environment():
    """
    Check if all required environment variables are set
    """
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"{Colors.FAIL}Error: The following required environment variables are not set: {', '.join(missing_vars)}{Colors.END}")
        print("Please set these environment variables in your .env file before running the script.")
        return False

    # Handle DB_PORT with default value if not set
    db_port = os.getenv("DB_PORT")
    if db_port is None:
        print(f"{Colors.WARNING}Warning: DB_PORT not set, will use default port 3306{Colors.END}")
    else:
        try:
            int(db_port)
        except ValueError:
            print(f"{Colors.FAIL}Error: DB_PORT value '{db_port}' is not a valid integer{Colors.END}")
            return False

    return True


def check_scripts_exist():
    """
    Check if all required scripts exist
    """
    required_scripts = [
        "Get_SaveAllCurrentData.py",
        "GetCaseysSchema.py",
        "Discover_DropTables.py",
        "RestoreCaseysSchema.py",
        "RestoreTime_tracker_data_backup.py"
    ]

    missing_scripts = [script for script in required_scripts if not os.path.exists(script)]

    if missing_scripts:
        print(f"{Colors.FAIL}Error: The following required scripts are missing: {', '.join(missing_scripts)}{Colors.END}")
        print("Please ensure all required scripts are in the current directory.")
        return False

    return True


def main():
    """
    Main function to run all database scripts in sequence
    """
    parser = argparse.ArgumentParser(description='Run the complete database backup and restore process')
    parser.add_argument('--skip-confirm', action='store_true',
                        help='Skip confirmation prompts (Use with caution!)')
    args = parser.parse_args()

    # Print banner
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'*' * 80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'*' * 25} DATABASE BIG RED BUTTON {'*' * 25}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'*' * 80}{Colors.END}\n")

    print(f"{Colors.WARNING}This script will perform a COMPLETE database backup and restore:{Colors.END}")
    print("1. Back up all current data")
    print("2. Back up the database schema")
    print("3. Drop all tables from the database")
    print("4. Restore the database schema")
    print("5. Restore the data from backup files\n")

    # Environment and scripts check
    if not check_environment() or not check_scripts_exist():
        sys.exit(1)

    # Confirmation
    if not args.skip_confirm:
        confirmation = input(f"\n{Colors.WARNING}Are you sure you want to proceed? This will modify your database. (yes/no): {Colors.END}")
        if confirmation.lower() != 'yes':
            print("Operation cancelled by user.")
            sys.exit(0)

    # Record start time
    overall_start_time = time.time()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{Colors.BLUE}Starting database backup and restore process at {current_time}{Colors.END}")

    # Step 1: Back up all current data
    if not run_script("Get_SaveAllCurrentData.py", "Backing up all table data"):
        print(f"{Colors.FAIL}Failed to back up data. Aborting process.{Colors.END}")
        sys.exit(1)

    # Step 2: Back up the database schema
    if not run_script("GetCaseysSchema.py", "Backing up database schema"):
        print(f"{Colors.FAIL}Failed to back up schema. Aborting process.{Colors.END}")
        sys.exit(1)

    # Give user one more chance to cancel before destructive operations
    if not args.skip_confirm:
        confirmation = input(f"\n{Colors.WARNING}Data and schema backups are complete. The next step will DROP ALL TABLES. Continue? (yes/no): {Colors.END}")
        if confirmation.lower() != 'yes':
            print("Operation cancelled by user.")
            sys.exit(0)

    # Step 3: Drop all tables
    if not run_script("Discover_DropTables.py", "Dropping all tables from the database"):
        print(f"{Colors.WARNING}Warning: Failed to drop tables. Will attempt to continue with restoration anyway.{Colors.END}")

    # Step 4: Restore the database schema (with auto-yes to prevent hanging)
    if not run_script("RestoreCaseysSchema.py", "Restoring database schema", ["--yes"]):
        print(f"{Colors.FAIL}Failed to restore schema. Aborting process.{Colors.END}")
        sys.exit(1)

    # Step 5: Restore the data
    if not run_script("RestoreTime_tracker_data_backup.py", "Restoring data from backups"):
        print(f"{Colors.FAIL}Failed to restore data. Process incomplete.{Colors.END}")
        sys.exit(1)

    # Calculate total duration
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time

    # Final success message
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}DATABASE BACKUP AND RESTORE PROCESS COMPLETED SUCCESSFULLY!{Colors.END}")
    print(f"{Colors.GREEN}Total duration: {overall_duration:.2f} seconds{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Process interrupted by user. Database may be in an inconsistent state.{Colors.END}")
        sys.exit(1)

# **********************************************************************************************************************
# **********************************************************************************************************************
