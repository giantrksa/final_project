# Use the Bitnami Spark image as the base
FROM bitnami/spark:3.4.1

# Install Python and pip
USER root
RUN install_packages python3 python3-pip

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy project files
COPY spark-consumer.py .

# Set the entrypoint to use spark-submit with Kafka package
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", "spark-consumer.py"]
