# dags/spark_streaming_dag.py

from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
import os

default_args = {
    "owner": "dibimbing",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

spark_master_url = f"spark://{os.getenv('SPARK_MASTER_HOST_NAME', 'spark-master')}:{os.getenv('SPARK_MASTER_PORT', '7077')}"

with DAG(
    dag_id="spark_streaming_dag",
    default_args=default_args,
    schedule_interval=None,  # Trigger manually or set as needed
    dagrun_timeout=timedelta(minutes=60),
    description="Spark Streaming job to process Kafka data",
    start_date=days_ago(1),
) as dag:

    spark_submit = SparkSubmitOperator(
        task_id="spark_submit_streaming",
        application="/spark-scripts/spark-streaming.py",
        conn_id="spark_main",
        executor_memory='2g',
        total_executor_cores=2,
    )

    spark_submit
