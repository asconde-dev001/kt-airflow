from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

mydag = DAG(
    'example_dag',
    description='A DAG that does nothing',
    schedule_interval='0 8 * * *',
    start_date=datetime(2023, 5, 5)
)

start_task = DummyOperator(task_id='start_task', dag=mydag)
inbetween_dag1 = DummyOperator(task_id='inbetween_dag1', dag=mydag)
inbetween_dag2 = DummyOperator(task_id='inbetween_dag2', dag=mydag)
end_task = DummyOperator(task_id='end_task', dag=mydag)

start_task >> inbetween_dag1 >> end_task
start_task >> inbetween_dag2