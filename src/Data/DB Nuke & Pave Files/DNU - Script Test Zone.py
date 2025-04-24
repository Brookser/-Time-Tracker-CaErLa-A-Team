#!/usr/bin/env python3
"""
MariaDB Database Full Restore Script

This script provides a complete solution for restoring both schema and data
from backup files. It handles circular dependencies and ensures proper restoration order.
"""

import os
import sys
import re
import json
import datetime
import argparse
import mariadb
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def connect_to_server():
    """
    Connect to MariaDB server without specifying a database
    """
    # Check if required environment variables are set
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST"]
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
        # Connect to MariaDB without specifying a database
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=db_port,
            connect_timeout=5
        )
        print(f"Successfully connected to MariaDB server at {os.getenv('DB_HOST')}:{db_port}")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)


def connect_to_database(db_name):
    """
    Establish connection to a specific MariaDB database
    """
    # Check if required environment variables are set
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST"]
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
            database=db_name,
            connect_timeout=5
        )
        print(f"Successfully connected to {db_name} database")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)


def extract_database_name(sql_file_path):
    """
    Extract the database name from the backup file
    """
    db_name = None

    try:
        with open(sql_file_path, 'r') as f:
            for line in f:
                # Extract database name from CREATE DATABASE statement
                db_name_match = re.search(r'CREATE DATABASE.*?`([^`]+)`', line)
                if db_name_match:
                    db_name = db_name_match.group(1)
                    break

                # Extract from header comment
                header_match = re.search(r'-- MariaDB Schema Backup for database: (\w+)', line)
                if header_match:
                    db_name = header_match.group(1)
                    break

        # If no database name found, use from environment variables
        if not db_name:
            db_name = os.getenv("DB_NAME")
            if not db_name:
                print("Error: Could not determine database name from backup file or environment variables")
                sys.exit(1)

        return db_name

    except IOError as e:
        print(f"Error reading backup file: {e}")
        sys.exit(1)


def execute_sql_file(conn, cursor, sql_file_path, db_name):
    """
    Execute SQL commands from the backup file
    Handles multi-statement queries and DELIMITER changes
    """
    print("Starting database restoration process...")

    try:
        with open(sql_file_path, 'r') as f:
            content = f.read()

        # Split the file into SQL statements
        current_delimiter = ';'
        statements = []
        current_statement = ''
        in_delimiter_mode = False

        for line in content.splitlines():
            # Skip comments and empty lines
            if line.strip().startswith('--') or not line.strip():
                continue

            # Skip database creation/drop statements
            if re.match(r'(CREATE|DROP)\s+DATABASE', line, re.IGNORECASE) or re.match(r'USE\s+', line, re.IGNORECASE):
                continue

            # Handle DELIMITER changes
            delimiter_match = re.match(r'DELIMITER\s+(\S+)', line)
            if delimiter_match:
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ''

                current_delimiter = delimiter_match.group(1)
                in_delimiter_mode = True if current_delimiter != ';' else False
                continue

            # Add line to current statement
            current_statement += line + '\n'

            # Check if statement is complete
            if line.strip().endswith(current_delimiter):
                # Remove delimiter from the end
                current_statement = current_statement.rstrip('\n')
                if in_delimiter_mode:
                    current_statement = current_statement[:-len(current_delimiter)]
                else:
                    current_statement = current_statement[:-1]  # Remove semicolon

                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ''

        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())

        # Execute statements
        total_statements = len(statements)
        print(f"Found {total_statements} SQL statements to execute")

        # Make sure we're using the right database
        cursor.execute(f"USE `{db_name}`")

        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for i, statement in enumerate(statements, 1):
            try:
                # Print progress
                if i % 10 == 0 or i == 1 or i == total_statements:
                    print(f"Executing statement {i}/{total_statements} ({int(i / total_statements * 100)}%)")

                cursor.execute(statement)
                conn.commit()
            except mariadb.Error as e:
                print(f"Error executing statement {i}: {e}")
                print(f"Statement: {statement[:150]}..." if len(statement) > 150 else f"Statement: {statement}")
                print("Continuing with next statement...")
                # Continue execution despite errors
                conn.rollback()

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        print("Database restoration completed successfully!")

    except IOError as e:
        print(f"Error reading backup file: {e}")
        sys.exit(1)


def verify_restoration(cursor, db_name):
    """
    Verify that database objects were created successfully
    """
    print("\nVerifying database restoration...")

    try:
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Verified {len(tables)} tables were created")
        if tables:
            print("Tables created:")
            for i, table in enumerate(tables):
                print(f"  {i + 1}. {table[0]}")

        # Check routines
        cursor.execute("""
            SELECT routine_type, COUNT(*) 
            FROM information_schema.routines 
            WHERE routine_schema = %s 
            GROUP BY routine_type
        """, (db_name,))
        routines = cursor.fetchall()
        for routine_type, count in routines:
            print(f"Verified {count} {routine_type.lower()}s were created")

        # Check triggers
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.triggers 
            WHERE trigger_schema = %s
        """, (db_name,))
        trigger_count = cursor.fetchone()[0]
        if trigger_count > 0:
            print(f"Verified {trigger_count} triggers were created")

        # Check views
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.views 
            WHERE table_schema = %s
        """, (db_name,))
        view_count = cursor.fetchone()[0]
        if view_count > 0:
            print(f"Verified {view_count} views were created")

    except mariadb.Error as e:
        print(f"Error verifying restored database: {e}")


def restore_database_schema(backup_file_path):
    """
    Main function to restore a database from a schema backup file
    """
    if not os.path.exists(backup_file_path):
        print(f"Error: Backup file {backup_file_path} does not exist")
        sys.exit(1)

    print(f"Using backup file: {backup_file_path}")

    # Extract database name
    db_name = extract_database_name(backup_file_path)
    print(f"Target database name: {db_name}")

    # Connect to MariaDB server (without database)
    conn = connect_to_server()
    cursor = conn.cursor()

    try:
        # Check if database exists
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]

        if db_name in databases:
            print(f"Database '{db_name}' already exists")
            response = input("Do you want to drop and recreate it? (yes/no): ").lower()
            if response == 'yes':
                print(f"Dropping database '{db_name}'...")
                cursor.execute(f"DROP DATABASE `{db_name}`")
                print(f"Creating database '{db_name}'...")
                cursor.execute(f"CREATE DATABASE `{db_name}`")
        else:
            # Create database if it doesn't exist
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE `{db_name}`")

        # Execute the SQL file
        print(f"Restoring schema to database: {db_name}")
        start_time = time.time()

        execute_sql_file(conn, cursor, backup_file_path, db_name)

        # Verify restoration
        verify_restoration(cursor, db_name)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Restoration completed in {duration:.2f} seconds")

    except Exception as e:
        print(f"Error during database restoration: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    print(f"Database '{db_name}' has been successfully restored!")
    return db_name


def find_most_recent_backup(base_dir=".", type_filter=None):
    """
    Scan for backup directories and return the path to the most recent one
    type_filter can be 'schema' or 'data' to filter by backup type
    """
    # Pattern to match backup directories
    if type_filter == 'schema':
        backup_pattern = r'.*_schema_backup_\d{8}_\d{6}\.sql$'
    elif type_filter == 'data':
        backup_pattern = r'.*_data_backup_\d{8}_\d{6}$'
    else:
        backup_pattern = r'.*(schema|data)_backup_\d{8}_\d{6}(.sql)?$'

    import re
    backups = []

    # Walk through directories and files
    for root, dirs, files in os.walk(base_dir):
        # Check directories for data backups
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if re.match(backup_pattern, dir_name):
                # Verify it's a valid backup by checking for metadata file
                if os.path.exists(os.path.join(dir_path, "backup_metadata.json")):
                    # Extract timestamp from directory name
                    timestamp_str = dir_name.split('_backup_')[1]
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        backups.append((dir_path, timestamp, 'data'))
                    except ValueError:
                        continue

        # Check files for schema backups
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if re.match(backup_pattern, file_name) and file_name.endswith('.sql'):
                # Extract timestamp from file name
                timestamp_str = file_name.split('_backup_')[1].split('.')[0]
                try:
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    backups.append((file_path, timestamp, 'schema'))
                except ValueError:
                    continue

    if not backups:
        return None

    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x[1], reverse=True)

    # If type_filter is specified, filter results
    if type_filter:
        filtered_backups = [b for b in backups if b[2] == type_filter]
        if filtered_backups:
            return filtered_backups[0][0]
        return None

    # Return the path to the most recent backup
    return backups[0][0]


def determine_table_order(db_name, backup_dir=None):
    """
    Analyzes database structure to determine optimal table loading order
    This function can be run after schema is restored but before data is loaded
    """
    conn = connect_to_database(db_name)
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No tables found in database")
            return []

        # Get foreign key dependencies
        dependencies = {}
        for table in tables:
            dependencies[table] = []

            # Query to get all foreign key constraints for this table
            cursor.execute("""
                SELECT 
                    REFERENCED_TABLE_NAME
                FROM 
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE
                    REFERENCED_TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (table,))

            for row in cursor.fetchall():
                referenced_table = row[0]
                if referenced_table != table:  # Skip self-references
                    dependencies[table].append(referenced_table)

        # Identify tables with no dependencies (base tables)
        base_tables = []
        for table, deps in dependencies.items():
            if not deps:
                base_tables.append(table)

        # Identify circular dependencies
        circular_tables = set()
        visited = set()

        def find_cycles(node, path=None):
            if path is None:
                path = []

            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                for table in cycle:
                    circular_tables.add(table)
                return True

            if node in visited:
                return False

            visited.add(node)
            path.append(node)

            for dep in dependencies.get(node, []):
                if find_cycles(dep, path[:]):
                    return True

            return False

        for table in tables:
            if table not in visited:
                find_cycles(table)

        # Create optimal loading order
        ordered_tables = []

        # First add tables with no dependencies
        ordered_tables.extend(base_tables)

        # Then add tables that depend only on already added tables
        remaining_tables = [t for t in tables if t not in ordered_tables and t not in circular_tables]
        added = True
        while added and remaining_tables:
            added = False
            for table in list(remaining_tables):
                deps = dependencies.get(table, [])
                if all(dep in ordered_tables for dep in deps):
                    ordered_tables.append(table)
                    remaining_tables.remove(table)
                    added = True

        # Finally add tables with circular dependencies
        ordered_tables.extend(sorted(circular_tables))

        # Save the order to a file in the backup directory if provided
        if backup_dir and os.path.isdir(backup_dir):
            order_file = os.path.join(backup_dir, "table_order.json")
            with open(order_file, 'w') as f:
                json.dump({
                    "ordered_tables": ordered_tables,
                    "circular_tables": list(circular_tables)
                }, f, indent=2)
            print(f"Table order saved to {order_file}")

        return ordered_tables

    except mariadb.Error as e:
        print(f"Error analyzing database structure: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def load_table_order(backup_dir):
    """
    Load the table order from a JSON file in the backup directory
    """
    order_file = os.path.join(backup_dir, "table_order.json")
    if os.path.exists(order_file):
        try:
            with open(order_file, 'r') as f:
                order_data = json.load(f)
                return order_data.get("ordered_tables", []), set(order_data.get("circular_tables", []))
        except Exception as e:
            print(f"Error loading table order: {e}")
    return None, None


def restore_table_data(db_name, backup_dir, tables=None, batch_size=1000, manual_order=None):
    """
    Restore data to tables from backup files
    Uses a smart ordering approach with foreign key constraints disabled
    """
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found.")
        sys.exit(1)

    # Make sure the backup directory contains the expected files
    if not os.path.exists(os.path.join(backup_dir, "backup_metadata.json")):
        print(f"Error: The specified directory doesn't appear to be a valid backup.")
        sys.exit(1)

    conn = connect_to_database(db_name)
    cursor = conn.cursor()

    try:
        # Read backup metadata
        with open(os.path.join(backup_dir, "backup_metadata.json"), 'r') as f:
            metadata = json.load(f)

        print(f"Restoring data from backup created on: {metadata.get('backup_date')}")
        print(f"Original database: {metadata.get('database')}")

        # Find all tables in the backup
        table_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')
                       and not f.endswith('_columns.json')
                       and not f == 'backup_metadata.json'
                       and not f == 'table_dependencies.json'
                       and not f == 'table_order.json']

        all_tables = [os.path.splitext(f)[0] for f in table_files]

        # Determine tables to restore
        if tables is None:
            tables_to_restore = all_tables
        else:
            tables_to_restore = [t for t in tables if t in all_tables]
            missing_tables = [t for t in tables if t not in all_tables]
            if missing_tables:
                print(f"Warning: The following requested tables were not found in the backup: {', '.join(missing_tables)}")

        # Determine the order for restoration
        if manual_order:
            print(f"Using manually specified table order: {', '.join(manual_order)}")
            ordered_tables = [t for t in manual_order if t in tables_to_restore]
        else:
            # First try to load the order from the backup
            ordered_tables, circular_tables = load_table_order(backup_dir)

            # If not available, analyze the database structure
            if not ordered_tables:
                print("Analyzing database structure to determine optimal loading order...")
                ordered_tables = determine_table_order(db_name, backup_dir)

            # Filter to include only tables we're restoring
            ordered_tables = [t for t in ordered_tables if t in tables_to_restore]

            if not ordered_tables:
                # Fallback to alphabetical order if nothing else works
                ordered_tables = sorted(tables_to_restore)

        # Make sure all tables to restore are included
        missing = [t for t in tables_to_restore if t not in ordered_tables]
        if missing:
            ordered_tables.extend(missing)

        print(f"Tables will be restored in this order: {', '.join(ordered_tables)}")

        start_time = datetime.datetime.now()
        successful_tables = []
        failed_tables = []

        # Disable foreign key checks for the entire restoration process
        print("Disabling foreign key checks for all restoration phases")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Process each table in the determined order
        for table_name in ordered_tables:
            table_file = os.path.join(backup_dir, f"{table_name}.json")
            if not os.path.exists(table_file):
                print(f"Warning: Data file for table '{table_name}' not found, skipping.")
                continue

            print(f"\nRestoring data for table: {table_name}")

            # Check if table exists
            try:
                cursor.execute(f"SELECT 1 FROM `{table_name}` LIMIT 1")
            except mariadb.Error as e:
                print(f"Error: Table '{table_name}' does not exist in the database.")
                print("Make sure you've restored the database schema first.")
                failed_tables.append(table_name)
                continue

            # Load column information if available
            columns_file = os.path.join(backup_dir, f"{table_name}_columns.json")
            columns = None
            if os.path.exists(columns_file):
                with open(columns_file, 'r') as f:
                    columns = json.load(f)

            # Load data from backup file
            with open(table_file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error: Could not parse JSON data for table '{table_name}': {e}")
                    failed_tables.append(table_name)
                    continue

            row_count = len(data)
            print(f"Found {row_count} rows to restore")

            if row_count == 0:
                print(f"Table '{table_name}' has no data to restore, skipping.")
                successful_tables.append(table_name)
                continue

            # Clear existing data
            try:
                cursor.execute(f"DELETE FROM `{table_name}`")
                print(f"Cleared existing data from table '{table_name}'")
            except mariadb.Error as e:
                print(f"Warning: Could not clear existing data: {e}")

            # Check for auto-increment fields
            cursor.execute(f"""
                SELECT column_name, extra 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = '{table_name}'
                AND extra LIKE '%auto_increment%'
            """)
            auto_increment_cols = [row[0] for row in cursor.fetchall()]

            # Get all column names for the table
            cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            db_columns = [row[0] for row in cursor.fetchall()]

            # Process data in batches
            total_batches = (row_count + batch_size - 1) // batch_size
            rows_inserted = 0

            for batch_num in range(total_batches):
                batch_start = batch_num * batch_size
                batch_end = min(batch_start + batch_size, row_count)
                batch = data[batch_start:batch_end]

                print(f"Processing batch {batch_num + 1}/{total_batches} ({batch_start + 1}-{batch_end} of {row_count})")

                if not batch:
                    continue

                # Handle potential schema differences
                # Get columns from the first row of data
                sample_row = batch[0]
                data_columns = list(sample_row.keys())

                # Find common columns between data and database schema
                common_columns = [col for col in data_columns if col in db_columns]

                if len(common_columns) < len(data_columns):
                    missing_columns = [col for col in data_columns if col not in db_columns]
                    print(f"Warning: Some columns in the backup data don't exist in the current schema: {', '.join(missing_columns)}")

                if not common_columns:
                    print(f"Error: No matching columns found for table '{table_name}'")
                    failed_tables.append(table_name)
                    break

                # Build INSERT statement with only common columns
                columns_str = ', '.join([f"`{col}`" for col in common_columns])
                placeholders = ', '.join(['%s'] * len(common_columns))

                insert_sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"

                # Extract values in the correct order
                rows_values = []
                for row in batch:
                    row_values = [row.get(col) for col in common_columns]
                    rows_values.append(row_values)

                # Execute batch insert
                try:
                    cursor.executemany(insert_sql, rows_values)
                    conn.commit()
                    rows_inserted += len(batch)
                    print(f"Inserted {len(batch)} rows")
                except mariadb.Error as e:
                    print(f"Error inserting data batch: {e}")
                    # Try individual inserts to identify problematic rows
                    print("Attempting individual row inserts...")
                    batch_success = 0
                    for i, row_values in enumerate(rows_values):
                        try:
                            cursor.execute(insert_sql, row_values)
                            conn.commit()
                            rows_inserted += 1
                            batch_success += 1
                        except mariadb.Error as row_e:
                            print(f"Error with row {batch_start + i + 1}: {row_e}")

                    if batch_success > 0:
                        print(f"Successfully inserted {batch_success} of {len(batch)} rows in this batch")

            if rows_inserted > 0:
                successful_tables.append(table_name)
                print(f"Successfully restored {rows_inserted} of {row_count} rows to table '{table_name}'")

                # Reset auto-increment counter if needed
                if auto_increment_cols and rows_inserted > 0:
                    for col in auto_increment_cols:
                        try:
                            cursor.execute(f"SELECT MAX(`{col}`) + 1 FROM `{table_name}`")
                            next_id = cursor.fetchone()[0]
                            if next_id:
                                cursor.execute(f"ALTER TABLE `{table_name}` AUTO_INCREMENT = {next_id}")
                                print(f"Reset auto_increment value for column '{col}' to {next_id}")
                        except mariadb.Error as e:
                            print(f"Warning: Could not reset auto_increment: {e}")
            else:
                failed_tables.append(table_name)
                print(f"Failed to restore any rows to table '{table_name}'")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("Re-enabled foreign key checks")

        # Print summary
        end_time = datetime.datetime.now()
        duration = end_time - start_time

        print("\n=== Restoration Summary ===")
        print(f"Total time: {duration}")
        print(f"Successfully restored tables: {len(successful_tables)}")
        print(f"Failed tables: {len(failed_tables)}")

        if successful_tables:
            print("\nSuccessful tables:")
            for table in successful_tables:
                print(f"- {table}")

        if failed_tables:
            print("\nFailed tables:")
            for table in failed_tables:
                print(f"- {table}")

        return successful_tables, failed_tables

    except mariadb.Error as e:
        print(f"Error during data restoration: {e}")
        sys.exit(1)
    finally:
        # Ensure foreign key checks are re-enabled
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except:
            pass
        cursor.close()
        conn.close()


def full_database_restore(schema_file, data_dir=None, tables=None, batch_size=1000, manual_order=None):
    """
    Perform a complete database restoration including schema and data
    """
    print("\n=== Starting Full Database Restoration ===")

    # 1. Restore schema
    print("\n--- Phase 1: Schema Restoration ---")
    db_name = restore_database_schema(schema_file)

    # 2. Analyze database structure to determine optimal table loading order
    if not manual_order:
        print("\n--- Phase 2: Table Order Analysis ---")
        ordered_tables = determine_table_order(db_name, data_dir)
        if ordered_tables:
            print(f"Determined optimal table loading order: {', '.join(ordered_tables)}")

    # 3. Restore data if data directory is provided
    if data_dir:
        print("\n--- Phase 3: Data Restoration ---")
        restore_table_data(db_name, data_dir, tables, batch_size, manual_order)

    print("\n=== Full Database Restoration Completed ===")
    return db_name


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