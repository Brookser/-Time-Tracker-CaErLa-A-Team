# src/Logic/Department.py

from src.Data.Database import Database

class Department:
    def __init__(self, dptid, name, manager_id=None, active=1):
        self.__dptid = dptid
        self.__name = name
        self.__manager_id = manager_id
        self.__active = active

    # Setters
    def set_name(self, name):
        self.__name = name

    def set_manager(self, manager_id):
        self.__manager_id = manager_id

    def set_active(self, active):
        self.__active = active

    # Getters
    def get_id(self):
        return self.__dptid

    def get_name(self):
        return self.__name

    def get_manager(self):
        return self.__manager_id

    def is_active(self):
        return self.__active

    # Save to database
    def save_to_database(self):
        Database.add_department(self.__dptid, self.__name, self.__manager_id, self.__active)

    # Static methods
    @staticmethod
    def get_all_departments():
        return Database.get_departments()
