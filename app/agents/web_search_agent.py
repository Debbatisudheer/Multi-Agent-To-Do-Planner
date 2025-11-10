# app/agents/web_search_agent.py
from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> dict:
    """
    Simple web search using DuckDuckGo.
    Returns a dict with a list of {title, href, body} items.
    No API key required.
    """
    if not query or not query.strip():
        return {"query": query, "results": [], "error": "Empty query"}

    try:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=max_results)
            normalized = []
            for r in results or []:
                normalized.append({
                    "title": r.get("title"),
                    "url": r.get("href") or r.get("url"),
                    "snippet": r.get("body"),
                })
            return {"query": query, "results": normalized}
    except Exception as e:
        return {"query": query, "results": [], "error": str(e)}
