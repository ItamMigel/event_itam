from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from services.event_service import EventService, EventDuplicateError

event_service = EventService()

event_router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={404: {"description": "Not Found"}},
)


class EventDto(BaseModel):
    id: UUID
    title: str
    short_description: str
    start_date: datetime
    location: str
    image_path: Optional[str] = None


class EventDetailDto(EventDto):
    description: str
    organizer: Optional[dict] = None


class EventGetAllResponse(BaseModel):
    events: List[EventDto]


class EventRegistrationRequest(BaseModel):
    participant_name: str
    participant_email: str
    participant_phone: Optional[str] = None


class EventRegistrationResponse(BaseModel):
    id: UUID
    message: str = "Registration successful"


class EventCreateRequest(BaseModel):
    title: str
    description: str
    short_description: str
    start_date: datetime
    location: str
    image_path: Optional[str] = None
    organizer_name: Optional[str] = None
    organizer_description: Optional[str] = None
    organizer_image_path: Optional[str] = None


class EventCreateResponse(BaseModel):
    id: UUID


@event_router.get("/", response_model=EventGetAllResponse)
async def get_all_events():
    """
    Get all events for the events listing page.
    """
    logger.info("get_all_events")
    events = await event_service.get_all_events()
    
    return EventGetAllResponse(
        events=[
            EventDto(
                id=event["id"],
                title=event["title"],
                short_description=event["short_description"],
                start_date=event["start_date"],
                location=event["location"],
                image_path=event["image_path"]
            )
            for event in events
        ]
    )


@event_router.get("/{event_id}", response_model=EventDetailDto)
async def get_event_by_id(event_id: UUID):
    """
    Get event details by ID for the event details page.
    """
    logger.info(f"get_event_by_id: {event_id}")
    event_data, found = await event_service.get_event_by_id(event_id)
    
    if not found:
        logger.error(f"get_event_by_id: {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    return EventDetailDto(
        id=event_data["id"],
        title=event_data["title"],
        short_description=event_data["short_description"],
        description=event_data["description"],
        start_date=event_data["start_date"],
        location=event_data["location"],
        image_path=event_data["image_path"],
        organizer=event_data.get("organizer")
    )


@event_router.post("/", response_model=EventCreateResponse, status_code=201)
async def create_event(event: EventCreateRequest):
    """
    Create a new event with optional image paths and organizer details.
    """
    logger.info(f"create_event: {event.title}")
    
    try:
        # Create event with organizer info if provided
        event_id = await event_service.create_event(
            title=event.title,
            description=event.description,
            short_description=event.short_description,
            start_date=event.start_date,
            location=event.location,
            image_path=event.image_path,
            organizer_name=event.organizer_name,
            organizer_description=event.organizer_description,
            organizer_image_path=event.organizer_image_path
        )
        
        return EventCreateResponse(id=event_id)
    except EventDuplicateError as e:
        logger.warning(f"Duplicate event attempt: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An event with title '{event.title}' at the same date and time already exists"
        )
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event due to an internal error"
        )


@event_router.post("/{event_id}/register", response_model=EventRegistrationResponse)
async def register_for_event(event_id: UUID, registration: EventRegistrationRequest):
    """
    Register a participant for an event.
    """
    logger.info(f"register_for_event: {event_id}, participant: {registration.participant_name}")
    
    # Check if event exists
    _, found = await event_service.get_event_by_id(event_id)
    if not found:
        logger.error(f"register_for_event: event {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Register participant
    registration_id = await event_service.register_participant(
        event_id=event_id,
        participant_name=registration.participant_name,
        participant_email=registration.participant_email,
        participant_phone=registration.participant_phone
    )
    
    return EventRegistrationResponse(id=registration_id)


@event_router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: UUID):
    """
    Delete an event by ID.
    """
    logger.info(f"delete_event: {event_id}")
    
    # Check if event exists
    _, found = await event_service.get_event_by_id(event_id)
    if not found:
        logger.error(f"delete_event: {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Delete the event
    success = await event_service.delete_event(event_id)
    if not success:
        logger.error(f"Failed to delete event: {event_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event"
        )
    
    return None 