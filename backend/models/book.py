"""
Book data model
"""

from typing import List, Optional
from pydantic import BaseModel


class Book(BaseModel):
    """Normalized book model"""
    id: str
    title: str
    author: str
    description: str
    categories: List[str]
    thumbnail: Optional[str] = None
    source: str
    similarity_score: Optional[float] = None
    # Additional fields for strict filtering
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    preview_link: Optional[str] = None







