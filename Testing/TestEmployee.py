from Logic.Employee import Employee

def test_employee_creation():
    emp = Employee("TEST01", "Test", "User", "D001", "test@example.com", None)

    assert emp.get_first_name() == "Test"
    assert emp.get_last_name() == "User"
    assert emp.get_email() == "test@example.com"
