import pytest
from unittest.mock import patch, MagicMock

# Importamos las herramientas a testear
from src.tools.steam import get_profile_tool, get_games_tool, get_current_game_tool

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
