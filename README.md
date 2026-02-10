# Student Performance Analysis System

A Python + MySQL based system to track student academic performance, analyze trends, and identify weak areas.

## Why this project exists
This project helps analyze student performance by tracking subjects, difficulty levels, and exam scores,
then identifying trends and weak areas to support academic improvement.

## Features

- Student and teacher login system
- Subject and difficulty tracking
- Exam score recording
- Performance trend analysis
- Weak area detection
- Teacher dashboard to view student reports

## Tech Stack

- Python
- MySQL
- mysql-connector-python

## How it Works

Students enter subjects, difficulty level, and exam marks.
The system calculates averages, detects performance trends, and suggests improvements.

Teachers can view individual student performance reports.

## Database

Schema is included in `database.sql`.

## How to Run

1. Update MySQL username, password, and database name in the connectin section before running
2. Import `database.sql` into MySQL
3. Update database credentials in `student_analysis.py`
4. Run: python_studentanalysis.py

## Author
Dhrupad Pant
