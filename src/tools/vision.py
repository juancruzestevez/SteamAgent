import logging
import base64
from io import BytesIO
from mss import mss
from PIL import Image
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from src.config.settings import settings

logger = logging.getLogger(__name__)

def take_screenshot_and_analyze_tool(query: str = "") -> str:
    """Toma una captura de la pantalla actual y la analiza usando el modelo de IA visual."""
    try:
        logger.debug("Tomando captura de pantalla...")
        with mss() as sct:
            # Tomamos la pantalla principal (monitor 1)
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
        # Reducir resolución para ahorrar tokens y mejorar la velocidad
        img.thumbnail((1280, 720))
        
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=80)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Enviar al LLM Visual
        provider = settings.get_active_provider()
        api_key = settings.get_active_api_key()
        model_name = settings.get_active_model()
        
        logger.debug("Analizando imagen con %s...", provider)
        vision_llm = None
        
        # Instanciamos temporalmente el LLM para soportar el mensaje multimodal
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            vision_llm = ChatOpenAI(model=model_name, openai_api_key=api_key, max_tokens=300)
        elif provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            vision_llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, max_tokens=300)
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            vision_llm = ChatAnthropic(model=model_name, anthropic_api_key=api_key, max_tokens=300)
        else:
            return f"El proveedor actual '{provider}' podría no soportar el paso de imágenes en este formato."
            
        prompt = (
            "Eres el módulo de visión de SteamAgent. Acabo de tomar una captura de pantalla del monitor del usuario. "
            f"El usuario necesita ayuda en su juego con esta duda: '{query}'\n\n"
            "Describe lo que ves en la pantalla con el mayor nivel de detalle útil para resolver su problema. "
            "Menciona qué juego parece ser, el entorno, enemigos, HUD, texto en pantalla, u obstáculos."
        )
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"},
                },
            ]
        )
        
        # Invocamos al modelo de visión
        response = vision_llm.invoke([message])
        
        return f"Análisis de lo que el usuario está viendo ahora mismo:\n{response.content}"
        
    except Exception as e:
        logger.error("Error en módulo de visión: %s", e)
        return f"Error técnico al analizar la pantalla: {str(e)}"

def get_vision_tools():
    """Devuelve las herramientas de visión."""
    return [
        Tool(
            name="analyze_screen",
            func=take_screenshot_and_analyze_tool,
            description="Útil para 'ver' la pantalla del usuario de forma autónoma. Úsala CUANDO el usuario diga que se quedó trabado, pida que 'mires' su juego o no sepa cómo avanzar en el lugar donde está. Input: la pregunta o duda específica del usuario."
        )
    ]
