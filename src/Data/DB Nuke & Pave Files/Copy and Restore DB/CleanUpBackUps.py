# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Cleans up the schema and data backup files
#                       leaving only the three most recent of each within the code base
# Input:            none
# Output:           confirmation message
# Sources:
#
# Change Log:       - 5.11.2025: Initial setup
#                   - 5.26.2025: Refactored script for better error handling and
#                       cleaner output

# A comprehensive script that will manage backup files by keeping only the most recent ones.
#
# Features
#
#     Intelligent Backup Detection:
#         • Finds schema backup files (matching *_schema_backup_*.sql)
#         • Finds data backup directories (matching *_data_backup_*)
#         • Sorts them by modification time to determine the most recent
#
#
#     Configurable Retention Policy:
#
#         • By default, keeps the 3 most recent backups of each type
#         • Can be adjusted with the --keep command-line argument
#
#
#     Safety Features:
#
#         • Dry run mode (--dry-run) to preview what would be deleted without actually deleting anything
#         • Confirmation prompt before deletion (can be bypassed with --yes)
#         • Detailed reporting of what's being kept and what's being removed
#
#
#     Detailed Reporting:
#
#         • Shows file/directory sizes in human-readable format
#         • Calculates total space that will be freed
#         • Timestamps when backups were created
#         • Color-coded output for better readability
#
#
#     Error Handling:
#
#         • Gracefully handles missing files or permissions issues
#         • Reports errors that occur during deletion


#
# **********************************************************************************************************************
# **********************************************************************************************************************  


"""
CleanUpBackups.py

This script finds and deletes all but the most recent schema and data backup files.
It keeps the 3 most recent backups of each type and removes the older ones to save disk space.

Types of backup files handled:
1. Schema backups (*_schema_backup_*.sql)
2. Data backups (directories matching *_data_backup_*)
"""

import os
import sys
import glob
import shutil
import argparse
import stat
import subprocess
from datetime import datetime


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


def find_backup_files(pattern, is_directory=False):
    """
    Find files or directories that match the given pattern
    """
    items = glob.glob(pattern)

    # Filter out non-directories if we're looking for directories
    if is_directory:
        items = [item for item in items if os.path.isdir(item)]
    else:
        items = [item for item in items if os.path.isfile(item)]

    if not items:
        return []

    # Add modification time to each item
    item_info = [(item, os.path.getmtime(item)) for item in items]

    # Sort by modification time (newest first)
    item_info.sort(key=lambda x: x[1], reverse=True)

    return item_info


def format_size(size_bytes):
    """
    Format size in bytes to human-readable format
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_directory_size(path):
    """
    Calculate the total size of a directory
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if not os.path.islink(file_path):
                    total_size += os.path.getsize(file_path)
    except (OSError, IOError):
        # If we can't access some files, just return what we could calculate
        pass
    return total_size


def make_writable(path):
    """
    Make a file or directory writable by removing read-only attributes
    """
    try:
        # Remove read-only attribute
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    except (OSError, IOError):
        pass


def remove_readonly_recursive(path):
    """
    Recursively remove read-only attributes from all files in a directory
    """
    try:
        for root, dirs, files in os.walk(path):
            # Make directories writable
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                make_writable(dir_path)

            # Make files writable
            for file_name in files:
                file_path = os.path.join(root, file_name)
                make_writable(file_path)

            # Make the current directory writable
            make_writable(root)
    except (OSError, IOError):
        pass


def delete_directory_windows(path):
    """
    Delete a directory on Windows using multiple methods
    """
    try:
        # Method 1: Try shutil.rmtree with error handler
        def handle_remove_readonly(func, path, exc):
            """Error handler to remove read-only files"""
            if os.path.exists(path):
                make_writable(path)
                func(path)

        shutil.rmtree(path, onerror=handle_remove_readonly)

        # Check if deletion was successful
        if not os.path.exists(path):
            return True, "Standard deletion successful"

    except Exception as e:
        pass

    # Method 2: Remove read-only attributes first, then try shutil.rmtree
    try:
        remove_readonly_recursive(path)
        shutil.rmtree(path)

        if not os.path.exists(path):
            return True, "Deletion after removing read-only attributes successful"

    except Exception as e:
        pass

    # Method 3: Use Windows rd command
    try:
        # Use subprocess for better control
        result = subprocess.run(['rd', '/S', '/Q', path],
                                shell=True,
                                capture_output=True,
                                text=True)

        if not os.path.exists(path):
            return True, "Windows rd command successful"
        else:
            return False, f"Windows rd command failed: {result.stderr}"

    except Exception as e:
        return False, f"Windows rd command error: {e}"

    return False, "All deletion methods failed"


def delete_directory_unix(path):
    """
    Delete a directory on Unix-like systems
    """
    try:
        # Try standard shutil.rmtree first
        shutil.rmtree(path)
        return True, "Standard deletion successful"
    except Exception as e:
        pass

    # Try rm -rf as fallback
    try:
        result = subprocess.run(['rm', '-rf', path],
                                capture_output=True,
                                text=True)

        if not os.path.exists(path):
            return True, "rm -rf command successful"
        else:
            return False, f"rm -rf command failed: {result.stderr}"

    except Exception as e:
        return False, f"rm -rf command error: {e}"


def delete_directory_safely(path):
    """
    Delete a directory using the appropriate method for the operating system
    """
    if os.name == 'nt':  # Windows
        return delete_directory_windows(path)
    else:  # Unix-like systems
        return delete_directory_unix(path)


def cleanup_backups(keep_count=3, dry_run=False, force=False):
    """
    Find and delete old backup files and directories
    """
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD} BACKUP CLEANUP UTILITY {Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

    print(f"Keeping the {Colors.BOLD}{keep_count} most recent backups{Colors.END} of each type")
    if dry_run:
        print(f"{Colors.WARNING}DRY RUN: No files will actually be deleted{Colors.END}")
    print()

    total_space_freed = 0

    # Process schema backups (SQL files)
    print(f"{Colors.HEADER}SCHEMA BACKUPS:{Colors.END}")
    schema_backups = find_backup_files("*_schema_backup_*.sql")

    if not schema_backups:
        print("  No schema backup files found")
    else:
        print(f"  Found {len(schema_backups)} schema backup files")

        # Keep the most recent files
        to_keep = schema_backups[:keep_count]
        to_delete = schema_backups[keep_count:]

        print(f"  Keeping {len(to_keep)} recent schema backups:")
        for item, mtime in to_keep:
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = os.path.getsize(item)
            print(f"    {Colors.GREEN}✓ {item}{Colors.END} ({mtime_str}, {format_size(size)})")

        if to_delete:
            print(f"\n  {Colors.WARNING}Will delete {len(to_delete)} older schema backups:{Colors.END}")
            schema_space = 0

            for item, mtime in to_delete:
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                size = os.path.getsize(item)
                schema_space += size
                action = "Would delete" if dry_run else "Deleting"
                print(f"    {Colors.FAIL}✗ {action}: {item}{Colors.END} ({mtime_str}, {format_size(size)})")

                if not dry_run:
                    try:
                        # Remove read-only attribute if present
                        make_writable(item)
                        os.remove(item)
                        print(f"      {Colors.GREEN}Successfully deleted{Colors.END}")
                    except Exception as e:
                        print(f"      {Colors.FAIL}Error deleting file: {e}{Colors.END}")

            print(f"  Space freed from schema backups: {Colors.BOLD}{format_size(schema_space)}{Colors.END}")
            total_space_freed += schema_space
        else:
            print("  No old schema backups to delete")

    # Process data backup directories
    print(f"\n{Colors.HEADER}DATA BACKUPS:{Colors.END}")
    data_backups = find_backup_files("*_data_backup_*", is_directory=True)

    if not data_backups:
        print("  No data backup directories found")
    else:
        print(f"  Found {len(data_backups)} data backup directories")

        # Keep the most recent directories
        to_keep = data_backups[:keep_count]
        to_delete = data_backups[keep_count:]

        print(f"  Keeping {len(to_keep)} recent data backups:")
        for item, mtime in to_keep:
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = get_directory_size(item)
            print(f"    {Colors.GREEN}✓ {item}{Colors.END} ({mtime_str}, {format_size(size)})")

        if to_delete:
            print(f"\n  {Colors.WARNING}Will delete {len(to_delete)} older data backups:{Colors.END}")
            data_space = 0

            for item, mtime in to_delete:
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                size = get_directory_size(item)
                data_space += size
                action = "Would delete" if dry_run else "Deleting"
                print(f"    {Colors.FAIL}✗ {action}: {item}{Colors.END} ({mtime_str}, {format_size(size)})")

                if not dry_run:
                    success, message = delete_directory_safely(item)
                    if success:
                        print(f"      {Colors.GREEN}✓ {message}{Colors.END}")
                    else:
                        print(f"      {Colors.FAIL}✗ {message}{Colors.END}")
                        print(f"      {Colors.WARNING}You may need to manually delete: {item}{Colors.END}")

            print(f"  Space freed from data backups: {Colors.BOLD}{format_size(data_space)}{Colors.END}")
            total_space_freed += data_space
        else:
            print("  No old data backups to delete")

    # Print summary
    print(f"\n{Colors.HEADER}SUMMARY:{Colors.END}")
    if dry_run:
        print(f"  {Colors.WARNING}DRY RUN - No files were actually deleted{Colors.END}")
        print(f"  Potential space that would be freed: {Colors.BOLD}{format_size(total_space_freed)}{Colors.END}")
    else:
        if total_space_freed > 0:
            print(f"  {Colors.GREEN}Successfully freed {Colors.BOLD}{format_size(total_space_freed)}{Colors.GREEN} of disk space{Colors.END}")
        else:
            print(f"  {Colors.GREEN}No space was freed - all backups were within the keep limit{Colors.END}")

    return total_space_freed > 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean up old database backup files')
    parser.add_argument('-k', '--keep', type=int, default=3,
                        help='Number of most recent backups to keep (default: 3)')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Show what would be deleted without actually deleting')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Skip confirmation prompt')

    args = parser.parse_args()

    if args.keep < 1:
        print(f"{Colors.FAIL}Error: Must keep at least 1 backup{Colors.END}")
        sys.exit(1)

    if not args.dry_run and not args.yes:
        print(f"{Colors.WARNING}This will delete all but the {args.keep} most recent backups of each type.{Colors.END}")
        response = input("Do you want to continue? (yes/no): ").lower()

        if response != "yes":
            print("Operation cancelled.")
            sys.exit(0)

    changed = cleanup_backups(args.keep, args.dry_run)

    if args.dry_run:
        print(f"\nRun without --dry-run to actually delete the files.")

# **********************************************************************************************************************
# **********************************************************************************************************************
