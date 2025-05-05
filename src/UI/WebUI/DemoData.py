# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:
# Date:             05.04.2025
# Description:      Changes to DB can be processed here
# Input:
# Output:
# Sources:
#
# Change Log:       - 05.04.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************
import os
import sys
import mariadb
import datetime
from dotenv import load_dotenv
from datetime import datetime
from src.Data.Database import Database

# Load environment variables from .env file
load_dotenv()

# Custom writer class to capture print statements
class CustomWriter:
    def __init__(self, file):
        self.file = file

    def write(self, text):
        self.file.write(text)

    def flush(self):
        self.file.flush()


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


def calculate_minutes(start_time, stop_time):
    """
    Calculate the time difference in minutes between start_time and stop_time
    """
    format_str = "%Y-%m-%d %H:%M:%S"
    start_dt = datetime.strptime(start_time, format_str)
    stop_dt = datetime.strptime(stop_time, format_str)

    # Calculate the difference in minutes
    diff_minutes = int((stop_dt - start_dt).total_seconds() / 60)
    return diff_minutes

def populate_demo_data():
    """
    Function to populate the database with the additional data from the images
    """
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Temporarily disable foreign key checks
        print("Temporarily disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Start transaction
        conn.autocommit = False

        print("\nPopulating time table...")
        time_entries = [
            # (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
            # 5/4/25 data set:
            ('DD5001', 'E004', 'SD0001', '2025-05-04 11:53:00', '2025-05-04 13:35:00', 'Organic local groupware', 0),
            ('DD5002', 'E004', 'SD0002', '2025-05-04 10:01:00', '2025-05-04 10:35:00', 'Managed optimizing contingency', 0),
            ('DD5003', 'E004', 'SD0005', '2025-05-04 10:54:00', '2025-05-04 11:08:00', 'Mandatory contextually-based paradigm', 0),
            ('DD5004', 'E015', 'SD0001', '2025-05-04 11:55:00', '2025-05-04 12:26:00', 'Cross-platform asynchronous open architecture', 0),
            ('DD5005', 'E015', 'SD0004', '2025-05-04 11:14:00', '2025-05-04 12:09:00', 'Optimized systemic monitoring', 0),
            ('DD5006', 'E015', 'P002', '2025-05-04 08:57:00', '2025-05-04 12:02:00', 'Sharable bifurcated analyzer', 0),
            ('DD5007', 'E015', 'SD0007', '2025-05-04 10:11:00', '2025-05-04 11:58:00', 'Business-focused 5th generation software', 0),
            ('DD5008', 'E9001', 'SD0002', '2025-05-04 11:27:00', '2025-05-04 12:39:00', 'User-friendly directional complexity', 0),
            ('DD5009', 'E9001', 'SD0005', '2025-05-04 11:57:00', '2025-05-04 12:56:00', 'Future-proofed multi-tasking ability', 0),
            ('DD5010', 'E9001', 'SD0004', '2025-05-04 10:52:00', '2025-05-04 11:35:00', 'Optional encompassing throughput', 0),
            ('DD5011', 'E9001', 'P10007', '2025-05-04 11:00:00', '2025-05-04 11:33:00', 'Function-based 24 hour Graphical User Interface', 0),
            ('DD5012', 'E9003', 'P10001', '2025-05-04 10:03:00', '2025-05-04 13:14:00', 'Profit-focused zero administration complexity', 0),
            ('DD5013', 'E9003', 'SD0002', '2025-05-04 10:04:00', '2025-05-04 11:27:00', 'Multi-layered scalable benchmark', 0),
            ('DD5014', 'E9003', 'SD0005', '2025-05-04 10:37:00', '2025-05-04 12:49:00', 'Realigned background extranet', 0),
            ('DD5015', 'E9003', 'P002', '2025-05-04 10:39:00', '2025-05-04 12:18:00', 'Profit-focused hybrid flexibility', 0),
            ('DD5016', 'E9004', 'SD0004', '2025-05-04 11:58:00', '2025-05-04 12:56:00', 'Multi-layered user-facing middleware', 0),
            ('DD5017', 'E9004', 'SD0005', '2025-05-04 10:06:00', '2025-05-04 11:45:00', 'Reverse-engineered intangible intranet', 0),
            ('DD5018', 'E9004', 'SD0007', '2025-05-04 11:48:00', '2025-05-04 13:17:00', 'Persistent coherent functionalities', 0),
            ('DD5019', 'E9004', 'SD0001', '2025-05-04 10:12:00', '2025-05-04 12:07:00', 'Synchronized zero tolerance migration', 0),
            ('DD5020', 'E9005', 'SD0001', '2025-05-04 09:53:00', '2025-05-04 11:52:00', 'Streamlined national toolset', 0),
            ('DD5021', 'E004', 'P002', '2025-05-04 10:03:00', '2025-05-04 10:53:00', 'Cloned stable flexibility', 0),
            ('DD5022', 'E015', 'SD0002', '2025-05-04 12:05:00', '2025-05-04 12:49:00', 'Fully-configurable directional access', 0),
            ('DD5023', 'E9001', 'SD0007', '2025-05-04 10:16:00', '2025-05-04 11:39:00', 'Ameliorated system-worthy conglomeration', 0),
            ('DD5024', 'E9003', 'P001', '2025-05-04 11:43:00', '2025-05-04 12:56:00', 'Distributed multimedia strategy', 0),
            ('DD5025', 'E9004', 'P10001', '2025-05-04 12:04:00', '2025-05-04 13:11:00', 'Future-proofed transitional archive', 0),
            ('DD5026', 'E9006', 'P001', '2025-05-04 10:19:00', '2025-05-04 10:37:00', 'Multi-lateral interactive process improvement', 0),
            ('DD5027', 'E004', 'SD0007', '2025-05-04 10:31:00', '2025-05-04 12:14:00', 'Optimized bifurcated challenge', 0),
            ('DD5028', 'E004', 'P001', '2025-05-04 10:06:00', '2025-05-04 12:07:00', 'Sharable asynchronous customer loyalty', 0),
            ('DD5029', 'E004', 'SD0001', '2025-05-04 10:08:00', '2025-05-04 11:47:00', 'Team-oriented directional time-frame', 0),
            ('DD5030', 'E004', 'SD0002', '2025-05-04 09:51:00', '2025-05-04 10:49:00', 'Multi-layered actuating internet service-desk', 0),
            ('DD5031', 'E004', 'SD0005', '2025-05-04 10:06:00', '2025-05-04 10:20:00', 'Diverse content-based initiative', 0),
            ('DD5032', 'E015', 'SD0001', '2025-05-04 11:08:00', '2025-05-04 12:09:00', 'Balanced 24 hour productivity', 0),
            ('DD5033', 'E015', 'SD0004', '2025-05-04 12:03:00', '2025-05-04 12:58:00', 'Object-based web-enabled implementation', 0),
            ('DD5034', 'E015', 'P002', '2025-05-04 10:34:00', '2025-05-04 12:39:00', 'Synergized leading edge alliance', 0),
            ('DD5035', 'E015', 'SD0007', '2025-05-04 09:51:00', '2025-05-04 11:38:00', 'Re-engineered web-enabled productivity', 0),
            ('DD5036', 'E9001', 'SD0002', '2025-05-04 11:34:00', '2025-05-04 12:46:00', 'Profound disintermediate synergy', 0),
            ('DD5037', 'E9001', 'SD0005', '2025-05-04 11:54:00', '2025-05-04 13:13:00', 'Optional explicit intranet', 0),
            ('DD5038', 'E9001', 'SD0004', '2025-05-04 09:59:00', '2025-05-04 10:42:00', 'Robust analyzing customer loyalty', 0),
            ('DD5039', 'E9001', 'P10007', '2025-05-04 10:04:00', '2025-05-04 11:33:00', 'Extended intangible interface', 0),
            ('DD5040', 'E9003', 'P10001', '2025-05-04 12:03:00', '2025-05-04 13:14:00', 'Reduced radical strategy', 0),
            ('DD5041', 'E9003', 'SD0002', '2025-05-04 10:27:00', '2025-05-04 11:50:00', 'Decentralized stable flexibility', 0),
            ('DD5042', 'E9003', 'SD0005', '2025-05-04 10:06:00', '2025-05-04 12:18:00', 'Sharable client-server open architecture', 0),
            ('DD5043', 'E9003', 'P002', '2025-05-04 10:17:00', '2025-05-04 11:59:00', 'Managed full-range emulation', 0),
            ('DD5044', 'E9004', 'SD0004', '2025-05-04 11:16:00', '2025-05-04 11:50:00', 'Progressive object-oriented portal', 0),
            ('DD5045', 'E9004', 'SD0005', '2025-05-04 11:35:00', '2025-05-04 11:49:00', 'Centralized contextually-based portal', 0),
            ('DD5046', 'E9004', 'SD0007', '2025-05-04 10:43:00', '2025-05-04 11:44:00', 'Digitized optimizing parallelism', 0),
            ('DD5047', 'E9004', 'SD0001', '2025-05-04 11:43:00', '2025-05-04 12:38:00', 'Fundamental secondary customer loyalty', 0),
            ('DD5048', 'E9006', 'SD0004', '2025-05-04 09:52:00', '2025-05-04 11:52:00', 'Down-sized actuating superstructure', 0),
            ('DD5049', 'E004', 'P002', '2025-05-04 10:42:00', '2025-05-04 12:29:00', 'Organized motivating implementation', 0),
            ('DD5050', 'E015', 'SD0006', '2025-05-04 10:45:00', '2025-05-04 11:57:00', 'Decentralized leading definition', 0),
            ('DD5051', 'E9001', 'SD0007', '2025-05-04 09:57:00', '2025-05-04 11:16:00', 'Organized content-based focus group', 0),
            ('DD5052', 'E9003', 'P001', '2025-05-04 11:17:00', '2025-05-04 12:20:00', 'Networked 3rd generation time-frame', 0),
            ('DD5053', 'E9004', 'P10001', '2025-05-04 10:24:00', '2025-05-04 10:57:00', 'Right-sized context-sensitive architecture', 0),
            ('DD5054', 'E9006', 'P001', '2025-05-04 11:07:00', '2025-05-04 12:18:00', 'Object-based demand-driven challenge', 0),
            ('DD5055', 'E004', 'SD0007', '2025-05-04 11:31:00', '2025-05-04 12:54:00', 'Proactive fault-tolerant capacity', 0),
            ('DD5056', 'E004', 'P001', '2025-05-04 10:04:00', '2025-05-04 12:16:00', 'Expanded value-added open architecture', 0)
            # ********************
            # ********************
            # 5/5/25 data set:
            # ('DD5001', 'E004', 'SD0001', '2025-05-05 11:53:00', '2025-05-05 13:35:00', 'Organic local groupware', 0),
            # ('DD5002', 'E004', 'SD0002', '2025-05-05 10:01:00', '2025-05-05 10:35:00', 'Managed optimizing contingency', 0),
            # ('DD5003', 'E004', 'SD0005', '2025-05-05 10:54:00', '2025-05-05 11:08:00', 'Mandatory contextually-based paradigm', 0),
            # ('DD5004', 'E015', 'SD0001', '2025-05-05 11:55:00', '2025-05-05 12:26:00', 'Cross-platform asynchronous open architecture', 0),
            # ('DD5005', 'E015', 'SD0004', '2025-05-05 11:14:00', '2025-05-05 12:09:00', 'Optimized systemic monitoring', 0),
            # ('DD5006', 'E015', 'P002', '2025-05-05 08:57:00', '2025-05-05 12:02:00', 'Sharable bifurcated analyzer', 0),
            # ('DD5007', 'E015', 'SD0007', '2025-05-05 10:11:00', '2025-05-05 11:58:00', 'Business-focused 5th generation software', 0),
            # ('DD5008', 'E9001', 'SD0002', '2025-05-05 11:27:00', '2025-05-05 12:39:00', 'User-friendly directional complexity', 0),
            # ('DD5009', 'E9001', 'SD0005', '2025-05-05 11:57:00', '2025-05-05 12:56:00', 'Future-proofed multi-tasking ability', 0),
            # ('DD5010', 'E9001', 'SD0004', '2025-05-05 10:52:00', '2025-05-05 11:35:00', 'Optional encompassing throughput', 0),
            # ('DD5011', 'E9001', 'P10007', '2025-05-05 11:00:00', '2025-05-05 11:33:00', 'Function-based 24 hour Graphical User Interface', 0),
            # ('DD5012', 'E9003', 'P10001', '2025-05-05 10:03:00', '2025-05-05 13:14:00', 'Profit-focused zero administration complexity', 0),
            # ('DD5013', 'E9003', 'SD0002', '2025-05-05 10:04:00', '2025-05-05 11:27:00', 'Multi-layered scalable benchmark', 0),
            # ('DD5014', 'E9003', 'SD0005', '2025-05-05 10:37:00', '2025-05-05 12:49:00', 'Realigned background extranet', 0),
            # ('DD5015', 'E9003', 'P002', '2025-05-05 10:39:00', '2025-05-05 12:18:00', 'Profit-focused hybrid flexibility', 0),
            # ('DD5016', 'E9004', 'SD0004', '2025-05-05 11:58:00', '2025-05-05 12:56:00', 'Multi-layered user-facing middleware', 0),
            # ('DD5017', 'E9004', 'SD0005', '2025-05-05 10:06:00', '2025-05-05 11:45:00', 'Reverse-engineered intangible intranet', 0),
            # ('DD5018', 'E9004', 'SD0007', '2025-05-05 11:48:00', '2025-05-05 13:17:00', 'Persistent coherent functionalities', 0),
            # ('DD5019', 'E9004', 'SD0001', '2025-05-05 10:12:00', '2025-05-05 12:07:00', 'Synchronized zero tolerance migration', 0),
            # ('DD5020', 'E9005', 'SD0001', '2025-05-05 09:53:00', '2025-05-05 11:52:00', 'Streamlined national toolset', 0),
            # ('DD5021', 'E004', 'P002', '2025-05-05 10:03:00', '2025-05-05 10:53:00', 'Cloned stable flexibility', 0),
            # ('DD5022', 'E015', 'SD0002', '2025-05-05 12:05:00', '2025-05-05 12:49:00', 'Fully-configurable directional access', 0),
            # ('DD5023', 'E9001', 'SD0007', '2025-05-05 10:16:00', '2025-05-05 11:39:00', 'Ameliorated system-worthy conglomeration', 0),
            # ('DD5024', 'E9003', 'P001', '2025-05-05 11:43:00', '2025-05-05 12:56:00', 'Distributed multimedia strategy', 0),
            # ('DD5025', 'E9004', 'P10001', '2025-05-05 12:04:00', '2025-05-05 13:11:00', 'Future-proofed transitional archive', 0),
            # ('DD5026', 'E9006', 'P001', '2025-05-05 10:19:00', '2025-05-05 10:37:00', 'Multi-lateral interactive process improvement', 0),
            # ('DD5027', 'E004', 'SD0007', '2025-05-05 10:31:00', '2025-05-05 12:14:00', 'Optimized bifurcated challenge', 0),
            # ('DD5028', 'E004', 'P001', '2025-05-05 10:06:00', '2025-05-05 12:07:00', 'Sharable asynchronous customer loyalty', 0),
            # ('DD5029', 'E004', 'SD0001', '2025-05-05 10:08:00', '2025-05-05 11:47:00', 'Team-oriented directional time-frame', 0),
            # ('DD5030', 'E004', 'SD0002', '2025-05-05 09:51:00', '2025-05-05 10:49:00', 'Multi-layered actuating internet service-desk', 0),
            # ('DD5031', 'E004', 'SD0005', '2025-05-05 10:06:00', '2025-05-05 10:20:00', 'Diverse content-based initiative', 0),
            # ('DD5032', 'E015', 'SD0001', '2025-05-05 11:08:00', '2025-05-05 12:09:00', 'Balanced 24 hour productivity', 0),
            # ('DD5033', 'E015', 'SD0004', '2025-05-05 12:03:00', '2025-05-05 12:58:00', 'Object-based web-enabled implementation', 0),
            # ('DD5034', 'E015', 'P002', '2025-05-05 10:34:00', '2025-05-05 12:39:00', 'Synergized leading edge alliance', 0),
            # ('DD5035', 'E015', 'SD0007', '2025-05-05 09:51:00', '2025-05-05 11:38:00', 'Re-engineered web-enabled productivity', 0),
            # ('DD5036', 'E9001', 'SD0002', '2025-05-05 11:34:00', '2025-05-05 12:46:00', 'Profound disintermediate synergy', 0),
            # ('DD5037', 'E9001', 'SD0005', '2025-05-05 11:54:00', '2025-05-05 13:13:00', 'Optional explicit intranet', 0),
            # ('DD5038', 'E9001', 'SD0004', '2025-05-05 09:59:00', '2025-05-05 10:42:00', 'Robust analyzing customer loyalty', 0),
            # ('DD5039', 'E9001', 'P10007', '2025-05-05 10:04:00', '2025-05-05 11:33:00', 'Extended intangible interface', 0),
            # ('DD5040', 'E9003', 'P10001', '2025-05-05 12:03:00', '2025-05-05 13:14:00', 'Reduced radical strategy', 0),
            # ('DD5041', 'E9003', 'SD0002', '2025-05-05 10:27:00', '2025-05-05 11:50:00', 'Decentralized stable flexibility', 0),
            # ('DD5042', 'E9003', 'SD0005', '2025-05-05 10:06:00', '2025-05-05 12:18:00', 'Sharable client-server open architecture', 0),
            # ('DD5043', 'E9003', 'P002', '2025-05-05 10:17:00', '2025-05-05 11:59:00', 'Managed full-range emulation', 0),
            # ('DD5044', 'E9004', 'SD0004', '2025-05-05 11:16:00', '2025-05-05 11:50:00', 'Progressive object-oriented portal', 0),
            # ('DD5045', 'E9004', 'SD0005', '2025-05-05 11:35:00', '2025-05-05 11:49:00', 'Centralized contextually-based portal', 0),
            # ('DD5046', 'E9004', 'SD0007', '2025-05-05 10:43:00', '2025-05-05 11:44:00', 'Digitized optimizing parallelism', 0),
            # ('DD5047', 'E9004', 'SD0001', '2025-05-05 11:43:00', '2025-05-05 12:38:00', 'Fundamental secondary customer loyalty', 0),
            # ('DD5048', 'E9006', 'SD0004', '2025-05-05 09:52:00', '2025-05-05 11:52:00', 'Down-sized actuating superstructure', 0),
            # ('DD5049', 'E004', 'P002', '2025-05-05 10:42:00', '2025-05-05 12:29:00', 'Organized motivating implementation', 0),
            # ('DD5050', 'E015', 'SD0006', '2025-05-05 10:45:00', '2025-05-05 11:57:00', 'Decentralized leading definition', 0),
            # ('DD5051', 'E9001', 'SD0007', '2025-05-05 09:57:00', '2025-05-05 11:16:00', 'Organized content-based focus group', 0),
            # ('DD5052', 'E9003', 'P001', '2025-05-05 11:17:00', '2025-05-05 12:20:00', 'Networked 3rd generation time-frame', 0),
            # ('DD5053', 'E9004', 'P10001', '2025-05-05 10:24:00', '2025-05-05 10:57:00', 'Right-sized context-sensitive architecture', 0),
            # ('DD5054', 'E9006', 'P001', '2025-05-05 11:07:00', '2025-05-05 12:18:00', 'Object-based demand-driven challenge', 0),
            # ('DD5055', 'E004', 'SD0007', '2025-05-05 11:31:00', '2025-05-05 12:54:00', 'Proactive fault-tolerant capacity', 0),
            # ('DD5056', 'E004', 'P001', '2025-05-05 10:04:00', '2025-05-05 12:16:00', 'Expanded value-added open architecture', 0)

        ]

        for entry in time_entries:
            try:
                # Parse dates for calculation of TOTAL_MINUTES
                start_time = datetime.strptime(entry[3], "%Y-%m-%d %H:%M:%S")  # Changed from entry[2] to entry[3]
                stop_time = datetime.strptime(entry[4], "%Y-%m-%d %H:%M:%S")  # Changed from entry[3] to entry[4]

                # Calculate minutes
                minutes_diff = int((stop_time - start_time).total_seconds() / 60)

                cursor.execute("""
                                    INSERT INTO time (TIMEID, EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6]))
                print(f"  Added time entry for {entry[1]}, duration: {minutes_diff} minutes")
            except mariadb.Error as e:
                print(f"  Error adding time entry for {entry[1]}: {e}")

            # Re-enable foreign key checks
        print("\nRe-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Commit the transaction
        conn.commit()
        print("\nAll additional data has been successfully inserted!")

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error during database population: {e}")
        print("All changes have been rolled back")
        sys.exit(1)
    finally:
        # Make sure foreign key checks are re-enabled even if an error occurs
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except:
            pass

        cursor.close()
        conn.close()


# *********************************
# *********************************
# *********************************

def deactivate_projects_range():
    """Deactivate projects from P10026 through P10046"""

    # Generate the list of project IDs to deactivate
    start_id = 10026
    end_id = 10046

    projects_to_deactivate = [f"P{id}" for id in range(start_id, end_id + 1)]

    successful_deactivations = 0
    failed_deactivations = 0

    print(f"Starting to deactivate projects from P{start_id} to P{end_id}...")

    for project_id in projects_to_deactivate:
        try:
            Database.deactivate_project(project_id)
            print(f"Successfully deactivated project: {project_id}")
            successful_deactivations += 1
        except Exception as e:
            print(f"Error deactivating project {project_id}: {e}")
            failed_deactivations += 1

    print(f"\nDeactivation complete:")
    print(f"Successfully deactivated: {successful_deactivations} projects")
    print(f"Failed to deactivate: {failed_deactivations} projects")
    print(f"Total projects processed: {len(projects_to_deactivate)}")






def update_managers_to_e9006():
    """Update all employees' MGR_EMPID to E9006"""
    # List of employees to update
    employees = ['E015', 'E9001', 'E9003', 'E9004', 'E9005', 'E9006']

    # Update each employee's manager to E9006
    for emp_id in employees:
        Database.update_employee_manager(emp_id, 'E9006')

    print(f"Successfully updated {len(employees)} employees to have manager E9006")


def add_departments():
    """Add departments to the database"""
    departments = [
        # (DPTID, DPT_NAME, MANAGERID, DPT_ACTIVE)
        ('D002', 'Sales', 'E9003', 1),
        ('D003', 'Popcorn Making', 'E9006', 1)
    ]

    for dept in departments:
        dptid, dpt_name, manager_id, active = dept
        try:
            Database.add_department(
                dptid=dptid,
                dpt_name=dpt_name,
                manager_id=manager_id,
                active=active
            )
            print(f"Successfully added department: {dpt_name} (ID: {dptid})")
        except Exception as e:
            print(f"Error adding department {dpt_name}: {e}")

    print("Finished adding departments")


def add_projects():
    """Add projects to the database"""
    projects = [
        # (PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
        ('Recipes', 'E015', '2025-05-04', None, 1),
        ('Fish', 'E9001', '2025-05-04', None, 1),
        ('Birds', 'E9003', '2025-05-04', None, 1),
        ('Plants', 'E9004', '2025-05-04', None, 1),
        ('Games', 'E9006', '2025-05-04', None, 1),
        ('Exercise', 'E004', '2025-05-04', None, 1),
        ('Languages', 'E004', '2025-05-04', None, 1)
    ]
    # First, let's check what's currently in the projects table
    cursor = Database.get_cursor()
    cursor.execute("SELECT PROJECTID FROM projects")
    existing_projects = cursor.fetchall()
    print("Existing project IDs:", existing_projects)

    for project in projects:
        name, created_by, date_created, prior_projectid, active = project
        try:
            # Let's explicitly handle the PROJECTID generation
            cursor = Database.get_cursor()

            # Get the next valid project ID
            cursor.execute("""
                    SELECT COALESCE(MAX(CAST(SUBSTRING(PROJECTID, 2) AS UNSIGNED)), 10000) + 1
                    FROM projects
                    WHERE PROJECTID REGEXP '^P[0-9]+$'
                """)
            next_id = cursor.fetchone()[0]
            project_id = f'P{next_id}'

            print(f"Generated project ID: {project_id} for project: {name}")

            # Now insert with the explicit project ID
            cursor.execute('''
                    INSERT INTO projects 
                    (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (project_id, name, created_by, date_created, prior_projectid, active))
            Database.commit()

            print(f"Successfully added project: {name} with ID: {project_id}")
        except Exception as e:
            print(f"Error adding project {name}: {e}")
            import traceback
            traceback.print_exc()

    print("Finished adding projects")

    for project in projects:
        name, created_by, date_created, prior_projectid, active = project
        try:
            # The add_project method expects a PROJECTID, but based on your schema
            # it should be auto-generated by the trigger, so we'll pass None
            Database.add_project(
                projectid=None,  # Will be auto-generated by trigger
                name=name,
                created_by=created_by,
                date_created=date_created,
                prior_projectid=prior_projectid,
                active=active
            )
            print(f"Successfully added project: {name}")
        except Exception as e:
            print(f"Error adding project {name}: {e}")

    print("Finished adding projects")




def add_employee_projects_data():
    """Add employee-project relationships to the database"""
    employee_projects = [
        ('E004', 'SD0001'),
        ('E004', 'SD0002'),
        ('E004', 'SD0005'),
        ('E015', 'SD0001'),
        ('E015', 'SD0004'),
        ('E015', 'P002'),
        ('E015', 'SD0007'),
        ('E9001', 'SD0002'),
        ('E9001', 'SD0005'),
        ('E9001', 'SD0004'),
        ('E9001', 'P10007'),
        ('E9003', 'P10001'),
        ('E9003', 'SD0002'),
        ('E9003', 'SD0005'),
        ('E9003', 'P002'),
        ('E9004', 'SD0004'),
        ('E9004', 'SD0005'),
        ('E9004', 'SD0007'),
        ('E9004', 'SD0001'),
        ('E9006', 'SD0004'),
        ('E004', 'P002'),
        ('E015', 'SD0006'),
        ('E9001', 'SD0007'),
        ('E9003', 'P001'),
        ('E9004', 'P10001'),
        ('E9006', 'P001'),
        ('E004', 'SD0007'),
        ('E004', 'P001')
    ]

    for empid, project_id in employee_projects:
        try:
            Database.add_employee_project(empid=empid, project_id=project_id)
            print(f"Successfully added employee {empid} to project {project_id}")
        except Exception as e:
            print(f"Error adding employee {empid} to project {project_id}: {e}")

    print(f"Finished adding {len(employee_projects)} employee-project relationships")


def add_special_projects():
    """Add special SD projects to the database"""
    special_projects = [
        ('SD0001', 'Special Development 1', 'E015', '2025-05-04 00:00:00', None, 1),
        ('SD0002', 'Special Development 2', 'E015', '2025-05-04 00:00:00', None, 1),
        ('SD0004', 'Special Development 4', 'E015', '2025-05-04 00:00:00', None, 1),
        ('SD0005', 'Special Development 5', 'E015', '2025-05-04 00:00:00', None, 1),
        ('SD0006', 'Special Development 6', 'E015', '2025-05-04 00:00:00', None, 1),
        ('SD0007', 'Special Development 7', 'E015', '2025-05-04 00:00:00', None, 1),
    ]

    for project_id, name, created_by, date_created, prior_projectid, active in special_projects:
        try:
            # Insert with explicit project ID (not auto-generated)
            cursor = Database.get_cursor()
            cursor.execute('''
                INSERT INTO projects 
                (PROJECTID, PROJECT_NAME, CREATED_BY, DATE_CREATED, PRIOR_PROJECTID, PROJECT_ACTIVE)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, name, created_by, date_created, prior_projectid, active))
            Database.commit()
            print(f"Successfully added special project: {project_id} - {name}")
        except Exception as e:
            print(f"Error adding special project {project_id}: {e}")

    print("Finished adding special projects")





# ***** SAMPLE CODE
# ***** UPDATES ALL EMPLOYEES IN employee_table to have the same MGR_EMPID
#
#  Or more simply, update all at once:
# def update_all_managers_to_e9006():
#     """Update all employees' MGR_EMPID to E9006"""
#     Database.update_all_employees_manager('E9006')
#     print("Successfully updated all employees to have manager E9006")

# *****
# ***** Run commands below this line; uncomment to run
# *****

# Completed
# update_managers_to_e9006()
# add_departments()

# Run the function


# DO NOT RUN THESE
# add_projects()
# add_employee_projects_data()
# deactivate_projects_range()

# correction for error in initial code:
# Run this function first
# add_special_projects()
populate_demo_data()
# **********************************************************************************************************************
# **********************************************************************************************************************
