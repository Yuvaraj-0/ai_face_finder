from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class Image(Base):
    __tablename__ = "images"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    event_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    photographer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # File info
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    # Cloudinary data
    cloudinary_public_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    cloudinary_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    cloudinary_secure_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    # Image metadata
    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Additional metadata (JSON field)
    image_metadata: Mapped[dict | None] = mapped_column(
    "metadata", JSON, nullable=True
)
    
    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    # Relationships
    event = relationship("Event", back_populates="images")