# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.24.2025
# Description:      Pulls Casey's DB schema and saves it for later in a
#                       file called time_tracker_schema_backup_20250424_111010.sql
#                       which can be found in the 'tests' folder
# Input:            none
# Output:           time_tracker_schema_backup_20250424_111010.sql
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.24.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

#!/usr/bin/env python3
"""
MariaDB Schema Backup Script

This script connects to a MariaDB instance and extracts complete schema information
that can be used to recreate the database if it becomes corrupt.
"""

import os
import sys
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


def backup_database_schema(output_file=None):
    """
    Main function to create a complete database schema backup
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Get database name
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]

        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # If no output file specified, create one based on database name and timestamp
        if not output_file:
            output_file = f"{db_name}_schema_backup_{timestamp}.sql"

        print(f"Creating schema backup for database: {db_name}")

        with open(output_file, 'w') as f:
            # Write header
            f.write(f"-- MariaDB Schema Backup for database: {db_name}\n")
            f.write(f"-- Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- This script contains all necessary information to recreate the database structure\n\n")

            # ------------------------
            # Database creation with character set and collation
            # ------------------------
            cursor.execute(f"""
                SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME 
                FROM INFORMATION_SCHEMA.SCHEMATA 
                WHERE SCHEMA_NAME = '{db_name}'
            """)
            charset_info = cursor.fetchone()

            f.write("-- Database recreation statement\n")
            f.write(f"DROP DATABASE IF EXISTS `{db_name}`;\n")
            f.write(f"CREATE DATABASE `{db_name}` ")
            f.write(f"CHARACTER SET {charset_info[0]} ")
            f.write(f"COLLATION {charset_info[1]};\n\n")
            f.write(f"USE `{db_name}`;\n\n")

            # ------------------------
            # Server variables (as comments)
            # ------------------------
            f.write("-- Important server variables\n")
            cursor.execute("""
                SHOW VARIABLES WHERE Variable_name IN (
                    'character_set_server', 'collation_server',
                    'max_connections', 'max_allowed_packet',
                    'innodb_buffer_pool_size', 'innodb_log_file_size',
                    'innodb_file_per_table', 'innodb_flush_log_at_trx_commit',
                    'sync_binlog', 'sql_mode'
                )
            """)
            server_vars = cursor.fetchall()
            for var in server_vars:
                f.write(f"-- {var[0]} = {var[1]}\n")
            f.write("\n")

            # ------------------------
            # Tables
            # ------------------------
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()

            if tables:
                f.write("-- Table structure\n\n")

                for table in tables:
                    table_name = table[0]
                    f.write(f"-- Structure for table `{table_name}`\n")
                    f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")

                    # Get CREATE TABLE statement
                    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                    create_table = cursor.fetchone()[1]
                    f.write(f"{create_table};\n\n")

            # ------------------------
            # Table data stats (as comments)
            # ------------------------
            f.write("-- Table data statistics\n")
            cursor.execute("""
                SELECT 
                    table_name, 
                    table_rows,
                    data_length,
                    index_length
                FROM 
                    information_schema.tables
                WHERE 
                    table_schema = DATABASE()
                    AND table_type = 'BASE TABLE'
                ORDER BY
                    table_name
            """)
            stats = cursor.fetchall()
            for stat in stats:
                table_name = stat[0]
                rows = stat[1] or 0
                data_size_mb = round((stat[2] or 0) / (1024 * 1024), 2)
                index_size_mb = round((stat[3] or 0) / (1024 * 1024), 2)
                f.write(f"-- Table `{table_name}`: ~{rows} rows, Data: {data_size_mb}MB, Indexes: {index_size_mb}MB\n")
            f.write("\n")

            # ------------------------
            # Views
            # ------------------------
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = DATABASE()
                ORDER BY table_name
            """)
            views = cursor.fetchall()

            if views:
                f.write("-- Views\n\n")

                # First drop all views to avoid dependency issues
                for view in views:
                    view_name = view[0]
                    f.write(f"DROP VIEW IF EXISTS `{view_name}`;\n")
                f.write("\n")

                # Then recreate them
                for view in views:
                    view_name = view[0]
                    f.write(f"-- Structure for view `{view_name}`\n")

                    cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
                    create_view = cursor.fetchone()[1]
                    f.write(f"{create_view};\n\n")

            # ------------------------
            # Stored procedures
            # ------------------------
            cursor.execute("""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_schema = DATABASE()
                AND routine_type = 'PROCEDURE'
                ORDER BY routine_name
            """)
            procedures = cursor.fetchall()

            if procedures:
                f.write("-- Stored procedures\n\n")
                f.write("DELIMITER $$\n\n")

                for proc in procedures:
                    proc_name = proc[0]
                    f.write(f"-- Structure for procedure `{proc_name}`\n")
                    f.write(f"DROP PROCEDURE IF EXISTS `{proc_name}`$$\n")

                    cursor.execute(f"SHOW CREATE PROCEDURE `{proc_name}`")
                    create_proc = cursor.fetchone()[2]
                    f.write(f"{create_proc}$$\n\n")

                f.write("DELIMITER ;\n\n")

            # ------------------------
            # Functions
            # ------------------------
            cursor.execute("""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_schema = DATABASE()
                AND routine_type = 'FUNCTION'
                ORDER BY routine_name
            """)
            functions = cursor.fetchall()

            if functions:
                f.write("-- Functions\n\n")
                f.write("DELIMITER $$\n\n")

                for func in functions:
                    func_name = func[0]
                    f.write(f"-- Structure for function `{func_name}`\n")
                    f.write(f"DROP FUNCTION IF EXISTS `{func_name}`$$\n")

                    cursor.execute(f"SHOW CREATE FUNCTION `{func_name}`")
                    create_func = cursor.fetchone()[2]
                    f.write(f"{create_func}$$\n\n")

                f.write("DELIMITER ;\n\n")

            # ------------------------
            # Triggers
            # ------------------------
            cursor.execute("""
                SELECT trigger_name 
                FROM information_schema.triggers 
                WHERE trigger_schema = DATABASE()
                ORDER BY trigger_name
            """)
            triggers = cursor.fetchall()

            if triggers:
                f.write("-- Triggers\n\n")
                f.write("DELIMITER $$\n\n")

                for trigger in triggers:
                    trigger_name = trigger[0]
                    f.write(f"-- Structure for trigger `{trigger_name}`\n")
                    f.write(f"DROP TRIGGER IF EXISTS `{trigger_name}`$$\n")

                    cursor.execute(f"SHOW CREATE TRIGGER `{trigger_name}`")
                    create_trigger = cursor.fetchone()[2]
                    f.write(f"{create_trigger}$$\n\n")

                f.write("DELIMITER ;\n\n")

            # ------------------------
            # Events
            # ------------------------
            cursor.execute("""
                SELECT event_name 
                FROM information_schema.events 
                WHERE event_schema = DATABASE()
                ORDER BY event_name
            """)
            events = cursor.fetchall()

            if events:
                f.write("-- Events\n\n")
                f.write("DELIMITER $$\n\n")

                for event in events:
                    event_name = event[0]
                    f.write(f"-- Structure for event `{event_name}`\n")
                    f.write(f"DROP EVENT IF EXISTS `{event_name}`$$\n")

                    cursor.execute(f"SHOW CREATE EVENT `{event_name}`")
                    create_event = cursor.fetchone()[3]
                    f.write(f"{create_event}$$\n\n")

                f.write("DELIMITER ;\n\n")

            # ------------------------
            # User privileges (as comments)
            # ------------------------
            f.write("-- User privileges (current connection user only)\n")
            try:
                cursor.execute("SHOW GRANTS")
                grants = cursor.fetchall()
                for grant in grants:
                    f.write(f"-- {grant[0]}\n")
            except mariadb.Error as e:
                f.write(f"-- Error retrieving grants: {e}\n")

            # ------------------------
            # Foreign key constraints
            # ------------------------
            cursor.execute("""
                SELECT 
                    table_name,
                    constraint_name
                FROM 
                    information_schema.table_constraints
                WHERE 
                    constraint_type = 'FOREIGN KEY'
                    AND table_schema = DATABASE()
                ORDER BY
                    table_name, constraint_name
            """)
            fks = cursor.fetchall()

            if fks:
                f.write("\n-- Foreign key information\n")
                for fk in fks:
                    table_name = fk[0]
                    constraint_name = fk[1]

                    cursor.execute(f"""
                        SELECT
                            column_name,
                            referenced_table_name,
                            referenced_column_name
                        FROM
                            information_schema.key_column_usage
                        WHERE
                            table_schema = DATABASE()
                            AND table_name = '{table_name}'
                            AND constraint_name = '{constraint_name}'
                    """)
                    fk_details = cursor.fetchall()

                    for detail in fk_details:
                        column = detail[0]
                        ref_table = detail[1]
                        ref_column = detail[2]
                        f.write(f"-- FK: {table_name}.{column} -> {ref_table}.{ref_column} ({constraint_name})\n")
                f.write("\n")

            # ------------------------
            # Indexes
            # ------------------------
            cursor.execute("""
                SELECT 
                    table_name,
                    index_name,
                    GROUP_CONCAT(column_name ORDER BY seq_in_index) as columns,
                    non_unique
                FROM
                    information_schema.statistics
                WHERE
                    table_schema = DATABASE()
                    AND index_name != 'PRIMARY'
                GROUP BY
                    table_name, index_name, non_unique
                ORDER BY
                    table_name, index_name
            """)
            indexes = cursor.fetchall()

            if indexes:
                f.write("-- Index information\n")
                for idx in indexes:
                    table_name = idx[0]
                    index_name = idx[1]
                    columns = idx[2]
                    is_unique = "UNIQUE" if idx[3] == 0 else "INDEX"

                    f.write(f"-- {is_unique}: {table_name}.{index_name} ({columns})\n")
                f.write("\n")

        print(f"Schema backup successfully created: {output_file}")
        return output_file

    except mariadb.Error as e:
        print(f"Error generating schema backup: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a comprehensive MariaDB schema backup')
    parser.add_argument('-o', '--output', help='Output SQL file path')
    args = parser.parse_args()

    print("=== MariaDB Schema Backup Tool ===")
    backup_file = backup_database_schema(args.output)
    print(f"=== Backup complete! Schema saved to: {backup_file} ===")
# **********************************************************************************************************************
# **********************************************************************************************************************
