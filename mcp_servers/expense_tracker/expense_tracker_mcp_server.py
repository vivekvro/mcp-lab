import logging
import sqlite3
from datetime import datetime
from fastmcp import FastMCP
from typing import Annotated,Optional
from dotenv import load_dotenv
from os import getenv






mcp = FastMCP(name="UserExpenseRecords")

logging.basicConfig(
    filename="expense.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"

)

username=getenv("USERNAME")
db_path = f"{username}_expense_tracking.db"
table_name = "ExpenseRecord"




# create Table if not exist

def create_ExpenseRecord_table():
    try :
        with sqlite3.connect(db_path) as conn :
            cur = conn.cursor()
            cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name}(

                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            amount REAL NOT NULL,
                            category TEXT,
                            subcategory TEXT,
                            description TEXT,
                            date TEXT
                        )
                """)
            conn.commit()
        logging.info(f"TABLE '{table_name}' CREATED")
    except Exception as e:
        logging.error(f"error : {e}")



# get current time if not given or failed to retrieve

def get_current_date()->str:
    date = datetime.now().strftime("%Y-%m-%d")
    return str(date)


# Insert Records

@mcp.tool()
def add_expense_records(amount:float,category:str="Unknown",subcategory:str="Unknown",description:str="No description",date:Optional[str]=None):
    """
    Add a new expense record to the ExpenseRecord table.

        Args:
            amount (float): Expense amount.
            category (str): Main category (e.g., Food, Travel).
            subcategory (str): Subcategory of expense.
            description (str): Optional description of the expense.
            date (str): Date in YYYY-MM-DD format. Defaults to current date.

        Returns:
            str: Success or error message.
        """
    if date is None:
        date=get_current_date()

    category = category.lower()
    subcategory = subcategory.lower()
    givendata = (amount, category, subcategory,description,date)
    try:
        with sqlite3.connect(db_path) as conn:
            query = f"""
                        INSERT INTO {table_name} (amount, category, subcategory,description,date)
                        VALUES (?,?,?,?,?);
            """
            cur = conn.cursor()
            cur.execute(query,givendata)
            conn.commit()
        logging.info(f"Values Inserted In {table_name} Successfully")
    except sqlite3.OperationalError :
        try:
            create_ExpenseRecord_table()
            with sqlite3.connect(db_path) as conn:
                query = f"""
                            INSERT INTO {table_name} (amount, category, subcategory,description,date)
                            VALUES (?,?,?,?,?);
                """
                cur = conn.cursor()
                cur.execute(query,givendata)
                conn.commit()
        except Exception as e:
            logging.error(f"Error inserting record: {e}")


# Get all Expense Records

@mcp.tool()
def get_all_expenses():
    """
    Get all Expense Records from  ExpenseRecord table
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(f""" SELECT * FROM {table_name} ORDER BY date DESC;""")
            rows = cur.fetchall()

        logging.info(f"Fetched all expense records ({len(rows)} rows)")
        return rows

    except Exception as e :
        logging.error(f"Error while fetching Records : {e}")
        return []



# get expense records by category

@mcp.tool()
def get_expenses_by_category(category:str):
    """
    Get Expense Records from  ExpenseRecord table by category
    Args:
        category (string): category name.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT * FROM {table_name}
                WHERE category = ?
                ORDER BY date DESC
            """, (category,))
            rows = cur.fetchall()

        logging.info(f"Fetched expense records ({len(rows)} rows)")
        return rows

    except Exception as e :
        logging.error(f"Error while fetching Records : {e}")
        return []



# get expense records by date range

@mcp.tool()
def get_expenses_by_date_range(start:str,end:str):
    """
    Get Expense Records from ExpenseRecord table between two dates.
    Args:
    category(string): category name
        start(string): format YYYY-MM-DD
        end(string): format YYYY-MM-DD
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""
                                SELECT * FROM {table_name} where date BETWEEN ? and ?
                """,(start,end))
            rows = cur.fetchall()

        logging.info(f"Fetched Expense Records by dates between %s - %s",start,end)
        return rows

    except Exception as e :
        logging.error(f"Error while fetching Records by dates : {e}")
        return []



# get expense records by date range and category

@mcp.tool()
def get_expenses_by_date_range_and_category(category: str, start: str, end: str):
    """
    Get Expense Records from ExpenseRecord table by category and date range.

    Args:
        category (str): category name
        start (str): format YYYY-MM-DD
        end (str): format YYYY-MM-DD
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT * FROM {table_name}
                WHERE category = ?
                AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (category, start, end))

            rows = cur.fetchall()

        logging.info("Fetched records for category '%s' between %s and %s",
                    category, start, end)
        return rows

    except Exception as e:
        logging.error(f"Error while fetching records: {e}")
        return []





if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=80001)

