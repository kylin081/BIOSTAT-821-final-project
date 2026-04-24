"""
clinical/patients.py

Patient-related business logic.
This module handles all patient data retrieval and calculations.
It does not depend on the API layer.
"""

import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "clinical.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_age(date_of_birth: str) -> int:
    """Calculate a patient's age in years from their date of birth.

    Args:
        date_of_birth: Date string in YYYY-MM-DD format.

    Returns:
        Age in full years.

    Example:
        >>> calculate_age("1980-03-15")
        46
    """
    birth = date.fromisoformat(date_of_birth)
    today = date.today()
    age = today.year - birth.year
    # Subtract 1 if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


def get_patient_by_id(patient_id: int) -> Optional[dict]:
    """Retrieve a single patient by their ID.

    Args:
        patient_id: The unique patient identifier.

    Returns:
        A dict with patient fields and computed age, or None if not found.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
        ).fetchone()

    if row is None:
        return None

    patient = dict(row)
    patient["age"] = calculate_age(patient["date_of_birth"])
    return patient


def list_all_patients() -> list[dict]:
    """Retrieve all patients from the database.

    Returns:
        A list of dicts, each representing a patient with computed age.
    """
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM patients").fetchall()

    patients = []
    for row in rows:
        patient = dict(row)
        patient["age"] = calculate_age(patient["date_of_birth"])
        patients.append(patient)
    return patients
