import logging,asyncio # planning for Async this server.
import sqlite3
from datetime import datetime
from fastmcp import FastMCP
from typing import Optional
import sys


mcp_ExpenseTracker = FastMCP(name="Expense_Tracker")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)

DB_PATH = "data/expense.db" #data\expense.db
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

@mcp_ExpenseTracker.tool()
def get_CurrenDate():
    """this tool return current date in YYYY-MM-DD format."""
    return get_current_date()



# ---------- ADD ----------
@mcp_ExpenseTracker.tool()
def add_expense_records(
    amount: float,
    category: str,
    subcategory: str,
    description: str,
    date: Optional[str],
    user_id : str =None
):
    """Adds a new expense record for a specific user with details such as amount, category, subcategory, description, and date. Automatically assigns the current date if not provided and ensures secure insertion into the database.

Arguments:

* amount (float): Monetary value of the expense.
* category (str): Main category of the expense (e.g., food, travel, bills).
* subcategory (str): More specific classification within the main category.
* description (str): Additional details or notes about the expense.
* date (Optional[str]): Date of the expense in YYYY-MM-DD format; defaults to the current date if not provided.
* user_id (str): REQUIRED unique identifier of the user; must always be provided and cannot be empty.
Returns:

* str: Confirmation message indicating successful addition of the expense.

Raises:

* ValueError: If user_id is missing in the configuration.
"""
    if not user_id:
        raise ValueError("user_id is required")

    if date is None:
        date = get_current_date()

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
@mcp_ExpenseTracker.tool()
def get_all_expenses(user_id:str=None):
    """Fetches all expense records associated with a specific user. Validates the presence of user context and retrieves data in descending order by date for efficient tracking and review.

Args:
* user_id (str): REQUIRED unique identifier of the user; must always be provided and cannot be empty.

Returns:

* List of all expense records for the given user, sorted by date (latest first).

Raises:

* ValueError: If user_id is missing in the configuration.
"""
    if not user_id:
        raise ValueError("user_id is required")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,))
        return cur.fetchall()


# ---------- BY CATEGORY ----------


@mcp_ExpenseTracker.tool()
def get_expenses_by_category(category: str,user_id:str=None):
    """Fetches user-specific expense records filtered by a given category. Ensures the database table exists before querying and returns results sorted in descending order by date for better readability and analysis.

    Arguments:

    * category (str): Expense category to filter by (e.g., food, travel, bills).
    user_id (str): REQUIRED unique identifier of the user; must always be provided and cannot be empty.

    Returns:

    * List of expense records matching the specified category.
    """
    user_id = user_id.lower().strip()
    if user_id is None:
        raise ValueError("Provide User ID")
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
@mcp_ExpenseTracker.tool()
def get_expenses_by_date_range( start_date: str, end_date: str, user_id:str):
    """Fetches user-specific expense records within a specified date range. Executes a secure, parameterized query to ensure data isolation and reliability.

Arguments:

* start_date (str): Start date of the range (inclusive), typically in YYYY-MM-DD format.
* end_date (str): End date of the range (inclusive), typically in YYYY-MM-DD format.
* user_id (str): REQUIRED unique identifier of the user; must always be provided and cannot be empty.

Returns:

* List of expense records that fall within the given date range.
"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = ? AND date BETWEEN ? AND ?
        """, (user_id, start_date, end_date))
        return cur.fetchall()


# ---------- BY CATEGORY + DATE ----------
@mcp_ExpenseTracker.tool()
def get_expenses_by_date_range_and_category(
    category: str, start: str, end: str, user_id:str
):
    """
        Fetches user-specific expense records filtered by category and a specified date range. Performs secure, parameterized database querying and returns results sorted in descending order by date for efficient tracking and analysis.

        Arguments:

        * category (str): Expense category to filter by (e.g., food, travel, bills).
        * start (str): Start date of the range (inclusive), typically in YYYY-MM-DD format.
        * end (str): End date of the range (inclusive), typically in YYYY-MM-DD format.
        * user_id (str): REQUIRED unique identifier of the user; must always be provided and cannot be empty.

        Returns:

        * List of expense records matching the given filters.
        """

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


# async def main():
#     tools = await mcp_ExpenseTracker.list_tools()
#     for tool in tools:
#         print(dir(tool))
#         break

# ---------- RUN ----------
if __name__ == "__main__":
    create_table()
    mcp_ExpenseTracker.run()#transport="http", port=8000