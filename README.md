# PDF Report Generator

A FastAPI service that generates PDF sales reports from SQLite data using Playwright and Chromium.

## Features

- FastAPI REST API
- SQLite database with seeded sales data
- Sales aggregation using SQL
- HTML report generation
- PDF rendering with Playwright + Chromium
- Idempotent daily report generation
- `force=true` support for generating a fresh report
- PDF file download endpoint
- Report metadata endpoint
- Health check endpoint

## Tech Stack

- Python 3.12
- FastAPI
- SQLite
- Playwright
- Chromium
- Uvicorn

## Project Structure

```text
pdf-report-generator/
├── main.py
├── db.py
├── seed.py
├── report.py
├── requirements.txt
├── README.md
├── report.db
└── reports/
    ├── 1.pdf
    └── 2.pdf
```

## Setup

### 1. Create a virtual environment

```powershell
py -3.12 -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Install Chromium

```powershell
python -m playwright install chromium
```

### 4. Seed the database

```powershell
python seed.py
```

## Run the API

Start the server with:

```powershell
uvicorn main:app --port 8000
```

> On Windows, run without `--reload` because Playwright/Chromium subprocess handling can fail with Uvicorn's reload process.

The API will be available at:

```text
http://localhost:8000
```

## API Endpoints

### Health Check

```http
GET /health
```

Example:

```powershell
curl.exe http://localhost:8000/health
```

Response:

```json
{
  "status": "ok"
}
```

### Generate Report

```http
POST /reports
```

Example:

```powershell
curl.exe -X POST http://localhost:8000/reports
```

First request of the day:

```json
{
  "id": 1,
  "file": "/reports/1/file"
}
```

The response uses `201 Created` when a new report is generated.

### Idempotent Report Generation

Calling the same endpoint again on the same day returns the existing report instead of generating another PDF.

```powershell
curl.exe -X POST http://localhost:8000/reports
```

Response:

```json
{
  "id": 1,
  "file": "/reports/1/file"
}
```

The repeated request returns `200 OK`.

### Force a New Report

Use:

```json
{
  "force": true
}
```

PowerShell:

```powershell
$body = @{ force = $true } | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/reports" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

This generates a new report ID and PDF.

Example:

```json
{
  "id": 2,
  "file": "/reports/2/file"
}
```

### Get Report Metadata

```http
GET /reports/{id}
```

Example:

```powershell
curl.exe http://localhost:8000/reports/1
```

Response:

```json
{
  "id": 1,
  "created_at": "2026-09-03",
  "file": "/reports/1/file"
}
```

### Download PDF

```http
GET /reports/{id}/file
```

Example:

```powershell
curl.exe http://localhost:8000/reports/1/file -o report.pdf
```

The endpoint returns the generated PDF with:

```text
Content-Type: application/pdf
```

## Report Contents

Each generated PDF contains:

- Total number of orders
- Total revenue
- Top 5 products by revenue
- Orders per day for the last 7 days
- Complete orders table

The HTML report uses a repeating table header and prevents individual table rows from being split across PDF pages.

## Verification

The implementation was tested locally with:

- `GET /health` → `200 OK`
- First `POST /reports` → `201 Created`
- Repeated `POST /reports` → `200 OK` with the same report ID
- `force=true` → new report ID with `201 Created`
- `GET /reports/{id}` → report metadata
- `GET /reports/{id}/file` → valid generated PDF
- Playwright + Chromium PDF generation
- SQLite aggregation queries

Example generated files:

```text
reports/
├── 1.pdf
└── 2.pdf
```

## Notes

The application uses Python 3.12 because the project's Playwright dependencies are compatible with this environment.

For Windows, the API should be started without Uvicorn's `--reload` option when generating PDFs through Playwright.

## License

This project was created as an assignment demonstrating a FastAPI-based PDF report generation service.
