from database import get_connection, create_tables

ranges = [
    ("hemoglobin", "male",   18, 120, "all", 13.5, 17.5),
    ("hemoglobin", "female", 18, 120, "all", 12.0, 15.5),
    ("glucose",    "male",   18, 120, "all", 70.0, 99.0),
    ("glucose",    "female", 18, 120, "all", 70.0, 99.0),
    ("creatinine", "male",   18, 120, "all", 0.74, 1.35),
    ("creatinine", "female", 18, 120, "all", 0.59, 1.04),
    ("sodium",     "male",   18, 120, "all", 136.0, 145.0),
    ("sodium",     "female", 18, 120, "all", 136.0, 145.0),
    ("potassium",  "male",   18, 120, "all", 3.5, 5.1),
    ("potassium",  "female", 18, 120, "all", 3.5, 5.1),
]

def seed():
    create_tables()
    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO reference_ranges
            (marker, sex, age_min, age_max, race, low, high)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ranges)
    print("Seeded successfully.")

if __name__ == "__main__":
    seed()