import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("cinema.db")


def get_connection():
    """Create a connection to the local SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the shows table and insert demo data only when it is empty."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shows (
                show_id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_name TEXT NOT NULL,
                show_time TEXT NOT NULL,
                total_seats INTEGER NOT NULL CHECK(total_seats > 0),
                booked_seats INTEGER NOT NULL DEFAULT 0
                    CHECK(booked_seats >= 0 AND booked_seats <= total_seats)
            )
        """)

        count = conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0]
        if count == 0:
            demo_rows = [
                ("Sky Force", "10:00 AM", 150, 100),
                ("Sky Force", "02:00 PM", 150, 125),
                ("The Wild Robot", "11:00 AM", 120, 72),
                ("The Wild Robot", "06:00 PM", 120, 96),
                ("Bhool Bhulaiyaa 3", "03:00 PM", 200, 160),
                ("Bhool Bhulaiyaa 3", "09:00 PM", 200, 110),
            ]
            conn.executemany("""
                INSERT INTO shows (movie_name, show_time, total_seats, booked_seats)
                VALUES (?, ?, ?, ?)
            """, demo_rows)


def get_shows():
    """Return all show records as a list of dictionaries."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT show_id, movie_name, show_time, total_seats, booked_seats
            FROM shows
            ORDER BY movie_name, show_time
        """).fetchall()

    columns = ["show_id", "movie_name", "show_time", "total_seats", "booked_seats"]
    return [dict(zip(columns, row)) for row in rows]


def add_show(movie_name, show_time, total_seats, booked_seats):
    """Insert a new movie show after validating its seat counts."""
    movie_name = movie_name.strip()
    if not movie_name:
        raise ValueError("Movie name cannot be empty.")
    if total_seats <= 0:
        raise ValueError("Total seats must be greater than zero.")
    if booked_seats < 0 or booked_seats > total_seats:
        raise ValueError("Booked seats must be between 0 and total seats.")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO shows (movie_name, show_time, total_seats, booked_seats)
            VALUES (?, ?, ?, ?)
        """, (movie_name, show_time, total_seats, booked_seats))


def update_booked_seats(show_id, booked_seats):
    """Update booked seats for one show."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT total_seats FROM shows WHERE show_id = ?", (show_id,)
        ).fetchone()

        if row is None:
            raise ValueError("Show not found.")

        total_seats = row[0]
        if booked_seats < 0 or booked_seats > total_seats:
            raise ValueError("Booked seats must be between 0 and total seats.")

        conn.execute(
            "UPDATE shows SET booked_seats = ? WHERE show_id = ?",
            (booked_seats, show_id)
        )
