from src.Data.Database import Database

class TimeEntry:
    def __init__(self, empid, projectid, start_time, stop_time=None, notes=None, manual_entry=0, total_minutes=None):
        self.__empid = empid
        self.__projectid = projectid
        self.__start_time = start_time
        self.__stop_time = stop_time
        self.__notes = notes
        self.__manual_entry = manual_entry
        self.__total_minutes = total_minutes

    # Setters
    def set_stop_time(self, stop_time):
        self.__stop_time = stop_time

    def set_notes(self, notes):
        self.__notes = notes

    def set_manual_entry(self, is_manual):
        self.__manual_entry = int(is_manual)

    # Getters
    def get_empid(self):
        return self.__empid

    def get_projectid(self):
        return self.__projectid

    def get_start_time(self):
        return self.__start_time

    def get_stop_time(self):
        return self.__stop_time

    def get_notes(self):
        return self.__notes

    def get_manual_entry(self):
        return self.__manual_entry

    def get_total_minutes(self):
        return self.__total_minutes


    def calculate_total_minutes(self):
        if self.__start_time and self.__stop_time:
            delta = self.__stop_time - self.__start_time
            self.__total_minutes = int(delta.total_seconds() / 60)

    # Save time entry to DB
    def save_to_database(self):
        print("🧪 Available methods on Database:")
        print(dir(Database))
        self.calculate_total_minutes()
        Database.add_time_entry(
            empid=self.__empid,
            projectid=self.__projectid,
            start_time=self.__start_time,
            stop_time=self.__stop_time,
            notes=self.__notes,
            manual_entry=self.__manual_entry,
            total_minutes=self.__total_minutes
        )

    # ****************************
    # written on 4.29.25 - EAB
    # ****************************

    # Update notes for an existing time entry
    def update_notes(self, timeid, new_notes):
        """
        Updates the notes field for an existing time entry.

        Args:
            timeid: The ID of the time entry to update
            new_notes: The new notes text to set
        """
        print("🧪 Available methods on Database:")
        print(dir(Database))
        # Update the instance notes as well
        self.set_notes(new_notes)
        # Call the database alter_notes method
        Database.alter_notes(
            timeid=timeid,
            notes=new_notes
        )

    # ****************************
    # end of 4.29.25 update - EAB
    # ****************************

    # Static method reporting
    @staticmethod
    def get_all_entries():
        return Database.get_all_time_entries()

    @staticmethod
    def get_time_entries_filtered(empid=None, start_date=None, end_date=None):
        return Database.get_time_entries_filtered(
            start_date=start_date,
            end_date=end_date,
            empid=empid
        )

    @staticmethod
    def get_all_employees():
        return Database.get_active_employees()

    @staticmethod
    def get_entries_for_empids(empids, start_date=None, end_date=None):
        return Database.get_time_entries_filtered_multiple_empids(empids, start_date, end_date)



