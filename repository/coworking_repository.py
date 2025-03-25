from datetime import date, datetime
from typing import List, Optional, Tuple, Dict
from uuid import UUID, uuid4

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from persistent.database import get_session
from persistent.tables import coworking_space, coworking_booking, coworking_occupancy


class CoworkingRepository:
    """Repository for coworking space related database operations."""

    async def get_all_coworking_spaces(self) -> List[dict]:
        """
        Retrieve all coworking spaces from the database.
        
        Returns:
            List[dict]: List of coworking space dictionaries
        """
        async with get_session() as session:
            query = select(coworking_space)
            result = await session.execute(query)
            spaces = [dict(row._mapping) for row in result.all()]
            return spaces

    async def get_coworking_by_id(self, coworking_id: UUID) -> Tuple[Optional[dict], bool]:
        """
        Retrieve a coworking space by ID.
        
        Args:
            coworking_id: UUID of the coworking space
            
        Returns:
            Tuple[Optional[dict], bool]: (coworking_data, found_flag)
        """
        async with get_session() as session:
            query = select(coworking_space).where(coworking_space.c.id == coworking_id)
            result = await session.execute(query)
            coworking_data = result.mappings().first()
            
            if coworking_data:
                return dict(coworking_data), True
            return None, False

    async def create_coworking_space(
        self,
        name: str,
        description: str,
        location: str,
        image_path: Optional[str] = None
    ) -> UUID:
        """
        Create a new coworking space in the database.
        
        Args:
            name: Coworking space name
            description: Coworking space description
            location: Coworking space location
            image_path: Path to coworking space image
            
        Returns:
            UUID: ID of the created coworking space
        """
        coworking_id = uuid4()
        
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    insert(coworking_space).values(
                        id=coworking_id,
                        name=name,
                        description=description,
                        location=location,
                        image_path=image_path,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                
        return coworking_id
        
    async def update_coworking_space(
        self,
        coworking_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> bool:
        """
        Update an existing coworking space.
        
        Args:
            coworking_id: ID of the coworking space to update
            name: New name (optional)
            description: New description (optional)
            location: New location (optional)
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
                if location is not None:
                    values["location"] = location
                if image_path is not None:
                    values["image_path"] = image_path
                    
                if values:
                    await session.execute(
                        update(coworking_space)
                        .where(coworking_space.c.id == coworking_id)
                        .values(**values)
                    )
                    
        return True
        
    async def delete_coworking_space(self, coworking_id: UUID) -> bool:
        """
        Delete a coworking space from the database.
        
        Args:
            coworking_id: ID of the coworking space to delete
            
        Returns:
            bool: Success flag
        """
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    delete(coworking_space)
                    .where(coworking_space.c.id == coworking_id)
                )
                
        return True
        
    async def create_booking(
        self,
        coworking_id: UUID,
        booking_date: date,
        customer_name: str,
        customer_phone: str
    ) -> UUID:
        """
        Create a new booking for a coworking space.
        
        Args:
            coworking_id: ID of the coworking space
            booking_date: Date of the booking
            customer_name: Name of the customer
            customer_phone: Phone number of the customer
            
        Returns:
            UUID: ID of the created booking
        """
        booking_id = uuid4()
        
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    insert(coworking_booking).values(
                        id=booking_id,
                        coworking_id=coworking_id,
                        booking_date=booking_date,
                        customer_name=customer_name,
                        customer_phone=customer_phone,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                
                # Update occupancy data
                await self._update_occupancy(session, coworking_id, booking_date)
                
        return booking_id
    
    async def get_occupancy_stats(self, coworking_id: UUID) -> List[dict]:
        """
        Get occupancy statistics for a coworking space.
        
        Args:
            coworking_id: ID of the coworking space
            
        Returns:
            List[dict]: List of occupancy data
        """
        async with get_session() as session:
            query = select(
                coworking_occupancy.c.date,
                coworking_occupancy.c.occupancy_percentage
            ).where(
                coworking_occupancy.c.coworking_id == coworking_id
            ).order_by(
                coworking_occupancy.c.date
            )
            
            result = await session.execute(query)
            occupancy_data = [dict(row._mapping) for row in result.all()]
            return occupancy_data
    
    async def _update_occupancy(
        self,
        session: AsyncSession,
        coworking_id: UUID,
        booking_date: date
    ) -> None:
        """
        Update occupancy data after a booking.
        
        Args:
            session: Database session
            coworking_id: ID of the coworking space
            booking_date: Date of the booking
        """
        # Count bookings for this date
        count_query = select(func.count()).where(
            (coworking_booking.c.coworking_id == coworking_id) &
            (coworking_booking.c.booking_date == booking_date)
        )
        result = await session.execute(count_query)
        booking_count = result.scalar()
        
        # Assuming a max of 10 bookings per day = 100% occupancy
        max_bookings = 10
        occupancy_percentage = min(int((booking_count / max_bookings) * 100), 100)
        
        # Check if we already have an occupancy record for this date
        check_query = select(coworking_occupancy).where(
            (coworking_occupancy.c.coworking_id == coworking_id) &
            (coworking_occupancy.c.date == booking_date)
        )
        result = await session.execute(check_query)
        existing_record = result.first()
        
        if existing_record:
            # Update existing record
            await session.execute(
                update(coworking_occupancy)
                .where(
                    (coworking_occupancy.c.coworking_id == coworking_id) &
                    (coworking_occupancy.c.date == booking_date)
                )
                .values(
                    occupancy_percentage=occupancy_percentage,
                    updated_at=datetime.now()
                )
            )
        else:
            # Create new record
            await session.execute(
                insert(coworking_occupancy).values(
                    id=uuid4(),
                    coworking_id=coworking_id,
                    date=booking_date,
                    occupancy_percentage=occupancy_percentage,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ) 