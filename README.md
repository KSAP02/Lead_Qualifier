
---
# 🚀 Lead Qualifier Dashboard

A full-stack application designed to help startup sales teams **qualify** and **analyze demo-request leads**.
[Project Demo Video](https://www.loom.com/share/09eb6f4ac87b42fe854963e1279a1ffe?sid=3a647c36-4192-45b8-b40d-101c31cb2912)

## 🧩 Tech Stack

- 🎯 **Frontend**: React + TypeScript (Vite)
- ⚡ **Backend**: Python FastAPI with SQLAlchemy ORM
- 🗄️ **Database**: SQLite
- 📊 **Data Analysis**: SQL queries + custom reports
- 🤖 **LLM Integration**: Enrich leads with quality & company summary
---

## 📁 Project Structure

```bash
lead-qualifier/
├── frontend/                 # React + TS frontend (Vite)
│   ├── src/
│   │   ├── components/       # Filters, LeadTable, LeadChart
│   │   ├── services/         # api.ts for API calls
│   │   ├── App.tsx           # Main dashboard component
│   │   └── main.tsx          # React entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                  # FastAPI backend
│   ├── app.py                # API routes (leads + events)
│   ├── models.py             # SQLAlchemy models (Lead, Event)
│   ├── database.py           # DB engine/session setup
│   ├── schemas.py            # Pydantic models for request/response
│   ├── analytics.py          # Analytics reporting logic
│   ├── lead_qualification.db # SQLite database file
│
├── data/                     # Lead generation and sample data
│   ├── leads.csv             # Sample raw lead data
│   └── generate_data.py      # Script to generate leads into DB
│
├── requirements.txt          # Backend dependencies
└── README.md                 # Project documentation


````

---

## 🛠️ Setup & Run Instructions

### 🔧 Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the FastAPI server (port 8000 by default)
python app.py # runs the fast api on port 8000
````

Runs at: [http://localhost:8000](http://localhost:8000)

---

### 💻 Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Runs at: [http://localhost:3000](http://localhost:3000)

---

### 📊 Analytics Terminal (SQL Reports)

Open a **new terminal**, activate the same backend environment, and run:

```bash
cd backend
python analytics.py
```

This generates:

* Usage reports
* Event counts
* Lead breakdowns
* Custom query results

---

## 🔄 Event Tracking

Every user interaction is **logged** in the backend with the following schema:

```json
{
  "userId": "user-123",
  "action": "filter",
  "data": {
    "filterType": "industry",
    "value": "Technology"
  },
  "timestamp": "2025-06-28T14:34:56Z"
}
```

These events are stored in the `events` table for usage analysis.

---

## 📈 SQL Queries & Results

### 🔍 Top 3 Filters Used in Last 7 Days

```sql
SELECT JSON_EXTRACT(data, '$.industry') AS industry,
       COUNT(*) AS uses
FROM events
WHERE action = 'filter'
  AND timestamp >= datetime('now', '-7 days')
  AND JSON_EXTRACT(data, '$.industry') IS NOT NULL
GROUP BY industry
ORDER BY uses DESC
LIMIT 3;
```

**Results:**

| Industry | Uses |
| -------- | ---- |
| Technology      | 7    |
| Healthcare      | 7    |
| Finance         | 1    |
---

### 📊 Pie vs. Bar Chart Preference

```sql
SELECT JSON_EXTRACT(data, '$.view') AS view,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM events WHERE action = 'toggle_view'), 2) AS pct
FROM events
WHERE action = 'toggle_view'
  AND JSON_EXTRACT(data, '$.view') IS NOT NULL
GROUP BY view;
```

**Results:**

| View | Pct   |
| ---- | ----- |
| chart | 42.86 |
| table | 57.14 |

---

## 📊 Sample `analytics.py` Report Output

```text
=== USAGE ANALYTICS REPORT ===

1. USER ACTION FREQUENCY:
   filter: 58 times
   refresh: 4 times
   toggle_view: 4 times

2. FILTER USAGE PATTERNS:
   Most filtered industries:
     Technology: 7 times
     Healthcare: 7 times
   Average size filter: 261 employees

3. ACTIVITY BY HOUR:
   14:00 - 28 events
   15:00 - 34 events
   16:00 - 3 events
   17:00 - 1 events

4. RECENT ACTIVITY (Last 7 days):
   2025-06-28: 66 events

5. LEAD QUALITY DISTRIBUTION:
   High: 5 (10.0%)
   Medium: 42 (84.0%)
   Low: 3 (6.0%)

6. INDUSTRY QUALITY BREAKDOWN:
   Technology:
     High: 1
     Medium: 16
     Low: 1
   Finance:
     Medium: 9
     Low: 1

7. SOURCE EFFECTIVENESS:
   Referral: 14 leads, 35.7% high quality
   Email: 14 leads, 0% high quality
```

---

## 🤖 LLM Integration

Every lead is enriched with:

* A **lead quality score**: `"High"`, `"Medium"`, `"Low"`
* A **1-sentence company summary**

### 🧠 Prompt Design

```
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
```

### 📦 Sample Enriched Lead

```json
{
  "id": 1,
  "name": "Hannah Lee",
  "company": "Mason and Sons",
  "industry": "Technology",
  "size": 330,
  "source": "Email",
  "quality": "Medium",
  "summary": "The sales lead from Hannah Lee at Mason and Sons, a technology company with 330 employees, sourced from email, is of medium quality. While the company size is decent, the lead source being email can vary in quality. Further qualification is needed to determine the potential of this lead.",
  "created_at": "2025-06-28T14:59:42.152568"
}
```

---

## ✅ Project Features Checklist

| Feature                                | Status |
| -------------------------------------- | ------ |
| React + TypeScript dashboard           | ✅ Done |
| FastAPI backend with database          | ✅ Done |
| Event tracking of user actions         | ✅ Done |
| SQLAlchemy + SQLite integration        | ✅ Done |
| SQL-based analytics via `analytics.py` | ✅ Done |
| LLM-based lead enrichment              | ✅ Done |

---
