MariaDB Data Backup for database: time_tracker
Generated on: 2025-05-12 11:18:28

This directory contains JSON files with data from all tables in the database.
Use these files to restore data after recreating the database schema.

Files:
- backup_metadata.json: Information about this backup
- table_dependencies.json: Table relationships for proper restoration order
- [table_name].json: Data for each table
- [table_name]_columns.json: Column information for each table
- time_tracker_all_data_20250512_111828.txt: All table data in a single text file

Note: This backup contains ONLY the data, not the schema.
Use the schema backup script to recreate the database structure first.
