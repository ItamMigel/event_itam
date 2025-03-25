from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from loguru import logger

from services.coworking_service import CoworkingService, CoworkingError

coworking_service = CoworkingService()

coworking_router = APIRouter(
    prefix="/coworking",
    tags=["Coworking"],
    responses={404: {"description": "Not Found"}},
)


class CoworkingSpaceDto(BaseModel):
    id: UUID
    name: str
    description: str
    location: str
    image_path: Optional[str] = None


class CoworkingSpacesResponse(BaseModel):
    spaces: List[CoworkingSpaceDto]


class OccupancyDataDto(BaseModel):
    date: date
    occupancy_percentage: int


class CoworkingDetailResponse(CoworkingSpaceDto):
    occupancy_data: List[OccupancyDataDto]


class BookingRequest(BaseModel):
    booking_date: date
    customer_name: str
    customer_phone: str


class BookingResponse(BaseModel):
    id: UUID
    message: str = "Booking created successfully"


class CoworkingCreateRequest(BaseModel):
    name: str
    description: str
    location: str
    image_path: Optional[str] = None


class CoworkingCreateResponse(BaseModel):
    id: UUID


@coworking_router.get("/", response_model=CoworkingSpacesResponse)
async def get_all_coworking_spaces():
    """
    Get all coworking spaces.
    """
    logger.info("get_all_coworking_spaces")
    spaces = await coworking_service.get_all_coworking_spaces()
    
    return CoworkingSpacesResponse(
        spaces=[
            CoworkingSpaceDto(
                id=space["id"],
                name=space["name"],
                description=space["description"],
                location=space["location"],
                image_path=space["image_path"]
            )
            for space in spaces
        ]
    )


@coworking_router.get("/{coworking_id}", response_model=CoworkingDetailResponse)
async def get_coworking_by_id(coworking_id: UUID):
    """
    Get coworking space details with occupancy data.
    """
    logger.info(f"get_coworking_by_id: {coworking_id}")
    
    # Get coworking space details
    coworking_data, found = await coworking_service.get_coworking_by_id(coworking_id)
    if not found:
        logger.error(f"get_coworking_by_id: {coworking_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coworking space not found")
    
    # Get occupancy statistics
    occupancy_data = await coworking_service.get_occupancy_stats(coworking_id)
    
    return CoworkingDetailResponse(
        id=coworking_data["id"],
        name=coworking_data["name"],
        description=coworking_data["description"],
        location=coworking_data["location"],
        image_path=coworking_data["image_path"],
        occupancy_data=[
            OccupancyDataDto(
                date=data["date"],
                occupancy_percentage=data["occupancy_percentage"]
            )
            for data in occupancy_data
        ]
    )


@coworking_router.post("/", response_model=CoworkingCreateResponse, status_code=201)
async def create_coworking_space(coworking: CoworkingCreateRequest):
    """
    Create a new coworking space.
    """
    logger.info(f"create_coworking_space: {coworking.name}")
    
    try:
        # Create coworking space
        coworking_id = await coworking_service.create_coworking_space(
            name=coworking.name,
            description=coworking.description,
            location=coworking.location,
            image_path=coworking.image_path
        )
        
        return CoworkingCreateResponse(id=coworking_id)
    except CoworkingError as e:
        logger.warning(f"Failed to create coworking space: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create coworking space: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating coworking space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create coworking space due to an internal error"
        )


@coworking_router.post("/{coworking_id}/booking", response_model=BookingResponse)
async def create_booking(coworking_id: UUID, booking: BookingRequest):
    """
    Create a new booking for a coworking space.
    """
    logger.info(f"create_booking for coworking: {coworking_id}")
    
    try:
        # Check if coworking space exists
        _, found = await coworking_service.get_coworking_by_id(coworking_id)
        if not found:
            logger.error(f"create_booking: coworking {coworking_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coworking space not found")
        
        # Create booking
        booking_id = await coworking_service.create_booking(
            coworking_id=coworking_id,
            booking_date=booking.booking_date,
            customer_name=booking.customer_name,
            customer_phone=booking.customer_phone
        )
        
        return BookingResponse(id=booking_id)
    except CoworkingError as e:
        logger.warning(f"Failed to create booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create booking: {str(e)}"
        )
    except HTTPException:
        # Пробрасываем HTTPException дальше без изменений
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking due to an internal error"
        )


@coworking_router.delete("/{coworking_id}", status_code=204)
async def delete_coworking_space(coworking_id: UUID):
    """
    Delete a coworking space.
    """
    logger.info(f"delete_coworking_space: {coworking_id}")
    
    try:
        # Check if coworking space exists
        _, found = await coworking_service.get_coworking_by_id(coworking_id)
        if not found:
            logger.error(f"delete_coworking_space: {coworking_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coworking space not found")
        
        # Delete the coworking space
        success = await coworking_service.delete_coworking_space(coworking_id)
        if not success:
            logger.error(f"Failed to delete coworking space: {coworking_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete coworking space"
            )
        
        return None
    except CoworkingError as e:
        logger.warning(f"Failed to delete coworking space: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete coworking space: {str(e)}"
        )
    except HTTPException:
        # Пробрасываем HTTPException дальше без изменений
        raise
    except Exception as e:
        logger.error(f"Error deleting coworking space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete coworking space due to an internal error"
        ) 