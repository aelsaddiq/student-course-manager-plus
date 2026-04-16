# Student Course Manager Plus

This is a more polished version of the Lab 8 project. It still meets the original requirements, but it also adds some extra features for practice and for fun.

## Extra features added
- password hashing
- drop class feature
- course search
- teacher filter
- average grade display
- "Not graded yet" instead of 0.0
- better navbar and cleaner styling
- dark mode toggle
- admin home page message
- confirmation popups before important actions

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Important
If you are switching from the older version of this project, delete `lab8.db` first so the app can rebuild the database with hashed passwords.

## Run
```bash
python app.py
```

Open `http://127.0.0.1:5000`
