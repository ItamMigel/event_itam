#!/bin/bash

# Create necessary directories
mkdir -p uploads/events uploads/organizers uploads/coworking data/pg

# Check if .env file exists, copy from .env.example if not
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
fi

# Variables for paths
EVENT_IMAGE_PATH="uploads/events"
ORGANIZER_IMAGE_PATH="uploads/organizers"
COWORKING_IMAGE_PATH="uploads/coworking"

# Generate sample images if they don't exist
if [ -z "$(ls -A $EVENT_IMAGE_PATH)" ] || [ -z "$(ls -A $ORGANIZER_IMAGE_PATH)" ] || [ -z "$(ls -A $COWORKING_IMAGE_PATH)" ]; then
    echo "Generating sample images for testing..."
    python scripts/generate_sample_images.py
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Check if we need to reset the database
if [ "$1" == "--reset-db" ]; then
    echo "Resetting database..."
    docker-compose up -d postgres
    sleep 5  # Give postgres time to start
    docker-compose run backend python scripts/reset_database.py
    docker-compose down
else
    # Apply database migrations without full reset
    echo "Applying database migrations..."
    docker-compose up -d postgres
    sleep 5  # Give postgres time to start
    docker-compose run backend python scripts/alter_event_table.py
    docker-compose down
fi

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d

echo "Services started! Access the API at http://localhost:8000"
echo "API documentation is available at http://localhost:8000/docs" 