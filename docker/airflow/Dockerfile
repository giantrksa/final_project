# docker/airflow/Dockerfile

# Use the official Airflow image as the base
FROM apache/airflow:2.5.1-python3.8

# Switch to root to install dependencies and modify file permissions
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy scripts, spark-scripts, and data
COPY scripts /opt/airflow/scripts
COPY spark-scripts /spark-scripts
COPY data /resources/data

# Ensure scripts are executable
RUN chmod +x /opt/airflow/scripts/*.sh

# Change ownership of scripts to airflow user
RUN chown -R airflow: /opt/airflow/scripts

# Switch to airflow user to install Python dependencies
USER airflow

# Copy and install Python dependencies
COPY dags/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs
COPY dags /opt/airflow/dags

# Set the ENTRYPOINT to the entrypoint.sh script
ENTRYPOINT ["/opt/airflow/scripts/entrypoint.sh"]

# Set the default command (will be overridden by docker-compose)
CMD ["airflow", "webserver"]
