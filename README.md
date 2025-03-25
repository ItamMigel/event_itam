# Event Management and Coworking System

A backend service for managing events and coworking spaces.

## Features

- Event management with details, organizers, and registration
- Coworking space booking with occupancy statistics
- RESTful API using FastAPI
- PostgreSQL database for data storage
- Docker containerization for easy deployment

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Pillow dependencies (for generating sample images)

### Installation and Setup

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Run the start script:

   - On Windows:
     ```powershell
     .\start.ps1
     ```
   - On Linux/macOS:
     ```bash
     chmod +x start.sh
     ./start.sh
     ```

   This script will:

   - Create necessary directories
   - Create a `.env` file from `.env.example` if needed
   - Generate sample images for testing
   - Start Docker containers

3. If you need to reset the database (in case of schema changes):

   - On Windows:
     ```powershell
     .\start.ps1 --reset-db
     ```
   - On Linux/macOS:
     ```bash
     ./start.sh --reset-db
     ```

4. The API should now be running at `http://localhost:8000`

## API Documentation

Once the application is running, you can access the automatically generated API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Events

- `GET /events` - Get all events
- `GET /events/{event_id}` - Get event details by ID
- `POST /events` - Create a new event
- `POST /events/{event_id}/register` - Register for an event
- `DELETE /events/{event_id}` - Delete an event

### Coworking

- `GET /coworking` - Get all coworking spaces
- `GET /coworking/{coworking_id}` - Get coworking space details with occupancy data
- `POST /coworking` - Create a new coworking space
- `POST /coworking/{coworking_id}/booking` - Create a booking for a coworking space
- `DELETE /coworking/{coworking_id}` - Delete a coworking space

## Using the API

### Creating an Event

Send a POST request to `/events/` with a JSON body:

```json
{
  "title": "Sample Event",
  "description": "Detailed event description",
  "short_description": "Brief overview",
  "start_date": "2023-12-25T12:00:00",
  "location": "Event Location",
  "image_path": "/uploads/events/sample_image.jpg",
  "organizer_name": "Organizer Name",
  "organizer_description": "Organizer description",
  "organizer_image_path": "/uploads/organizers/sample_organizer.jpg"
}
```

All image paths are optional text fields (they don't require actual file uploads).

**Note:** Events must have unique combinations of `title` and `start_date`. Attempting to create an event with the same title and date will result in a `409 Conflict` error.

### Creating a Coworking Space

Send a POST request to `/coworking/` with a JSON body:

```json
{
  "name": "Coworking Space Name",
  "description": "Detailed description",
  "location": "Address",
  "image_path": "/uploads/coworking/sample_image.jpg"
}
```

The image_path is optional.

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors, check:

1. Your `.env` file has the correct PostgreSQL connection details
2. The PostgreSQL container is running properly:
   ```bash
   docker-compose ps
   ```
3. Verify the data directories have proper permissions

### Database Schema Errors

If you encounter errors related to database schema (e.g., type mismatches), reset the database:

1. Run the start script with the `--reset-db` parameter:

   ```bash
   ./start.sh --reset-db
   ```

   or

   ```powershell
   .\start.ps1 --reset-db
   ```

2. This will drop all tables and recreate them with the correct schema.

### Duplicate Event Error

If you receive a `409 Conflict` error when creating an event, it means an event with the same title and date already exists. You should either:

1. Change the event title
2. Change the event date/time
3. Update the existing event instead of creating a new one

### Image Generation

If sample image generation fails:

1. Ensure Pillow is installed:
   ```bash
   pip install pillow
   ```
2. Check that the uploads directory exists and is writable
3. Run the image generation script manually:
   ```bash
   python scripts/generate_sample_images.py
   ```
