from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import os
import shutil

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 5),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'file_sensor_example',
    default_args=default_args,
    description='An example DAG that uses a FileSensor',
    schedule_interval="@once" #None
)

# Define the tasks
def move_files():
    source_folder = '/app/source/sensors_sample'
    destination_folder = '/app/datalake/bronze/sensor_sample'
    source_files = os.listdir(source_folder)
    for source_file in source_files:
        source_file_path = os.path.join(source_folder, source_file)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        destination_file_name = f"{timestamp}_{source_file}"
        destination_file_path = os.path.join(destination_folder, destination_file_name)
        if not os.path.exists(destination_file_path):
            shutil.move(source_file_path, destination_file_path)
            print(f"Moved {source_file} to {destination_file_path}")
        else:
            print(f"{destination_file_name} already exists in {destination_folder}")

file_sensor = FileSensor(
    task_id='file_sensor',
    dag=dag,
    filepath='/app/source/sensors_sample',
    poke_interval=5,
    timeout=60*60,
)

copy_file = PythonOperator(
    task_id='move_files',
    python_callable=move_files,
    dag=dag,
)

# Define the task dependencies
file_sensor >> copy_file