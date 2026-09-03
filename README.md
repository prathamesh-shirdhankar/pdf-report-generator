# PDF Report Generator

A small backend feature: query sales data with SQL, render it into a real PDF
report, and serve it by link. Built for FlyRank Internship, Backend Track,
Week 4, Assignment A8.

## What this is

An API with three endpoints:
- `POST /reports` — generates a sales report PDF from `report.db` and returns its id + download link
- `GET /reports/{id}` — returns the report's metadata
- `GET /reports/{id}/file` — downloads the actual PDF

Dataset: the "little shop" — ~200 seeded fake orders (customer, product, amount, date).

## How to run it

```bash
# 1. create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. seed the database (safe to run more than once)
python seed.py

# 4. start the API
uvicorn main:app --reload --port 8000
```

Then, in another terminal:

```bash
# generate a report (takes a few seconds — that's expected)
time curl -i -X POST http://localhost:8000/reports

# download it
curl -o my-report.pdf http://localhost:8000/reports/1/file
```

## Aggregation SQL (Stage 2)

TODO: paste the four queries from `report.py` here.

## Proof: generate → download

TODO: paste your terminal output from the POST + curl download above.

## Stage 4 — why not do this in the request forever?

TODO: one sentence — at what point would you move this work into a background job?

## Stage 5 — duplicate requests

TODO: two sentences — what does the once-per-day check protect against, and a
real-world example where a missing check like this costs money.

## Screenshot

TODO: add a screenshot of page 1 of a generated PDF here.
