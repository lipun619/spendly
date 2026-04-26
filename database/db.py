import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            password_hash TEXT   NOT NULL,
            created_at   TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    user_id = cursor.lastrowid

    expenses = [
        (user_id, 450.00,  "Food",          "2026-04-01", "Grocery run"),
        (user_id, 120.00,  "Transport",     "2026-04-03", "Auto fare"),
        (user_id, 1800.00, "Bills",         "2026-04-05", "Electricity bill"),
        (user_id, 350.00,  "Health",        "2026-04-08", "Pharmacy"),
        (user_id, 600.00,  "Entertainment", "2026-04-10", "Movie night"),
        (user_id, 2500.00, "Shopping",      "2026-04-14", "Clothes"),
        (user_id, 200.00,  "Other",         "2026-04-17", "Miscellaneous"),
        (user_id, 380.00,  "Food",          "2026-04-20", "Restaurant dinner"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()


def create_user(name, email, password):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, generate_password_hash(password)),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return user


def get_user_stats(user_id):
    conn = get_db()
    row = conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN strftime('%Y-%m', date) = strftime('%Y-%m', 'now') THEN amount END), 0.0) AS total_this_month,
            COALESCE(SUM(amount), 0.0) AS total_all_time,
            COUNT(*) AS expense_count
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    top_row = conn.execute(
        """
        SELECT category FROM expenses
        WHERE user_id = ?
        GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    return {
        "total_this_month": row["total_this_month"] if row else 0.0,
        "total_all_time":   row["total_all_time"]   if row else 0.0,
        "expense_count":    row["expense_count"]    if row else 0,
        "top_category":     top_row["category"]     if top_row else None,
    }


def get_recent_expenses(user_id, limit=5):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, amount, category, date, description
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()
    return rows


def get_expenses_by_category(user_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT category, COALESCE(SUM(amount), 0.0) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return rows
