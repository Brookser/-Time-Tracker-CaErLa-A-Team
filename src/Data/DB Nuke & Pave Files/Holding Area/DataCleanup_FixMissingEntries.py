# **********************************************************************************************************************
# **********************************************************************************************************************   
# Author:           Erika Brooks
# TTfeature:        Test_01
# Date:             05.16.2025
# Description:      Data cleanup; fixes these specific types of issues:

#                        1. Projects with No Employee Assignments:
#                         - P10002 (Created by: E9013)
#                         - P10004 (Created by: E9003)
#                         - P10008 (Created by: E9023)
#                         - P10013 (Created by: E9005)
#                         - P10020 (Created by: E9001)
#                         - P10022 (Created by: E9019)
#                         - P10023 (Created by: E9019)
#                         - P10025 (Created by: E9013)
#                         - P10026 (Created by: E015)
#                         - P10027 (Created by: E9001)
#                         - P10028 (Created by: E9003)
#                         - P10029 (Created by: E9004)
#                         - P10030 (Created by: E9006)
#                         - P10033 (Created by: E015)
#                         - P10034 (Created by: E9001)
#                         - P10035 (Created by: E9003)
#                         - P10036 (Created by: E9004)
#                         - P10037 (Created by: E9006)
#                         - P10040 (Created by: E015)
#                         - P10041 (Created by: E9001)
#                         - P10042 (Created by: E9003)
#                         - P10043 (Created by: E9004)
#                         - P10044 (Created by: E9006)
#                         - P10047 (Created by: E015)
#                         - P10048 (Created by: E9001)
#                         - P10049 (Created by: E9003)
#                         - P10050 (Created by: E9004)
#                         - P10051 (Created by: E9006)
#                         - P10052 (Created by: E004)
#                         - P_214b1665 (Created by: E012)
#
#                         2. Projects Where Creator is Not Assigned:
#                         - Project P10005 created by E9010, but creator not assigned
#                         - Project P10006 created by E9004, but creator not assigned
#                         - Project P10007 created by E9004, but creator not assigned
#                         - Project P10009 created by E9001, but creator not assigned
#                         - Project P10010 created by E9005, but creator not assigned
#                         - Project P10011 created by E9005, but creator not assigned
#                         - Project P10012 created by E9005, but creator not assigned
#                         - Project P10014 created by E9021, but creator not assigned
#                         - Project P10015 created by E9021, but creator not assigned
#                         - Project P10016 created by E9010, but creator not assigned
#                         - Project P10017 created by E9023, but creator not assigned
#                         - Project P10018 created by E9013, but creator not assigned
#                         - Project P10021 created by E9001, but creator not assigned
#                         - Project P10024 created by E9019, but creator not assigned
#
#                         3. Employee-Project Assignments for Non-Existent Projects:
#                         - P_ece415c0 (Assigned employees: E001, E004, E013, E014)
#                         - P_f505695e (Assigned employees: E001, E004)
#                         - SD0001 (Assigned employees: E004, E015, E9004)
#                         - SD0002 (Assigned employees: E004, E9001, E9003)
#                         - SD0005 (Assigned employees: E004, E9001, E9003, E9004)
#                         - SD0007 (Assigned employees: E004, E015, E9001, E9004)
#                         - P_64d9b214 (Assigned employees: E012, E013, E9012)
#                         - P_9febc212 (Assigned employees: E012, E9011, E9013, E9023)
#                         - P_39442928 (Assigned employees: E013, E014, E9004, E9006)
#                         - P_79229fbf (Assigned employees: E013, E9006)
#                         - P_831b5a2f (Assigned employees: E013)
#                         - P_f279b1fe (Assigned employees: E013)
#                         - P_f7b57295 (Assigned employees: E013, E014, E9006)
#                         - P_f9dfdd2e (Assigned employees: E013, E9006)
#                         - SD0004 (Assigned employees: E015, E9001, E9004, E9006)
#                         - SD0006 (Assigned employees: E015)
#                         - P_5b0ea510 (Assigned employees: E9006)
#                         - P_7293ffc0 (Assigned employees: TEST01)
#                         - P_dc6125b5 (Assigned employees: TEST01)
#                         - P_fbbfa098 (Assigned employees: TEST01)

#
# Input:            none
# Output:           confirmation message
# Sources:          Project Charter - Jira Story: Tests 1 & 2
#
# Change Log:       - 05.16.2025: Initial setup
#
# **********************************************************************************************************************
# **********************************************************************************************************************  


# read the last couple of Claude input and reply in conversation Database Data Analysis



# **********************************************************************************************************************
# **********************************************************************************************************************
