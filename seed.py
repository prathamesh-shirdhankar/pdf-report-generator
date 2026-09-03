"""
seed.py — Stage 1
Fills report.db with ~200 random orders. Run it as many times as you like:
it deletes all existing rows first, so the row count never doubles.

Run with:  python seed.py
"""

import random
from datetime import datetime, timedelta

from db import get_conn, init_db

CUSTOMERS = ["Aria Patel", "Ben Lucas", "Chidi Okafor", "Dana Kim", "Elena Ruiz",
             "Farid Hassan", "Grace Liu", "Hana Sato", "Ivan Petrov", "Julia Novak"]

PRODUCTS = ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub", "Webcam", "Desk Lamp", "Monitor Stand"]


def seed(n_orders: int = 200):
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    # Delete first — running this script twice must leave exactly one clean copy.
    cur.execute("DELETE FROM orders")

    rows = []
    now = datetime.now()
    for _ in range(n_orders):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(5, 200), 2)
        days_ago = random.randint(0, 29)
        created_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append((customer, product, amount, created_at))

    cur.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    print(f"Seeded {count} orders into report.db")


if __name__ == "__main__":
    seed()
