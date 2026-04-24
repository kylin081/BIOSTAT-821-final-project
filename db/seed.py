"""
db/seed.py

Initializes the SQLite database and inserts sample data.
Run this script to (re)create all tables and populate them with test data.

Usage:
    python db/seed.py
"""

import sqlite3
from pathlib import Path

# Paths
DB_PATH = Path(__file__).parent.parent / "clinical.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db() -> sqlite3.Connection:
    """Create tables from schema.sql."""
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def seed_patients(conn: sqlite3.Connection) -> None:
    """Insert sample patients."""
    patients = [
        ("Alice", "Johnson", "1980-03-15", "F"),
        ("Bob", "Smith", "1945-07-22", "M"),
        ("Carol", "Lee", "1992-11-30", "F"),
        ("David", "Brown", "1968-01-10", "M"),
        ("Eva", "Martinez", "2000-06-05", "F"),
    ]
    conn.executemany(
        """INSERT INTO patients
           (first_name, last_name, date_of_birth, sex)
           VALUES (?, ?, ?, ?)""",
        patients,
    )
    conn.commit()


def seed_lab_results(conn: sqlite3.Connection) -> None:
    """Insert sample lab results, including some abnormal values."""
    lab_results = [
        # (patient_id, lab_name, value, unit, collected_at)
        # Alice — normal
        (1, "glucose", 95.0, "mg/dL", "2026-01-10 08:30:00"),
        (1, "hemoglobin", 13.5, "g/dL", "2026-01-10 08:30:00"),
        (1, "wbc", 6.2, "10^9/L", "2026-01-10 08:30:00"),
        # Bob — high glucose (diabetic range), low hemoglobin (anemia)
        (2, "glucose", 210.0, "mg/dL", "2026-02-14 09:00:00"),
        (2, "hemoglobin", 10.8, "g/dL", "2026-02-14 09:00:00"),
        (2, "wbc", 7.1, "10^9/L", "2026-02-14 09:00:00"),
        # Carol — normal
        (3, "glucose", 88.0, "mg/dL", "2026-03-01 07:45:00"),
        (3, "hemoglobin", 14.1, "g/dL", "2026-03-01 07:45:00"),
        # David — high WBC (possible infection)
        (4, "glucose", 102.0, "mg/dL", "2026-03-20 10:15:00"),
        (4, "wbc", 13.5, "10^9/L", "2026-03-20 10:15:00"),
        # Eva — low glucose (hypoglycemia)
        (5, "glucose", 58.0, "mg/dL", "2026-04-05 06:00:00"),
        (5, "hemoglobin", 12.9, "g/dL", "2026-04-05 06:00:00"),
    ]
    conn.executemany(
        """INSERT INTO lab_results
           (patient_id, lab_name, value, unit, collected_at)
           VALUES (?, ?, ?, ?, ?)""",
        lab_results,
    )
    conn.commit()


def main() -> None:
    print(f"Initializing database at: {DB_PATH}")
    conn = init_db()
    print("Tables created.")

    seed_patients(conn)
    print("Patients seeded.")

    seed_lab_results(conn)
    print("Lab results seeded.")

    conn.close()
    print("Done. Database is ready.")


if __name__ == "__main__":
    main()
