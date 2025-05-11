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
#         • Reports any errors that occur during deletion
#
#
#
#     Usage
#         ***BASH COMMANDS Basic usage (keeps 3 most recent backups)***
#             python CleanUpBackups.py
#
#         ***Keep a different number of backups***
#             python CleanUpBackups.py --keep 5
#
#         ***Preview what would be deleted without actually deleting***
#             python CleanUpBackups.py --dry-run
#
#         ***Skip confirmation prompt (useful for automated cleanup)***
#             python CleanUpBackups.py --yes
#
#     Example Output
#         The script provides clear, color-coded output like this:
#             • Green ✓ for files being kept
#             • Red ✗ for files being deleted
#             • Detailed information about each file (date modified, size)
#             • Summary of total space freed
#
#     This script complements the backup workflow by preventing the accumulation of unnecessary backup files and ensuring
#       there is always a recent backup available in case of emergency.
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
    return total_size


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
                        os.remove(item)
                    except Exception as e:
                        print(f"      {Colors.FAIL}Error: {e}{Colors.END}")

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
                    try:
                        # For Windows: Make files writable before deletion
                        if os.name == 'nt':  # Check if running on Windows
                            for root, dirs, files in os.walk(item):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    try:
                                        # Make the file writable
                                        os.chmod(file_path, 0o777)
                                    except:
                                        pass

                        # Try to delete the directory
                        shutil.rmtree(item)

                    except Exception as e:
                        print(f"      {Colors.FAIL}Error: {e}{Colors.END}")
                        print(f"      {Colors.WARNING}Attempting alternative deletion method...{Colors.END}")

                        # Alternative method for Windows: use system commands
                        try:
                            if os.name == 'nt':  # Windows
                                # Use the Windows RD command with /S /Q for silent recursive delete
                                os.system(f'rd /S /Q "{item}"')
                            else:  # Unix-like
                                # Use rm -rf for Unix-like systems
                                os.system(f'rm -rf "{item}"')

                            # Check if directory still exists
                            if not os.path.exists(item):
                                print(f"      {Colors.GREEN}Alternative deletion successful{Colors.END}")
                            else:
                                print(f"      {Colors.FAIL}Alternative deletion also failed{Colors.END}")
                                print(f"      {Colors.WARNING}Try manually deleting: {item}{Colors.END}")
                        except Exception as alt_e:
                            print(f"      {Colors.FAIL}Alternative deletion error: {alt_e}{Colors.END}")

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
