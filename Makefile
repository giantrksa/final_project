# Makefile

.PHONY: all build up down restart logs clean producer dash

all: build up

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all

producer:
	docker exec -it dibimbing_project_airflow_1 python /opt/airflow/scripts/kafka_producer.py

dash:
	docker exec -it dibimbing_project_dash-app_1 python /app/lastodash.py
