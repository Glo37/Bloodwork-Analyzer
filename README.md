# Patient Bloodwork Analyzer

A REST API built in Python and Flask that analyzes patient bloodwork results against demographic-adjusted reference ranges and returns color-coded risk statuses per marker.

## Features

- Analyzes lab results and classifies each marker as green (normal), yellow (borderline), or red (abnormal)
- Adjusts alarm severity based on patient race and ethnicity using peer-reviewed clinical research
- Tracks patient results over multiple visits and detects trends (consistently abnormal, trending upward/downward)
- Returns a 1-10 alarm score per marker that accounts for current status, past visit history, and race-sensitive markers
- Surfaces relevant race and ethnicity clinical facts alongside each result
- Input validation with descriptive error messages on all requests

## Tech Stack

- Python
- Flask
- SQLite
- REST API

## Project Structure

    bloodwork-analyzer/
    ├── app.py          # Flask routes and input validation
    ├── models.py       # Patient, LabResult, StatusResult, TrendResult classes
    ├── analyzer.py     # Analysis logic, alarm scoring, trend detection
    ├── database.py     # SQLite connection, queries, and data functions
    ├── seed.py         # Populates reference ranges table

## Setup

    pip3 install flask
    python3 seed.py
    python3 app.py

## API Routes

### POST /analyze
Submit a patient and their lab results for analysis.

Request body:

    {
      "name": "Gloria",
      "age": 21,
      "sex": "female",
      "race": "black",
      "ethnicity": "african american",
      "results": [
        {"marker": "hemoglobin", "value": 11.2, "unit": "g/dL"},
        {"marker": "glucose", "value": 105.0, "unit": "mg/dL"},
        {"marker": "creatinine", "value": 1.1, "unit": "mg/dL"}
      ]
    }

Response:

    {
      "patient_id": 1,
      "results": [
        {
          "marker": "hemoglobin",
          "value": 11.2,
          "unit": "g/dL",
          "low": 12.0,
          "high": 15.5,
          "status": "red",
          "alarm_score": 9,
          "message": "Abnormal — consult a provider",
          "race_fact": "Hemoglobin variation in African populations has 94% heritability with distinct genetic loci compared to European populations. (Source: GWAS of HbF in SCD)"
        }
      ]
    }

### GET /patient/<id>
Returns a patient's profile and full visit history.

### GET /patient/<id>/trends
Returns trend analysis across all visits including flags for consistently abnormal or trending markers.

## Supported Markers

Hemoglobin, glucose, creatinine, sodium, potassium

## Clinical Research Sources

- GWAS of Fetal Hemoglobin in Sickle Cell Disease (Cameroon, Tanzania, USA)
- ESKD Cohort Study — serum creatinine differences by race (CJASN)
- NHANES 1999–2018 — cardiometabolic health trends by race and ethnicity (ACC)
- AHA Review — racial and ethnic disparities in cardiovascular outcomes

## Notes

The system is designed to support race-specific reference ranges as that data becomes available from population-level clinical studies. Current ranges follow general clinical standards while alarm scoring and clinical facts already adjust meaningfully by race and ethnicity.