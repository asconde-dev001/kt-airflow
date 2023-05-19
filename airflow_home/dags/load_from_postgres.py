import re
import logging

from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta
import csv

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
    'postgres_pipeline',
    default_args=default_args,
    description='A DAG that loads tables from a PostgreSQL database to a local file',
    schedule_interval=None
)

# Define the tasks
def generate_csv_list():
    # Read the list of tables to ingest from a CSV file
    with open('/app/datalake/load_from_postgres/table_list.csv', 'r') as f:
        reader = csv.reader(f)
        table_list = [row[0] for row in reader][1:]
    logging.info(f'Table list: {" ".join(table_list)}')
    return table_list

def generate_filename():
    # Generate the output file name based on the current date and time
    return '/app/datalake/bronze/load_from_postgres/output_{}.csv'.format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

def query_database(table_name, output_file):
    # Query the database and write the results to a file
    pg_hook = PostgresHook(postgres_conn_id='postgres_local')
    query = 'SELECT * FROM {}'.format(table_name)
    result = pg_hook.get_records(query)
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(result)

start_task = DummyOperator(task_id='start_task', dag=dag)
end_load = DummyOperator(task_id='end_load', dag=dag)

table_list = generate_csv_list()

for table_name in table_list:
    output_filename = f'{table_name} {datetime.now().strftime("%Y%m%d%H%M%S")}'
    query_task = PostgresOperator(
        task_id='query_{}'.format(table_name),
        postgres_conn_id='postgres_local',
        sql='SELECT * FROM {};'.format(table_name),
        dag=dag
    )

    output_file = BashOperator(
        task_id='create_output_file_{}'.format(table_name),
        bash_command='touch /app/datalake/bronze/load_from_postgres/{}'.format(output_filename),
        dag=dag
    )

    write_to_file = PythonOperator(
        task_id='write_{}_to_file'.format(table_name),
        python_callable=query_database,
        op_kwargs={'table_name': table_name, 'output_file': f"/app/datalake/bronze/load_from_postgres/{output_filename}"},
        dag=dag
    )

    start_task >> query_task >> output_file >> write_to_file >> end_load

create_customer_orders_table = PostgresOperator(
    task_id='create_customer_orders_table',
    postgres_conn_id='postgres_local',
    sql="""
    create table if not exists customer_orders as 
    SELECT
        c.customerid, firstname, lastname, email,
        orderdate, totalamount, current_timestamp as load_ts
    FROM customers c
    INNER JOIN orders o
        ON c.customerid = o.customerid
    LIMIT 0;
    """,
    dag=dag
)

populate_customers_orders_table = PostgresOperator(
    task_id='populate_customers_orders_table',
    postgres_conn_id='postgres_local',
    sql="""
    INSERT INTO customer_orders (customerid, firstname, lastname, email, orderdate, totalamount, load_ts)
    SELECT
        c.customerid, c.firstname, c.lastname, c.email,
        o.orderdate, o.totalamount, current_timestamp as load_ts
    FROM customers c
    INNER JOIN orders o
        ON c.customerid = o.customerid;
    """,
    dag=dag
)

end_load >> create_customer_orders_table >> populate_customers_orders_table