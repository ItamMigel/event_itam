from datetime import date
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from repository.coworking_repository import CoworkingRepository


class CoworkingError(Exception):
    """Базовое исключение для операций с коворкингами."""
    pass


class CoworkingService:
    """Service for coworking space operations."""
    
    def __init__(self):
        self.coworking_repository = CoworkingRepository()
    
    async def get_all_coworking_spaces(self) -> List[Dict[str, Any]]:
        """
        Get all coworking spaces.
        
        Returns:
            List[Dict[str, Any]]: List of coworking space dictionaries
        """
        return await self.coworking_repository.get_all_coworking_spaces()
    
    async def get_coworking_by_id(self, coworking_id: UUID) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Get a coworking space by ID.
        
        Args:
            coworking_id: UUID of the coworking space
            
        Returns:
            Tuple[Optional[Dict[str, Any]], bool]: (coworking_data, found_flag)
        """
        return await self.coworking_repository.get_coworking_by_id(coworking_id)
    
    async def create_coworking_space(
        self,
        name: str,
        description: str,
        location: str,
        image_path: Optional[str] = None
    ) -> UUID:
        """
        Create a new coworking space.
        
        Args:
            name: Coworking space name
            description: Coworking space description
            location: Coworking space location
            image_path: Path to coworking space image
            
        Returns:
            UUID: ID of the created coworking space
            
        Raises:
            CoworkingError: If there's an error creating the coworking space
        """
        try:
            return await self.coworking_repository.create_coworking_space(
                name=name,
                description=description,
                location=location,
                image_path=image_path
            )
        except IntegrityError as e:
            logger.error(f"IntegrityError creating coworking space: {e}")
            raise CoworkingError(f"Error creating coworking space: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating coworking space: {e}")
            raise CoworkingError(f"Error creating coworking space: {str(e)}")
    
    async def update_coworking_space(
        self,
        coworking_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> bool:
        """
        Update a coworking space.
        
        Args:
            coworking_id: ID of the coworking space to update
            name: New name (optional)
            description: New description (optional)
            location: New location (optional)
            image_path: New image path (optional)
            
        Returns:
            bool: Success flag
        """
        try:
            return await self.coworking_repository.update_coworking_space(
                coworking_id=coworking_id,
                name=name,
                description=description,
                location=location,
                image_path=image_path
            )
        except IntegrityError as e:
            logger.error(f"IntegrityError updating coworking space: {e}")
            raise CoworkingError(f"Error updating coworking space: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating coworking space: {e}")
            raise CoworkingError(f"Error updating coworking space: {str(e)}")
    
    async def delete_coworking_space(self, coworking_id: UUID) -> bool:
        """
        Delete a coworking space.
        
        Args:
            coworking_id: ID of the coworking space to delete
            
        Returns:
            bool: Success flag
        """
        try:
            return await self.coworking_repository.delete_coworking_space(coworking_id)
        except Exception as e:
            logger.error(f"Error deleting coworking space: {e}")
            raise CoworkingError(f"Error deleting coworking space: {str(e)}")
    
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
        try:
            return await self.coworking_repository.create_booking(
                coworking_id=coworking_id,
                booking_date=booking_date,
                customer_name=customer_name,
                customer_phone=customer_phone
            )
        except IntegrityError as e:
            logger.error(f"IntegrityError creating booking: {e}")
            raise CoworkingError(f"Error creating booking: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            raise CoworkingError(f"Error creating booking: {str(e)}")
    
    async def get_occupancy_stats(self, coworking_id: UUID) -> List[Dict[str, Any]]:
        """
        Get occupancy statistics for a coworking space.
        
        Args:
            coworking_id: ID of the coworking space
            
        Returns:
            List[Dict[str, Any]]: List of occupancy data (date and percentage)
        """
        try:
            return await self.coworking_repository.get_occupancy_stats(coworking_id)
        except Exception as e:
            logger.error(f"Error getting occupancy stats: {e}")
            raise CoworkingError(f"Error getting occupancy stats: {str(e)}") 