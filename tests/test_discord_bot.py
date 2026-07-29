import pytest
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from src.interfaces.discord_bot import SteamDiscordBot

@pytest.mark.asyncio
@patch("discord.Client.user", new_callable=PropertyMock)
async def test_discord_bot_ignores_itself(mock_user):
    # Setup
    agent_mock = MagicMock()
    bot = SteamDiscordBot(agent=agent_mock)
    
    # Mock bot user
    bot_user = MagicMock()
    mock_user.return_value = bot_user
    
    # Mock message from the bot itself
    message = MagicMock()
    message.author = bot_user
    
    await bot.on_message(message)
    
    # Agent shouldn't be called
    agent_mock.chat.assert_not_called()

@pytest.mark.asyncio
@patch("discord.Client.user", new_callable=PropertyMock)
async def test_discord_bot_replies_when_mentioned(mock_user):
    agent_mock = MagicMock()
    # Mock synchronous chat response
    agent_mock.chat.return_value = "Hola desde SteamAgent"
    
    bot = SteamDiscordBot(agent=agent_mock)
    
    bot_user = MagicMock()
    bot_user.id = 12345
    mock_user.return_value = bot_user
    
    message = MagicMock()
    message.author = MagicMock() # Not the bot
    message.mentions = [bot_user]
    message.content = "<@12345> recomiendame un juego"
    message.reply = AsyncMock()
    
    # Mock the async context manager for typing
    typing_mock = MagicMock()
    typing_mock.__aenter__ = AsyncMock(return_value=None)
    typing_mock.__aexit__ = AsyncMock(return_value=None)
    message.channel.typing.return_value = typing_mock
    
    # Execute the event
    await bot.on_message(message)
    
    # Assert chat was called with cleaned content
    agent_mock.chat.assert_called_once_with("recomiendame un juego")
    
    # Assert bot replied
    message.reply.assert_called_once_with("Hola desde SteamAgent")
