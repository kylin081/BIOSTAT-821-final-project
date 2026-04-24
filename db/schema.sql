-- Clinical Data System
-- SQLite Database Schema

-- Drop tables if they exist (for clean re-initialization)
DROP TABLE IF EXISTS lab_results;
DROP TABLE IF EXISTS patients;

-- Patients table
CREATE TABLE patients (
    patient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name   TEXT    NOT NULL,
    last_name    TEXT    NOT NULL,
    date_of_birth TEXT   NOT NULL,  -- format: YYYY-MM-DD
    sex          TEXT    NOT NULL CHECK(sex IN ('M', 'F', 'Other'))
);

-- Lab results table
CREATE TABLE lab_results (
    result_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL,
    lab_name     TEXT    NOT NULL,  -- e.g. 'glucose', 'hemoglobin'
    value        REAL    NOT NULL,
    unit         TEXT    NOT NULL,  -- e.g. 'mg/dL', 'g/dL'
    collected_at  TEXT    NOT NULL,  -- format: YYYY-MM-DD HH:MM:SS
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);