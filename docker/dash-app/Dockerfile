# dibimbing_project/docker/dash-app/Dockerfile

FROM python:3.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ../../apps/dash-lastodash/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Dash app
COPY ../../apps/dash-lastodash /app

# Expose port
EXPOSE 8050

# Command to run Dash app
CMD ["python", "lastodash.py"]
