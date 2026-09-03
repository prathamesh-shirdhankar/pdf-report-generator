"""
main.py

Stage 0: GET /health

Stage 4: POST /reports, GET /reports/{id}, GET /reports/{id}/file

Stage 5: POST /reports is idempotent — one report per day, unless force=true.
"""

import os

from datetime import datetime

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse

from db import get_conn, init_db
from report import build_report


app = FastAPI()

REPORTS_DIR = "reports"


@app.on_event("startup")
def startup():
    init_db()
    os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
async def create_report(payload: dict = Body(default={})):
    force = payload.get("force", False)
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    if not force:
        # Stage 5 — same day, same result. No new file, no new row.
        existing = cur.execute(
            """
            SELECT id, path, created_at
            FROM reports
            WHERE created_at = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (today,),
        ).fetchone()

        if existing:
            conn.close()
            return _existing_report_response(existing, status_code=200)

    # Generate a fresh report: query -> render -> save PDF -> insert row.
    cur.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        ("", today),
    )

    report_id = cur.lastrowid

    path = os.path.join(
        REPORTS_DIR,
        f"{report_id}.pdf",
    )

    # Async Playwright requires awaiting the report generation.
    await build_report(path)

    cur.execute(
        "UPDATE reports SET path = ? WHERE id = ?",
        (path, report_id),
    )

    conn.commit()
    conn.close()

    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file",
    }


def _existing_report_response(row, status_code: int):
    # FastAPI needs a Response object to set a non-default status code
    # on a dict return.
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={
            "id": row["id"],
            "file": f"/reports/{row['id']}/file",
        },
    )


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = get_conn()

    row = conn.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,),
    ).fetchone()

    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="report not found",
        )

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file",
    }


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_conn()

    row = conn.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,),
    ).fetchone()

    conn.close()

    if row is None or not row["path"] or not os.path.exists(row["path"]):
        raise HTTPException(
            status_code=404,
            detail="report file not found",
        )

    return FileResponse(
        row["path"],
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf",
    )
