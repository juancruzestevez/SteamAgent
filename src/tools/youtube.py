import logging
import re
from urllib.parse import urlparse, parse_qs
from ddgs import DDGS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_core.tools import Tool

logger = logging.getLogger(__name__)

def get_youtube_transcript_tool(query: str) -> str:
    """Busca un video en YouTube y devuelve su transcripción."""
    logger.debug("Buscando video de YouTube para: %s", query)
    try:
        # Buscar el video en DDG
        # Usamos site:youtube.com para forzar que los resultados sean videos de YouTube
        with DDGS() as search:
            results = list(search.text(f"{query} site:youtube.com", max_results=3))
            
        if not results:
            return "No se encontraron videos de YouTube para esa búsqueda."
            
        # Filtrar solo links de youtube válidos
        video_url = None
        title = None
        video_id = None
        
        for r in results:
            href = r.get("href", "")
            if "youtube.com/watch" in href or "youtu.be/" in href:
                video_url = href
                title = r.get("title")
                
                # Extraer ID del video
                if "youtube.com/watch" in href:
                    parsed_url = urlparse(href)
                    v = parse_qs(parsed_url.query).get("v")
                    if v:
                        video_id = v[0]
                elif "youtu.be/" in href:
                    video_id = href.split("youtu.be/")[1].split("?")[0]
                
                if video_id:
                    break
        
        if not video_id:
            return "No se encontró un enlace válido de YouTube en los primeros resultados."
            
        logger.debug("Video encontrado: %s (ID: %s)", title, video_id)
        
        # Obtener transcripción (intentar español primero, luego inglés)
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        except TranscriptsDisabled:
            return f"Video encontrado ('{title}'), pero los subtítulos/transcripción están desactivados por el autor."
        except NoTranscriptFound:
            return f"Video encontrado ('{title}'), pero no hay transcripción disponible en español ni inglés."
            
        # Unir texto
        full_text = " ".join([t['text'].replace('\n', ' ') for t in transcript_list])
        # Limpiar texto de espacios extra
        full_text = re.sub(' +', ' ', full_text)
        
        # Limitar a 15000 caracteres para no desbordar el contexto del LLM
        max_chars = 15000
        truncated = False
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars]
            truncated = True
            
        response = f"Video encontrado: {title}\nURL: {video_url}\n\nTranscripción:\n{full_text}"
        if truncated:
            response += "\n\n[Transcripción truncada por longitud...]"
            
        return response
        
    except Exception as e:
        logger.error("Error al procesar video de YouTube: %s", e)
        return f"Error al obtener la transcripción del video: {str(e)}"

def get_youtube_tools():
    """Devuelve las herramientas relacionadas con YouTube."""
    return [
        Tool(
            name="get_youtube_guide",
            func=get_youtube_transcript_tool,
            description="Útil para buscar guías en formato video (YouTube) y leer exactamente lo que dice el youtuber (transcripción). Úsala para obtener pasos detallados de un gameplay o solución. Input: El tema a buscar (ej: 'Elden ring Margit boss fight guide')."
        )
    ]
