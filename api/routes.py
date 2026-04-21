from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import sys
import os
import re

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from config.config import Config

router = APIRouter()

# Setup database connection
try:
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    engine = None
    SessionLocal = None
    print(f"Failed to initialize database connection for API: {e}")

# Dependency to get DB session
def get_db():
    if not SessionLocal:
        raise HTTPException(status_code=500, detail="Database connection not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _row_to_dict(row):
    # Depending on sqlalchemy version, mapping row might be required
    row_dict = {}
    for column, value in row._mapping.items():
        row_dict[column] = value
    return row_dict

@router.get("/jobs")
def get_jobs(skill: str = Query(None, description="Filter jobs by skill"), db: Session = Depends(get_db)):
    """Retrieve all jobs, optionally filtered by skill."""
    try:
        if skill:
            # Prepare safely to prevent SQL injection
            sql = text("SELECT * FROM jobs WHERE skills ILIKE :skill ORDER BY scraped_at DESC")
            result = db.execute(sql, {"skill": f"%{skill}%"}).fetchall()
        else:
            sql = text("SELECT * FROM jobs ORDER BY scraped_at DESC")
            result = db.execute(sql).fetchall()
        
        return {"data": [_row_to_dict(row) for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Retrieve basic statistics about the jobs."""
    try:
        # 1. Total jobs
        total_sql = text("SELECT COUNT(*) as count FROM jobs")
        total_jobs = db.execute(total_sql).scalar()
        
        # 2. Avg salary logic (basic implementation)
        # Assuming salary might be '100000-150000' or similar string representation.
        # We parse the strings in memory for a rough average (a pure DB query would be complex if format is inconsistent).
        salaries_sql = text("SELECT salary FROM jobs WHERE salary IS NOT NULL AND salary != 'Not specified' AND salary != 'Unknown'")
        salaries = db.execute(salaries_sql).fetchall()
        
        total_salary = 0
        valid_salaries_count = 0
        for r in salaries:
            val = str(r[0])
            # Extract numbers
            numbers = [int(n) for n in re.findall(r"\d+", val.replace(',', ''))]
            if numbers:
                avg_for_record = sum(numbers) / len(numbers)
                # Adjust if numbers are listed in thousands e.g. 150k -> 150000
                if "k" in val.lower() and avg_for_record < 1000:
                    avg_for_record *= 1000
                
                total_salary += avg_for_record
                valid_salaries_count += 1
                
        avg_salary = total_salary / valid_salaries_count if valid_salaries_count > 0 else 0
        
        # 3. Top skills (memory aggregation based on comma separated string)
        skills_sql = text("SELECT skills FROM jobs WHERE skills IS NOT NULL AND skills != 'Unknown'")
        skills_data = db.execute(skills_sql).fetchall()
        
        skill_counts = {}
        for r in skills_data:
            job_skills = [s.strip().lower() for s in str(r[0]).split(',')]
            for s in job_skills:
                if s:
                    skill_counts[s] = skill_counts.get(s, 0) + 1
                    
        # Sort and get top 5
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_skills_list = [{"skill": k, "count": v} for k, v in top_skills]
        
        return {
            "total_jobs": total_jobs,
            "average_salary_estimate": f"${avg_salary:,.2f}",
            "top_skills": top_skills_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
