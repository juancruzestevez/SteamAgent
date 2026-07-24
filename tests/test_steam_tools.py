import pytest
from unittest.mock import patch, MagicMock

# Importamos las herramientas a testear
from src.tools.steam import get_profile_tool, get_games_tool, get_current_game_tool, get_store_info_tool

# --- Tests ---
@patch("src.tools.steam._get_steam_api")
def test_get_profile_tool_success(mock_get_api):
    """Verifica que el perfil se formatee correctamente como texto."""
    # Mock de la API
    mock_api = MagicMock()
    mock_api.get_player_summary.return_value = {
        "personaname": "Gamer123",
        "personastate": 1,
        "profileurl": "https://steamcommunity.com/id/gamer123",
        "loccountrycode": "AR"
    }
    mock_get_api.return_value = mock_api

    # Ejecutar tool
    result = get_profile_tool("mi perfil")

    # Verificar que el texto de salida contenga la información formateada
    assert "Gamer123" in result
    assert "🟢 Conectado" in result
    assert "AR" in result

@patch("src.tools.steam._get_steam_api")
def test_get_profile_tool_error(mock_get_api):
    """Verifica que maneje correctamente un error devuelto por la API."""
    mock_api = MagicMock()
    mock_api.get_player_summary.return_value = {"error": "Usuario privado"}
    mock_get_api.return_value = mock_api

    result = get_profile_tool("mi perfil")
    assert "Error: Usuario privado" in result

@patch("src.tools.steam._get_steam_api")
def test_get_games_tool_success(mock_get_api):
    """Verifica que los juegos se ordenen por tiempo y se formateen las horas."""
    mock_api = MagicMock()
    mock_api.get_owned_games.return_value = {
        "game_count": 2,
        "games": [
            {"name": "Juego Nuevo", "playtime_forever": 120},  # 2 horas
            {"name": "Juego Viejo", "playtime_forever": 600}   # 10 horas
        ]
    }
    mock_get_api.return_value = mock_api

    result = get_games_tool("mis juegos")

    # El juego viejo debería aparecer primero por tener más horas
    assert "Total de juegos: 2" in result
    assert "1. Juego Viejo - 10.0 horas" in result
    assert "2. Juego Nuevo - 2.0 horas" in result

@patch("src.tools.steam._get_steam_api")
def test_get_current_game_tool_playing(mock_get_api):
    """Verifica que devuelva el juego si el usuario está jugando."""
    mock_api = MagicMock()
    mock_api.get_player_summary.return_value = {
        "gameextrainfo": "Counter-Strike 2",
        "gameid": "730"
    }
    mock_get_api.return_value = mock_api

    result = get_current_game_tool("")
    assert "Counter-Strike 2" in result
    assert "730" in result

@patch("src.tools.steam._get_steam_api")
def test_get_current_game_tool_not_playing(mock_get_api):
    """Verifica que indique que no está jugando a nada."""
    mock_api = MagicMock()
    # Sin las keys gameextrainfo
    mock_api.get_player_summary.return_value = {
        "personaname": "Gamer123"
    }
    mock_get_api.return_value = mock_api

    result = get_current_game_tool("")
    assert "no está jugando a ningún juego" in result

@patch("src.tools.steam._get_steam_api")
def test_get_store_info_tool_success(mock_get_api):
    """Verifica que recupere la información de la tienda correctamente."""
    mock_api = MagicMock()
    # Mock search
    mock_api.search_store_game.return_value = {
        "items": [{"id": 1091500}]
    }
    # Mock details
    mock_api.get_store_app_details.return_value = {
        "1091500": {
            "success": True,
            "data": {
                "name": "Cyberpunk 2077",
                "short_description": "Un RPG de acción...",
                "price_overview": {
                    "final_formatted": "ARS$ 2000",
                    "discount_percent": 50
                },
                "platforms": {"windows": True, "mac": False, "linux": False},
                "categories": [{"description": "Un jugador"}]
            }
        }
    }
    mock_get_api.return_value = mock_api

    result = get_store_info_tool("Cyberpunk")
    assert "Cyberpunk 2077" in result
    assert "ARS$ 2000 (-50%)" in result
    assert "Windows" in result
    assert "Un jugador" in result
