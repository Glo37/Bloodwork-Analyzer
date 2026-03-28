from flask import Flask, request, jsonify
from models import Patient, LabResult
from analyzer import BloodworkAnalyzer
from database import save_patient, save_visit, get_patient, get_patient_history, create_tables, find_patient

app = Flask(__name__)
analyzer = BloodworkAnalyzer()

create_tables()

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if not data.get("age") or not isinstance(data["age"], int) or data["age"] <= 0:
        errors.append("age must be a positive integer")
    if not data.get("sex") or data["sex"].lower() not in ["male", "female"]:
        errors.append("sex must be male or female")
    if not data.get("race"):
        errors.append("race is required")
    if not data.get("ethnicity"):
        errors.append("ethnicity is required")
    if not data.get("results") or len(data["results"]) == 0:
        errors.append("at least one result is required")

    if errors:
        return jsonify({"errors": errors}), 400

    patient = Patient(
        name=data["name"],
        age=data["age"],
        sex=data["sex"].lower(),
        race=data["race"].lower(),
        ethnicity=data["ethnicity"].lower()
    )

    results = [
        LabResult(
            marker=r["marker"].lower(),
            value=r["value"],
            unit=r["unit"]
        )
        for r in data["results"]
    ]


    existing_id = find_patient(patient.name, patient.sex, patient.race)
    patient_id = existing_id if existing_id else save_patient(patient)
    status_results = analyzer.evaluate(patient, results, patient_id)

    for result in status_results:
        save_visit(patient_id, result)

    return jsonify({
        "patient_id": patient_id,
        "results": [vars(s) for s in status_results]
    })

@app.route("/patient/<int:patient_id>", methods=["GET"])
def get_patient_route(patient_id):
    patient = get_patient(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    history = get_patient_history(patient_id)

    return jsonify({
        "patient": {
            "id": patient[0],
            "name": patient[1],
            "age": patient[2],
            "sex": patient[3],
            "race": patient[4],
            "ethnicity": patient[5]
        },
        "history": [
            {
                "marker": row[0],
                "value": row[1],
                "unit": row[2],
                "status": row[3],
                "alarm_score": row[4],
                "visit_date": row[5]
            }
            for row in history
        ]
    })

@app.route("/patient/<int:patient_id>/trends", methods=["GET"])
def get_trends(patient_id):
    patient = get_patient(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    trends = analyzer.get_trends(patient_id)

    return jsonify([
        {
            "marker": t.marker,
            "flags": t.flags,
            "history": t.history
        }
        for t in trends
    ])

if __name__ == "__main__":
    app.run(debug=True)