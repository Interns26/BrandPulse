# BrandPulse

## Real-Time Customer Intelligence & Competitor Monitoring Platform

BrandPulse is an AI-powered intelligence platform that collects customer and competitor information, analyzes it using AI, stores structured intelligence in PostgreSQL, and exposes the results through REST APIs.

The platform transforms raw information into structured, actionable business intelligence.

---

## 🚀 Key Features

* Continuously ingests customer and competitor-related content
* Performs sentiment and intent analysis on customer content
* Monitors competitive news sources
* Detects competitor vulnerabilities
* Supports six vulnerability types:

  * System Outages
  * Price Increases
  * PR Crises
  * Layoffs
  * Product Defects
  * Data Breaches
* Calculates a 0–100 Opportunity Score
* Generates AI-powered action briefs
* Fact-checks generated intelligence against source content
* Stores raw articles and processed intelligence in PostgreSQL
* Exposes intelligence through FastAPI
* Supports scheduled ingestion and processing
* Runs in a Dockerized environment

---

# 🏗️ Architecture

```text
                 DATA SOURCES
                      │
                      ▼
              ┌───────────────┐
              │   INGESTION   │
              │ RSS / News    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  PostgreSQL   │
              │  Articles DB  │
              └───────┬───────┘
                      │
                      ▼
             ┌──────────────────┐
             │   AI PIPELINE    │
             │                  │
             │ Vulnerability    │
             │ Detection        │
             │       ↓          │
             │ Opportunity      │
             │ Scoring          │
             │       ↓          │
             │ Action Brief     │
             │       ↓          │
             │ Fact Audit       │
             └────────┬─────────┘
                      │
                      ▼
             Vulnerability Results
                      │
                      ▼
                  FastAPI
                      │
                      ▼
              Frontend / Consumers
```

---

# 🔄 End-to-End Flow

```text
News / Customer Content
          ↓
       Ingestion
          ↓
      Data Cleaning
          ↓
       PostgreSQL
          ↓
     AI Processing
          ↓
  Structured Intelligence
          ↓
       PostgreSQL
          ↓
        FastAPI
          ↓
   Frontend / Consumers
```

---

# 📌 Sprint 1

The initial customer intelligence pipeline was:

```text
Ingestion
    ↓
Sentiment Analysis
    ↓
Intent Analysis
    ↓
Database
```

The goal was to transform raw customer/community content into structured sentiment and intent information.

---

# 📌 Sprint 2

Sprint 2 extends the existing foundation into competitive intelligence:

```text
Competitive News
       ↓
    Ingestion
       ↓
   Articles DB
       ↓
Unprocessed Articles
       ↓
Vulnerability Detection
       ↓
Opportunity Scoring
       ↓
Action Brief Generation
       ↓
Fact Audit
       ↓
Vulnerability Results DB
       ↓
      FastAPI
```

---

# 🤖 AI Intelligence Pipeline

The main pipeline is:

```python
run_vulnerability_pipeline(articles)
```

It processes each article through multiple stages.

### 1. Vulnerability Detection

The classifier determines whether an article contains a relevant competitor vulnerability.

Supported vulnerability categories:

* System Outage
* Price Increase
* PR Crisis
* Layoffs
* Product Defect
* Data Breach

The classifier produces information such as:

* Relevance
* Matched competitors
* Vulnerability type
* Confidence score

---

### 2. Opportunity Scoring

Relevant vulnerabilities are scored using:

* Severity
* Coverage volume
* Urgency

The final Opportunity Score is normalized to **0–100**.

Example:

```json
{
  "opportunity_score": 47.0,
  "severity_score": 80.0,
  "volume_score": 50.0,
  "urgency_score": 0.0,
  "priority_label": "MEDIUM"
}
```

---

### 3. Action Brief Generation

A local SLM generates an action brief using:

* Competitor
* Vulnerability type
* Article context
* Opportunity Score

The resulting intelligence can include:

* Headline
* Vulnerability summary
* Target department
* Recommended action
* Urgency

---

### 4. Fact Audit

The generated action brief is checked against the original article.

The audit returns:

```json
{
  "is_passed": true,
  "flagged_claims": []
}
```

This helps ensure that generated intelligence is grounded in the source content.

---

# 📰 Competitive News Ingestion

Competitive news is fetched through:

```python
fetch_competitive_news_articles()
```

The ingestion flow is:

```text
RSS Sources
    ↓
Fetch Articles
    ↓
Resolve URLs
    ↓
Extract Content
    ↓
Clean / Validate
    ↓
Competitive Filtering
    ↓
Structured Article
```

Multiple extraction methods are used as fallbacks when necessary:

```text
Fundus
   ↓
Trafilatura
   ↓
Newspaper4k
   ↓
Readability
```

The system also handles situations where websites block automated access or article extraction fails.

---

# 🗄️ Database

BrandPulse uses **PostgreSQL** for persistent storage.

The database stores:

* Raw articles
* Customer posts
* Sources
* Ingestion information
* Vulnerability results
* AI-generated intelligence

## Article Processing State

Articles contain a processing state:

```text
vulnerability_processed
```

This allows the system to identify which articles still need competitive intelligence processing.

---

# 🔁 Competitive Intelligence Orchestration

The two main orchestration functions are:

```python
scheduled_competitive_ingestion_job()
```

and:

```python
run_competitive_intelligence_job()
```

### `scheduled_competitive_ingestion_job()`

This is the high-level Sprint 2 workflow.

```text
Fetch competitive news
        ↓
Save articles to DB
        ↓
Run competitive intelligence job
        ↓
Close DB session
```

### `run_competitive_intelligence_job()`

This handles the DB → AI → DB workflow:

```text
Articles DB
     ↓
Find unprocessed articles
     ↓
Convert DB records to pipeline input
     ↓
Run AI pipeline
     ↓
Save vulnerability results
     ↓
Mark articles as processed
     ↓
Commit transaction
```

---

# 🔌 API

BrandPulse uses **FastAPI** to expose processed intelligence to consumers.

The API layer separates consumers from direct database access:

```text
PostgreSQL
     ↓
Service Layer
     ↓
FastAPI
     ↓
Consumers
```

FastAPI provides interactive API documentation through Swagger UI.

### Main Development Endpoints

```text
GET /
GET /api/health
GET /docs
GET /openapi.json
```

The vulnerability API exposes the processed competitive intelligence to downstream consumers.

---

# ⏰ Scheduler

BrandPulse uses **APScheduler** for scheduled background processing.

The application startup flow is:

```text
FastAPI Startup
      ↓
Initialize Database
      ↓
Start Scheduler
      ↓
Run Scheduled Jobs
```

The competitive intelligence scheduler executes:

```python
scheduled_competitive_ingestion_job()
```

---

# 📁 Project Structure

```text
backend/
│
├── app/
│   │
│   ├── ai/
│   │   ├── vulnerability_classifier.py
│   │   ├── vulnerability_pipeline.py
│   │   ├── opportunity_scorer.py
│   │   ├── slm_generator.py
│   │   ├── fact_auditor.py
│   │   └── vulnerability_prompts.py
│   │
│   ├── api/
│   │   ├── articles.py
│   │   ├── vulnerability.py
│   │   ├── routes_posts.py
│   │   └── routes_stats.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── ingestion/
│   │   ├── rss_fetcher.py
│   │   ├── news_fetcher.py
│   │   └── scheduler.py
│   │
│   ├── services/
│   │   ├── article_service.py
│   │   └── vulnerability_service.py
│   │
│   ├── schemas/
│   │   └── vulnerability.py
│   │
│   ├── config.py
│   └── main.py
│
├── models_storage/
├── Dockerfile
└── requirements.txt
```

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic

### AI / NLP

* Hugging Face Transformers
* Local NLP models
* Local SLM
* Sentiment Analysis
* Intent Classification
* Vulnerability Classification
* Fact Auditing

### Ingestion

* RSS
* Feedparser
* curl_cffi
* Fundus
* Trafilatura
* Newspaper4k
* Readability

### Scheduling

* APScheduler

### Infrastructure

* Docker
* Docker Compose

### Development

* Git
* GitHub
* VS Code
* DBeaver

---

# ▶️ Running BrandPulse

## Prerequisites

* Docker Desktop
* Docker Compose
* Git

## Clone Repository

```bash
git clone <repository-url>
cd interns26-brandpulse
```

## Start Application

```bash
docker compose up --build
```

Or run in the background:

```bash
docker compose up -d --build
```

## Check Containers

```bash
docker compose ps
```

---

# 📖 API Documentation

Once the backend is running:

```text
http://localhost:8000/docs
```

OpenAPI:

```text
http://localhost:8000/openapi.json
```

Health check:

```text
http://localhost:8000/api/health
```

---

# 🐘 Database Verification

Check total articles:

```sql
SELECT COUNT(*)
FROM articles;
```

Check processed articles:

```sql
SELECT COUNT(*)
FROM articles
WHERE vulnerability_processed = TRUE;
```

Check unprocessed articles:

```sql
SELECT COUNT(*)
FROM articles
WHERE vulnerability_processed = FALSE;
```

Check vulnerability results:

```sql
SELECT *
FROM vulnerability_results;
```

---

# 🧪 End-to-End Verification

A complete competitive intelligence cycle should follow:

```text
1. Fetch competitive news
          ↓
2. Save article
          ↓
3. Article appears in PostgreSQL
          ↓
4. Find unprocessed article
          ↓
5. Run AI pipeline
          ↓
6. Generate vulnerability result
          ↓
7. Save vulnerability result
          ↓
8. Mark article as processed
          ↓
9. Expose result through API
```

---

# 📋 Logging

BrandPulse uses Python's `logging` module for application and scheduler logs.

Useful logs include:

* Application startup
* Database initialization
* Scheduler startup
* News fetching
* Article persistence
* AI processing
* Processing errors
* Application shutdown

View backend logs with:

```bash
docker compose logs -f backend
```

View the latest logs:

```bash
docker compose logs --tail=100 backend
```

---

# ⚠️ Current Limitations

Some publisher websites may:

* Block automated requests
* Use Cloudflare protection
* Fail DNS resolution
* Reject automated clients
* Provide incomplete article content

Local AI inference can also take significant time when processing multiple articles.

Slack alert integration is **not currently implemented**.

---

# 🔮 Future Improvements

Potential future improvements include:

* Slack alert integration
* More competitive news sources
* Improved article extraction
* Faster batch AI inference
* Better duplicate detection
* Improved opportunity scoring
* Frontend/dashboard integration
* Cloud deployment
* Monitoring and observability
* Additional vulnerability categories

---

# 🎯 Product Goal

BrandPulse turns:

```text
Raw Customer & Competitor Information
                  ↓
             AI Analysis
                  ↓
        Structured Intelligence
                  ↓
           Business Action
```

The ultimate goal is to reduce manual monitoring and help teams identify important customer and competitor signals faster.

---

## Summary

BrandPulse combines **data ingestion, AI analysis, PostgreSQL persistence, scheduled orchestration, and FastAPI APIs** into a single competitive intelligence platform.

The Sprint 2 competitive intelligence flow is:

```text
Professional News
       ↓
    Ingestion
       ↓
   Articles DB
       ↓
Vulnerability Detection
       ↓
Opportunity Scoring
       ↓
 Action Brief
       ↓
   Fact Audit
       ↓
Vulnerability Results DB
       ↓
     FastAPI
       ↓
Frontend / Consumers
```

**BrandPulse turns raw information into structured, actionable competitive intelligence.**
