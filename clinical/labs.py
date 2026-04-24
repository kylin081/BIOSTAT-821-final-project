"""
clinical/labs.py
================
Lab result analysis module for clinical data.

Mirrors the structure of clinical/patients.py:
  - Uses the same SQLite database (clinical.db) via get_connection()
  - Returns plain dicts (sqlite3.Row -> dict), no ORM or API dependency
  - Pure-logic helpers (NORMAL_RANGES, is_abnormal) have no I/O side effects

Expected schema
---------------
    CREATE TABLE lab_results (
        lab_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id   INTEGER NOT NULL,
        lab_name     TEXT    NOT NULL,
        value        REAL    NOT NULL,
        unit         TEXT    NOT NULL DEFAULT '',
        collected_at TEXT    NOT NULL,   -- ISO-8601, e.g. '2024-03-15T09:30:00'
        notes        TEXT             DEFAULT ''
    );
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Database connection  (identical pattern to patients.py)
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).parent.parent / "clinical.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# 1.  Reference-range catalogue  (pure data, no I/O)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReferenceRange:
    """Inclusive [low, high] normal range for a lab test."""
    low: float
    high: float
    unit: str = ""
    description: str = ""


# Keys are normalised: lowercase + stripped.
NORMAL_RANGES: dict[str, ReferenceRange] = {
    # Metabolic / basic panel
    "glucose":    ReferenceRange(70.0, 99.0, "mg/dL", "Fasting blood glucose"),
    "bun":        ReferenceRange(7.0, 20.0, "mg/dL", "Blood urea nitrogen"),
    "creatinine": ReferenceRange(0.6, 1.2, "mg/dL", "Serum creatinine"),
    "sodium":     ReferenceRange(136.0, 145.0, "mEq/L", "Serum sodium"),
    "potassium":  ReferenceRange(3.5, 5.0, "mEq/L", "Serum potassium"),
    "chloride":   ReferenceRange(98.0, 107.0, "mEq/L", "Serum chloride"),
    "co2":        ReferenceRange(22.0, 29.0, "mEq/L", "Carbon dioxide / bicarbonate"),
    "calcium":    ReferenceRange(8.5, 10.5, "mg/dL", "Serum calcium"),
    "magnesium":  ReferenceRange(1.7, 2.2, "mg/dL", "Serum magnesium"),
    "phosphorus": ReferenceRange(2.5, 4.5, "mg/dL", "Serum phosphorus"),
    # Liver function
    "alt":           ReferenceRange(7.0, 56.0, "U/L", "Alanine aminotransferase"),
    "ast":           ReferenceRange(10.0, 40.0, "U/L", "Aspartate aminotransferase"),
    "alp":           ReferenceRange(44.0, 147.0, "U/L", "Alkaline phosphatase"),
    "bilirubin":     ReferenceRange(0.1, 1.2, "mg/dL", "Total bilirubin"),
    "albumin":       ReferenceRange(3.4, 5.4, "g/dL", "Serum albumin"),
    "total protein": ReferenceRange(6.0, 8.3, "g/dL", "Total serum protein"),
    # Complete blood count
    "hemoglobin":  ReferenceRange(12.0, 17.5, "g/dL", "Hemoglobin"),
    "hematocrit":  ReferenceRange(36.0, 50.0, "%", "Hematocrit"),
    "wbc":         ReferenceRange(4.5, 11.0, "10^3/uL", "White blood cell count"),
    "rbc":         ReferenceRange(4.2, 5.9, "10^6/uL", "Red blood cell count"),
    "platelets":   ReferenceRange(150.0, 400.0, "10^3/uL", "Platelet count"),
    "mcv":         ReferenceRange(80.0, 100.0, "fL", "Mean corpuscular volume"),
    "mch":         ReferenceRange(27.0, 33.0, "pg", "Mean corpuscular haemoglobin"),
    "mchc":        ReferenceRange(32.0, 36.0, "g/dL", "MCH concentration"),
    "rdw":         ReferenceRange(11.5, 14.5, "%", "Red cell distribution width"),
    "neutrophils": ReferenceRange(1.8, 7.7, "10^3/uL", "Absolute neutrophil count"),
    "lymphocytes": ReferenceRange(1.0, 4.8, "10^3/uL", "Absolute lymphocyte count"),
    # Lipid panel
    "total cholesterol": ReferenceRange(0.0, 199.0, "mg/dL", "Total cholesterol"),
    "ldl":               ReferenceRange(0.0, 99.0, "mg/dL", "LDL cholesterol"),
    "hdl":               ReferenceRange(40.0, 9999.0, "mg/dL", "HDL cholesterol"),
    "triglycerides":     ReferenceRange(0.0, 149.0, "mg/dL", "Triglycerides"),
    # Thyroid
    "tsh": ReferenceRange(0.4, 4.0, "mIU/L", "Thyroid-stimulating hormone"),
    "t4":  ReferenceRange(5.0, 12.0, "ug/dL", "Total thyroxine"),
    "t3":  ReferenceRange(80.0, 200.0, "ng/dL", "Total triiodothyronine"),
    # Coagulation
    "pt":  ReferenceRange(11.0, 13.5, "seconds", "Prothrombin time"),
    "inr": ReferenceRange(0.8, 1.1, "", "International normalised ratio"),
    "ptt": ReferenceRange(25.0, 35.0, "seconds", "Partial thromboplastin time"),
    # Hormones / miscellaneous
    "hba1c":              ReferenceRange(0.0, 5.6, "%", "Glycated haemoglobin"),
    "ferritin":           ReferenceRange(12.0, 300.0, "ng/mL", "Serum ferritin"),
    "iron":               ReferenceRange(60.0, 170.0, "ug/dL", "Serum iron"),
    "uric acid":          ReferenceRange(2.4, 7.0, "mg/dL", "Uric acid"),
    "c-reactive protein": ReferenceRange(0.0, 1.0, "mg/dL", "C-reactive protein"),
    "esr":         ReferenceRange(0.0, 20.0, "mm/hr", "Erythrocyte sedimentation rate"),
    "vitamin d":          ReferenceRange(20.0, 50.0, "ng/mL", "25-hydroxyvitamin D"),
    "vitamin b12":        ReferenceRange(200.0, 900.0, "pg/mL", "Vitamin B12"),
    "folate":             ReferenceRange(2.7, 17.0, "ng/mL", "Serum folate"),
    "psa":         ReferenceRange(0.0, 4.0, "ng/mL", "Prostate-specific antigen"),
    "amylase":            ReferenceRange(30.0, 110.0, "U/L", "Serum amylase"),
    "lipase":             ReferenceRange(0.0, 160.0, "U/L", "Serum lipase"),
}


def _normalise(lab_name: str) -> str:
    """Return a canonical lookup key for a lab name."""
    return lab_name.strip().lower()


def get_reference_range(lab_name: str) -> ReferenceRange | None:
    """Return the ReferenceRange for *lab_name*, or None if unknown.

    Lookup is case-insensitive and strips surrounding whitespace.
    """
    return NORMAL_RANGES.get(_normalise(lab_name))


# ---------------------------------------------------------------------------
# 2.  Pure-logic helper  (no I/O)
# ---------------------------------------------------------------------------

def is_abnormal(lab_name: str, value: float) -> bool:
    """Return True if *value* falls outside the normal range for *lab_name*.

    Args:
        lab_name: Name of the lab test (case-insensitive).
        value:    Numeric measurement to evaluate.

    Returns:
        True if the value is below the lower bound or above the upper bound
        of the reference range; False if it is within the normal range.

    Raises:
        ValueError: If *lab_name* is not present in NORMAL_RANGES.

    Example:
        >>> is_abnormal("glucose", 85.0)
        False
        >>> is_abnormal("glucose", 250.0)
        True
    """
    ref = get_reference_range(lab_name)
    if ref is None:
        raise ValueError(
            f"Unknown lab test '{lab_name}'. "
            "Add it to NORMAL_RANGES or verify the spelling."
        )
    return value < ref.low or value > ref.high


def _annotate(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a dict and attach the computed 'abnormal' flag."""
    result = dict(row)
    ref = get_reference_range(result["lab_name"])
    if ref is not None:
        result["abnormal"] = is_abnormal(result["lab_name"], result["value"])
    else:
        result["abnormal"] = None   # lab not in catalogue
    return result


# ---------------------------------------------------------------------------
# 3.  Database-backed query functions  (mirror patients.py style)
# ---------------------------------------------------------------------------

def get_patient_labs(patient_id: int) -> list[dict]:
    """Retrieve all lab results for a patient, ordered by collection time.

    Args:
        patient_id: The unique patient identifier (matches patients.patient_id).

    Returns:
        A list of dicts, one per lab result, each containing all columns from
        the lab_results table plus a computed 'abnormal' key:
          - True  — value is outside the reference range
          - False — value is within the reference range
          - None  — lab name is not in NORMAL_RANGES (cannot be evaluated)
        Returns an empty list if the patient has no recorded results.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM   lab_results
            WHERE  patient_id = ?
            ORDER  BY collected_at ASC
            """,
            (patient_id,),
        ).fetchall()

    return [_annotate(row) for row in rows]


def get_abnormal_labs(patient_id: int | None = None) -> list[dict]:
    """Return all lab results whose values fall outside normal reference ranges.

    Args:
        patient_id: If provided, restrict results to that patient only.
                    If omitted (default), search across all patients.

    Returns:
        A list of dicts for every result flagged as abnormal (abnormal=True),
        ordered by collection time.  Results for lab names absent from
        NORMAL_RANGES are excluded (their 'abnormal' value is None, not True).
    """
    if patient_id is not None:
        candidates = get_patient_labs(patient_id)
    else:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM lab_results ORDER BY collected_at ASC"
            ).fetchall()
        candidates = [_annotate(row) for row in rows]

    return [r for r in candidates if r["abnormal"] is True]