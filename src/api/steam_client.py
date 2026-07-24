import logging
from typing import Dict, List, Optional

import requests

from src.cache import cached
from src.config import settings

logger = logging.getLogger(__name__)


class SteamAPI:
    def __init__(self):
        self.api_key = settings.steam_api_key
        self.user_id = settings.steam_user_id
        self.base_url = "https://api.steampowered.com"
        
        if not self.api_key:
            raise ValueError("❌ STEAM_API_KEY no encontrada. Configura tu archivo .env")
        if not self.user_id:
            raise ValueError("❌ STEAM_USER_ID no encontrado. Configura tu archivo .env")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Realiza una petición GET a la API de Steam."""
        if params is None:
            params = {}
        params['key'] = self.api_key
        logger.debug("Realizando petición GET a %s", endpoint)
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            logger.debug("Respuesta exitosa de %s (status %d)", endpoint, response.status_code)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Error en petición a %s: %s", endpoint, e)
            return {"error": f"Error al conectar con Steam API: {str(e)}"}
    
    @cached(ttl=60, key_prefix='steam_')
    def get_player_summary(self, steam_id: Optional[str] = None) -> Dict:
        """Obtiene el resumen del perfil de un jugador."""
        target_id = steam_id or self.user_id
        endpoint = "/ISteamUser/GetPlayerSummaries/v2/"
        params = {"steamids": target_id}
        logger.debug("Obteniendo resumen del jugador %s", target_id)
        result = self._make_request(endpoint, params)
        if "error" in result: return result
        players = result.get("response", {}).get("players", [])
        if not players:
            logger.error("No se encontró información del jugador %s", target_id)
            return {"error": "No se encontró información del jugador"}
        return players[0]
    
    @cached(ttl=300, key_prefix='steam_')
    def get_owned_games(self, steam_id: Optional[str] = None, include_free: bool = False) -> Dict:
        """Obtiene la lista de juegos del usuario."""
        target_id = steam_id or self.user_id
        endpoint = "/IPlayerService/GetOwnedGames/v1/"
        params = {
            "steamid": target_id,
            "include_appinfo": 1,
            "include_played_free_games": 1 if include_free else 0
        }
        logger.debug("Obteniendo juegos del usuario %s", target_id)
        result = self._make_request(endpoint, params)
        return result.get("response", {}) if "error" not in result else result
    
    def get_player_achievements(self, app_id: int, steam_id: Optional[str] = None) -> Dict:
        """Obtiene los logros de un juego para el jugador."""
        target_id = steam_id or self.user_id
        endpoint = "/ISteamUserStats/GetPlayerAchievements/v1/"
        params = {"steamid": target_id, "appid": app_id}
        logger.debug("Obteniendo logros del juego %d para %s", app_id, target_id)
        result = self._make_request(endpoint, params)
        return result.get("playerstats", {}) if "error" not in result else result
    
    def get_user_stats_for_game(self, app_id: int, steam_id: Optional[str] = None) -> Dict:
        """Obtiene las estadísticas del usuario para un juego."""
        target_id = steam_id or self.user_id
        endpoint = "/ISteamUserStats/GetUserStatsForGame/v2/"
        params = {"steamid": target_id, "appid": app_id}
        logger.debug("Obteniendo stats del juego %d para %s", app_id, target_id)
        result = self._make_request(endpoint, params)
        return result.get("playerstats", {}) if "error" not in result else result
    
    @cached(ttl=300, key_prefix='steam_')
    def get_recently_played_games(self, steam_id: Optional[str] = None) -> Dict:
        """Obtiene los juegos jugados recientemente."""
        target_id = steam_id or self.user_id
        endpoint = "/IPlayerService/GetRecentlyPlayedGames/v1/"
        params = {"steamid": target_id, "count": 10}
        logger.debug("Obteniendo juegos recientes del usuario %s", target_id)
        result = self._make_request(endpoint, params)
        return result.get("response", {}) if "error" not in result else result
    
    def search_game_by_name(self, game_name: str, owned_games: list) -> dict | None:
        """Busca un juego por nombre en la lista de juegos del usuario.

        Realiza una búsqueda insensible a mayúsculas/minúsculas.

        Args:
            game_name: Nombre del juego a buscar.
            owned_games: Lista de juegos devuelta por get_owned_games.

        Returns:
            Diccionario con la info del juego si se encuentra, None en caso contrario.
        """
        game_name_lower = game_name.lower()
        for game in owned_games:
            if game_name_lower in game.get("name", "").lower():
                return game
        return None

    @cached(ttl=3600)
    def search_store_game(self, term: str) -> dict:
        """Busca un juego por nombre en la tienda pública de Steam.
        
        Útil para obtener el appid de un juego que el usuario no posee necesariamente.
        
        Args:
            term: Término de búsqueda (ej: 'Elden Ring')
            
        Returns:
            Respuesta JSON de la tienda de Steam.
        """
        url = "https://store.steampowered.com/api/storesearch/"
        try:
            response = requests.get(url, params={"term": term, "l": "spanish", "cc": "AR"})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Error en storesearch para '%s': %s", term, e)
            return {"error": str(e)}

    @cached(ttl=3600)
    def get_store_app_details(self, appid: int) -> dict:
        """Obtiene los detalles públicos de la tienda para un juego específico.
        
        Incluye precio, descripción, plataformas y categorías.
        
        Args:
            appid: ID del juego en Steam.
            
        Returns:
            Respuesta JSON con los detalles de la tienda.
        """
        url = "https://store.steampowered.com/api/appdetails"
        try:
            response = requests.get(url, params={"appids": appid, "l": "spanish", "cc": "AR"})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Error en appdetails para appid %s: %s", appid, e)
            return {"error": str(e)}
