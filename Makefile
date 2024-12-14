# Makefile

.PHONY: build up down logs producer spark-run websocket-stream dashboard

# Build all Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down --remove-orphans

# View logs for all services
logs:
	docker-compose logs -f

# Start the Producer service
producer:
	docker-compose up -d producer

# Run the Spark Consumer service
spark-run:
	docker-compose up -d spark-consumer

# Run the Dashboard
dashboard:
	docker-compose up -d dashboard

# Run all services: Producer, Spark, WebSocket, Dashboard
all-services:
	$(MAKE) producer
	$(MAKE) spark-run
	$(MAKE) dashboard
