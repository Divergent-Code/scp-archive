"""Data models for SCP Archive entries."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class SCPEntry:
    """Represents an SCP article, tale, or GOI format."""
    id: str
    title: str
    url: str
    object_class: Optional[str] = None
    secondary_class: Optional[str] = None
    containment_procedures: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    author: Optional[str] = None
    rating: int = 0
    created_date: Optional[str] = None
    entry_type: str = "scp"
    related_scps: list[str] = field(default_factory=list)
    content_html: str = ""
    content_md: str = ""
    series: Optional[int] = None
    image_urls: list[str] = field(default_factory=list)
    license: Optional[str] = None          # e.g. "CC BY-SA 3.0"
    source_url: Optional[str] = None       # canonical URL from licensebox

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "SCPEntry":
        return cls(**data)