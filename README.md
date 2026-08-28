# BrandPulse

## Real-Time Customer Intelligence & Competitor Monitoring Platform

BrandPulse is an AI-powered intelligence platform that collects customer and competitor information, analyzes it using AI, stores structured intelligence in PostgreSQL, and exposes the results through REST APIs.

The platform transforms raw information into structured, actionable business intelligence.

---

## Key Features

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
* Calculates a 0-100 Opportunity Score
* Generates AI-powered action briefs
* Fact-checks generated intelligence against source content
* Matches vulnerabilities to relevant customer posts via a semantic relevance engine
* Clusters related content into narratives using embeddings and density-based clustering
* Stores raw articles and processed intelligence in PostgreSQL
* Exposes intelligence through FastAPI
* Supports scheduled ingestion and processing
* Runs in a Dockerized environment

---

# Architecture

```text
                 DATA SOURCES
                      |
                      v
              +---------------+
              |   INGESTION   |
              | RSS / News    |
              +-------+-------+
                      |
                      v
              +---------------+
              |  PostgreSQL   |
              |  Articles DB  |
              +-------+-------+
                      |
                      v
             +------------------+
             |   AI PIPELINE    |
             |                  |
             | Vulnerability    |
             | Detection        |
             |       v          |
             | Opportunity      |
             | Scoring          |
             |       v          |
             | Action Brief     |
             |       v          |
             | Fact Audit       |
             +--------+---------+
                      |
                      v
             Vulnerability Results
                      |
                      v
                  FastAPI
                      |
                      v
              Frontend / Consumers
```

---

# End-to-End Flow

```text
News / Customer Content
          v
       Ingestion
          v
      Data Cleaning
          v
       PostgreSQL
          v
     AI Processing
          v
  Structured Intelligence
          v
       PostgreSQL
          v
        FastAPI
          v
   Frontend / Consumers
```

---

# Sprint 1

The initial customer intelligence pipeline was:

```text
Ingestion
    v
Sentiment Analysis
    v
Intent Analysis
    v
Database
```

The goal was to transform raw customer/community content into structured sentiment and intent information.

---

# Sprint 2

Sprint 2 extends the existing foundation into competitive intelligence:

```text
Competitive News
       v
    Ingestion
       v
   Articles DB
       v
Unprocessed Articles
       v
Vulnerability Detection
       v
Opportunity Scoring
       v
Action Brief Generation
       v
Fact Audit
       v
Vulnerability Results DB
       v
      FastAPI
```

---

# AI Intelligence Pipeline (Sprint 2)

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

The final Opportunity Score is normalized to **0-100**.

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

# Sprint 3: Narrative Intelligence

Sprint 3 explored a shift from single-article vulnerability detection toward narrative-level intelligence, in order to identify broader patterns across multiple related articles and posts rather than treating each item in isolation.

### Planned Approach

```text
Raw Content
     v
Embedding Generation (BGE-M3)
     v
Density-Based Clustering (HDBSCAN)
     v
Narrative Groups
     v
Entity Extraction (GLiNER)
     v
Narrative-Level Features
(cluster size, entity co-occurrence, growth)
     v
Campaign / Relevance Scoring (XGBoost)
```

### Completion Status

The following components were completed and demonstrated:

* **Embedding generation:** Content embeddings produced using BGE-M3
* **Clustering:** Density-based clustering (HDBSCAN) applied to embeddings to group related content into narratives
* **Campaign intelligence extensions:** Initial additions to campaign generation, including strategy and channel type fields

The following components were scoped but not completed in this sprint:

* Entity extraction and narrative-level entity features (GLiNER)
* Final XGBoost-based campaign/relevance scoring model

### Review

A Sprint 3 review and handoff demo was held with the team and project leads. The demo covered the completed embedding and clustering pipeline and was successfully presented, alongside a discussion of the remaining scope (entity extraction and scoring) as a direction for future work.

---

# Competitive News Ingestion

Competitive news is fetched through:

```python
fetch_competitive_news_articles()
```

The ingestion flow is:

```text
RSS Sources
    v
Fetch Articles
    v
Resolve URLs
    v
Extract Content
    v
Clean / Validate
    v
Competitive Filtering
    v
Structured Article
```

Multiple extraction methods are used as fallbacks when necessary:

```text
Fundus
   v
Trafilatura
   v
Newspaper4k
   v
Readability
```

The system also handles situations where websites block automated access or article extraction fails.

---

# Database

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

# Competitive Intelligence Orchestration

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
        v
Save articles to DB
        v
Run competitive intelligence job
        v
Close DB session
```

### `run_competitive_intelligence_job()`

This handles the DB -> AI -> DB workflow:

```text
Articles DB
     v
Find unprocessed articles
     v
Convert DB records to pipeline input
     v
Run AI pipeline
     v
Save vulnerability results
     v
Mark articles as processed
     v
Commit transaction
```

---

# API

BrandPulse uses **FastAPI** to expose processed intelligence to consumers.

The API layer separates consumers from direct database access:

```text
PostgreSQL
     v
Service Layer
     v
FastAPI
     v
Consumers
```

FastAPI provides interactive API documentation through Swagger UI.

### Main Development Endpoints

```text
GET /
GET /api/health
GET /docs
```

The vulnerability API exposes the processed competitive intelligence to downstream consumers.

---

# Scheduler

BrandPulse uses **APScheduler** for scheduled background processing.

The application startup flow is:

```text
FastAPI Startup
      v
Initialize Database
      v
Start Scheduler
      v
Run Scheduled Jobs
```

The competitive intelligence scheduler executes:

```python
scheduled_competitive_ingestion_job()
```

---

# Project Structure

```text
backend/
|
+-- app/
|   |
|   +-- ai/
|   |   +-- vulnerability_classifier.py
|   |   +-- vulnerability_pipeline.py
|   |   +-- opportunity_scorer.py
|   |   +-- slm_generator.py
|   |   +-- fact_auditor.py
|   |   +-- vulnerability_prompts.py
|   |
|   +-- api/
|   |   +-- articles.py
|   |   +-- vulnerability.py
|   |   +-- routes_posts.py
|   |   +-- routes_stats.py
|   |
|   +-- database/
|   |   +-- models.py
|   |   +-- session.py
|   |
|   +-- ingestion/
|   |   +-- rss_fetcher.py
|   |   +-- news_fetcher.py
|   |   +-- scheduler.py
|   |
|   +-- services/
|   |   +-- article_service.py
|   |   +-- vulnerability_service.py
|   |
|   +-- schemas/
|   |   +-- vulnerability.py
|   |
|   +-- config.py
|   +-- main.py
|
+-- models_storage/
+-- Dockerfile
+-- requirements.txt
```

---

# Technology Stack

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
* BGE-M3 Embeddings
* HDBSCAN Clustering

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

# Running BrandPulse

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

# API Documentation

Once the backend is running:

```text
http://localhost:8000/docs
```

Frontend:

```text
http://localhost:5173
```

Health check:

```text
http://localhost:8000/api/health
```

---

# End-to-End Verification

A complete competitive intelligence cycle should follow:

```text
1. Fetch competitive news
          v
2. Save article
          v
3. Article appears in PostgreSQL
          v
4. Find unprocessed article
          v
5. Run AI pipeline
          v
6. Generate vulnerability result
          v
7. Save vulnerability result
          v
8. Mark article as processed
          v
9. Expose result through API
```

---

# Logging

BrandPulse uses Python's `logging` module for application and scheduler logs.
View backend logs with:

```bash
docker compose logs -f backend
```

View the latest logs:

```bash
docker compose logs --tail=100 backend
```

---

# Current Limitations

Some publisher websites may:

* Block automated requests
* Use Cloudflare protection
* Fail DNS resolution
* Reject automated clients
* Provide incomplete article content

Local AI inference can also take significant time when processing multiple articles.

The Sprint 3 narrative intelligence pipeline is partially complete: embedding generation and clustering are functional, while entity extraction and final campaign/relevance scoring remain unfinished.

---

# Future Improvements

Potential future improvements include:

* Slack alert integration
* More competitive news sources
* Improved article extraction
* Faster batch AI inference
* Better duplicate detection
* Improved opportunity scoring
* Completing entity extraction (GLiNER) for narrative features
* Completing XGBoost-based campaign/relevance scoring
* Frontend/dashboard integration
* Cloud deployment
* Monitoring and observability
* Additional vulnerability categories

---

# Product Goal

BrandPulse turns:

```text
Raw Customer & Competitor Information
                  v
             AI Analysis
                  v
        Structured Intelligence
                  v
           Business Action
```

The ultimate goal is to reduce manual monitoring and help teams identify important customer and competitor signals faster.

---

## Summary

BrandPulse combines data ingestion, AI analysis, PostgreSQL persistence, scheduled orchestration, and FastAPI APIs into a single competitive intelligence platform.

The Sprint 2 competitive intelligence flow is:

```text
Professional News
       v
    Ingestion
       v
   Articles DB
       v
Vulnerability Detection
       v
Opportunity Scoring
       v
 Action Brief
       v
   Fact Audit
       v
Vulnerability Results DB
       v
     FastAPI
       v
Frontend / Consumers
```

Sprint 3 extended this work toward narrative-level intelligence, with embedding generation and clustering completed, and entity extraction and final campaign scoring left as future work.

**BrandPulse turns raw information into structured, actionable competitive intelligence.**
