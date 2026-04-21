# Automated Job Data Pipeline

An end-to-end Data Engineering project that scrapes job listings from static and dynamic websites, cleanses the data, stores raw/structured data in databases, and exposes it via a RESTful API.

## Project Structure
```
job-data-pipeline/
│── scraper/
│   ├── static_scraper.py      (Requests + BS4)
│   ├── dynamic_scraper.py     (Selenium)
│
│── pipeline/
│   ├── transform.py           (Pandas)
│   ├── load_postgres.py       (SQLAlchemy / psycopg2)
│   ├── load_mongo.py          (pymongo)
│
│── api/
│   ├── main.py                (FastAPI App)
│   ├── routes.py              (Endpoints)
│
│── scheduler/
│   ├── run_pipeline.py        (Cron Orchestrator)
│
│── config/
│   ├── config.py              (Pydantic/Dotenv config loader)
│   ├── .env                   (Environment variables)
```

## Prerequisites

- Python 3.10+
- **Chrome / ChromeDriver** installed for Selenium (if scraping dynamically).
- Docker and Docker-Compose (if testing locally with the provided databases).

## Setup Instructions

### 1. Database Setup (Locally utilizing Docker)
To easily run Postgres and MongoDB locally:
```bash
docker-compose up -d
```
This will start MongoDB on `localhost:27017` and PostgreSQL on `localhost:5432`.

### 2. Python Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Verify or edit `config/.env`. Default credentials match the `docker-compose.yml`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=jobscraper

MONGO_URI=mongodb://localhost:27017/
MONGO_DB=jobscraper
MONGO_COLLECTION=raw_jobs
```

### 4. Running the Pipeline manually
To run the automated pipeline (scrapes sites, transforms data, loads to databases):
```bash
python scheduler/run_pipeline.py
```
Check `pipeline.log` for output.

### 5. Running the REST API
Start the FastAPI server:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- GET `/jobs` : Returns all structured jobs.
- GET `/jobs?skill=python` : Returns filtered jobs.
- GET `/stats` : Returns total jobs, estimated average salary, and top skills.

### 6. Scheduling via Cron (Linux/Mac)
To schedule this script to run every 6 hours, open your crontab (`crontab -e`) and add:
```bash
0 */6 * * * cd /path/to/job-data-pipeline && /path/to/venv/bin/python scheduler/run_pipeline.py >> cron.log 2>&1
```
*On Windows, you can use Task Scheduler to execute `run_pipeline.py`*
