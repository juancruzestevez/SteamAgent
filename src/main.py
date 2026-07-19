import logging

from src.config.logging_config import setup_logging
from src.agent.brain import SteamAgent

logger = logging.getLogger(__name__)


def main():
    """Punto de entrada principal de la aplicación SteamAgent."""
    setup_logging()

    print("🤖 Steam Agent Modular (Consola)")
    logger.info("SteamAgent iniciado correctamente")

    agent = SteamAgent()
    logger.info("Agente instanciado y listo para recibir consultas")

    while True:
        user_input = input("\nUsted: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            logger.info("Usuario finalizó la sesión")
            break
        logger.debug("Consulta recibida: %s", user_input)
        response = agent.chat(user_input)
        logger.debug("Respuesta generada (%d caracteres)", len(response))
        print(f"\nAgente: {response}")

if __name__ == "__main__":
    main()
