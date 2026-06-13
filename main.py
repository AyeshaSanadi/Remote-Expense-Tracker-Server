from fastmcp import FastMCP
from contextlib import asynccontextmanager

import os
import json
import aiosqlite

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "expenses.db"
)

CATEGORIES_PATH = os.path.join(
    os.path.dirname(__file__),
    "expense_category.json"
)


# --------------------------------------------------
# Database Initialization
# --------------------------------------------------

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            "PRAGMA journal_mode=WAL"
        )

        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

        await db.commit()

        print("Database initialized successfully")


# --------------------------------------------------
# MCP Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(server):
    await init_db()
    yield


mcp = FastMCP(
    name="RemoteExpenseTracker",
    lifespan=lifespan
)


# --------------------------------------------------
# Add Expense
# --------------------------------------------------

@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Add a new expense.
    """

    async with aiosqlite.connect(DB_PATH) as conn:

        cursor = await conn.execute(
            """
            INSERT INTO expenses(
                date,
                amount,
                category,
                subcategory,
                note
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                date,
                amount,
                category,
                subcategory,
                note
            )
        )

        await conn.commit()

        return {
            "status": "ok",
            "expense_id": cursor.lastrowid
        }


# --------------------------------------------------
# List Expenses
# --------------------------------------------------

@mcp.tool()
async def list_expenses():
    """
    Return all expenses.
    """

    async with aiosqlite.connect(DB_PATH) as conn:

        cursor = await conn.execute(
            """
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            ORDER BY id ASC
            """
        )

        cols = [d[0] for d in cursor.description]

        rows = await cursor.fetchall()

        return [
            dict(zip(cols, row))
            for row in rows
        ]


# --------------------------------------------------
# Summarize Expenses
# --------------------------------------------------

@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None
):
    """
    Summarize expenses between two dates.
    """

    async with aiosqlite.connect(DB_PATH) as conn:

        query = """
            SELECT
                category,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += """
            GROUP BY category
            ORDER BY category
        """

        cursor = await conn.execute(
            query,
            params
        )

        cols = [d[0] for d in cursor.description]

        rows = await cursor.fetchall()

        return [
            dict(zip(cols, row))
            for row in rows
        ]


# --------------------------------------------------
# Categories Resource
# --------------------------------------------------

@mcp.resource(
    "expense://categories",
    mime_type="application/json"
)
async def categories():

    with open(
        CATEGORIES_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


# --------------------------------------------------
# Run Server
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )