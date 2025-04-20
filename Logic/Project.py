from Data.Database import Database
from datetime import datetime

class Project:
    def __init__(self, projectid, name, created_by, date_created=None, prior_projectid=None, active=1):
        self.__projectid = projectid
        self.__name = name
        self.__created_by = created_by
        self.__date_created = date_created or datetime.now()
        self.__prior_projectid = prior_projectid
        self.__active = active

    # Setters
    def deactivate(self):
        self.__active = 0

    def set_prior_project(self, prior_id):
        self.__prior_projectid = prior_id

    # Getters
    def get_id(self):
        return self.__projectid

    def get_name(self):
        return self.__name

    def is_active(self):
        return self.__active == 1

    # Save project to DB
    def save_to_database(self):
        print("📝 Preparing to insert project with:")
        print("ID:", self.__projectid)
        print("Name:", self.__name)
        print("Created by:", self.__created_by)
        print("Date:", self.__date_created)
        print("Prior:", self.__prior_projectid)
        print("Active:", self.__active)
        Database.add_project(
            projectid=self.__projectid,
            name=self.__name,
            created_by=self.__created_by,
            date_created=self.__date_created,
            prior_projectid=self.__prior_projectid,
            active=self.__active
        )

    # Static method for dropdowns or reporting
    @staticmethod
    def get_all_projects():
        return Database.get_all_projects()

    @staticmethod
    def get_active_projects():
        return Database.get_active_projects()
