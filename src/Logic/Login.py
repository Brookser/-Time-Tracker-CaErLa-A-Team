from src.Data.Database import Database
from datetime import datetime

class Login:
    def __init__(self, loginid, empid, password, last_reset=None, force_reset=0):
        self.__loginid = loginid
        self.__empid = empid
        self.__password = password
        self.__last_reset = last_reset or datetime.now()
        self.__force_reset = force_reset

    # Setters
    def set_password(self, new_password):
        self.__password = new_password
        self.__last_reset = datetime.now()
        self.__force_reset = 0
        self.update_password()

    def force_password_reset(self):
        self.__force_reset = 1
        self.update_password()

    # Getters
    def get_empid(self):
        return self.__empid

    def get_loginid(self):
        return self.__loginid

    def needs_password_reset(self):
        return self.__force_reset == 1

    def get_password(self):
        return self.__password

    def get_last_reset(self):
        return self.__last_reset

    # Save to DB
    def save_to_database(self):
        Database.add_login(
            loginid=self.__loginid,
            empid=self.__empid,
            password=self.__password,
            last_reset=self.__last_reset,
            force_reset=self.__force_reset
        )

    def update_password(self):
        Database.update_password(
            empid=self.__empid,
            new_password=self.__password,
            last_reset=self.__last_reset,
            force_reset=self.__force_reset
        )

    # Static method to fetch login record
    # @staticmethod
    # def get_by_empid(empid):
    #     row = Database.get_login_by_empid(empid)
    #     if row:
    #         return Login(
    #             loginid=row[0],
    #             empid=row[1],
    #             password=row[2],
    #             last_reset=row[3],
    #             force_reset=row[4]
    #         )
    #     return None

    @staticmethod
    def get_by_email(email):
        row = Database.get_login_by_email(email)
        if row:
            return Login(
                loginid=row[0],
                empid=row[1],
                password=row[2],
                last_reset=row[3],
                force_reset=row[4]
            )
        return None
