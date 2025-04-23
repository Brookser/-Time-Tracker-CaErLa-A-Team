from src.Logic.Login import Login
from datetime import datetime


def test_login_force_reset_check():
    login = FakeLogin("login_TEST01", "TEST01", "secret123")

    # ❌ Expected failure: `force_reset` is not implemented yet
    assert login.force_reset == 1  # AttributeError

def test_login_force_reset_flag():
    login = Login("login_TEST01", "TEST01", "secret123")

    login.force_password_reset()

    # ✅ Expected: force_reset should now be 1 (True)
    assert login.needs_password_reset() is True  # should return True

def test_login_full_lifecycle():
    login = Login("login_TEST02", "TEST01", "password123")

    # Save to DB
    login.save_to_database()

    # Retrieve and assert
    db_login = Login.get_by_empid("TEST01")

    # ✅ Expected: Should return a tuple from the DB matching inserted values
    assert db_login is not None  # should not be None
    assert db_login[0] == "login_TEST02"  # LOGINID
    assert db_login[1] == "TEST01"        # EMPID
    assert db_login[2] == "password123"   # PASSWORD
    assert isinstance(db_login[3], datetime)  # LAST_RESET
    assert db_login[4] == 0  # FORCE_RESET flag should default to 0