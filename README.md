# PWP 2020
# PROJECT NAME
Frolf Tracker
# Group information
* Student 1. Tomi Lehto, @student.oulu.fi
* Student 2. Julius Rintamäki, @student.oulu.fi
* Student 3. Ville Karsikko, @student.oulu

## Run server with docker
> docker-compose up

## Run locally 
# Dependencies
See requirements.txt
> pip install -r requirments.txt
# Setup
> pip install -e .

# Execution
> export FLASK_APP=frolftracker

> export FLASK_ENV=development

> python3 -c "from frolftracker import db, create_app; db.create_all(app=create_app())"

> flask run

# Running tests with coverage report

> pytest --cov-report term-missing --cov=frolftracker
