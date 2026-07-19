"""
Módulo de memoria conversacional para SteamAgent.

Proporciona una memoria de ventana deslizante que retiene los últimos
*k* intercambios del usuario para dar contexto al agente ReAct.
"""

import logging

from langchain_classic.memory import ConversationBufferWindowMemory

logger = logging.getLogger(__name__)


def create_memory(max_messages: int = 10) -> ConversationBufferWindowMemory:
    """Crea y devuelve una instancia de memoria conversacional.

    Args:
        max_messages: Cantidad máxima de intercambios a retener.

    Returns:
        Instancia de ``ConversationBufferWindowMemory`` configurada.
    """
    logger.info("Memoria conversacional creada (ventana k=%d)", max_messages)
    return ConversationBufferWindowMemory(
        k=max_messages,
        memory_key="chat_history",
        return_messages=False,
    )
