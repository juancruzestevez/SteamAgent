"""
Cerebro del agente de Steam.

Configura el LLM (multi-proveedor), las herramientas y el agente ReAct
con memoria conversacional de ventana deslizante.
"""

import logging

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent

from src.config.settings import settings
from src.agent.memory import create_memory
from src.tools.search import get_search_tools
from src.tools.steam import get_steam_tools

logger = logging.getLogger(__name__)


class SteamAgent:
    """Agente conversacional de Steam basado en ReAct con soporte multi-proveedor."""

    def __init__(self):
        # --- Selección de proveedor LLM ---
        provider = settings.get_active_provider()
        model = settings.get_active_model()
        api_key = settings.get_active_api_key()

        if provider == "groq":
            self.llm = ChatGroq(
                model=model,
                temperature=settings.llm_temperature,
                groq_api_key=api_key,
            )
        elif provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=settings.llm_temperature,
                google_api_key=api_key,
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                temperature=settings.llm_temperature,
                openai_api_key=api_key,
            )
        elif provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model,
                temperature=settings.llm_temperature,
                anthropic_api_key=api_key,
            )
        else:
            raise ValueError(f"Proveedor LLM no soportado: '{provider}'")

        logger.info("LLM configurado → proveedor=%s, modelo=%s", provider, model)
        print(f"🚀 Usando motor: {provider.capitalize()} ({model} - ReAct)")

        # --- Herramientas ---
        self.tools = get_steam_tools() + get_search_tools()

        # --- Memoria conversacional ---
        self.memory = create_memory(max_messages=settings.max_memory_messages)

        # --- Prompt ReAct ---
        self.prompt = self._create_react_prompt()

        # --- Agente ReAct ---
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            memory=self.memory,
        )

        logger.info("SteamAgent inicializado correctamente")

    def _create_react_prompt(self):
        """Genera el prompt ReAct con sección de historial de conversación."""
        template = """Eres SteamAgent, el asistente experto y amigable de videojuegos del usuario.
Tienes acceso a las siguientes herramientas:

{tools}

REGLAS DE CONTEXTO MUY IMPORTANTES:
- Si el usuario te pide ayuda, consejos, guías o tiene dudas sobre cómo avanzar y NO menciona explícitamente el nombre de un juego, debes asumir que está jugando ahora mismo.
- En ese caso, usa SIEMPRE la herramienta 'get_current_game' PRIMERO para averiguar a qué está jugando.
- Luego, si necesitas buscar en internet, usa la herramienta 'search_web' y asegúrate de INCLUIR el nombre del juego que obtuviste en tu búsqueda (ej: "[Nombre del juego] cómo vencer al dragón").

Para usar una herramienta, debes usar EXACTAMENTE este formato:

Thought: ¿Qué debo hacer? Siempre piensa en español.
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: el parámetro de entrada para la acción
Observation: el resultado de la acción
... (este proceso de Thought/Action/Action Input/Observation puede repetirse)
Thought: ¡Ya tengo la respuesta final!
Final Answer: la respuesta final para el usuario en español.

Historial de conversación:
{chat_history}

Comienza!

Pregunta: {input}
Thought: {agent_scratchpad}"""

        return PromptTemplate.from_template(template)

    def chat(self, user_message: str) -> str:
        """Procesa un mensaje del usuario y devuelve la respuesta del agente.

        Args:
            user_message: Texto del mensaje del usuario.

        Returns:
            Respuesta generada por el agente.
        """
        logger.debug("Mensaje recibido: %s", user_message)
        response = self.agent_executor.invoke({"input": user_message})
        return response["output"]
