# docker/dash-app/Dockerfile

# Use Python 3.7 slim as base
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY apps/dash-lastodash/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY apps/dash-lastodash/ /app

# Expose port
EXPOSE 8050

# Run the Dash app with Gunicorn
CMD ["gunicorn", "lastodash:server", "-b", "0.0.0.0:8050"]
