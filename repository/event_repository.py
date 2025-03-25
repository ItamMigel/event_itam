from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from loguru import logger
from sqlalchemy import select, insert, update, delete, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from persistent.database import get_session
from persistent.tables import event, organizer, event_organizer


class EventRepository:
    """Repository for event-related database operations."""

    async def get_all_events(self) -> List[dict]:
        """
        Retrieve all events from the database.
        
        Returns:
            List[dict]: List of event dictionaries
        """
        async with get_session() as session:
            query = select(
                event.c.id,
                event.c.title,
                event.c.short_description,
                event.c.start_date,
                event.c.location,
                event.c.image_path
            ).order_by(event.c.start_date)
            
            result = await session.execute(query)
            events = [dict(row._mapping) for row in result.all()]
            return events

    async def get_event_by_id(self, event_id: UUID) -> Tuple[Optional[dict], bool]:
        """
        Retrieve an event by its ID.
        
        Args:
            event_id: UUID of the event
            
        Returns:
            Tuple[Optional[dict], bool]: (event_data, found_flag)
        """
        async with get_session() as session:
            # Get event data
            event_query = select(event).where(event.c.id == event_id)
            event_result = await session.execute(event_query)
            event_data = event_result.mappings().first()
            
            if not event_data:
                return None, False
            
            # Get organizer data
            organizer_query = select(
                organizer.c.id,
                organizer.c.name,
                organizer.c.description,
                organizer.c.image_path
            ).select_from(
                join(
                    event_organizer,
                    organizer,
                    event_organizer.c.organizer_id == organizer.c.id
                )
            ).where(event_organizer.c.event_id == event_id)
            
            organizer_result = await session.execute(organizer_query)
            organizer_data = organizer_result.mappings().first()
            
            # Combine event and organizer data
            result = dict(event_data)
            if organizer_data:
                result["organizer"] = dict(organizer_data)
            else:
                result["organizer"] = None
                
            return result, True

    async def create_event(
        self,
        title: str,
        description: str,
        short_description: str,
        start_date: datetime,
        location: str,
        image_path: Optional[str] = None,
        organizer_id: Optional[UUID] = None
    ) -> UUID:
        """
        Create a new event in the database.
        
        Args:
            title: Event title
            description: Full event description
            short_description: Short description for event cards
            start_date: Event start date and time
            location: Event location
            image_path: Path to event image file
            organizer_id: ID of the organizer for this event
            
        Returns:
            UUID: ID of the created event
        """
        event_id = uuid4()
        
        async with get_session() as session:
            async with session.begin():
                # Insert event
                await session.execute(
                    insert(event).values(
                        id=event_id,
                        title=title,
                        description=description,
                        short_description=short_description,
                        start_date=start_date,
                        location=location,
                        image_path=image_path,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                
                # Link to organizer if provided
                if organizer_id:
                    await session.execute(
                        insert(event_organizer).values(
                            event_id=event_id,
                            organizer_id=organizer_id
                        )
                    )
                    
        return event_id
        
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
        async with get_session() as session:
            async with session.begin():
                # Update event data
                values = {"updated_at": datetime.now()}
                if title is not None:
                    values["title"] = title
                if description is not None:
                    values["description"] = description
                if short_description is not None:
                    values["short_description"] = short_description
                if start_date is not None:
                    values["start_date"] = start_date
                if location is not None:
                    values["location"] = location
                if image_path is not None:
                    values["image_path"] = image_path
                    
                if values:
                    await session.execute(
                        update(event)
                        .where(event.c.id == event_id)
                        .values(**values)
                    )
                
                # Update organizer association if provided
                if organizer_id:
                    # First delete existing association
                    await session.execute(
                        delete(event_organizer)
                        .where(event_organizer.c.event_id == event_id)
                    )
                    
                    # Then create new association
                    await session.execute(
                        insert(event_organizer).values(
                            event_id=event_id,
                            organizer_id=organizer_id
                        )
                    )
                    
        return True
        
    async def delete_event(self, event_id: UUID) -> bool:
        """
        Delete an event from the database.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            bool: Success flag
        """
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    delete(event)
                    .where(event.c.id == event_id)
                )
                
        return True 