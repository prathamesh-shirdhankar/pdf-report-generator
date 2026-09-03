"""
report.py

Stage 2: get_report_data() turns 200 rows into a handful of numbers.

Stage 3: render_html() turns those numbers into a page, generate_pdf() turns
the page into a real PDF file (via headless Chromium through Playwright).
"""

from datetime import datetime, timedelta

from playwright.async_api import async_playwright

from db import get_conn


def get_report_data() -> dict:
    """Stage 2 — one function, four aggregation queries, one dict of results."""
    conn = get_conn()
    cur = conn.cursor()

    total_orders = cur.execute(
        "SELECT COUNT(*) AS n FROM orders"
    ).fetchone()["n"]

    total_revenue = cur.execute(
        "SELECT SUM(amount) AS s FROM orders"
    ).fetchone()["s"] or 0

    top_products = cur.execute(
        """
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
        """
    ).fetchall()

    seven_days_ago = (
        datetime.now() - timedelta(days=6)
    ).strftime("%Y-%m-%d")

    orders_per_day = cur.execute(
        """
        SELECT created_at AS day, COUNT(*) AS n
        FROM orders
        WHERE created_at >= ?
        GROUP BY created_at
        ORDER BY created_at
        """,
        (seven_days_ago,),
    ).fetchall()

    all_orders = cur.execute(
        """
        SELECT customer, product, amount, created_at
        FROM orders
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": [dict(row) for row in top_products],
        "orders_per_day": [dict(row) for row in orders_per_day],
        "all_orders": [dict(row) for row in all_orders],
    }


def render_html(data: dict) -> str:
    """Stage 3 — build the report HTML from the report data."""
    today = datetime.now().strftime("%B %d, %Y")

    top_products_rows = "".join(
        f"<tr><td>{p['product']}</td>"
        f"<td>${p['revenue']:.2f}</td></tr>"
        for p in data["top_products"]
    )

    per_day_rows = "".join(
        f"<tr><td>{d['day']}</td><td>{d['n']}</td></tr>"
        for d in data["orders_per_day"]
    )

    all_orders_rows = "".join(
        f"<tr><td>{o['created_at']}</td>"
        f"<td>{o['customer']}</td>"
        f"<td>{o['product']}</td>"
        f"<td>${o['amount']:.2f}</td></tr>"
        for o in data["all_orders"]
    )

    return f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Helvetica, Arial, sans-serif;
            color: #1a1a1a;
            margin: 32px;
        }}

        h1 {{
            font-size: 22px;
            margin-bottom: 0;
        }}

        .subtitle {{
            color: #666;
            margin-top: 4px;
            margin-bottom: 24px;
        }}

        .totals {{
            display: flex;
            gap: 32px;
            margin-bottom: 24px;
        }}

        .total-box {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px 20px;
        }}

        .total-box .label {{
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
        }}

        .total-box .value {{
            font-size: 20px;
            font-weight: bold;
        }}

        h2 {{
            font-size: 15px;
            margin-top: 28px;
            margin-bottom: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}

        thead {{
            display: table-header-group;
        }}

        th {{
            text-align: left;
            background: #f4f4f4;
            padding: 6px 8px;
            border-bottom: 1px solid #ccc;
        }}

        td {{
            padding: 6px 8px;
            border-bottom: 1px solid #eee;
        }}

        tr {{
            break-inside: avoid;
        }}
    </style>
    </head>

    <body>
        <h1>Sales Report</h1>
        <div class="subtitle">Generated {today}</div>

        <div class="totals">
            <div class="total-box">
                <div class="label">Total Orders</div>
                <div class="value">{data['total_orders']}</div>
            </div>

            <div class="total-box">
                <div class="label">Total Revenue</div>
                <div class="value">${data['total_revenue']:.2f}</div>
            </div>
        </div>

        <h2>Top 5 Products by Revenue</h2>

        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
                {top_products_rows}
            </tbody>
        </table>

        <h2>Orders — Last 7 Days</h2>

        <table>
            <thead>
                <tr>
                    <th>Day</th>
                    <th>Orders</th>
                </tr>
            </thead>
            <tbody>
                {per_day_rows}
            </tbody>
        </table>

        <h2>All Orders</h2>

        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Product</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {all_orders_rows}
            </tbody>
        </table>
    </body>
    </html>
    """


async def generate_pdf(html: str, path: str):
    """Stage 3 — render HTML to PDF using async Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        page = await browser.new_page()

        await page.set_content(html)

        await page.pdf(
            path=path,
            format="A4",
            print_background=True,
        )

        await browser.close()


async def build_report(path: str) -> dict:
    """Convenience wrapper used by the API: query -> render -> write PDF."""
    data = get_report_data()
    html = render_html(data)

    await generate_pdf(html, path)

    return data