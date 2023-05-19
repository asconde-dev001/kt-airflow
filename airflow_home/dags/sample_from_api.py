import json
import os
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 5),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Python function that fetches data from the API and writes it to a .json file
def fetch_data_from_api_and_save():
    # Send a GET request to the API
    response = requests.get('https://jsonplaceholder.typicode.com/posts')

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response data as JSON
        data = response.json()

        # Get the current timestamp in a human-readable format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define the file path where the data will be saved
        file_path = f'/app/datalake/bronze/sample_from_api/data_{timestamp}.json'

        # Make sure the directory for the file exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Open the file in write mode and dump the JSON data into it
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        # If the request was not successful, raise an exception
        raise Exception(f'Request failed with status code {response.status_code}')

# Define the DAG
with DAG('ingest_data_from_api_dag',
         default_args=default_args,
         description='DAG to ingest data from an API and save it to a .json file',
         schedule_interval=timedelta(days=1),
         ) as dag:

    # Define a PythonOperator task that calls the fetch_data_from_api_and_save function
    fetch_and_save_task = PythonOperator(
        task_id='fetch_and_save',
        python_callable=fetch_data_from_api_and_save,
    )

    # Set the task to run when the DAG is executed
    fetch_and_save_task
