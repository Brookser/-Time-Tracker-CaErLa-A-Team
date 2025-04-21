# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             04.20.2025
# Description:      Example: runs tests to:
#                   • count number of required password resets
#                   • retrieve inactive projects from the database
#                   •
#                   •
#                   •
# Input:            none
# Output:           Expected results as follows:
#                   • expected resets: 2096	Godfrey	Gaye
#                   •
#                   •
#                   •
#                   •
# Sources:          Project Charter - Jira Story: Test 1
#
# Change Log:       - xx.xx.2025:
#
# **********************************************************************************************************************
# **********************************************************************************************************************  

import mariadb
import os
from dotenv import load_dotenv
load_dotenv()



def get_force_reset_logins():
    """
    Retrieve login IDs where FORCE_RESET is set to true
    using the existing Database class for connection.
    """
    try:
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            connect_timeout=5
        )

        # Create a cursor from the connection
        cursor = conn.cursor()

        # Query to find logins with FORCE_RESET enabled
        query = "SELECT LOGINID FROM login_table WHERE FORCE_RESET = 1"
        cursor.execute(query)

        # Fetch all matching login IDs
        logins = cursor.fetchall()

        if not logins:
            print("No accounts with FORCE_RESET enabled were found.")
        else:
            print("Accounts requiring password reset:")
            print("----------------------------------")
            for login in logins:
                print(login[0])

        # Close cursor (connection will be handled by Database class)
        cursor.close()

        return [login[0] for login in logins]

    except Exception as error:
        print(f"Error retrieving data: {error}")
        return []




def run_all_tests():
    get_force_reset_logins()

if __name__ == "__main__":
    run_all_tests()

# **********************************************************************************************************************
# **********************************************************************************************************************
