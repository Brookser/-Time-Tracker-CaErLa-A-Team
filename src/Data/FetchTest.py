from src.Logic.Employee import Employee
# from Logic.Login import import Login
# from Logic.Project import Project
# from Logic.TimeEntry import TimeEntry

#------------
# GET and print active employees
print("\n✅ All Active Employees:")
for emp in Employee.get_all_active_employees():
    print(emp)
#------------
