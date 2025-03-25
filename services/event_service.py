from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from repository.event_repository import EventRepository
from repository.organizer_repository import OrganizerRepository


class EventDuplicateError(Exception):
    """Raised when trying to create an event with a duplicate title and start_date."""
    pass


class EventService:
    """Service for event-related operations."""
    
    def __init__(self):
        self.event_repository = EventRepository()
        self.organizer_repository = OrganizerRepository()
    
    async def get_all_events(self) -> List[Dict[str, Any]]:
        """
        Get all events.
        
        Returns:
            List[Dict[str, Any]]: List of event dictionaries
        """
        return await self.event_repository.get_all_events()
    
    async def get_event_by_id(self, event_id: UUID) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Get an event by ID.
        
        Args:
            event_id: UUID of the event
            
        Returns:
            Tuple[Optional[Dict[str, Any]], bool]: (event_data, found_flag)
        """
        return await self.event_repository.get_event_by_id(event_id)
    
    async def create_event(
        self,
        title: str,
        description: str,
        short_description: str,
        start_date: datetime,
        location: str,
        image_path: Optional[str] = None,
        organizer_name: Optional[str] = None,
        organizer_description: Optional[str] = None,
        organizer_image_path: Optional[str] = None
    ) -> UUID:
        """
        Create a new event with optional organizer.
        
        Args:
            title: Event title
            description: Full event description
            short_description: Short description for event cards
            start_date: Event start date and time
            location: Event location
            image_path: Path to event image file
            organizer_name: Organizer name (will create if not exists)
            organizer_description: Organizer description
            organizer_image_path: Path to organizer image
            
        Returns:
            UUID: ID of the created event
            
        Raises:
            EventDuplicateError: If an event with the same title and start_date already exists
        """
        # Проверяем, не существует ли уже события с таким же названием и датой
        try:
            events = await self.event_repository.get_all_events()
            for event in events:
                # Сравниваем только дату и время, игнорируя миллисекунды и часовой пояс
                event_date = event["start_date"]
                if (event["title"] == title and 
                    event_date.year == start_date.year and
                    event_date.month == start_date.month and
                    event_date.day == start_date.day and
                    event_date.hour == start_date.hour and
                    event_date.minute == start_date.minute):
                    raise EventDuplicateError(f"Event with title '{title}' and date {start_date} already exists")
        except Exception as e:
            if not isinstance(e, EventDuplicateError):
                logger.error(f"Error checking for duplicate events: {e}")
                # Продолжаем выполнение, даже если проверка не удалась
            else:
                raise
        
        organizer_id = None
        
        # Create or get organizer if name is provided
        if organizer_name:
            # Try to find existing organizer
            organizers = await self.organizer_repository.get_all_organizers()
            existing_organizer = next(
                (org for org in organizers if org["name"] == organizer_name), 
                None
            )
            
            if existing_organizer:
                # Обработка ID в зависимости от типа
                org_id = existing_organizer["id"]
                if isinstance(org_id, UUID) or hasattr(org_id, 'bytes'):
                    # Если это уже UUID или PostgreSQL UUID объект
                    organizer_id = org_id
                elif isinstance(org_id, str):
                    # Если это строка
                    organizer_id = UUID(org_id)
                else:
                    logger.warning(f"Unexpected ID type: {type(org_id)}")
                    organizer_id = UUID(str(org_id))
                
                logger.info(f"Using existing organizer: {organizer_name}")
                
                # Update organizer if new details provided
                if organizer_description or organizer_image_path:
                    await self.organizer_repository.update_organizer(
                        organizer_id=organizer_id,
                        description=organizer_description,
                        image_path=organizer_image_path
                    )
            else:
                # Create new organizer
                organizer_id = await self.organizer_repository.create_organizer(
                    name=organizer_name,
                    description=organizer_description,
                    image_path=organizer_image_path
                )
                logger.info(f"Created new organizer: {organizer_name}")
        
        try:
            # Create event
            event_id = await self.event_repository.create_event(
                title=title,
                description=description,
                short_description=short_description,
                start_date=start_date,
                location=location,
                image_path=image_path,
                organizer_id=organizer_id
            )
            return event_id
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e) and "uq_event_title_start_date" in str(e):
                logger.error(f"Integrity error creating event: {e}")
                raise EventDuplicateError(f"Event with title '{title}' and date {start_date} already exists")
            raise
    
    async def update_event(
        self,
        event_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        short_description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        location: Optional[str] = None,
        image_path: Optional[str] = None,
        organizer_id: Optional[UUID] = None
    ) -> bool:
        """
        Update an existing event.
        
        Args:
            event_id: ID of the event to update
            title: New title (optional)
            description: New description (optional)
            short_description: New short description (optional)
            start_date: New start date (optional)
            location: New location (optional)
            image_path: New image path (optional)
            organizer_id: New organizer ID (optional)
            
        Returns:
            bool: Success flag
        """
        try:
            return await self.event_repository.update_event(
                event_id=event_id,
                title=title,
                description=description,
                short_description=short_description,
                start_date=start_date,
                location=location,
                image_path=image_path,
                organizer_id=organizer_id
            )
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e) and "uq_event_title_start_date" in str(e):
                logger.error(f"Integrity error updating event: {e}")
                raise EventDuplicateError(f"Event with title '{title}' and date {start_date} already exists")
            raise
    
    async def delete_event(self, event_id: UUID) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            bool: Success flag
        """
        return await self.event_repository.delete_event(event_id)
        
    async def register_participant(
        self,
        event_id: UUID,
        participant_name: str,
        participant_email: str,
        participant_phone: Optional[str] = None
    ) -> UUID:
        """
        Register a participant for an event.
        
        Args:
            event_id: ID of the event to register for
            participant_name: Name of the participant
            participant_email: Email of the participant
            participant_phone: Phone number of the participant (optional)
            
        Returns:
            UUID: ID of the registration
        """
        from uuid import uuid4
        from datetime import datetime
        from persistent.database import get_session
        from persistent.tables import event_registration
        from sqlalchemy import insert
        
        registration_id = uuid4()
        
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    insert(event_registration).values(
                        id=registration_id,
                        event_id=event_id,
                        participant_name=participant_name,
                        participant_email=participant_email,
                        participant_phone=participant_phone,
                        registration_date=datetime.now(),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                
        logger.info(f"Registered participant {participant_name} for event {event_id}")
        return registration_id 