import logging
import asyncio
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class SteamDiscordBot(commands.Bot):
    """Bot de Discord para interactuar con SteamAgent."""
    
    def __init__(self, agent, *args, **kwargs):
        # Configuramos los intents requeridos para leer mensajes
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents, *args, **kwargs)
        self.agent = agent
        
    async def setup_hook(self):
        logger.info("Bot de Discord inicializado y sincronizando...")
        
    async def on_ready(self):
        logger.info("Conectado a Discord como %s (ID: %s)", self.user, self.user.id)
        print(f"👾 Bot online en Discord: {self.user}")
        
    async def on_message(self, message: discord.Message):
        # No respondernos a nosotros mismos
        if message.author == self.user:
            return
            
        # Solo responder si el bot es mencionado explícitamente
        if self.user in message.mentions:
            # Limpiamos el texto de la mención (<@ID>)
            clean_content = message.content.replace(f"<@{self.user.id}>", "").strip()
            
            if not clean_content:
                await message.reply("¡Hola! ¿En qué puedo ayudarte con tus juegos hoy? 🎮")
                return
                
            try:
                # Mostramos que el bot está "escribiendo..." en Discord
                async with message.channel.typing():
                    # El agente ReAct de LangChain bloquea el hilo, así que lo ejecutamos 
                    # asíncronamente en un hilo separado para no congelar el bot de Discord.
                    response = await asyncio.to_thread(self.agent.chat, clean_content)
                    
                # Mandar la respuesta al canal
                # Si es muy larga (Discord límite 2000 chars), podríamos partirla, pero asumimos texto moderado
                if len(response) > 2000:
                    response = response[:1995] + "..."
                    
                await message.reply(response)
                
            except Exception as e:
                logger.error("Error al procesar el mensaje en Discord: %s", e)
                await message.reply("Uy, ocurrió un error técnico en mis circuitos y no pude responder tu pregunta. 🔧")
