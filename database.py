import sqlite3

DB = "bloodwork.db"

def get_connection():
    return sqlite3.connect(DB)

def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reference_ranges (
                id INTEGER PRIMARY KEY,
                marker TEXT,
                sex TEXT,
                age_min INTEGER,
                age_max INTEGER,
                race TEXT,
                low REAL,
                high REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                sex TEXT,
                race TEXT,
                ethnicity TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                marker TEXT,
                value REAL,
                unit TEXT,
                status TEXT,
                alarm_score INTEGER,
                visit_date TEXT DEFAULT (date('now')),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)

def get_range(marker, sex, age, race):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT low, high FROM reference_ranges
            WHERE marker = ?
            AND sex = ?
            AND age_min <= ? AND age_max >= ?
            AND (race = ? OR race = 'all')
            ORDER BY race DESC
            LIMIT 1
        """, (marker, sex, age, age, race)).fetchone()
    return row

def save_patient(patient):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO patients (name, age, sex, race, ethnicity)
            VALUES (?, ?, ?, ?, ?)
        """, (patient.name, patient.age, patient.sex, patient.race, patient.ethnicity))
        return cursor.lastrowid
    
def find_patient(name, sex, race):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id FROM patients
            WHERE name = ? AND sex = ? AND race = ?
            LIMIT 1
        """, (name, sex, race)).fetchone()
    return row[0] if row else None

def save_visit(patient_id, result):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO visits (patient_id, marker, value, unit, status, alarm_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, result.marker, result.value, result.unit, result.status, result.alarm_score))

def get_patient_history(patient_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT marker, value, unit, status, alarm_score, visit_date
            FROM visits
            WHERE patient_id = ?
            ORDER BY visit_date ASC
        """, (patient_id,)).fetchall()
    return rows

def get_patient(patient_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, name, age, sex, race, ethnicity
            FROM patients
            WHERE id = ?
        """, (patient_id,)).fetchone()
    return row