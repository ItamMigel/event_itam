from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from persistent.database import get_session
from persistent.tables import organizer


class OrganizerRepository:
    """Repository for organizer-related database operations."""

    async def get_all_organizers(self) -> List[dict]:
        """
        Retrieve all organizers from the database.
        
        Returns:
            List[dict]: List of organizer dictionaries
        """
        async with get_session() as session:
            query = select(organizer)
            result = await session.execute(query)
            organizers = [dict(row._mapping) for row in result.all()]
            return organizers

    async def get_organizer_by_id(self, organizer_id: UUID) -> Tuple[Optional[dict], bool]:
        """
        Retrieve an organizer by ID.
        
        Args:
            organizer_id: UUID of the organizer
            
        Returns:
            Tuple[Optional[dict], bool]: (organizer_data, found_flag)
        """
        async with get_session() as session:
            query = select(organizer).where(organizer.c.id == organizer_id)
            result = await session.execute(query)
            organizer_data = result.mappings().first()
            
            if organizer_data:
                return dict(organizer_data), True
            return None, False

    async def create_organizer(
        self,
        name: str,
        description: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> UUID:
        """
        Create a new organizer in the database.
        
        Args:
            name: Organizer name
            description: Organizer description
            image_path: Path to organizer image
            
        Returns:
            UUID: ID of the created organizer
        """
        organizer_id = uuid4()
        
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    insert(organizer).values(
                        id=organizer_id,
                        name=name,
                        description=description,
                        image_path=image_path,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                
        return organizer_id
        
    async def update_organizer(
        self,
        organizer_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> bool:
        """
        Update an existing organizer.
        
        Args:
            organizer_id: ID of the organizer to update
            name: New name (optional)
            description: New description (optional)
            image_path: New image path (optional)
            
        Returns:
            bool: Success flag
        """
        async with get_session() as session:
            async with session.begin():
                values = {"updated_at": datetime.now()}
                if name is not None:
                    values["name"] = name
                if description is not None:
                    values["description"] = description
                if image_path is not None:
                    values["image_path"] = image_path
                    
                if values:
                    await session.execute(
                        update(organizer)
                        .where(organizer.c.id == organizer_id)
                        .values(**values)
                    )
                    
        return True
        
    async def delete_organizer(self, organizer_id: UUID) -> bool:
        """
        Delete an organizer from the database.
        
        Args:
            organizer_id: ID of the organizer to delete
            
        Returns:
            bool: Success flag
        """
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    delete(organizer)
                    .where(organizer.c.id == organizer_id)
                )
                
        return True 