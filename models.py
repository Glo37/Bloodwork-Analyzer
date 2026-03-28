class Patient:
    def __init__(self, name, age, sex, race, ethnicity):
        self.name = name
        self.age = age
        self.sex = sex
        self.race = race
        self.ethnicity = ethnicity

class LabResult:
    def __init__(self, marker, value, unit):
        self.marker = marker
        self.value = value
        self.unit = unit

class StatusResult:
    def __init__(self, marker, value, unit, low, high, status, alarm_score, message, race_fact):
        self.marker = marker
        self.value = value
        self.unit = unit
        self.low = low
        self.high = high
        self.status = status
        self.alarm_score = alarm_score
        self.message = message
        self.race_fact = race_fact

class TrendResult:
    def __init__(self, marker, flags, history):
        self.marker = marker
        self.flags = flags
        self.history = history