"""Database models and connection for the SCP Archive."""

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scp_archive.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SCPModel(Base):
    """SQLAlchemy model for SCP entries."""
    __tablename__ = "scp_entries"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    object_class = Column(String, index=True, nullable=True)
    secondary_class = Column(String, nullable=True)
    containment_procedures = Column(Text, default="")
    description = Column(Text, default="")
    tags_json = Column(Text, default="[]")  # Stored as JSON string
    author = Column(String, nullable=True)
    rating = Column(Integer, default=0)
    created_date = Column(String, nullable=True)
    entry_type = Column(String, default="scp", index=True)
    related_scps_json = Column(Text, default="[]")
    content_html = Column(Text, default="")
    content_md = Column(Text, default="")
    series = Column(Integer, nullable=True)
    image_urls_json = Column(Text, default="[]")

    @property
    def tags(self) -> list[str]:
        return json.loads(self.tags_json) if self.tags_json else []

    @tags.setter
    def tags(self, value: list[str]):
        self.tags_json = json.dumps(value)

    @property
    def related_scps(self) -> list[str]:
        return json.loads(self.related_scps_json) if self.related_scps_json else []

    @related_scps.setter
    def related_scps(self, value: list[str]):
        self.related_scps_json = json.dumps(value)

    @property
    def image_urls(self) -> list[str]:
        return json.loads(self.image_urls_json) if self.image_urls_json else []

    @image_urls.setter
    def image_urls(self, value: list[str]):
        self.image_urls_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "object_class": self.object_class,
            "secondary_class": self.secondary_class,
            "containment_procedures": self.containment_procedures,
            "description": self.description,
            "tags": self.tags,
            "author": self.author,
            "rating": self.rating,
            "created_date": self.created_date,
            "entry_type": self.entry_type,
            "related_scps": self.related_scps,
            "series": self.series,
            "image_urls": self.image_urls,
        }

    def to_card(self) -> dict:
        """Return a compact version for list displays."""
        return {
            "id": self.id,
            "title": self.title,
            "object_class": self.object_class,
            "tags": self.tags[:5],
            "author": self.author,
            "rating": self.rating,
            "entry_type": self.entry_type,
            "description": self.description[:200] if self.description else "",
            "series": self.series,
        }


class TagModel(Base):
    """Model for tag-based indexing."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    count = Column(Integer, default=0)


def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_from_json(db: Session, json_file: str):
    """Import scraped data from JSON into the database."""
    with open(json_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    count = 0
    for entry_data in entries:
        # Check if exists
        existing = db.query(SCPModel).filter(SCPModel.id == entry_data["id"]).first()
        if existing:
            continue

        tags = entry_data.get("tags", [])
        related = entry_data.get("related_scps", [])
        images = entry_data.get("image_urls", [])

        # Determine series from ID
        series = None
        id_match = entry_data["id"]
        import re
        match = re.search(r'SCP-(\d+)', id_match)
        if match:
            num = int(match.group(1))
            series = ((num - 1) // 1000) + 1

        model = SCPModel(
            id=entry_data["id"],
            title=entry_data.get("title", ""),
            url=entry_data.get("url", ""),
            object_class=entry_data.get("object_class"),
            secondary_class=entry_data.get("secondary_class"),
            containment_procedures=entry_data.get("containment_procedures", ""),
            description=entry_data.get("description", ""),
            tags_json=json.dumps(tags),
            author=entry_data.get("author"),
            rating=entry_data.get("rating", 0),
            created_date=entry_data.get("created_date"),
            entry_type=entry_data.get("entry_type", "scp"),
            related_scps_json=json.dumps(related),
            content_html=entry_data.get("content_html", ""),
            content_md=entry_data.get("content_md", ""),
            series=series,
            image_urls_json=json.dumps(images),
        )
        db.add(model)

        # Update tag counts
        for tag in tags:
            tag_model = db.query(TagModel).filter(TagModel.name == tag).first()
            if tag_model:
                tag_model.count += 1
            else:
                db.add(TagModel(name=tag, count=1))

        count += 1

    db.commit()
    return count