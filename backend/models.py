from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base
import json

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    size = Column(Integer, nullable=False)
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    quality = Column(String(50), nullable=False, default="Medium")
    summary = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', company='{self.company}')>"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    data = Column(JSON, nullable=True)  # Store JSON data
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Event(id={self.id}, action='{self.action}', timestamp='{self.timestamp}')>"