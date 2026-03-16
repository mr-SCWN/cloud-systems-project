from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel


class TitleCreate(BaseModel):
    show_id: str
    content_type: Literal["Movie", "TV Show"]
    title: str
    director: Optional[str] = None
    cast_members: Optional[str] = None
    country: Optional[str] = None
    date_added: Optional[date] = None
    release_year: int
    rating: Optional[str] = None
    duration_raw: Optional[str] = None
    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None
    listed_in: Optional[str] = None
    description: str


class TitleUpdate(BaseModel):
    content_type: Optional[Literal["Movie", "TV Show"]] = None
    title: Optional[str] = None
    director: Optional[str] = None
    cast_members: Optional[str] = None
    country: Optional[str] = None
    date_added: Optional[date] = None
    release_year: Optional[int] = None
    rating: Optional[str] = None
    duration_raw: Optional[str] = None
    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None
    listed_in: Optional[str] = None
    description: Optional[str] = None