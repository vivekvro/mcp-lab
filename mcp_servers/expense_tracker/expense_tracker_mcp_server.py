import logging
import sqlite3
from datetime import datetime
from fastmcp import FastMCP
from typing import Optional

mcp = FastMCP(name="UserExpenseRecords")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_PATH = "data/expense.db"
TABLE_NAME = "ExpenseRecord"


# ---------- DB INIT ----------
def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount REAL NOT NULL,
                category TEXT,
                subcategory TEXT,
                description TEXT,
                date TEXT
            )
        """)
        conn.commit()


# ---------- UTIL ----------
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


# ---------- ADD ----------
@mcp.tool()
def add_expense_records(
    user_id: str,
    amount: float,
    category: str = "Unknown",
    subcategory: str = "Unknown",
    description: str = "No description",
    date: Optional[str] = None
):
    if not user_id:
        raise ValueError("user_id is required")

    if date is None:
        date = get_current_date()

    create_table()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {TABLE_NAME}
            (user_id, amount, category, subcategory, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, category.lower(), subcategory.lower(), description, date))
        conn.commit()

    return "Expense added successfully"


# ---------- GET ALL ----------
@mcp.tool()
def get_all_expenses(user_id: str):
    if not user_id:
        raise ValueError("user_id is required")

    create_table()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,))
        return cur.fetchall()


# ---------- BY CATEGORY ----------
@mcp.tool()
def get_expenses_by_category(user_id: str, category: str):
    create_table()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ? AND category = ?
            ORDER BY date DESC
        """, (user_id, category.lower()))
        return cur.fetchall()


# ---------- BY DATE RANGE ----------
@mcp.tool()
def get_expenses_by_date_range(user_id: str, start: str, end: str):
    create_table()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ? AND date BETWEEN ? AND ?
        """, (user_id, start, end))
        return cur.fetchall()


# ---------- BY CATEGORY + DATE ----------
@mcp.tool()
def get_expenses_by_date_range_and_category(
    user_id: str, category: str, start: str, end: str
):
    create_table()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ?
            AND category = ?
            AND date BETWEEN ? AND ?
            ORDER BY date DESC
        """, (user_id, category.lower(), start, end))
        return cur.fetchall()


# ---------- RUN ----------
if __name__ == "__main__":
    create_table()
    mcp.run(transport="http", host="0.0.0.0", port=8001)