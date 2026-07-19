import logging

from ddgs import DDGS
from langchain_core.tools import Tool

logger = logging.getLogger(__name__)


def search_web_tool(query: str) -> str:
    """Realiza una búsqueda web utilizando DuckDuckGo."""
    logger.debug("Búsqueda web iniciada: '%s'", query)
    try:
        with DDGS() as search:
            results = [result for result in search.text(query, max_results=5)]
        if not results:
            logger.warning("Sin resultados para la búsqueda: '%s'", query)
            return "No se encontraron resultados relevantes en internet para esa búsqueda."
        
        logger.debug("Búsqueda completada: %d resultados para '%s'", len(results), query)
        formatResults = ''
        for r in results:
            formatResults += f"Título: {r.get('title')}\nFuente: {r.get('href')}\nResumen: {r.get('body')}\n\n"
        return formatResults
    except Exception as e:
        logger.error("Error en búsqueda web '%s': %s", query, e)
        return f"Error técnico al realizar la búsqueda web: {str(e)}"


def get_search_tools():
    """Devuelve la lista de herramientas de búsqueda web disponibles."""
    return [
        Tool(name="search_web", func=search_web_tool, description="Útil para buscar información en internet sobre juegos, guías, lore o noticias actuales.")
    ]