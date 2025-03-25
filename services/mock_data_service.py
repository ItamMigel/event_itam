from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from typing import List, Dict, Any, Optional

from loguru import logger
from sqlalchemy import select

from persistent.database import get_session
from services.event_service import EventService
from services.coworking_service import CoworkingService


class MockDataService:
    """Service for creating mock data for testing."""
    
    def __init__(self):
        self.event_service = EventService()
        self.coworking_service = CoworkingService()
        
    async def initialize_mock_data(self) -> None:
        """Initialize mock data for testing the application."""
        logger.info("Initializing mock data...")
        
        # Check if we already have data to avoid duplication
        async with get_session() as session:
            # Check for events
            event_count_query = select(1).limit(1)
            event_result = await session.execute(event_count_query)
            events_exist = event_result.scalar() is not None
            
            # Check for coworking spaces
            coworking_count_query = select(1).limit(1)
            coworking_result = await session.execute(coworking_count_query)
            coworking_exist = coworking_result.scalar() is not None
            
        if events_exist and coworking_exist:
            logger.info("Mock data already exists, skipping initialization")
            return
        
        await self._create_mock_events()
        await self._create_mock_coworking_spaces()
        
        logger.info("Mock data initialization complete")
    
    async def _create_mock_events(self) -> None:
        """Create mock events and organizers."""
        events = [
            {
                "title": "Tech Conference 2023",
                "description": "A three-day conference featuring the latest in technology trends, with workshops, keynotes, and networking opportunities. Join industry leaders and innovators as they discuss AI, blockchain, cloud computing, and more.",
                "short_description": "Annual tech conference with workshops and keynotes",
                "start_date": datetime.now() + timedelta(days=30),
                "location": "Convention Center, Downtown",
                "image_path": "/uploads/events/tech_conference.jpg",
                "organizer_name": "TechEvents Inc.",
                "organizer_description": "Leading technology event organizer",
                "organizer_image_path": "/uploads/organizers/tech_events.png"
            },
            {
                "title": "Web Development Workshop",
                "description": "Learn modern web development techniques from industry experts. This hands-on workshop covers frontend frameworks, backend development, and deployment strategies. Perfect for beginners and intermediate developers looking to enhance their skills.",
                "short_description": "Hands-on workshop for web developers",
                "start_date": datetime.now() + timedelta(days=15),
                "location": "Digital Academy, Tech District",
                "image_path": "/uploads/events/web_dev_workshop.jpg",
                "organizer_name": "Code Masters",
                "organizer_description": "Coding education specialists",
                "organizer_image_path": "/uploads/organizers/code_masters.png"
            },
            {
                "title": "Startup Pitch Night",
                "description": "An exciting evening where promising startups present their business ideas to potential investors. Entrepreneurs will have 5 minutes to pitch, followed by Q&A. Networking session and refreshments provided after the presentations.",
                "short_description": "Startups pitch to investors",
                "start_date": datetime.now() + timedelta(days=7),
                "location": "Innovation Hub, Financial District",
                "image_path": "/uploads/events/pitch_night.jpg",
                "organizer_name": "Venture Connect",
                "organizer_description": "Connecting startups with investors",
                "organizer_image_path": "/uploads/organizers/venture_connect.png"
            }
        ]
        
        for event_data in events:
            await self.event_service.create_event(**event_data)
            
        logger.info(f"Created {len(events)} mock events")
    
    async def _create_mock_coworking_spaces(self) -> None:
        """Create mock coworking spaces with sample bookings."""
        coworking_spaces = [
            {
                "name": "Downtown Hub",
                "description": "A modern coworking space in the heart of downtown, featuring high-speed internet, meeting rooms, and a coffee bar. Perfect for freelancers and small teams.",
                "location": "123 Main Street, Downtown",
                "image_path": "/uploads/coworking/downtown_hub.jpg"
            },
            {
                "name": "Tech Village",
                "description": "Collaborative workspace designed for tech startups and developers. Features dedicated desks, private offices, and a gaming lounge for relaxation.",
                "location": "456 Innovation Avenue, Tech District",
                "image_path": "/uploads/coworking/tech_village.jpg"
            }
        ]
        
        for space_data in coworking_spaces:
            coworking_id = await self.coworking_service.create_coworking_space(**space_data)
            
            # Create some bookings for this space
            await self._create_mock_bookings(coworking_id)
            
        logger.info(f"Created {len(coworking_spaces)} mock coworking spaces with bookings")
    
    async def _create_mock_bookings(self, coworking_id: UUID) -> None:
        """Create mock bookings for a coworking space."""
        # Sample customer data
        customers = [
            {"name": "Alice Johnson", "phone": "+1234567890"},
            {"name": "Bob Smith", "phone": "+9876543210"},
            {"name": "Charlie Brown", "phone": "+5554443333"},
            {"name": "Diana Prince", "phone": "+1112223334"}
        ]
        
        # Create bookings for the next 14 days with random distribution
        today = date.today()
        for i in range(14):
            booking_date = today + timedelta(days=i)
            
            # Create 1-3 bookings per day
            booking_count = i % 3 + 1
            for j in range(booking_count):
                if j >= len(customers):
                    continue
                    
                customer = customers[j]
                await self.coworking_service.create_booking(
                    coworking_id=coworking_id,
                    booking_date=booking_date,
                    customer_name=customer["name"],
                    customer_phone=customer["phone"]
                ) 