# File: app.py
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

from database import SessionLocal, engine, Base
from models import Lead as LeadModel, Event as EventModel
from schemas import Lead, LeadResponse, EventData, EventResponse
import csv
import asyncio

# Load environment variables
load_dotenv()

# Optional LLM integration
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    LLM_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Qualification API", version="1.0.0")

# CORS middleware - Permissive for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def enhance_lead_with_llm(name: str, company: str, industry: str, size: int, source: str) -> dict:
    """
    Use LLM to determine lead quality and generate summary based on lead data
    """
    if not LLM_AVAILABLE:
        # Default quality logic when LLM is not available
        if size >= 500 and source in ["Referral", "Trade Show"]:
            quality = "High"
        elif size >= 100 and source not in ["Organic"]:
            quality = "Medium"
        else:
            quality = "Low"
        
        summary = f"Lead from {company} in {industry} industry with {size} employees. Source: {source}."
        return {"quality": quality, "summary": summary}
    
    try:
        prompt = f"""
        Analyze this sales lead and determine its quality and provide a brief summary:
        
        Contact: {name}
        Company: {company}
        Industry: {industry}
        Company Size: {size} employees
        Lead Source: {source}
        
        Based on this information:
        1. Assign a quality rating: "High", "Medium", or "Low"
        2. Provide a brief summary (max 100 words)
        
        Consider:
        - Larger companies (350+ employees) are typically higher quality
        - Referrals and trade show leads are usually higher quality
        - Technology and Healthcare industries often have higher budgets
        - Organic and email sources can vary in quality
        
        Respond in this exact JSON format:
        {{"quality": "High/Medium/Low", "summary": "Brief summary here"}}
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        
        import json
        result = json.loads(response.choices[0].message.content.strip())
        print(f"LLM response: {result}")
        return result
    
    except Exception as e:
        print(f"LLM enhancement failed: {e}")
        # Fallback to rule-based logic
        if size >= 500 and source in ["Referral", "Trade Show"]:
            quality = "High"
        elif size >= 100 and source not in ["Organic"]:
            quality = "Medium"
        else:
            quality = "Low"
        
        summary = f"Lead from {company} in {industry} industry with {size} employees. Source: {source}."
        return {"quality": quality, "summary": summary}

# Load sample data on startup with LLM enhancement
@app.on_event("startup")
async def load_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_leads = db.query(LeadModel).first()
        if existing_leads:
            return
        
        # Load data from CSV
        csv_path = "../data/leads.csv"
        if os.path.exists(csv_path):
            print("Loading and enhancing leads with LLM...")
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Parse datetime string
                    created_at_str = row['created_at'].replace('Z', '+00:00')
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                    except:
                        created_at = datetime.now()
                    
                    # Get LLM enhancement for quality and summary
                    enhancement = await enhance_lead_with_llm(
                        name=row['name'],
                        company=row['company'],
                        industry=row['industry'],
                        size=int(row['size']),
                        source=row['source']
                    )
                    
                    lead = LeadModel(
                        id=int(row['id']),
                        name=row['name'],
                        company=row['company'],
                        industry=row['industry'],
                        size=int(row['size']),
                        source=row['source'],
                        created_at=created_at,
                        quality=enhancement['quality'],
                        summary=enhancement['summary']
                    )
                    db.add(lead)
                    
                    # Add a small delay to avoid rate limiting
                    if LLM_AVAILABLE:
                        await asyncio.sleep(0.5)
            
            db.commit()
            print("Sample data loaded and enhanced successfully")
        else:
            print(f"CSV file not found at {csv_path}")
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Lead Qualification API is running"}

@app.get("/api/leads", response_model=List[LeadResponse])
async def get_leads(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    size: Optional[int] = Query(None, description="Filter by company size"),
    db: Session = Depends(get_db)
):
    """
    Get leads with optional filtering by industry and size
    """
    try:
        query = db.query(LeadModel)
        
        if industry:
            query = query.filter(LeadModel.industry.ilike(f"%{industry}%"))
        
        if size:
            query = query.filter(LeadModel.size >= size)
        
        leads = query.all()
        
        # Log the filter event for analytics
        filter_data = {}
        if industry:
            filter_data['industry'] = industry
        if size:
            filter_data['size'] = size
        
        event = EventModel(
            action="filter",
            data=filter_data if filter_data else None,
            timestamp=datetime.now()
        )
        db.add(event)
        db.commit()
        
        # Convert to response format
        response_leads = []
        for lead in leads:
            response_leads.append(LeadResponse(
                id=str(lead.id),
                name=lead.name,
                company=lead.company,
                industry=lead.industry,
                size=lead.size,
                source=lead.source,
                created_at=lead.created_at.isoformat(),
                quality=lead.quality,
                summary=lead.summary
            ))
        
        return response_leads
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")

@app.post("/api/events", response_model=EventResponse)
async def post_event(
    event_data: EventData,
    db: Session = Depends(get_db)
):
    """
    Log a user interaction event for analytics
    """
    try:
        # Parse timestamp if provided, otherwise use current time
        if hasattr(event_data, 'timestamp') and event_data.timestamp:
            try:
                timestamp = datetime.fromisoformat(event_data.timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        event = EventModel(
            action=event_data.action,
            data=event_data.data,
            timestamp=timestamp
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return EventResponse(
            id=event.id,
            action=event.action,
            data=event.data,
            timestamp=event.timestamp.isoformat()
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging event: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)