"""
api/main.py
===========
REST API layer for the clinical application.

All data access goes through the clinical/ library.
This module contains no direct database calls.

Run with:
    uvicorn api.main:app --reload

Endpoints
---------
GET /patients/{id}           — patient info + computed age
GET /patients/{id}/labs      — all lab results for a patient
GET /labs/abnormal           — all abnormal lab results (optional ?patient_id=)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from clinical.labs import get_abnormal_labs, get_patient_labs
from clinical.patients import get_patient_by_id

app = FastAPI(
    title="Clinical API",
    description="Patient and lab result endpoints backed by the clinical library.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# GET /patients/{id}
# ---------------------------------------------------------------------------


@app.get(
    "/patients/{patient_id}",
    summary="Get patient by ID",
    response_description="Patient record with computed age",
)
def read_patient(patient_id: int) -> JSONResponse:
    """Return a single patient's information.

    - **patient_id**: integer primary key from the patients table

    Raises **404** if no patient with that ID exists.
    """
    patient = get_patient_by_id(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found.",
        )
    return JSONResponse(content=patient)


# ---------------------------------------------------------------------------
# GET /patients/{id}/labs
# ---------------------------------------------------------------------------


@app.get(
    "/patients/{patient_id}/labs",
    summary="Get all lab results for a patient",
    response_description="List of lab results with abnormal flag",
)
def read_patient_labs(patient_id: int) -> JSONResponse:
    """Return every lab result recorded for a patient, in chronological order.

    Each result includes an **abnormal** field:
    - `true`  — value is outside the reference range
    - `false` — value is within the reference range
    - `null`  — lab name is not in the reference catalogue

    Raises **404** if no patient with that ID exists.
    """
    patient = get_patient_by_id(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found.",
        )
    labs = get_patient_labs(patient_id)
    return JSONResponse(content=labs)


# ---------------------------------------------------------------------------
# GET /labs/abnormal
# ---------------------------------------------------------------------------


@app.get(
    "/labs/abnormal",
    summary="Get all abnormal lab results",
    response_description="List of abnormal lab results across all patients",
)
def read_abnormal_labs(
    patient_id: int | None = Query(
        default=None,
        description="Restrict results to a single patient (optional).",
    ),
) -> JSONResponse:
    """Return every lab result whose value falls outside the normal range.

    Pass **?patient_id=** to scope results to one patient.
    Results for unrecognised lab names are excluded.

    Raises **404** when **patient_id** is supplied but the patient does not exist.
    """
    if patient_id is not None:
        patient = get_patient_by_id(patient_id)
        if patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Patient {patient_id} not found.",
            )
    labs = get_abnormal_labs(patient_id=patient_id)
    return JSONResponse(content=labs)
