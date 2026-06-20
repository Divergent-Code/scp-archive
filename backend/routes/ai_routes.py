"""AI Guide routes for the SCP Archive."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db, SCPModel
from ai.guide import AIGuide

router = APIRouter(prefix="/api/ai", tags=["ai"])
guide = AIGuide()


class AskRequest(BaseModel):
    question: str
    context_ids: Optional[list[str]] = None


class RecommendRequest(BaseModel):
    scp_id: str


@router.get("/status")
def ai_status():
    """Check if the AI guide is configured."""
    return {
        "available": guide.is_available(),
        "message": "AI Guide is ready" if guide.is_available() else "AI Guide not configured - set OPENAI_API_KEY"
    }


@router.post("/ask")
def ask_ai(request: AskRequest, db: Session = Depends(get_db)):
    """Ask the AI guide a question."""
    if not guide.is_available():
        raise HTTPException(status_code=503, detail="AI Guide is not configured")

    context = None
    if request.context_ids:
        context = []
        for cid in request.context_ids:
            entry = db.query(SCPModel).filter(SCPModel.id == cid).first()
            if entry:
                context.append(entry.to_dict())

    answer = guide.ask(request.question, context)
    return {"question": request.question, "answer": answer}


@router.post("/recommend")
def recommend(request: RecommendRequest, db: Session = Depends(get_db)):
    """Get recommendations based on an SCP."""
    entry = db.query(SCPModel).filter(SCPModel.id == request.scp_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{request.scp_id}' not found")

    recommendation = guide.recommend(entry.id, entry.title, entry.tags, entry.description)
    return {
        "based_on": request.scp_id,
        "recommendation": recommendation,
    }


@router.post("/smart-search")
def smart_search(query: str = Query(...), db: Session = Depends(get_db)):
    """Natural language search interpreted by AI."""
    result = guide.smart_search(query, db)
    return result