FROM python:3.7.2-stretch

RUN mkdir -p /app
RUN mkdir -p /app/frolftracker
WORKDIR /app

COPY requirements.txt /app
COPY setup.py /app
COPY frolftracker /app/frolftracker
RUN pip install --no-cache-dir -r requirements.txt
RUN ls
RUN pip install .
RUN python -c "from frolftracker import db, create_app; db.create_all(app=create_app())"
COPY . /app 
