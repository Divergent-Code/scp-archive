"""SCP article CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from database import get_db, SCPModel

router = APIRouter(prefix="/api/scps", tags=["scps"])


@router.get("")
def list_scps(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    object_class: Optional[str] = None,
    entry_type: Optional[str] = None,
    series: Optional[int] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "rating",
    db: Session = Depends(get_db),
):
    """List SCP entries with filtering and pagination."""
    query = db.query(SCPModel)

    # Filters
    if object_class:
        query = query.filter(SCPModel.object_class == object_class)
    if entry_type:
        query = query.filter(SCPModel.entry_type == entry_type)
    if series:
        query = query.filter(SCPModel.series == series)
    if tag:
        query = query.filter(SCPModel.tags_json.contains(f'"{tag}"'))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                SCPModel.title.ilike(search_term),
                SCPModel.id.ilike(search_term),
                SCPModel.description.ilike(search_term),
                SCPModel.containment_procedures.ilike(search_term),
            )
        )

    # Sort
    if sort == "rating":
        query = query.order_by(SCPModel.rating.desc())
    elif sort == "title":
        query = query.order_by(SCPModel.title)
    elif sort == "newest":
        query = query.order_by(SCPModel.created_date.desc())
    elif sort == "oldest":
        query = query.order_by(SCPModel.created_date)

    # Pagination
    total = query.count()
    total_pages = math.ceil(total / per_page)
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [item.to_card() for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/{entry_id}")
def get_scp(entry_id: str, db: Session = Depends(get_db)):
    """Get a single SCP entry by ID."""
    entry = db.query(SCPModel).filter(SCPModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{entry_id}' not found")
    return entry.to_dict()


@router.get("/{entry_id}/related")
def get_related(entry_id: str, db: Session = Depends(get_db)):
    """Get related SCPs for an entry."""
    entry = db.query(SCPModel).filter(SCPModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    related = []
    for rel_id in entry.related_scps:
        rel = db.query(SCPModel).filter(SCPModel.id == rel_id).first()
        if rel:
            related.append(rel.to_card())

    return {"items": related, "count": len(related)}