from src.Logic.Employee import Employee

def test_employee_creation():
    emp = Employee(
        empid="E123",
        first_name="Ada",
        last_name="Lovelace",
        dptid="ENG",
        email="ada@example.com",
        mgr_empid="E001",
        active=1
    )

    assert emp.get_empid() == "E123"
    assert emp.get_first_name() == "Ada"
    assert emp.get_last_name() == "Lovelace"
    assert emp.get_dptid() == "ENG"
    assert emp.get_email() == "ada@example.com"
    assert emp.get_mgr_empid() == "E001"
    assert emp.is_active() is True
