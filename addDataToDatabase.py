import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-cab91-default-rtdb.firebaseio.com/"
})

ref = db.reference('students')

# add data to the database
total_attendance = 0
data = {
    "20051412":
        {
            "name": "Arpita Sahoo",
            "major": "CSE",
            "pass_year": 2024,
            "total_attendance": 0,
            "CGPA": 9.18,
            "current_sem": "6th",
            "last_attendance_time": "2023-04-15 00:54:34",
            "heading1": "cgpa",
            "heading2": "semester",
            "heading3": "pass-year"
        },
    "852741":
        {
            "name": "Emily Blunt",
            "major": "drama",
            "pass_year": 2025,
            "total_attendance": 0,
            "CGPA": 8.34,
            "current_sem": "4th",
            "last_attendance_time": "2023-04-15 00:54:34",
            "heading1": "cgpa",
            "heading2": "semester",
            "heading3": "pass-year"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Economics",
            "pass_year": 2024,
            "total_attendance": 0,
            "CGPA": 9.27,
            "current_sem": "7th",
            "last_attendance_time": "2023-04-15 00:54:34",
            "heading1": "cgpa",
            "heading2": "semester",
            "heading3": "pass-year"
        }

}

# sending data to realtime database
for key, value in data.items():
    ref.child(key).set(value)
