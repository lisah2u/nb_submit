import pytest
import sqlite3
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from app import app, Submission


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create a test database and clean it up after tests."""
    test_db_name = "test_submissions.db"
    
    # Remove test database if it exists
    if os.path.exists(test_db_name):
        os.remove(test_db_name)
    
    # Create test database with the same schema
    conn = sqlite3.connect(test_db_name)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            timestamp DATETIME,
            answers TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
    yield test_db_name
    
    # Cleanup
    if os.path.exists(test_db_name):
        os.remove(test_db_name)


def test_root_endpoint_returns_welcome_message(client):
    """Test that the '/' endpoint returns the expected welcome message."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI!"}


def test_submit_endpoint_inserts_valid_data(client, test_db, monkeypatch):
    """Test that the '/submit' endpoint successfully inserts valid submission data into the database."""
    # Monkey patch the database connection to use test database
    original_connect = sqlite3.connect
    
    def mock_connect(db_name):
        if db_name == "submissions.db":
            return original_connect(test_db)
        return original_connect(db_name)
    
    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    
    # Prepare test data
    test_submission = {
        "student_id": "student123",
        "answers": {
            "question1": "answer1",
            "question2": "answer2"
        }
    }
    
    # Submit data via API
    response = client.post("/submit", json=test_submission)
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Verify data was inserted into database
    conn = sqlite3.connect(test_db)
    cursor = conn.execute("SELECT student_id, answers FROM submissions WHERE student_id = ?", ("student123",))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "student123"
    assert json.loads(row[1]) == test_submission["answers"]


def test_submissions_table_created_on_startup():
    """Test that the 'submissions' table is created correctly on application startup."""
    # Check the main database that was created when the app module was imported
    db_name = "submissions.db"
    
    assert os.path.exists(db_name), "Database file should exist after app startup"
    
    # Connect and verify table structure
    conn = sqlite3.connect(db_name)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions'")
    table_exists = cursor.fetchone()
    
    assert table_exists is not None, "submissions table should exist"
    
    # Verify table schema
    cursor = conn.execute("PRAGMA table_info(submissions)")
    columns = cursor.fetchall()
    conn.close()
    
    # Expected columns: id, student_id, timestamp, answers
    column_names = [col[1] for col in columns]
    assert "id" in column_names
    assert "student_id" in column_names
    assert "timestamp" in column_names
    assert "answers" in column_names
    
    # Verify id is primary key and autoincrement
    id_column = [col for col in columns if col[1] == "id"][0]
    assert id_column[5] == 1  # pk field should be 1 for primary key


def test_timestamp_stored_in_eastern_timezone(client, test_db, monkeypatch):
    """Test that the 'timestamp' in the database is stored in the 'America/New_York' timezone."""
    # Monkey patch the database connection to use test database
    original_connect = sqlite3.connect
    
    def mock_connect(db_name):
        if db_name == "submissions.db":
            return original_connect(test_db)
        return original_connect(db_name)
    
    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    
    # Prepare test data
    test_submission = {
        "student_id": "student456",
        "answers": {"question1": "answer1"}
    }
    
    # Capture the time before submission
    eastern = ZoneInfo("America/New_York")
    before_time = datetime.now(eastern)
    
    # Submit data via API
    response = client.post("/submit", json=test_submission)
    assert response.status_code == 200
    
    # Capture the time after submission
    after_time = datetime.now(eastern)
    
    # Retrieve the stored timestamp
    conn = sqlite3.connect(test_db)
    cursor = conn.execute("SELECT timestamp FROM submissions WHERE student_id = ?", ("student456",))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    stored_timestamp_str = row[0]
    
    # Parse the stored timestamp
    stored_timestamp = datetime.fromisoformat(stored_timestamp_str)
    
    # Verify the timestamp has timezone info and is in Eastern timezone
    assert stored_timestamp.tzinfo is not None, "Timestamp should have timezone information"
    
    # Verify the timezone offset matches Eastern timezone at the time of submission
    # Eastern timezone offset varies (-05:00 or -04:00 depending on DST)
    eastern_offset = stored_timestamp.utcoffset()
    expected_offset = before_time.utcoffset()
    assert eastern_offset == expected_offset, f"Timestamp should be in America/New_York timezone"
    
    # Verify the timestamp is within the expected time range
    assert before_time <= stored_timestamp <= after_time, "Timestamp should be between before and after times"
