# File: analytics.py
"""
SQL queries for usage analysis - Run this script to analyze user behavior
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text, case
from database import SessionLocal, engine
from models import Lead as LeadModel, Event as EventModel
from datetime import datetime, timedelta
import json

def get_lead_by_id(lead_id: int) -> dict:
    """
    Retrieve a single lead by ID and return as dictionary payload
    """
    db = SessionLocal()
    try:
        lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
        
        if not lead:
            return {"error": f"Lead with ID {lead_id} not found"}
        
        return {
            "id": lead.id,
            "name": lead.name,
            "company": lead.company,
            "quality": lead.quality,
            "summary": lead.summary,
            "industry": lead.industry,
            "size": lead.size,
            "source": lead.source,
            "email": getattr(lead, 'email', None),  # If email field exists
            "phone": getattr(lead, 'phone', None),  # If phone field exists
            "created_at": lead.created_at.isoformat() if hasattr(lead, 'created_at') else None,
            "updated_at": lead.updated_at.isoformat() if hasattr(lead, 'updated_at') else None
        }
    
    finally:
        db.close()

def get_usage_analytics():
    """
    Comprehensive usage analytics from stored events
    """
    db = SessionLocal()
    
    print("=== USAGE ANALYTICS REPORT ===\n")
    
    try:
        # 1. Most common user actions
        print("1. USER ACTION FREQUENCY:")
        action_counts = db.query(
            EventModel.action,
            func.count(EventModel.id).label('count')
        ).group_by(EventModel.action).order_by(func.count(EventModel.id).desc()).all()
        
        for action, count in action_counts:
            print(f"   {action}: {count} times")
        
        # 2. Filter usage patterns
        print("\n2. FILTER USAGE PATTERNS:")
        filter_events = db.query(EventModel).filter(EventModel.action == 'filter').all()
        
        industry_filters = {}
        size_filters = []
        
        for event in filter_events:
            if event.data:
                if 'industry' in event.data:
                    industry = event.data['industry']
                    industry_filters[industry] = industry_filters.get(industry, 0) + 1
                if 'size' in event.data:
                    size_filters.append(event.data['size'])
        
        print("   Most filtered industries:")
        for industry, count in sorted(industry_filters.items(), key=lambda x: x[1], reverse=True):
            print(f"     {industry}: {count} times")
        
        if size_filters:
            avg_size_filter = sum(size_filters) / len(size_filters)
            print(f"   Average size filter: {avg_size_filter:.0f} employees")
        
        # 3. Activity by time patterns
        print("\n3. ACTIVITY PATTERNS:")
        
        # Hourly activity
        hourly_activity = db.query(
            func.strftime('%H', EventModel.timestamp).label('hour'),
            func.count(EventModel.id).label('count')
        ).group_by(func.strftime('%H', EventModel.timestamp)).all()
        
        print("   Activity by hour:")
        for hour, count in sorted(hourly_activity, key=lambda x: int(x[0])):
            print(f"     {hour}:00 - {count} events")
        
        # 4. Recent activity (last 7 days)
        print("\n4. RECENT ACTIVITY (Last 7 days):")
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_events = db.query(
            func.date(EventModel.timestamp).label('date'),
            func.count(EventModel.id).label('count')
        ).filter(
            EventModel.timestamp >= seven_days_ago
        ).group_by(func.date(EventModel.timestamp)).order_by('date').all()
        
        for date, count in recent_events:
            print(f"   {date}: {count} events")
        
        # 5. Overall statistics
        print("\n5. OVERALL STATISTICS:")
        total_events = db.query(EventModel).count()
        unique_days = db.query(func.count(func.distinct(func.date(EventModel.timestamp)))).scalar()
        
        print(f"   Total events logged: {total_events}")
        print(f"   Days with activity: {unique_days}")
        if unique_days > 0:
            print(f"   Average events per day: {total_events / unique_days:.1f}")
        
    finally:
        db.close()

def get_lead_analytics():
    """
    Lead quality and distribution analytics
    """
    db = SessionLocal()
    
    print("\n=== LEAD ANALYTICS REPORT ===\n")
    
    try:
        # 1. Lead quality distribution (from LLM analysis)
        print("1. LEAD QUALITY DISTRIBUTION:")
        quality_counts = db.query(
            LeadModel.quality,
            func.count(LeadModel.id).label('count')
        ).group_by(LeadModel.quality).all()
        
        total_leads = sum(count for _, count in quality_counts)
        for quality, count in quality_counts:
            percentage = (count / total_leads) * 100
            print(f"   {quality}: {count} leads ({percentage:.1f}%)")
        
        # 2. Industry breakdown with quality
        print("\n2. INDUSTRY BREAKDOWN WITH QUALITY:")
        industry_quality = db.query(
            LeadModel.industry,
            LeadModel.quality,
            func.count(LeadModel.id).label('count')
        ).group_by(LeadModel.industry, LeadModel.quality).all()
        
        industry_data = {}
        for industry, quality, count in industry_quality:
            if industry not in industry_data:
                industry_data[industry] = {}
            industry_data[industry][quality] = count
        
        for industry, qualities in industry_data.items():
            total = sum(qualities.values())
            print(f"   {industry} ({total} total):")
            for quality, count in qualities.items():
                percentage = (count / total) * 100
                print(f"     {quality}: {count} ({percentage:.1f}%)")
        
        # 3. Company size analysis - FIXED VERSION
        print("\n3. COMPANY SIZE ANALYSIS:")
        size_ranges = db.query(
            case(
                (LeadModel.size < 50, 'Small (1-49)'),
                (LeadModel.size < 200, 'Medium (50-199)'),
                (LeadModel.size < 500, 'Large (200-499)'),
                else_='Enterprise (500+)'
            ).label('size_range'),
            func.count(LeadModel.id).label('count'),
            func.avg(LeadModel.size).label('avg_size')
        ).group_by('size_range').all()
        
        for size_range, count, avg_size in size_ranges:
            print(f"   {size_range}: {count} leads (avg: {avg_size:.0f} employees)")
        
        # 4. Source effectiveness (based on quality)
        print("\n4. SOURCE EFFECTIVENESS:")
        source_quality = db.query(
            LeadModel.source,
            LeadModel.quality,
            func.count(LeadModel.id).label('count')
        ).group_by(LeadModel.source, LeadModel.quality).all()
        
        source_data = {}
        for source, quality, count in source_quality:
            if source not in source_data:
                source_data[source] = {'High': 0, 'Medium': 0, 'Low': 0, 'total': 0}
            source_data[source][quality] = count
            source_data[source]['total'] += count
        
        for source, data in source_data.items():
            high_rate = (data['High'] / data['total']) * 100 if data['total'] > 0 else 0
            print(f"   {source}: {data['total']} leads, {high_rate:.1f}% high quality")
        
    finally:
        db.close()

def get_industry_filter_usage():
    """
    Get the top 3 industries that were filtered/selected most in the last 7 days
    """
    db = SessionLocal()
    
    try:
        print("🔍 Top 3 Industries Filtered in Last 7 Days\n")
        
        print("```sql")
        industry_sql = """SELECT JSON_EXTRACT(data, '$.industry') AS industry,
       COUNT(*) AS uses
FROM events
WHERE action = 'filter'
  AND timestamp >= datetime('now', '-7 days')
  AND JSON_EXTRACT(data, '$.industry') IS NOT NULL
GROUP BY industry
ORDER BY uses DESC
LIMIT 3;"""
        print(industry_sql)
        print("```\n")
        
        print("**Results:**\n")
        
        # Execute the query
        result = db.execute(text(industry_sql))
        industry_results = result.fetchall()
        
        if industry_results:
            print("| Industry | Uses |")
            print("| -------- | ---- |")
            for industry, uses in industry_results:
                industry_name = industry if industry else "Unknown"
                print(f"| {industry_name:<15} | {uses:<4} |")
        else:
            # Fallback: try different data structures
            print("No results with '$.industry' - trying alternative data structures...\n")
            
            # Try looking for industry in different JSON paths
            alt_queries = [
                "JSON_EXTRACT(data, '$.filters.industry')",
                "JSON_EXTRACT(data, '$.selectedIndustry')",
                "JSON_EXTRACT(data, '$.filter_industry')"
            ]
            
            for alt_path in alt_queries:
                alt_sql = f"""SELECT {alt_path} AS industry,
           COUNT(*) AS uses
    FROM events
    WHERE action = 'filter'
      AND timestamp >= datetime('now', '-7 days')
      AND {alt_path} IS NOT NULL
    GROUP BY industry
    ORDER BY uses DESC
    LIMIT 3;"""
                
                try:
                    result = db.execute(text(alt_sql))
                    alt_results = result.fetchall()
                    
                    if alt_results:
                        print(f"Found results using {alt_path}:")
                        print("| Industry | Uses |")
                        print("| -------- | ---- |")
                        for industry, uses in alt_results:
                            industry_name = industry if industry else "Unknown"
                            print(f"| {industry_name:<15} | {uses:<4} |")
                        break
                except:
                    continue
            else:
                # If no JSON structure works, analyze from your analytics.py approach
                print("Analyzing from existing event data structure:\n")
                
                # Get filter events and analyze their data
                filter_events_sql = """SELECT data, timestamp
                FROM events 
                WHERE action = 'filter'
                  AND timestamp >= datetime('now', '-7 days')
                ORDER BY timestamp DESC"""
                
                result = db.execute(text(filter_events_sql))
                filter_events = result.fetchall()
                
                industry_counts = {}
                
                for data, timestamp in filter_events:
                    if data:
                        # Handle different data formats
                        if isinstance(data, str):
                            try:
                                data = json.loads(data)
                            except:
                                continue
                        
                        # Look for industry in various possible keys
                        industry = None
                        possible_keys = ['industry', 'selectedIndustry', 'filter_industry', 'industryFilter']
                        
                        for key in possible_keys:
                            if isinstance(data, dict) and key in data:
                                industry = data[key]
                                break
                        
                        if industry:
                            industry_counts[industry] = industry_counts.get(industry, 0) + 1
                
                if industry_counts:
                    print("| Industry | Uses |")
                    print("| -------- | ---- |")
                    sorted_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    for industry, uses in sorted_industries:
                        print(f"| {industry:<15} | {uses:<4} |")
                else:
                    print("| Industry | Uses |")
                    print("| -------- | ---- |")
                    print("| No data  | 0    |")
        
        print("\n" + "---" * 20 + "\n")
        
        # Also show the view preference query
        print("### 📊 Pie vs. Bar Chart Preference\n")
        
        print("```sql")
        view_sql = """SELECT JSON_EXTRACT(data, '$.view') AS view,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM events WHERE action = 'toggle_view'), 2) AS pct
FROM events
WHERE action = 'toggle_view'
  AND JSON_EXTRACT(data, '$.view') IS NOT NULL
GROUP BY view;"""
        print(view_sql)
        print("```\n")
        
        print("**Results:**\n")
        
        # Execute the view preference query
        result = db.execute(text(view_sql))
        view_results = result.fetchall()
        
        if view_results:
            print("| View | Pct   |")
            print("| ---- | ----- |")
            for view, pct in view_results:
                view_name = view if view else "unknown"
                print(f"| {view_name:<4} | {pct:<5} |")
        else:
            # Try alternative approach for view preferences
            print("No toggle_view events found - checking for view-related events...\n")
            
            view_events_sql = """SELECT action, data
            FROM events 
            WHERE (action LIKE '%view%' OR action LIKE '%chart%' OR action LIKE '%toggle%')
            ORDER BY timestamp DESC
            LIMIT 10"""
            
            try:
                result = db.execute(text(view_events_sql))
                view_events = result.fetchall()
                
                if view_events:
                    print("Found view-related events:")
                    for action, data in view_events:
                        data_str = json.dumps(data) if data else "No data"
                        print(f"  {action}: {data_str}")
                else:
                    print("| View | Pct   |")
                    print("| ---- | ----- |")
                    print("| No data | 0.00  |")
            except:
                print("| View | Pct   |")
                print("| ---- | ----- |")
                print("| No data | 0.00  |")
            
    except Exception as e:
        print(f"Error executing queries: {e}")
        
    finally:
        db.close()

def custom_sql_query(query_description, sql_query):
    """
    Execute custom SQL queries for specific analysis
    """
    print(f"\n=== CUSTOM QUERY: {query_description} ===")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            
            print(f"Columns: {list(columns)}")
            for row in rows:
                print(f"   {dict(zip(columns, row))}")
    
    except Exception as e:
        print(f"Query error: {e}")

if __name__ == "__main__":
    # Get a specific lead by ID
    lead = get_lead_by_id(1)
    print("Lead by ID:")
    print(json.dumps(lead, indent=2))
    
    # Run all analytics
    get_usage_analytics()
    get_lead_analytics()
    get_industry_filter_usage()  # Add this line
    
    # Example custom queries
    print("\n" + "="*50)
    
    # Custom query 1: Events by day with action breakdown
    custom_sql_query(
        "Events per day with action breakdown",
        """
        SELECT 
            DATE(timestamp) as date,
            action,
            COUNT(*) as count
        FROM events 
        GROUP BY DATE(timestamp), action 
        ORDER BY date DESC, count DESC
        """
    )
    
    # Custom query 2: High quality leads by source
    custom_sql_query(
        "High quality leads by source",
        """
        SELECT 
            source,
            COUNT(*) as high_quality_count,
            AVG(size) as avg_company_size
        FROM leads 
        WHERE quality = 'High'
        GROUP BY source 
        ORDER BY high_quality_count DESC
        """
    )
    
    # Custom query 3: Filter events with data
    custom_sql_query(
        "Recent filter events with parameters",
        """
        SELECT 
            timestamp,
            data
        FROM events 
        WHERE action = 'filter' 
        AND data IS NOT NULL
        ORDER BY timestamp DESC 
        LIMIT 10
        """
    )