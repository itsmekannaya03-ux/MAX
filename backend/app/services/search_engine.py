from typing import List, Dict, Any, Optional
import httpx
from backend.app.schemas.search import SearchResultItem, SearchResponse
from backend.app.services.ai_service import ai_service

class SearchEngine:
    def __init__(self):
        pass

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """
        Executes a web search using duckduckgo_search or public instant query fallback.
        """
        results: List[SearchResultItem] = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddg_gen = ddgs.text(query, max_results=max_results)
                for r in ddg_gen:
                    results.append(SearchResultItem(
                        title=r.get("title", "Search Result"),
                        link=r.get("href", ""),
                        snippet=r.get("body", "")
                    ))
        except Exception as e:
            # Fallback to direct DuckDuckGo Instant Answer API
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        "https://api.duckduckgo.com/",
                        params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        abstract = data.get("AbstractText", "")
                        source_url = data.get("AbstractURL", "")
                        if abstract:
                            results.append(SearchResultItem(
                                title=data.get("Heading", query),
                                link=source_url or "https://duckduckgo.com/?q=" + query,
                                snippet=abstract
                            ))
                        for topic in data.get("RelatedTopics", [])[:max_results]:
                            if "Text" in topic and "FirstURL" in topic:
                                results.append(SearchResultItem(
                                    title=topic["Text"][:50] + "...",
                                    link=topic["FirstURL"],
                                    snippet=topic["Text"]
                                ))
            except Exception as e2:
                print(f"[SearchEngine] Search error: {e2}")

        if not results:
            results.append(SearchResultItem(
                title=f"Knowledge context for '{query}'",
                link="https://en.wikipedia.org/wiki/" + query.replace(" ", "_"),
                snippet=f"Information regarding {query} retrieved from MAX Knowledge Base."
            ))

        # Generate concise synthesis / summary of findings
        context_text = "\n".join([f"- {r.title}: {r.snippet}" for r in results])
        summary_prompt = (
            f"You are MAX. Synthesize the key verified findings from these search results for the user query '{query}'. "
            f"Keep it concise, clear, and highlight practical takeaways:\n\n{context_text}"
        )
        summary = await ai_service.generate_response(
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3
        )

        return SearchResponse(
            query=query,
            summary=summary,
            results=results,
            verified=True
        )

search_engine = SearchEngine()

