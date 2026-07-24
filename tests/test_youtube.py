import pytest
from unittest.mock import patch, MagicMock
from src.tools.youtube import get_youtube_transcript_tool

@patch("src.tools.youtube.DDGS")
@patch("src.tools.youtube.YouTubeTranscriptApi")
def test_get_youtube_transcript_success(mock_yt, mock_ddgs):
    # Mock DDGS
    mock_search = MagicMock()
    mock_search.text.return_value = [
        {"href": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "Never Gonna Give You Up"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_search

    # Mock YT API
    mock_yt.get_transcript.return_value = [
        {"text": "Never gonna give you up,"},
        {"text": "never gonna let you down"}
    ]

    result = get_youtube_transcript_tool("Rick Astley")

    assert "Never Gonna Give You Up" in result
    assert "Never gonna give you up, never gonna let you down" in result
    assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in result

@patch("src.tools.youtube.DDGS")
@patch("src.tools.youtube.YouTubeTranscriptApi")
def test_get_youtube_transcript_no_subs(mock_yt, mock_ddgs):
    from youtube_transcript_api import TranscriptsDisabled
    mock_search = MagicMock()
    mock_search.text.return_value = [
        {"href": "https://youtu.be/test1234", "title": "Video sin subs"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_search

    mock_yt.get_transcript.side_effect = TranscriptsDisabled("test1234")

    result = get_youtube_transcript_tool("Test")
    assert "están desactivados por el autor" in result
