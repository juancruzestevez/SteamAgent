"""
Configuración centralizada del sistema de logging para SteamAgent.

Proporciona una función para configurar el logger raíz con un formato
profesional y silenciar loggers de terceros ruidosos.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura y devuelve el logger raíz del proyecto.

    Establece un formato consistente para todos los mensajes de log
    y reduce el ruido de librerías de terceros configurándolas en WARNING.

    Args:
        level: Nivel de logging deseado (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        El logger raíz ya configurado.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Formato profesional: timestamp | nivel | módulo | mensaje
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configurar el logger raíz
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,
    )

    # Silenciar loggers ruidosos de terceros
    noisy_loggers = [
        "httpx",
        "urllib3",
        "requests",
        "langchain",
        "langchain_core",
        "langchain_google_genai",
        "openai",
        "httpcore",
        "google",
        "google.generativeai",
        "grpc",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logger = logging.getLogger("steam_agent")
    logger.debug("Sistema de logging inicializado (nivel=%s)", level.upper())
    return logger
