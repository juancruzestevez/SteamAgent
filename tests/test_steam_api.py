import pytest
from src.api.steam_client import SteamAPI
from unittest.mock import patch, MagicMock

# --- Fixtures ---
@pytest.fixture
def steam_api(monkeypatch):
    """Crea una instancia de SteamAPI con claves falsas para evitar errores de validación."""
    monkeypatch.setenv("STEAM_API_KEY", "fake_key")
    monkeypatch.setenv("STEAM_USER_ID", "123456789")
    # Forzar la recarga de settings puede ser complicado, así que parcheamos directamente
    with patch("src.api.steam_client.settings") as mock_settings:
        mock_settings.steam_api_key = "fake_key"
        mock_settings.steam_user_id = "123456789"
        yield SteamAPI()

# --- Tests ---
def test_steam_api_initialization(steam_api):
    """Verifica que SteamAPI se inicialice con las claves correctas."""
    assert steam_api.api_key == "fake_key"
    assert steam_api.user_id == "123456789"

@patch("src.api.steam_client.requests.get")
def test_make_request_success(mock_get, steam_api):
    """Verifica que _make_request arme bien la URL y retorne JSON en caso de éxito."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": {"success": True}}
    mock_get.return_value = mock_response

    # Ejecutar
    result = steam_api._make_request("/TestEndpoint")

    # Verificar
    mock_get.assert_called_once_with(
        "https://api.steampowered.com/TestEndpoint", 
        params={"key": "fake_key"}
    )
    assert result == {"response": {"success": True}}

@patch("src.api.steam_client.requests.get")
def test_make_request_error(mock_get, steam_api):
    """Verifica que _make_request maneje errores HTTP devolviendo un dict con 'error'."""
    import requests
    mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

    result = steam_api._make_request("/TestEndpoint")

    assert "error" in result
    assert "404 Not Found" in result["error"]

def test_search_game_by_name(steam_api):
    """Prueba la lógica de búsqueda de un juego en la lista local."""
    mock_owned_games = [
        {"appid": 10, "name": "Counter-Strike"},
        {"appid": 570, "name": "Dota 2"}
    ]
    
    # Búsqueda exacta
    result = steam_api.search_game_by_name("Dota 2", mock_owned_games)
    assert result["appid"] == 570

    # Búsqueda insensible a mayúsculas
    result = steam_api.search_game_by_name("counter-strike", mock_owned_games)
    assert result["appid"] == 10

    # Juego no encontrado
    result = steam_api.search_game_by_name("Portal", mock_owned_games)
    assert result is None
