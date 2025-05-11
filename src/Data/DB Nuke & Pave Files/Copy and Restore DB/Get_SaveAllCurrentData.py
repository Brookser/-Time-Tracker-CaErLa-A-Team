# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.24.2025
# Description:      Discovers all existing data in the DB and then creates
#                       a file of the data so data can be restored
# Input:            none
# Output:           a new time_tracker_data_backup_xxxxxxxx_xxxxxx file folder
#                       within the Data tree
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.05.2025: Initial setup
#                   - 05.11.2025: Updated to also send all data to a single text file to account for an
#                       edge case where the backup file folder system fails or is corrupt
#
# **********************************************************************************************************************
# **********************************************************************************************************************  
# !/usr/bin/env python3
"""
MariaDB Data Backup Script

This script connects to a MariaDB instance and extracts all data from existing tables
to JSON files that can be used to repopulate tables in the event of corruption.
It also creates a consolidated .txt file with all the data.
"""

import os
import sys
import json
import datetime
import mariadb
import argparse
from dotenv import load_dotenv

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


def backup_table_data(output_dir=None):
    """
    Main function to create backups of all data in existing tables
    """
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get database name
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()['DATABASE()']

        # Create timestamp for directory name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # If no output directory specified, create one based on database name and timestamp
        if not output_dir:
            output_dir = f"{db_name}_data_backup_{timestamp}"

        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Creating data backup for database: {db_name}")
        print(f"Backup directory: {output_dir}")

        # Create a metadata file with information about the backup
        metadata = {
            "database": db_name,
            "backup_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "tables": []
        }

        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return output_dir

        # Get table dependencies for restoration order
        cursor.execute("""
            SELECT 
                table_name, 
                referenced_table_name
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE()
            AND referenced_table_name IS NOT NULL
        """)
        dependencies = cursor.fetchall()

        # Save dependencies to a file
        with open(os.path.join(output_dir, "table_dependencies.json"), 'w') as f:
            json.dump(dependencies, f, default=str)

        # Create a single txt file for all data with similar naming convention
        txt_filename = f"{db_name}_all_data_{timestamp}.txt"
        txt_filepath = os.path.join(output_dir, txt_filename)

        # Open the txt file for writing
        with open(txt_filepath, 'w') as txt_file:
            # Write header to txt file
            txt_file.write(f"MariaDB Data Backup for database: {db_name}\n")
            txt_file.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txt_file.write("=" * 80 + "\n\n")

            for table in tables:
                table_name = table['table_name']
                print(f"Processing table: {table_name}")

                # Get number of rows
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                row_count = cursor.fetchone()['count']

                # Add table to metadata
                metadata['tables'].append({
                    "name": table_name,
                    "rows": row_count
                })

                # Write table header to txt file
                txt_file.write(f"TABLE: {table_name}\n")
                txt_file.write(f"ROWS: {row_count}\n")
                txt_file.write("-" * 80 + "\n")

                # Skip empty tables but create an empty file
                if row_count == 0:
                    print(f"  Table {table_name} is empty")
                    with open(os.path.join(output_dir, f"{table_name}.json"), 'w') as f:
                        json.dump([], f)
                    txt_file.write("No data (table is empty)\n\n")
                    continue

                # Get column information for the table
                cursor.execute(f"""
                    SELECT 
                        column_name, 
                        data_type,
                        column_type
                    FROM information_schema.columns
                    WHERE 
                        table_schema = DATABASE()
                        AND table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()

                # Save column metadata for restoration
                with open(os.path.join(output_dir, f"{table_name}_columns.json"), 'w') as f:
                    json.dump(columns, f, default=str)

                # Write column headers to txt file
                column_names = [col['column_name'] for col in columns]
                txt_file.write(f"Columns: {', '.join(column_names)}\n\n")

                # Fetch data in batches to avoid memory issues with large tables
                batch_size = 5000
                total_batches = (row_count + batch_size - 1) // batch_size  # Ceiling division

                print(f"  Exporting {row_count} rows in {total_batches} batch(es)")

                # Open file for writing JSON
                with open(os.path.join(output_dir, f"{table_name}.json"), 'w') as f:
                    f.write('[\n')  # Start JSON array

                    for batch_num in range(total_batches):
                        offset = batch_num * batch_size
                        print(f"  Batch {batch_num + 1}/{total_batches}")

                        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {batch_size} OFFSET {offset}")
                        batch_data = cursor.fetchall()

                        # Write batch data to JSON file
                        for i, row in enumerate(batch_data):
                            json_str = json.dumps(row, default=str)
                            # Add comma if not the last row of the last batch
                            if batch_num < total_batches - 1 or i < len(batch_data) - 1:
                                f.write(f"  {json_str},\n")
                            else:
                                f.write(f"  {json_str}\n")

                            # Write data to txt file in a readable format
                            txt_file.write(f"Row {offset + i + 1}: {json_str}\n")

                    f.write(']')  # End JSON array

                # Add a separator between tables in txt file
                txt_file.write("\n" + "=" * 80 + "\n\n")

        # Save metadata
        with open(os.path.join(output_dir, "backup_metadata.json"), 'w') as f:
            json.dump(metadata, f, default=str, indent=2)

        # Create a README file with instructions for restoration
        with open(os.path.join(output_dir, "README.txt"), 'w') as f:
            f.write(f"MariaDB Data Backup for database: {db_name}\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("This directory contains JSON files with data from all tables in the database.\n")
            f.write("Use these files to restore data after recreating the database schema.\n\n")
            f.write("Files:\n")
            f.write("- backup_metadata.json: Information about this backup\n")
            f.write("- table_dependencies.json: Table relationships for proper restoration order\n")
            f.write("- [table_name].json: Data for each table\n")
            f.write("- [table_name]_columns.json: Column information for each table\n")
            f.write(f"- {txt_filename}: All table data in a single text file\n\n")
            f.write("Note: This backup contains ONLY the data, not the schema.\n")
            f.write("Use the schema backup script to recreate the database structure first.\n")

        print(f"\nData backup successfully created in directory: {output_dir}")
        print(f"All data also written to: {txt_filepath}")
        print(f"Total tables processed: {len(tables)}")
        return output_dir

    except mariadb.Error as e:
        print(f"Error generating data backup: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create data backups of all MariaDB tables')
    parser.add_argument('-o', '--output', help='Output directory for backup files')
    args = parser.parse_args()

    print("=== MariaDB Table Data Backup Tool ===")
    backup_file = backup_table_data(args.output)
    print(f"=== Backup complete! Data saved to: {backup_file} ===")

# **********************************************************************************************************************
# **********************************************************************************************************************
