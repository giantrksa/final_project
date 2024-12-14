import os
import json
import time
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "well_logs")
LAS_FILE_PATH = os.getenv("LAS_FILE_PATH", "/data/alcor1.las")

def read_las_data(filepath):
    """Reads LAS data from a file and extracts data rows."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    start_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('~A'):
            start_index = i + 1
            break
    data_lines = [l.strip() for l in lines[start_index:] if l.strip() and not l.strip().startswith('#')]
    return data_lines

def parse_line_to_json(line):
    """Parses a single LAS data line into a JSON object."""
    parts = line.split()
    if len(parts) < 14:
        return None
    keys = ["depth", "dgrc", "btvpvs", "btcs", "btsflag", "btcss", "r15p", "r09p", "r39p", "r27p", "ewxt", "alcdlc", "tnps", "aldclc"]
    try:
        values = [float(p) for p in parts]
    except ValueError:
        return None
    return dict(zip(keys, values))

if __name__ == "__main__":
    print("Starting Kafka producer...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        data_lines = read_las_data(LAS_FILE_PATH)
        print(f"Loaded {len(data_lines)} rows from LAS file.")

        for idx, row in enumerate(data_lines):
            data_dict = parse_line_to_json(row)
            if data_dict:
                producer.send(TOPIC_NAME, data_dict)
                print(f"Sent row {idx + 1}/{len(data_lines)}: {data_dict}")
                time.sleep(1)  # Wait 20 seconds before sending the next row

        print("All data sent successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed.")
