from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

try:
    from .routes import router as api_router
except ImportError:
    from routes import router as api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Data Pipeline API",
    description="API to expose processed job listings stored in PostgreSQL.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Job Data Pipeline API is running."}

if __name__ == "__main__":
    import uvicorn
    # Typically run via `uvicorn api.main:app --reload`
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
