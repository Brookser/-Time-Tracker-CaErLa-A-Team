from src.Logic.TimeEntry import TimeEntry
from datetime import datetime, timedelta

def test_time_entry_all_fields():
    start = datetime(2025, 4, 20, 13, 0)
    stop = start + timedelta(hours=2)

    entry = TimeEntry(
        empid="E001",
        projectid="P001",
        start_time=start,
        stop_time=stop,
        notes="Completed project setup",
        manual_entry=1
    )

    entry.calculate_total_minutes()

    assert entry.get_empid() == "E001"
    assert entry.get_projectid() == "P001"
    assert entry.get_start_time() == start
    assert entry.get_stop_time() == stop
    assert entry.get_notes() == "Completed project setup"
    assert entry.get_manual_entry() == 1
    assert entry.get_total_minutes() == 120




def test_time_entry_manual_start_stop_and_save():
    start = datetime(2025, 4, 20, 9, 30)
    stop = datetime(2025, 4, 20, 11, 0)

    entry = TimeEntry(
        empid="E001",
        projectid="P001",
        start_time=start,
        stop_time=stop,
        notes="Entered start/stop manually",
        manual_entry=1
    )

    entry.save_to_database()  # 🔥 this saves it to the DB

    assert entry.get_total_minutes() == 90