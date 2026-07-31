import pytest
from unittest.mock import patch, MagicMock
from src.tools.vision import take_screenshot_and_analyze_tool

@patch("src.tools.vision.mss")
@patch("src.tools.vision.settings")
def test_take_screenshot_success(mock_settings, mock_mss):
    # Mock settings
    mock_settings.get_active_provider.return_value = "openai"
    mock_settings.get_active_model.return_value = "gpt-4o-mini"
    mock_settings.get_active_api_key.return_value = "fake_key"
    
    # Mock MSS (screenshot library)
    mock_sct = MagicMock()
    mock_sct.monitors = [{}, {"width": 1920, "height": 1080}]
    
    mock_img = MagicMock()
    mock_img.size = (1920, 1080)
    mock_img.bgra = b"fake_bgra_bytes_that_are_long_enough_hopefully" * 1000
    mock_sct.grab.return_value = mock_img
    
    mock_mss.return_value.__enter__.return_value = mock_sct
    
    # Mock PIL Image (evitamos errores al decodificar los bytes falsos)
    with patch("src.tools.vision.Image.frombytes") as mock_pil:
        mock_pil_img = MagicMock()
        mock_pil_img.save = MagicMock()
        mock_pil.return_value = mock_pil_img
        
        # Mock ChatOpenAI invocation (imported dynamically)
        with patch("langchain_openai.ChatOpenAI") as mock_chat_cls:
            mock_chat_instance = MagicMock()
            mock_chat_instance.invoke.return_value = MagicMock(content="Veo al jefe final con poca vida.")
            mock_chat_cls.return_value = mock_chat_instance
            
            result = take_screenshot_and_analyze_tool("Como lo mato?")
            
            assert "Análisis" in result
            assert "jefe final" in result
