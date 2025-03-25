from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

# Define metadata
metadata = MetaData()

# Event table
event = Table(
    "event",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("title", Text, nullable=False),
    Column("description", Text, nullable=False),
    Column("short_description", Text, nullable=False),
    Column("start_date", DateTime(timezone=True), nullable=False),
    Column("location", Text, nullable=False),
    Column("image_path", Text, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    UniqueConstraint("title", "start_date", name="uq_event_title_start_date"),
)

# Organizer table
organizer = Table(
    "organizer",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text, nullable=True),
    Column("image_path", Text, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

# Event-Organizer association table
event_organizer = Table(
    "event_organizer",
    metadata,
    Column("event_id", UUID, ForeignKey("event.id", ondelete="CASCADE"), primary_key=True),
    Column("organizer_id", UUID, ForeignKey("organizer.id", ondelete="CASCADE"), primary_key=True),
)

# Event registration table
event_registration = Table(
    "event_registration",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("event_id", UUID, ForeignKey("event.id", ondelete="CASCADE"), nullable=False),
    Column("participant_name", Text, nullable=False),
    Column("participant_email", Text, nullable=False),
    Column("participant_phone", Text, nullable=True),
    Column("registration_date", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

# Coworking space table
coworking_space = Table(
    "coworking_space",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text, nullable=False),
    Column("location", Text, nullable=False),
    Column("image_path", Text, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

# Coworking booking table
coworking_booking = Table(
    "coworking_booking",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("coworking_id", UUID, ForeignKey("coworking_space.id", ondelete="CASCADE"), nullable=False),
    Column("booking_date", DateTime, nullable=False),
    Column("customer_name", Text, nullable=False),
    Column("customer_phone", Text, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

# Coworking occupancy table
coworking_occupancy = Table(
    "coworking_occupancy",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("coworking_id", UUID, ForeignKey("coworking_space.id", ondelete="CASCADE"), nullable=False),
    Column("date", DateTime, nullable=False),
    Column("occupancy_percentage", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
) 