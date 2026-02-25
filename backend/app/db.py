"""
Database configuration and models
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, LargeBinary, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(String)
    author_name = Column(String)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)  # image, video
    text_embedding = Column(LargeBinary, nullable=True)  # Serialized 384-dim vector
    image_embedding = Column(LargeBinary, nullable=True)  # Serialized 512-dim vector
    has_image = Column(Boolean, default=False)  # Flag for faster queries
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    post_metadata = Column(JSON, default={})


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class InteractionLog(Base):
    __tablename__ = "interactions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    post_id = Column(String)
    interaction_type = Column(String)  # like, comment, share, view
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction_metadata = Column(JSON, default={})


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

