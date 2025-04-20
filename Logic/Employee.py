from Data.Database import Database

class Employee:
    def __init__(self, empid, first_name, last_name, dptid, email=None, mgr_empid=None, active=1):
        self.__empid = empid
        self.__first_name = first_name
        self.__last_name = last_name
        self.__dptid = dptid
        self.__email = email
        self.__mgr_empid = mgr_empid
        self.__active = active

    # Setters
    def set_email(self, email):
        self.__email = email

    def set_mgr_empid(self, mgr_empid):
        self.__mgr_empid = mgr_empid

    def set_active(self, active):
        self.__active = active

    # Getters
    def get_empid(self):
        return self.__empid

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_dptid(self):
        return self.__dptid

    def get_email(self):
        return self.__email

    def get_mgr_empid(self):
        return self.__mgr_empid

    def is_active(self):
        return self.__active == 1

    # Save this employee to the database
    def save_to_database(self):
        Database.add_employee(
            empid=self.__empid,
            first_name=self.__first_name,
            last_name=self.__last_name,
            dptid=self.__dptid,
            email=self.__email,
            mgr_empid=self.__mgr_empid,
            active=self.__active
        )

    # Static method to fetch all active employees
    @staticmethod
    def get_all_active_employees():
        return Database.get_active_employees()