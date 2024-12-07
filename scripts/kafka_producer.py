# scripts/kafka_producer.py

import os
import time
import json
import lasio
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = 'las-data'

def read_las_file(file_path):
    las = lasio.read(file_path)
    df = las.df().reset_index()
    return df.to_dict(orient='records')

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    las_file = '/resources/data/alcor1.las'  # Ensure this file exists
    data = read_las_file(las_file)

    for record in data:
        producer.send(TOPIC, record)
        print(f"Sent record: {record}")
        time.sleep(1)  # Simulate streaming by waiting 1 second between records

    producer.flush()

if __name__ == "__main__":
    main()
