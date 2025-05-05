# **********************************************************************************************************************
# **********************************************************************************************************************
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Discovers existing tables in DB, then drops all tables
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 04.20.2025: Initial setup of tests
#
# **********************************************************************************************************************
# **********************************************************************************************************************


# *******************************
#  🔹 PROJECT QUERIES - CONTINUED
# written on 5.4.2025 - EAB
# *******************************

@classmethod
def deactivate_project(cls, projectid):
    """
    Deactivates a project by setting PROJECT_ACTIVE to 0.

    Args:
        projectid: The ID of the project to deactivate
    """
    cursor = cls.get_cursor()
    cursor.execute('''
        UPDATE projects
        SET PROJECT_ACTIVE = 0
        WHERE PROJECTID = ?
    ''', (projectid,))
    cls.commit()


@classmethod
def activate_project(cls, projectid):
    """
    Activates a project by setting PROJECT_ACTIVE to 1.

    Args:
        projectid: The ID of the project to activate
    """
    cursor = cls.get_cursor()
    cursor.execute('''
        UPDATE projects
        SET PROJECT_ACTIVE = 1
        WHERE PROJECTID = ?
    ''', (projectid,))
    cls.commit()

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

    # ======================
    # 🔹 TimeEntry Queries - Continued
    # written on 5.4.2025 - EAB
    # *******************************

# so DemoData.py can run correctly
    @classmethod
    def erikas_add_time_entry(cls, empid, projectid, start_time, stop_time, notes, manual_entry):
        cursor = cls.get_cursor()

        # Try a simple insert first
        try:
            cursor.execute('''
                INSERT INTO time (EMPID, PROJECTID, START_TIME, STOP_TIME, MANUAL_ENTRY)
                VALUES (%s, %s, %s, %s, %s)
            ''', (empid, projectid, start_time, stop_time, manual_entry))
            cls.commit()
            print("Simple insert successful!")
        except Exception as e:
            print(f"Simple insert failed: {e}")

        # Now try with notes
        try:
            cursor.execute('''
                INSERT INTO time (EMPID, PROJECTID, START_TIME, STOP_TIME, NOTES, MANUAL_ENTRY)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (empid, projectid, start_time, stop_time, notes, manual_entry))
            cls.commit()
            print("Full insert successful!")
        except Exception as e:
            print(f"Full insert failed: {e}")

    # ****************************
    # end of 5.4.2025 update - EAB
    # ****************************

# ****************************

# **********************************************************************************************************************
# **********************************************************************************************************************
