"""
SCP Archive API Server
FastAPI application serving the SCP Foundation archive.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os

from database import init_db
from routes.scps import router as scps_router
from routes.tags import router as tags_router
from routes.ai_routes import router as ai_router

app = FastAPI(
    title="SCP Foundation Archive API",
    description="Interactive archive of the SCP Foundation universe",
    version="1.0.0",
)

# CORS - allow the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(scps_router)
app.include_router(tags_router)
app.include_router(ai_router)


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    """API root."""
    return {
        "name": "SCP Foundation Archive API",
        "version": "1.0.0",
        "endpoints": {
            "scps": "/api/scps",
            "scp_detail": "/api/scps/{id}",
            "related": "/api/scps/{id}/related",
            "tags": "/api/tags",
            "stats": "/api/tags/stats",
            "ai_status": "/api/ai/status",
            "ai_ask": "/api/ai/ask",
            "ai_recommend": "/api/ai/recommend",
            "ai_smart_search": "/api/ai/smart-search",
        },
        "docs": "/docs",
    }


@app.post("/api/import")
def import_data(db=Depends(import_db_dep)):
    """Import scraped data into the database."""
    from database import import_from_json
    
    json_path = os.path.join("data", "scp_archive.json")
    if not os.path.exists(json_path):
        return {"error": f"No data file found at {json_path}"}
    
    count = import_from_json(db, json_path)
    return {"imported": count, "source": json_path}


def import_db_dep():
    """Dependency for import endpoint."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)