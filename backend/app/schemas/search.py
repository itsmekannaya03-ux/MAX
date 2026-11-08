from pydantic import BaseModel
from typing import List, Optional

class SearchResultItem(BaseModel):
    title: str
    link: str
    snippet: str

class SearchResponse(BaseModel):
    query: str
    summary: str
    results: List[SearchResultItem]
    verified: bool = True

