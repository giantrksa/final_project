# Makefile

.PHONY: build up down logs exec bash

# Build Docker images without cache
build:
	docker-compose build --no-cache airflow-webserver airflow-scheduler dash-app

# Start all services in detached mode
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs for all services
logs:
	docker-compose logs -f

# Execute a command in the airflow-webserver container
exec-webserver:
	docker-compose exec airflow-webserver /bin/bash

# Execute a command in the airflow-scheduler container
exec-scheduler:
	docker-compose exec airflow-scheduler /bin/bash

# Execute a command in the postgres container
exec-postgres:
	docker-compose exec postgres psql -U postgres -d postgres_dw

# Execute a command in the kafka container
exec-kafka:
	docker-compose exec kafka bash

# Execute a command in the spark-master container
exec-spark-master:
	docker-compose exec spark-master bash

# Execute a command in the spark-worker container
exec-spark-worker:
	docker-compose exec spark-worker bash

# Execute a command in the dash-app container
exec-dash-app:
	docker-compose exec dash-app /bin/bash
