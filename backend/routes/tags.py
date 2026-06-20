"""Tags and categories routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db, TagModel, SCPModel

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("")
def list_tags(
    min_count: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all tags with their counts."""
    tags = (
        db.query(TagModel)
        .filter(TagModel.count >= min_count)
        .order_by(desc(TagModel.count))
        .limit(limit)
        .all()
    )
    return {
        "items": [{"name": t.name, "count": t.count} for t in tags],
        "total": len(tags),
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get archive statistics."""
    total_scps = db.query(SCPModel).filter(SCPModel.entry_type == "scp").count()
    total_tales = db.query(SCPModel).filter(SCPModel.entry_type == "tale").count()
    total_goi = db.query(SCPModel).filter(SCPModel.entry_type == "goi-format").count()
    total_tags = db.query(TagModel).count()
    
    class_dist = {}
    for row in db.query(SCPModel.object_class, SCPModel.id).distinct().all():
        cls = row[0] or "Unknown"
        class_dist[cls] = class_dist.get(cls, 0) + 1

    return {
        "total_entries": total_scps + total_tales + total_goi,
        "scps": total_scps,
        "tales": total_tales,
        "goi_formats": total_goi,
        "total_tags": total_tags,
        "class_distribution": class_dist,
    }