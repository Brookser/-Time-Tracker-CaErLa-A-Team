# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.24.2025
# Description:      Restores DB from the most recent Get&SaveData.py results
#                        named time_tracker_data_backup_xxxxxxxx_xxxxxx in the
#                        DB Nuke & Pave Files
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.24.2025: Initial setup o
#
# **********************************************************************************************************************
# **********************************************************************************************************************  
import os
import sys
import re
import json
import datetime
import argparse
import mariadb
import time
import glob
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Rest of the connect_to_server and other functions remain the same...

def find_most_recent_backup(base_dir=".", type_filter=None):
    """
    Scan for backup directories and return the path to the most recent one
    type_filter can be 'schema' or 'data' to filter by backup type
    """
    print(f"Searching for backups in directory: {base_dir}")
    print(f"Looking for backup type: {type_filter}")

    # If no type filter specified, try to find any backup
    if type_filter is None:
        # First try to find data backup
        data_backup = find_most_recent_backup(base_dir, 'data')
        if data_backup:
            return data_backup

        # If no data backup found, try to find schema backup
        return find_most_recent_backup(base_dir, 'schema')

    # Pattern to match backup directories
    if type_filter == 'schema':
        backup_pattern = r'.*_schema_backup_\d{8}_\d{6}(\.sql)?$'
    elif type_filter == 'data':
        backup_pattern = r'.*_data_backup_\d{8}_\d{6}$'
    else:
        backup_pattern = r'.*(schema|data)_backup_\d{8}_\d{6}(\.sql)?$'

    backups = []

    # Debug: List all files and directories in the base_dir
    print(f"Contents of {base_dir}:")
    for item in os.listdir(base_dir):
        print(f"  - {item}")

    # Walk through directories and files
    for root, dirs, files in os.walk(base_dir):
        # Check directories for data backups
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if re.match(backup_pattern, dir_name):
                # For data backups, verify it's a valid backup by checking for metadata file
                if type_filter != 'schema' and os.path.exists(os.path.join(dir_path, "backup_metadata.json")):
                    # Extract timestamp from directory name
                    match = re.search(r'_backup_(\d{8}_\d{6})', dir_name)
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            backups.append((dir_path, timestamp, 'data'))
                            print(f"Found data backup: {dir_path} from {timestamp}")
                        except ValueError:
                            continue
                # For schema backups in directory format
                elif type_filter == 'schema':
                    schema_files = glob.glob(os.path.join(dir_path, "*.sql"))
                    for schema_file in schema_files:
                        match = re.search(r'_backup_(\d{8}_\d{6})', os.path.basename(schema_file))
                        if match:
                            timestamp_str = match.group(1)
                            try:
                                timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                                backups.append((schema_file, timestamp, 'schema'))
                                print(f"Found schema backup file: {schema_file} from {timestamp}")
                            except ValueError:
                                continue

        # Check files for schema backups
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith('.sql') and re.match(backup_pattern, file_name):
                # Extract timestamp from file name
                match = re.search(r'_backup_(\d{8}_\d{6})', file_name)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        backups.append((file_path, timestamp, 'schema'))
                        print(f"Found schema backup file: {file_path} from {timestamp}")
                    except ValueError:
                        continue

            # Special case: Check if data backup directories contain schema files
            if type_filter == 'schema' and re.match(r'.*_data_backup_\d{8}_\d{6}$', os.path.basename(root)):
                if file_name.endswith('.sql'):
                    # This could be a schema file inside a data backup directory
                    file_path = os.path.join(root, file_name)
                    match = re.search(r'_backup_(\d{8}_\d{6})', os.path.basename(root))
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            backups.append((file_path, timestamp, 'schema'))
                            print(f"Found schema file in data directory: {file_path} from {timestamp}")
                        except ValueError:
                            continue

    if not backups:
        print(f"No {type_filter} backups found in {base_dir}")
        return None

    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x[1], reverse=True)
    print(f"Found {len(backups)} backups, newest is {backups[0][0]} from {backups[0][1]}")

    # Return the path to the most recent backup
    return backups[0][0]


# Main code remains the same...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Restore a MariaDB database (schema and data)')
    parser.add_argument('--schema', help='Path to the schema backup SQL file')
    parser.add_argument('--data', help='Directory containing the data backup files')
    parser.add_argument('--tables', help='Comma-separated list of specific tables to restore')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for inserts (default: 1000)')
    parser.add_argument('--auto', action='store_true', help='Automatically use the most recent backups')
    parser.add_argument('--search-dir', help='Directory to search for backups (default: current directory)')
    parser.add_argument('--order', help='Comma-separated list of tables in the order they should be restored')
    parser.add_argument('--schema-only', action='store_true', help='Only restore the database schema')
    parser.add_argument('--data-only', action='store_true', help='Only restore the data (assumes schema exists)')
    parser.add_argument('--create-schema-from-data', action='store_true', help='Create schema file from data backup if no schema file found')

    args = parser.parse_args()

    print("=== MariaDB Full Database Restoration Tool ===")

    # Determine schema file and data directory
    schema_file = args.schema
    data_dir = args.data
    search_dir = args.search_dir if args.search_dir else "."

    # Auto-find backups if requested
    if args.auto or (not schema_file and not args.data_only) or (not data_dir and not args.schema_only):
        if not schema_file and not args.data_only:
            schema_file = find_most_recent_backup(search_dir, 'schema')
            if not schema_file and args.create_schema_from_data:
                # Find data backup and extract schema file from it
                data_backup = find_most_recent_backup(search_dir, 'data')
                if data_backup:
                    print(f"No schema backup files found, but data backup exists: {data_backup}")
                    # Check if data backup has a schema file inside
                    schema_files = glob.glob(os.path.join(data_backup, "*.sql"))
                    if schema_files:
                        schema_file = schema_files[0]
                        print(f"Using schema file from data backup: {schema_file}")
                    else:
                        print("No schema files found in data backup directory")

            if not schema_file:
                print("Error: No schema backup files found. Please specify a schema file or create a backup first.")
                sys.exit(1)
            print(f"Using most recent schema backup found: {schema_file}")

        if not data_dir and not args.schema_only:
            data_dir = find_most_recent_backup(search_dir, 'data')
            if not data_dir:
                print("Warning: No data backup directories found. Only schema will be restored.")
            else:
                print(f"Using most recent data backup found: {data_dir}")

    # Parse specific tables if provided
    tables_to_restore = None
    if args.tables:
        tables_to_restore = [t.strip() for t in args.tables.split(',')]
        print(f"Will restore only the following tables: {', '.join(tables_to_restore)}")

    # Parse manual table order if provided
    manual_order = None
    if args.order:
        manual_order = [t.strip() for t in args.order.split(',')]
        print(f"Will use the specified table order: {', '.join(manual_order)}")

    # Perform restoration based on options
    if args.schema_only:
        print("\n--- Schema-Only Restoration ---")
        restore_database_schema(schema_file)
    elif args.data_only:
        if not data_dir:
            print("Error: Data directory must be specified for data-only restoration")
            sys.exit(1)

        print("\n--- Data-Only Restoration ---")
        # Get database name from environment variable
        db_name = os.getenv("DB_NAME")
        if not db_name:
            print("Error: DB_NAME environment variable must be set for data-only restoration")
            sys.exit(1)

        restore_table_data(
            db_name,
            data_dir,
            tables=tables_to_restore,
            batch_size=args.batch_size,
            manual_order=manual_order
        )
    else:
        # Full restoration
        db_name = full_database_restore(
            schema_file,
            data_dir,
            tables=tables_to_restore,
            batch_size=args.batch_size,
            manual_order=manual_order
        )

    print("=== Restoration process completed ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
