# File: schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

# Lead schemas
class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=100)
    size: int = Field(..., ge=1)
    source: str = Field(..., min_length=1, max_length=100)
    quality: str = Field(default="Medium", max_length=50)
    summary: Optional[str] = Field(None, max_length=1000)

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class LeadResponse(BaseModel):
    """Response model that matches the frontend Lead interface"""
    id: str  # Frontend expects string
    name: str
    company: str
    industry: str
    size: int
    source: str
    created_at: str  # Frontend expects ISO string
    quality: str
    summary: str

# Event schemas
class EventData(BaseModel):
    """Event data model that matches frontend EventData interface"""
    action: str = Field(..., min_length=1)
    data: Optional[Any] = None  # Changed from Dict[str, Any] to Any for more flexibility
    timestamp: Optional[str] = None  # Optional, will be set server-side if not provided

class Event(BaseModel):
    id: int
    action: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        orm_mode = True

class EventResponse(BaseModel):
    """Response model for events"""
    id: int
    action: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str  # ISO string format

# Filter schemas
class LeadFilter(BaseModel):
    industry: Optional[str] = None
    size: Optional[int] = None