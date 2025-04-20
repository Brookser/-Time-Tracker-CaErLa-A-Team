from src.Logic.Department import Department

def test_department_creation():
    dept = Department("D001", "Engineering", "E001")
    assert dept.get_id() == "D001"
    assert dept.get_name() == "Engineering"
    assert dept.get_manager() == "E001"
    assert dept.is_active() == 1
