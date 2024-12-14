# Well Logs Streaming Pipeline

This project implements a streaming data pipeline for processing well logs data using Kafka, Spark, and PostgreSQL. The data is streamed from LAS files through Kafka to a Spark consumer, where it is stored in a PostgreSQL database with additional petrophysics calculations.

## Project Files

1. **`producer.py`**
   - Reads LAS data and streams it to a Kafka topic.

2. **`spark-consumer.py`**
   - Consumes data from Kafka and stores it row-by-row in a PostgreSQL table.

3. **`petrophysics-consumer.py`**
   - Calculates petrophysics metrics for the stored data and saves it into a separate schema in PostgreSQL.

4. **`docker-compose.yml`**
   - Defines the services for Kafka, Spark, and PostgreSQL.

5. **`Makefile`**
   - Simplifies the deployment and execution process.

HOW TO RUN

1. **`make up`**
   - Build and start the Docker containers.

2. **`make producer`**
   - Run the producer script to stream data to Kafka.

3. **`make spark-run`**
   - Start the Spark consumer to process and store well logs.

4. **`make down`**
   - Reset.