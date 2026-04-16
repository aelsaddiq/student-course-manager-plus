# Student Course Manager

A full-stack web application built with Flask that simulates a simple academic management system. The app supports different user roles (students, teachers, and administrators) and allows interaction with courses, enrollments, and grades through a clean web interface.

## Overview

This project is designed to model how a basic school system works. Students can enroll in classes, teachers can manage grades, and administrators can manage the entire system through an admin dashboard.

The goal was to build a functional and easy-to-use system while also improving usability with better UI and additional features.

## Features

### Student

* View enrolled courses
* Browse all available courses
* See class capacity and remaining seats
* Enroll in courses (if not full)
* Drop enrolled courses
* View grades (or "Not graded yet" if not assigned)
* See average grade across enrolled courses

### Teacher

* View assigned courses
* View enrolled students in each course
* Update student grades

### Admin

* Full CRUD functionality for users, courses, and enrollments
* Admin dashboard powered by Flask-Admin

## Additional Functionality

* Password hashing for secure authentication
* Search courses by name
* Filter courses by instructor
* Dark mode toggle
* Confirmation prompts for important actions
* Responsive and improved UI design

## Tech Stack

* Python
* Flask
* SQLAlchemy
* Flask-Admin
* SQLite
* HTML / CSS

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd student-course-manager-plus
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

## Demo Accounts

Student

```
aditya.ranganath / student123
```

Teacher

```
ammon.hepworth / teacher123
```

Admin

```
admin / admin123
```

## Notes

* The database is automatically created using SQLite on first run
* Sample data is seeded automatically
* If needed, delete `lab8.db` to reset the database

## Future Improvements

* Role-based permissions with finer control
* GPA calculation using a 4.0 scale
* Deployment to a live server
* Improved UI/UX with a frontend framework

## Author

Ayoub El-Saddiq
