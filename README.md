# Bulk Certificate Generator API

A FastAPI backend that accepts a list of recipients, validates the input, creates one certificate PDF per valid recipient, tracks generation status, and exposes generated certificates for download.

## Features

- Bulk certificate generation
- Input validation with Pydantic
- Relational database using SQLite and SQLAlchemy
- Background processing with FastAPI BackgroundTasks
- Per-recipient success/failure tracking
- Job progress reporting
- Individual certificate retrieval
- Automated tests with pytest
- One predefined certificate template

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab
- Pytest

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       └── certificate_generator.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_failure_handling.py
├── certificates/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Create a generation job

`POST /jobs`

Example:

```json
{
  "event_name": "Python Workshop",
  "certificate_title": "Certificate of Completion",
  "recipients": [
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    },
    {
      "name": "Priya Sharma",
      "email": "priya@example.com"
    }
  ]
}
```

The API immediately returns a job ID while certificates are processed in the background.

Example:

```json
{
  "job_id": 1,
  "status": "queued",
  "total": 2
}
```

## Check progress

`GET /jobs/{job_id}`

The response contains:

- total recipients
- processed count
- successful count
- failed count
- progress percentage
- per-recipient status
- certificate URL for successful generations
- error message for failed generations

## Retrieve a certificate

`GET /certificates/{recipient_id}`

The endpoint returns the generated PDF.

## Failure handling

Each recipient is processed independently inside a `try/except` block. If one certificate fails, its status is marked as `failed` and processing continues for the remaining recipients.

## Testing

Run:

```bash
pytest -q
```

The test suite covers:

1. API availability
2. Job creation
3. Input validation
4. Certificate generation
5. Job progress/status
6. Certificate retrieval
7. Individual certificate failure without stopping the batch

## Design Decisions

### SQLite + SQLAlchemy

SQLite is a relational database that keeps the assignment easy to run locally without requiring an external database server. SQLAlchemy provides a clean ORM layer.

### Background processing

FastAPI BackgroundTasks is used so the job creation request can return a job ID without waiting for every PDF to finish. The client can poll the job status endpoint.

For a production-scale system, a dedicated worker queue such as Celery/RQ with Redis would be a stronger option.

### One predefined template

The assignment requires one predefined certificate template, so the implementation keeps the certificate layout fixed and only injects recipient/event data.

## API documentation

FastAPI automatically provides interactive Swagger documentation at `/docs`.
