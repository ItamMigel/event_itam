# Create necessary directories
New-Item -ItemType Directory -Force -Path "uploads/events" | Out-Null
New-Item -ItemType Directory -Force -Path "uploads/organizers" | Out-Null
New-Item -ItemType Directory -Force -Path "uploads/coworking" | Out-Null
New-Item -ItemType Directory -Force -Path "data/pg" | Out-Null

# Check if .env file exists, copy from .env.example if not
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example"
    Copy-Item .env.example .env
}

# Variables for paths
$EVENT_IMAGE_PATH = "uploads/events"
$ORGANIZER_IMAGE_PATH = "uploads/organizers"
$COWORKING_IMAGE_PATH = "uploads/coworking"

# Generate sample images if they don't exist
if ((Get-ChildItem -Path $EVENT_IMAGE_PATH -File).Count -eq 0 -or 
    (Get-ChildItem -Path $ORGANIZER_IMAGE_PATH -File).Count -eq 0 -or 
    (Get-ChildItem -Path $COWORKING_IMAGE_PATH -File).Count -eq 0) {
    Write-Host "Generating sample images for testing..."
    python scripts/generate_sample_images.py
}

# Stop existing containers
Write-Host "Stopping existing containers..."
docker-compose down

# Check if we need to reset the database
if ($args[0] -eq "--reset-db") {
    Write-Host "Resetting database..."
    docker-compose up -d postgres
    Start-Sleep -Seconds 5  # Give postgres time to start
    docker-compose run backend python scripts/reset_database.py
    docker-compose down
}
else {
    # Apply database migrations without full reset
    Write-Host "Applying database migrations..."
    docker-compose up -d postgres
    Start-Sleep -Seconds 5  # Give postgres time to start
    docker-compose run backend python scripts/alter_event_table.py
    docker-compose down
}

# Start Docker containers
Write-Host "Starting Docker containers..."
docker-compose up -d

Write-Host "Services started! Access the API at http://localhost:8000"
Write-Host "API documentation is available at http://localhost:8000/docs"