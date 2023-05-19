# Use the official Python 3.7 image as the base image
FROM python:3.7-slim-buster

# Set the working directory to /app
WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        default-libmysqlclient-dev \
        libpq-dev \
        && \
    rm -rf /var/lib/apt/lists/*

# Install Airflow and its dependencies
RUN pip install --no-cache-dir \
    'apache-airflow[postgres,mysql,celery,crypto,ssh,kubernetes]==2.2.3'

RUN pip install markupsafe==1.1.1

# Set the AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/app/airflow

# Initialize the Airflow database
RUN airflow db init

# Set up the Airflow scheduler to run separately
CMD ["airflow", "scheduler"]

# Set up the Airflow webserver to run separately
CMD ["airflow", "webserver"]
