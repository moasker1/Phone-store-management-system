@echo off
rem Step 1: Start Django development server
start cmd /k python manage.py runserver

rem Step 2: Open a browser and visit the local server in a new tab
start "" http://127.0.0.1:8000/
