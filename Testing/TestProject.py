from Logic.Project import Project
from datetime import datetime

def test_project_creation_all_fields():
    project = Project(
        projectid="PX01",
        name="Build Dashboard",
        created_by="E001",
        date_created=datetime(2025, 4, 20, 10, 0, 0),
        prior_projectid="PX00",
        active=1
    )

    assert project.get_id() == "PX01"
    assert project.get_name() == "Build Dashboard"
    assert project.get_created_by() == "E001"
    assert project.get_date_created() == datetime(2025, 4, 20, 10, 0, 0)
    assert project.get_prior_projectid() == "PX00"
    assert project.is_active() is True