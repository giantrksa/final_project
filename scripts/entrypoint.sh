#!/bin/bash
# scripts/entrypoint.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Initialize Airflow database
airflow db init

# Set up Airflow connections
echo "AUTH_ROLE_PUBLIC = 'Admin'" >> /opt/airflow/webserver_config.py

# Add PostgreSQL connections
airflow connections add 'postgres_main' \
    --conn-type 'postgres' \
    --conn-login "$POSTGRES_USER" \
    --conn-password "$POSTGRES_PASSWORD" \
    --conn-host postgres \
    --conn-port "$POSTGRES_PORT" \
    --conn-schema "$POSTGRES_DB"

airflow connections add 'postgres_dw' \
    --conn-type 'postgres' \
    --conn-login "$POSTGRES_USER" \
    --conn-password "$POSTGRES_PASSWORD" \
    --conn-host postgres \
    --conn-port "$POSTGRES_PORT" \
    --conn-schema "$POSTGRES_DB"

# Export Kafka bootstrap servers
export KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Initialize PostgreSQL tables
# Using psql to run the SQL script
psql -h postgres -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/airflow/dags/init_postgres.sql

# Execute the passed command (webserver or scheduler)
exec "$@"