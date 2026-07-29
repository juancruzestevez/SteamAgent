import sys
from src.config.settings import settings
from src.agent.brain import SteamAgent
from src.interfaces.discord_bot import SteamDiscordBot
import logging

logging.basicConfig(level=logging.INFO)

def main():
    token = settings.discord_token
    if not token:
        print("❌ Error: No se encontró DISCORD_TOKEN en las variables de entorno.")
        print("Por favor, configura tu token en el archivo .env primero.")
        sys.exit(1)
        
    print("Inicializando el cerebro del agente...")
    agent = SteamAgent()
    
    print("Iniciando conexión con Discord...")
    bot = SteamDiscordBot(agent=agent)
    
    bot.run(token)

if __name__ == "__main__":
    main()
