"""
Tools for farmer and MSME scheme search with lazy initialization
This file must NOT initialize any services at import time
"""
from typing import Optional
import json

# Global variables - but NOT initialized yet!
_farmer_search: Optional[object] = None
_msme_search: Optional[object] = None

def get_farmer_search():
    """Lazy initialization of farmer search service"""
    global _farmer_search
    if _farmer_search is None:
        from config.settings import settings
        
        if settings.use_mock_search:
            from src.services.mock_vertex_search import MockVertexSearchService
            _farmer_search = MockVertexSearchService(settings.farmer_datastore_id or "farmer")
        else:
            from src.services.vertex_search import VertexSearchService
            _farmer_search = VertexSearchService(settings.farmer_datastore_id)
    return _farmer_search

def get_msme_search():
    """Lazy initialization of MSME search service"""
    global _msme_search
    if _msme_search is None:
        from config.settings import settings
        
        if settings.use_mock_search:
            from src.services.mock_vertex_search import MockVertexSearchService
            _msme_search = MockVertexSearchService(settings.msme_datastore_id or "msme")
        else:
            from src.services.vertex_search import VertexSearchService
            _msme_search = VertexSearchService(settings.msme_datastore_id)
    return _msme_search

def search_farmer_schemes(query: str, top_k: int = 10) -> str:
    """
    Search for farmer schemes in the Vertex AI Search datastore.
    
    Args:
        query: Search query describing farmer needs
        top_k: Maximum number of schemes to return
    
    Returns:
        JSON string containing list of relevant farmer schemes
    """
    try:
        schemes = get_farmer_search().search(query, top_k)
        return json.dumps([scheme.model_dump() for scheme in schemes], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

def search_msme_schemes(query: str, top_k: int = 10) -> str:
    """
    Search for MSME schemes in the Vertex AI Search datastore.
    
    Args:
        query: Search query describing business needs
        top_k: Maximum number of schemes to return
    
    Returns:
        JSON string containing list of relevant MSME schemes
    """
    try:
        schemes = get_msme_search().search(query, top_k)
        return json.dumps([scheme.model_dump() for scheme in schemes], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Export all tools
ALL_TOOLS = [search_farmer_schemes, search_msme_schemes]