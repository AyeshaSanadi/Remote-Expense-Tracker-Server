from fastmcp import FastMCP
import os
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = "F:\MCP\ExpenseTracker\expense_category.json"

mcp = FastMCP(name="ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()


@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add expenses to the db"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "ok", "id":cursor.lastrowid}


@mcp.tool()
def list_expenses():
    "list all the expenses from db"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC")
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]


@mcp.tool()
def summarize(start_date, end_date, category=None):
    """ Sumarize expense by category within an inclusive date range"""
    with sqlite3.connect(DB_PATH) as conn:
        query = (
            """SELECT category, SUM(amount) AS total_amount FROM expenses WHERE date BETWEEN ? AND ?"""
        )
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cursor = conn.execute(query, params)
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # if we want to build remote server then we need to specify the transport which they are working on.
    mcp.run("http", )