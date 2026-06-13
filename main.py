# converting whole code to async and await functionality
# bcaz if multiple user perform simulteneously operation on db then that should not be crashed or work unexpected.

from fastmcp import FastMCP
import os
import aiosqlite
import json
import asyncio

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__),"expense_category.json")

mcp = FastMCP(name="ExpenseTracker")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as c:
        await c.execute("PRAGMA journal_mode=WAL")
        await c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        await c.commit()

asyncio.run(init_db())


@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add expenses to the db"""
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        await conn.commit()
        return {"status": "ok", "id":cursor.lastrowid}


@mcp.tool()
async def list_expenses():
    "list all the expenses from db"
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC")
        cols = [d[0] for d in cursor.description]
        rows = await cursor.fetchall()
        return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def summarize(start_date, end_date, category=None):
    """ Sumarize expense by category within an inclusive date range"""
    async with aiosqlite.connect(DB_PATH) as conn:
        query = (
            """SELECT category, SUM(amount) AS total_amount FROM expenses WHERE date BETWEEN ? AND ?"""
        )
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cursor = await conn.execute(query, params)
        cols = [d[0] for d in cursor.description]
        rows = await cursor.fetchall()
        return [dict(zip(cols, r)) for r in rows]


@mcp.resource("expense://categories", mime_type="application/json")
async def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # if we want to build remote server then we need to specify the transport which they are working on.
    mcp.run(transport="http", host="127.0.0.1", port=8000)
