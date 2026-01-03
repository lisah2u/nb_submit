from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3
import json
import os
from fastapi import Header, HTTPException
from fastapi import Depends

API_KEY = os.environ.get("API_KEY")

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

app = FastAPI()
eastern = ZoneInfo("America/New_York")

# Initialize database
# Use /data/submissions.db on Railway, ./submissions.db locally
DB_PATH = os.environ.get("DB_PATH", "./submissions.db")
conn = sqlite3.connect(DB_PATH)
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
def submit(data: Submission, _: str = Depends(verify_key)):
    conn = sqlite3.connect(DB_PATH)
    timestamp = datetime.now(eastern).isoformat()
    conn.execute(
        "INSERT INTO submissions (student_id, timestamp, answers) VALUES (?, ?, ?)",
        (data.student_id, timestamp, json.dumps(data.answers))
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}
    
@app.get("/submissions")
def get_submissions(_: str = Depends(verify_key)):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM submissions").fetchall()
    conn.close()
    return {"submissions": rows}
    
@app.get("/submissions")
def get_submissions(_: str = Depends(verify_key)):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM submissions ORDER BY timestamp DESC LIMIT 20").fetchall()
    conn.close()
    return {"submissions": rows}
    
@app.get("/submissions/{student_id}")
def get_student_submissions(student_id: str, _: str = Depends(verify_key)):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM submissions WHERE student_id = ? ORDER BY timestamp DESC LIMIT 20").fetchall()
    conn.close()
    return {"submissions": rows}