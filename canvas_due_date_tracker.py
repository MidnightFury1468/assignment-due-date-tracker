from flask import Flask, render_template, request, jsonify, session
import requests
from datetime import datetime
import pytz

# Details of Canvas API
API_URL = "https://canvas.sydney.edu.au/api/v1"
API_TOKEN = "3156~wWnBJenUcDFDVYUxPMR3kTa3eXUN2DCX89D9u8BCAAFBxHNQx9k9HJKLtnfmhx4n"
HEADERS = {'Authorization':f'Bearer {API_TOKEN}'}

COURSE_PARAMS = {
        'enrollment_state': 'active',
        'per_page': 100,
        'includep[]': 'term',
        'state[]': ['available', 'created', 'claimed', 'published', 'unpublished']
}

#AEST timezone setup
AEST = pytz.timezone('Australia/Sydney')

#List courses (helper function for testing)
def list_courses():
    courses = get_courses()

    print("Your Canvas Courses:\n")
    for course in courses:
        print(f"{course['name']} (ID: {course['id']})")


#Getting courses
def get_courses(params=COURSE_PARAMS):
    response = requests.get(f"{API_URL}/courses", headers=HEADERS, params=params)
    return response.json()

#Get course assignments
def get_assignments(course_id, params=None):
    response = requests.get(f"{API_URL}/courses/{course_id}/assignments", headers=HEADERS, params=params)
    return response.json()

#Main tracker function
def track_due_dates():
    courses = get_courses()
    
    #Asking user for course codes to track
    subject_codes = input("Enter course IDs (8-digit codes) you wish to track separated by commas (e.g. XXXX1000,XXXX1001,XXXX10002): ")
    subject_codes = [code.strip() for code in subject_codes.split(',')]

    matched_courses = []

    for subject_code in subject_codes:
        matched = False
        for course in courses:
            if subject_code in course['name'].upper():
                matched_courses.append(course)
                matched = True
                break
        if not matched:
            print(f"\nCourse with subject code '{subject_code}' not found in your Canvas courses.")

    print("\n Upcoming Canvas Assignments: \n")

    for course in matched_courses:
        course_id = course['id']
        course_name = course['name']
        try:
            assignments = get_assignments(course_id)
            for assignment in assignments:
                due_at = assignment.get('due_at')
                if due_at:
                    due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                    due_date = due_date.astimezone(AEST)

                    # Ensuring current time is timezone-aware
                    time_now = datetime.now(AEST)

                    if due_date > time_now:
                        print(f"[{course_name}] {assignment['name']} - Due: {due_date.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"Could not fetch assignments for {course_name}: {e}")

if __name__ == "__main__":
    track_due_dates()
    #list_courses()


