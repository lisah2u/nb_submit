from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3
import json

app = FastAPI()
eastern = ZoneInfo("America/New_York")

# Initialize database
conn = sqlite3.connect("submissions.db")
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

class Submission(BaseModel):
    student_id: str
    answers: dict

@app.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}

@app.post("/submit")
def submit(data: Submission):
    conn = sqlite3.connect("submissions.db")
    timestamp = datetime.now(eastern).isoformat()
    conn.execute(
        "INSERT INTO submissions (student_id, timestamp, answers) VALUES (?, ?, ?)",
        (data.student_id, timestamp, json.dumps(data.answers))
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}