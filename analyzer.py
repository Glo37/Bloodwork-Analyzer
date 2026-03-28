from models import Patient, LabResult, StatusResult, TrendResult
from database import get_range, get_patient_history

RACE_FACTS = {
    "black": {
        "hemoglobin": "Hemoglobin variation in African populations has 94% heritability with distinct genetic loci compared to European populations. Borderline values may warrant additional screening for sickle cell related conditions. (Source: GWAS of HbF in SCD, Cameroon/Tanzania/USA)",
        "creatinine": "Black patients show significantly higher serum creatinine (+1.68 mg/dL) than non-Hispanic White patients even after adjusting for muscle mass, suggesting the difference is not purely physiological. Standard eGFR equations may underestimate kidney disease severity in Black patients. (Source: ESKD Cohort Study, CJASN)"
    },
    "asian": {
        "creatinine": "Asian patients show higher serum creatinine (+1.61 mg/dL) than non-Hispanic White patients independent of muscle mass differences, suggesting race-based creatinine adjustments are insufficient for accurate kidney function assessment. (Source: ESKD Cohort Study, CJASN)"
    },
    "hispanic": {
        "creatinine": "Hispanic patients show moderately higher serum creatinine (+0.83 mg/dL) than non-Hispanic White patients independent of muscle mass, indicating standard reference ranges may not fully apply. (Source: ESKD Cohort Study, CJASN)",
        "glucose": "Mexican American adults had the lowest prevalence of optimal cardiometabolic health (3.2%) compared to non-Hispanic White adults (8.4%) in 2017-2018, with glucose being one of the largest declining components. Elevated glucose values warrant close monitoring. (Source: NHANES 1999-2018, ACC)"
    },
    "all": {
        "glucose": "Only 6.8% of U.S. adults had optimal cardiometabolic health in 2017-2018, down from 1999. Optimal glucose levels declined from 59.4% to 36.9% across all populations. (Source: NHANES 1999-2018, ACC)",
        "cardiovascular": "Racial and ethnic disparities in cardiovascular outcomes are driven by differences in hypertension, diabetes, and social determinants of health. (Source: AHA CAD and Stroke Disparities Review)"
    }
}

class BloodworkAnalyzer:

    def evaluate(self, patient, results, patient_id=None):
        return [self._evaluate_single(patient, r, patient_id) for r in results]

    def _evaluate_single(self, patient, result, patient_id):
        range_row = get_range(result.marker, patient.sex, patient.age, patient.race)

        if range_row is None:
            return StatusResult(
                marker=result.marker,
                value=result.value,
                unit=result.unit,
                low=0,
                high=0,
                status="unknown",
                alarm_score=0,
                message="No reference range found",
                race_fact=None
            )

        low, high = range_row
        status, message = self._classify(result.value, low, high)
        alarm_score = self._calculate_alarm(result.value, low, high, status, patient, result.marker, patient_id)
        race_fact = self._get_race_fact(patient.race, result.marker)

        return StatusResult(
            marker=result.marker,
            value=result.value,
            unit=result.unit,
            low=low,
            high=high,
            status=status,
            alarm_score=alarm_score,
            message=message,
            race_fact=race_fact
        )

    def _classify(self, value, low, high):
        margin = (high - low) * 0.1

        if low <= value <= high:
            return "green", "Normal"
        elif (low - margin) <= value <= (high + margin):
            return "yellow", "Borderline"
        else:
            return "red", "Abnormal — consult a provider"

    def _calculate_alarm(self, value, low, high, status, patient, marker, patient_id):
        score = 0

        if status == "green":
            score = 2
        elif status == "yellow":
            score = 5
        elif status == "red":
            score = 7

        race_sensitive_markers = {
            "black": ["hemoglobin", "creatinine"],
            "asian": ["creatinine"],
            "hispanic": ["creatinine", "glucose"]
        }

        if patient.race in race_sensitive_markers:
            if marker in race_sensitive_markers[patient.race]:
                score += 1

        if patient_id:
            history = get_patient_history(patient_id)
            past = [h for h in history if h[0] == marker]

            if len(past) >= 1 and past[-1][3] in ["yellow", "red"]:
                score += 1
            if len(past) >= 2 and all(h[3] in ["yellow", "red"] for h in past[-2:]):
                score += 1

        return min(score, 10)

    def _get_race_fact(self, race, marker):
        race_facts = RACE_FACTS.get(race, {})
        fact = race_facts.get(marker)
        if not fact:
            fact = RACE_FACTS.get("all", {}).get(marker)
        return fact

    def get_trends(self, patient_id):
        history = get_patient_history(patient_id)

        markers = {}
        for row in history:
            marker, value, unit, status, alarm_score, visit_date = row
            if marker not in markers:
                markers[marker] = []
            markers[marker].append({
                "value": value,
                "unit": unit,
                "status": status,
                "alarm_score": alarm_score,
                "visit_date": visit_date
            })

        trends = []
        for marker, visits in markers.items():
            flags = []

            statuses = [v["status"] for v in visits]

            if len(statuses) >= 2 and all(s == "red" for s in statuses[-2:]):
                flags.append("Consistently abnormal across last 2 visits")
            if len(statuses) >= 3 and all(s in ["yellow", "red"] for s in statuses[-3:]):
                flags.append("Persistently elevated or abnormal across last 3 visits")

            values = [v["value"] for v in visits]
            if len(values) >= 2:
                if values[-1] > values[-2]:
                    flags.append("Trending upward since last visit")
                elif values[-1] < values[-2]:
                    flags.append("Trending downward since last visit")

            trends.append(TrendResult(
                marker=marker,
                flags=flags,
                history=visits
            ))

        return trends