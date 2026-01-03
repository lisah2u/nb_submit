# nb_submit

A FastAPI application for collecting and storing student jupyter notebook submissions with timezone-aware timestamps.

## Overview

This application provides a simple REST API for students to submit their answers, which are stored in a SQLite database with timestamps in the America/New_York timezone.

## Features

- **FastAPI** web framework 
- **SQLite** database for persistent storage
- **Timezone-aware timestamps** using America/New_York timezone
- **JSON answer storage** supporting flexible question formats
- **Railway deployment** with hosted database and API key management

## Installation

### Prerequisites

- Python 3.13.5 or higher
- `uv` package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd nb_submit
```

2. Create a virtual environment:
```bash
uv venv
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Running Locally

Start the development server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### GET `/`
Returns a welcome message.

**Response:**
```json
{
  "message": "Hello from FastAPI!"
}
```

#### POST `/submit`
Submit student answers to be stored in the database.

**Request Body:**
```json
{
  "student_id": "student123",
  "answers": {
    "question1": "answer1",
    "question2": "answer2"
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

## Deployment

This application is deployed on [Railway](https://railway.app/) with the following configuration:

- **Database**: SQLite database hosted on Railway
- **API Key**: Managed through Railway environment variables

### Environment Variables

The following environment variables should be configured in Railway:

- `API_KEY`: Authentication key for the API 

## Database Schema

The `submissions` table has the following structure:

| Column      | Type         | Description                                    |
|-------------|--------------|------------------------------------------------|
| id          | INTEGER      | Primary key (auto-increment)                   |
| student_id  | TEXT         | Unique identifier for the student              |
| timestamp   | DATETIME     | Submission time in America/New_York timezone   |
| answers     | TEXT         | JSON-encoded student answers                   |

## Testing

Run the test suite:
```bash
pytest test_app.py -v
```

### Test Coverage

The test suite is pretty minimal but includes:
- Root endpoint validation
- Submission endpoint with database insertion
- Database table schema verification
- Timezone-aware timestamp validation

## Development

### Project Structure

```
nb_submit/
├── app.py              # Main FastAPI application
├── test_app.py         # Unit tests
├── requirements.txt    # Python dependencies
├── submissions.db      # SQLite database (generated)
└── README.md          # This file
```

### Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pytest` - Testing framework (dev)
- `httpx` - HTTP client for testing (dev)

## License

See [LICENSE](LICENSE) file for details.


