from Logic.Project import Project
import pytest

def test_project_initialization():
    proj = Project("PX01", "Test Project", "E001")
    assert proj.get_id() == "PX01"
    assert proj.get_name() == "Test Project"
    assert proj.is_active() is True
