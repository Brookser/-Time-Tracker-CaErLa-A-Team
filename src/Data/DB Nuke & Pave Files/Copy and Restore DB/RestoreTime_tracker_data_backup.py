# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      looks to most recent time_tracker_data_backup folder and repopulates data
#                       based on contents of folder
# Input:            most recent time_tracker_data_backup folder & contents
# Output:           confirmation message
#
# Change Log:       - 05.05.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

import os
import sys
import json
import datetime
import mariadb
import argparse
import glob
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


def connect_to_database():
    """
    Establish connection to MariaDB using environment variables with proper error handling
    """
    # Check if required environment variables are set
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: The following required environment variables are not set: {', '.join(missing_vars)}")
        print("Please set these environment variables in your .env file before running the script.")
        sys.exit(1)

    # Handle DB_PORT with default value if not set
    db_port = os.getenv("DB_PORT")
    if db_port is None:
        db_port = 3306  # Default MariaDB port
        print(f"Warning: DB_PORT not set, using default port {db_port}")
    else:
        try:
            db_port = int(db_port)
        except ValueError:
            print(f"Error: DB_PORT value '{db_port}' is not a valid integer")
            sys.exit(1)

    try:
        # Connect to MariaDB
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=db_port,
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )
        print(f"Successfully connected to {os.getenv('DB_NAME')} database")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)


def find_latest_backup():
    """
    Find the most recent backup directory
    """
    # Look for directories matching the backup pattern
    backup_dirs = glob.glob("time_tracker_data_backup_*")

    if not backup_dirs:
        print("Error: No backup directories found.")
        sys.exit(1)

    # Sort by timestamp (newest first)
    backup_dirs.sort(reverse=True)

    latest_backup = backup_dirs[0]
    print(f"Found latest backup: {latest_backup}")

    return latest_backup


def determine_table_order(backup_dir):
    """
    Determine the correct order to restore tables based on dependencies
    """
    # Read dependency information from the backup
    with open(os.path.join(backup_dir, "table_dependencies.json"), 'r') as f:
        dependencies = json.load(f)

    # Read metadata to get all tables
    with open(os.path.join(backup_dir, "backup_metadata.json"), 'r') as f:
        metadata = json.load(f)

    all_tables = [table["name"] for table in metadata["tables"]]

    # Build dependency graph
    dep_graph = {table: [] for table in all_tables}
    for dep in dependencies:
        if dep["referenced_table_name"] is not None:
            # The table depends on the referenced table
            dep_graph[dep["table_name"]].append(dep["referenced_table_name"])

    # Topological sort to determine restoration order
    restoration_order = []
    visited = set()
    temp_visited = set()

    def visit(table):
        # If we've already visited this node, nothing to do
        if table in visited:
            return
        # If we're in the process of visiting this node, we have a cycle
        if table in temp_visited:
            print(f"Warning: Cyclic dependency detected involving table {table}")
            return

        # Mark node as temporarily visited
        temp_visited.add(table)

        # Visit all dependencies first
        for dep in dep_graph.get(table, []):
            if dep in all_tables:  # Only visit if it's a table we need to restore
                visit(dep)

        # Remove from temporary set and add to permanently visited
        temp_visited.remove(table)
        visited.add(table)

        # Add to restoration order
        restoration_order.append(table)

    # Visit all nodes
    for table in all_tables:
        if table not in visited:
            visit(table)

    return restoration_order


def restore_table_data(backup_dir, tables_to_restore=None, disable_checks=False):
    """
    Function to restore database from a backup directory
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Get metadata
        with open(os.path.join(backup_dir, "backup_metadata.json"), 'r') as f:
            metadata = json.load(f)

        print(f"Restoring data from backup created on: {metadata['backup_date']}")
        print(f"Database: {metadata['database']}")

        # Determine the order to restore tables
        restoration_order = determine_table_order(backup_dir)

        # If specific tables were requested, filter the restoration order
        if tables_to_restore:
            restoration_order = [table for table in restoration_order if table in tables_to_restore]

        # Report on tables to be restored
        print(f"\nWill restore tables in this order: {', '.join(restoration_order)}")

        # Disable foreign key checks if requested
        if disable_checks:
            print("\nTemporarily disabling foreign key checks...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            conn.autocommit = False

        # Process each table
        for table in restoration_order:
            table_file = os.path.join(backup_dir, f"{table}.json")

            # Skip if the file doesn't exist
            if not os.path.exists(table_file):
                print(f"Skipping {table}: No data file found")
                continue

            # Load the data from the file
            with open(table_file, 'r') as f:
                data = json.load(f)

            # Skip if there's no data
            if not data:
                print(f"Skipping {table}: No data to restore")
                continue

            print(f"\nRestoring data for table: {table}")
            print(f"  Rows to restore: {len(data)}")

            # Get column information from the first row
            # This assumes consistent column structure across all rows
            columns = list(data[0].keys())

            # Build the SQL for inserting
            placeholders = ", ".join(["?"] * len(columns))
            column_str = ", ".join([f"`{col}`" for col in columns])

            sql = f"INSERT INTO `{table}` ({column_str}) VALUES ({placeholders})"

            # Process in batches
            batch_size = 1000
            batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]

            # Track progress
            total_inserted = 0
            errors = 0

            for batch_num, batch in enumerate(batches):
                try:
                    print(f"  Processing batch {batch_num + 1}/{len(batches)}")

                    # Prepare and execute each row
                    for row in batch:
                        values = [row[col] for col in columns]
                        try:
                            cursor.execute(sql, values)
                            total_inserted += 1
                        except mariadb.Error as e:
                            errors += 1
                            if errors <= 5:  # Only show first few errors
                                print(f"    Error inserting row: {e}")
                            elif errors == 6:
                                print("    Additional errors suppressed...")

                    # Commit the batch
                    if not disable_checks:
                        conn.commit()

                except mariadb.Error as e:
                    print(f"  Error processing batch: {e}")
                    if not disable_checks:
                        conn.rollback()
                    errors += 1

            # Report on the table
            print(f"  Inserted {total_inserted} rows with {errors} errors")

        # Re-enable foreign key checks and commit if they were disabled
        if disable_checks:
            print("\nRe-enabling foreign key checks...")
            conn.commit()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.autocommit = True

        print("\nDatabase restoration complete!")

    except Exception as e:
        print(f"Error during database restoration: {e}")
        if disable_checks:
            conn.rollback()
        sys.exit(1)
    finally:
        # Make sure foreign key checks are re-enabled even if an error occurs
        if disable_checks:
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                conn.autocommit = True
            except:
                pass

        cursor.close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Restore data from a MariaDB backup directory')
    parser.add_argument('backup_dir', help='Directory containing backup files (default: auto-detect latest)',
                        nargs='?', default=None)
    parser.add_argument('-t', '--tables', help='Specific tables to restore (comma-separated)', type=str)
    parser.add_argument('-d', '--disable-fk', help='Disable foreign key checks during restoration', action='store_true')
    args = parser.parse_args()

    # Use specified backup directory or find the latest
    backup_dir = args.backup_dir
    if backup_dir is None:
        backup_dir = find_latest_backup()

    # Process table list if provided
    tables_to_restore = None
    if args.tables:
        tables_to_restore = [t.strip() for t in args.tables.split(',')]

    print("=== MariaDB Data Restoration Tool ===")
    print(f"Backup directory: {backup_dir}")

    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory {backup_dir} not found.")
        sys.exit(1)

    restore_table_data(backup_dir, tables_to_restore, args.disable_fk)
    print("=== Data restoration complete! ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
