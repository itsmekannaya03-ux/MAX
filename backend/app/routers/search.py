from fastapi import APIRouter, Query
from backend.app.schemas.search import SearchResponse
from backend.app.services.search_engine import search_engine

router = APIRouter(prefix="/api/search", tags=["Knowledge & Search"])

@router.get("", response_model=SearchResponse)
async def search_web(q: str = Query(...), limit: int = 5):
    return await search_engine.search(query=q, max_results=limit)

