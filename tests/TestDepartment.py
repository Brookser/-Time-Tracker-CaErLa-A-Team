from src.Logic.Department import Department

def test_department_creation():
    dept = Department("D001", "Engineering", "E001")
    assert dept.get_id() == "D001"
    assert dept.get_name() == "Engineering"
    assert dept.get_manager_id() == "E001"
    assert dept.get_active_status() == 1