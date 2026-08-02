import logging
from src.interfaces.voice_bot import SteamVoiceBot

# Silenciar algunos warnings de librerías de terceros que molestan en consola
logging.getLogger("pynput").setLevel(logging.ERROR)
logging.getLogger("whisper").setLevel(logging.ERROR)

def main():
    print("========================================")
    print("      STEAM AGENT - MODO VOZ (STT/TTS)  ")
    print("========================================")
    
    bot = SteamVoiceBot()
    bot.start()

if __name__ == "__main__":
    main()
