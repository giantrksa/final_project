# dags/kafka_streaming_dag.py

from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from kafka import KafkaConsumer
import json
import psycopg2
import os

default_args = {
    "owner": "dibimbing",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def consume_kafka():
    KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    TOPIC = 'las-data'
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres_dw')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='airflow-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    cursor = conn.cursor()

    for message in consumer:
        record = message.value
        # Insert record into PostgreSQL
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['%s'] * len(record))
        insert_query = f"INSERT INTO las_data ({columns}) VALUES ({placeholders})"
        cursor.execute(insert_query, list(record.values()))
        conn.commit()
        print(f"Inserted record into Postgres: {record}")

    cursor.close()
    conn.close()

with DAG(
    dag_id="kafka_streaming_dag",
    default_args=default_args,
    schedule_interval=None,  # Trigger manually or set as needed
    dagrun_timeout=timedelta(minutes=60),
    description="Consume LAS data from Kafka and store in Postgres",
    start_date=days_ago(1),
) as dag:

    consume_task = PythonOperator(
        task_id="consume_kafka_task",
        python_callable=consume_kafka,
    )

    consume_task
