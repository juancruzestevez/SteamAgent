import logging

from langchain_core.tools import Tool
from src.api.steam_client import SteamAPI

logger = logging.getLogger(__name__)

_steam_api: SteamAPI | None = None


def _get_steam_api() -> SteamAPI:
    """Inicialización perezosa de la instancia de SteamAPI."""
    global _steam_api
    if _steam_api is None:
        _steam_api = SteamAPI()
    return _steam_api


def get_profile_tool(query: str) -> str:
    """Obtiene información del perfil de Steam."""
    logger.debug("Herramienta invocada: get_steam_profile")
    result = _get_steam_api().get_player_summary()
    if "error" in result:
        logger.error("Error al obtener perfil: %s", result['error'])
        return f"Error: {result['error']}"
    logger.debug("Perfil obtenido: %s", result.get('personaname', 'N/A'))
    return f"""Información del Perfil:
- Nombre: {result.get('personaname', 'N/A')}
- Estado: {'🟢 Conectado' if result.get('personastate') == 1 else '⚫ Desconectado'}
- Perfil: {result.get('profileurl', 'N/A')}
- País: {result.get('loccountrycode', 'N/A')}"""

def get_games_tool(query: str) -> str:
    """Obtiene la lista de juegos del usuario."""
    logger.debug("Herramienta invocada: get_steam_games")
    result = _get_steam_api().get_owned_games()
    if "error" in result:
        logger.error("Error al obtener juegos: %s", result['error'])
        return f"Error: {result['error']}"
    games = sorted(result.get('games', []), key=lambda x: x.get('playtime_forever', 0), reverse=True)
    top_games = games[:10]
    logger.debug("Juegos obtenidos: %d total, mostrando top 10", result.get('game_count', 0))
    response = f"Total de juegos: {result.get('game_count', 0)}\n\nTop 10 juegos más jugados:\n"
    for i, game in enumerate(top_games, 1):
        hours = game.get('playtime_forever', 0) / 60
        response += f"{i}. {game.get('name', 'N/A')} - {hours:.1f} horas\n"
    return response

def get_achievements_tool(game_name: str) -> str:
    """Obtiene logros de un juego específico."""
    logger.debug("Herramienta invocada: get_steam_achievements (juego='%s')", game_name)
    owned_games = _get_steam_api().get_owned_games()
    if "error" in owned_games:
        logger.error("Error al obtener juegos para logros: %s", owned_games['error'])
        return f"Error: {owned_games['error']}"
    game_found = _get_steam_api().search_game_by_name(game_name, owned_games.get('games', []))
    if not game_found:
        logger.warning("Juego no encontrado para logros: '%s'", game_name)
        return f"No se encontró el juego '{game_name}'"
    
    result = _get_steam_api().get_player_achievements(game_found['appid'])
    if "error" in result:
        logger.error("Error al obtener logros de '%s': %s", game_name, result['error'])
        return f"Error: {result['error']}"
    
    achievements = result.get('achievements', [])
    unlocked = sum(1 for ach in achievements if ach.get('achieved') == 1)
    total = len(achievements)
    logger.debug("Logros de %s: %d/%d desbloqueados", game_found['name'], unlocked, total)
    response = f"Logros de {game_found['name']}: {unlocked}/{total}\n"
    recent = sorted([a for a in achievements if a.get('achieved') == 1], 
                    key=lambda x: x.get('unlocktime', 0), reverse=True)[:5]
    for ach in recent:
        response += f"✅ {ach.get('name', 'N/A')}\n"
    return response

def get_current_game_tool(query: str = "") -> str:
    """Obtiene el juego que el usuario está jugando actualmente."""
    logger.debug("Herramienta invocada: get_current_game")
    result = _get_steam_api().get_player_summary()
    
    if "error" in result:
        logger.error("Error al obtener perfil para el juego actual: %s", result['error'])
        return f"Error: {result['error']}"
    
    game_title = result.get('gameextrainfo')
    game_id = result.get('gameid')
    
    if game_title:
        logger.debug("Juego actual detectado: %s", game_title)
        return f"🎮 El usuario está jugando actualmente a: '{game_title}' (AppID: {game_id}). Usa esta información para darle contexto."
    
    logger.debug("El usuario no está jugando a nada")
    return "El usuario no está jugando a ningún juego en este momento o su perfil está oculto."


def get_store_info_tool(query: str) -> str:
    """Busca información de un juego en la tienda de Steam."""
    logger.debug("Herramienta invocada: get_store_info, query: %s", query)
    api = _get_steam_api()
    
    search_result = api.search_store_game(query)
    if "error" in search_result:
        return f"Error al buscar en la tienda: {search_result['error']}"
        
    items = search_result.get("items", [])
    if not items:
        return f"No se encontró el juego '{query}' en la tienda de Steam."
        
    # Tomamos el primer resultado que tenga appid
    best_match = items[0]
    appid = best_match.get("id")
    
    if not appid:
        return f"Se encontraron resultados pero no se pudo determinar el AppID para '{query}'."
    
    details_result = api.get_store_app_details(appid)
    if "error" in details_result:
        return f"Error al obtener detalles del juego: {details_result['error']}"
        
    app_data = details_result.get(str(appid), {})
    if not app_data.get("success"):
        return "No se pudo obtener la información detallada del juego en la tienda."
        
    data = app_data.get("data", {})
    name = data.get("name", "Desconocido")
    desc = data.get("short_description", "")
    
    price_overview = data.get("price_overview")
    if price_overview:
        price = price_overview.get("final_formatted", "Gratis/No disponible")
        discount = price_overview.get("discount_percent", 0)
        price_str = f"{price} (-{discount}%)" if discount > 0 else price
    else:
        price_str = "Gratis o no disponible"
        
    platforms = data.get("platforms", {})
    plats = []
    if platforms.get("windows"): plats.append("Windows")
    if platforms.get("mac"): plats.append("Mac")
    if platforms.get("linux"): plats.append("Linux")
    
    categories = [cat.get("description") for cat in data.get("categories", [])][:5]
    
    return (
        f"🎮 {name}\n"
        f"💰 Precio: {price_str}\n"
        f"💻 Plataformas: {', '.join(plats)}\n"
        f"🏷️ Categorías: {', '.join(categories)}\n\n"
        f"📝 Descripción: {desc}"
    )


def get_steam_tools():
    """Devuelve la lista de herramientas de Steam disponibles para el agente."""
    return [
        Tool(name="get_steam_profile", func=get_profile_tool, description="Obtiene información del perfil del usuario de Steam."),
        Tool(name="get_steam_games", func=get_games_tool, description="Obtiene la lista de juegos y horas jugadas del usuario."),
        Tool(name="get_steam_achievements", func=get_achievements_tool, description="Obtiene logros de un juego. Input: nombre exacto del juego."),
        Tool(name="get_current_game", func=get_current_game_tool, description="Verifica si el usuario está jugando a algún juego en este momento y devuelve su nombre."),
        Tool(name="get_store_info", func=get_store_info_tool, description="Busca un juego en la Tienda de Steam para ver su precio, descripción y si tiene descuentos. Input: nombre del juego.")
    ]
