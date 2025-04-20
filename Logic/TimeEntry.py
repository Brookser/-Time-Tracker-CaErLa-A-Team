from Data.Database import Database

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
    # -------

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

    # Static method for filtering on reports
    @staticmethod
    def get_time_entries_filtered(project_id, start_date, end_date):
        return Database.get_time_entries_filtered(project_id, start_date, end_date)
