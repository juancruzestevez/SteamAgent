"""
Configuración centralizada de SteamAgent.

Utiliza pydantic-settings para cargar variables de entorno desde el archivo
.env y validar la configuración al inicio de la aplicación. Expone un
singleton `settings` listo para importar en cualquier módulo.
"""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global de la aplicación.

    Los valores se cargan automáticamente desde variables de entorno y/o
    desde un archivo `.env` en la raíz del proyecto.
    """

    # --- Claves de API (obligatorias) ---
    steam_api_key: str
    steam_user_id: str

    # --- Claves de LLM (opcionales individualmente) ---
    groq_api_key: str | None = None
    google_api_key: str | None = None
    # Alias: .env.example también menciona GEMINI_API_KEY
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # --- Configuración del LLM ---
    llm_provider: str = "auto"
    """'auto' intenta groq, gemini, openai, anthropic en ese orden. Forzar con 'groq', 'gemini', 'openai' o 'anthropic'."""
    llm_model_groq: str = "llama-3.3-70b-versatile"
    llm_model_gemini: str = "gemini-2.0-flash"
    llm_model_openai: str = "gpt-4o-mini"
    llm_model_anthropic: str = "claude-3-5-sonnet-latest"
    llm_temperature: float = 0.0

    # --- Caché y memoria ---
    cache_ttl_seconds: int = 300
    max_memory_messages: int = 10

    # --- Logging ---
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------
    @model_validator(mode="after")
    def _validate_llm_keys(self) -> Settings:
        """Verifica que las claves de API necesarias estén presentes según el
        proveedor de LLM seleccionado.

        También unifica ``gemini_api_key`` → ``google_api_key`` para simplificar
        el resto del código.
        """
        # Unificar GEMINI_API_KEY como alias de GOOGLE_API_KEY
        if self.google_api_key is None and self.gemini_api_key is not None:
            self.google_api_key = self.gemini_api_key

        provider = self.llm_provider.lower()

        if provider == "groq":
            if not self.groq_api_key:
                raise ValueError(
                    "Se seleccionó llm_provider='groq' pero GROQ_API_KEY no está "
                    "definida. Añádela a tu archivo .env."
                )
        elif provider == "gemini":
            if not self.google_api_key:
                raise ValueError(
                    "Se seleccionó llm_provider='gemini' pero GOOGLE_API_KEY / "
                    "GEMINI_API_KEY no está definida. Añádela a tu archivo .env."
                )
        elif provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "Se seleccionó llm_provider='openai' pero OPENAI_API_KEY no está "
                    "definida. Añádela a tu archivo .env."
                )
        elif provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError(
                    "Se seleccionó llm_provider='anthropic' pero ANTHROPIC_API_KEY no está "
                    "definida. Añádela a tu archivo .env."
                )
        elif provider == "auto":
            if not any([self.groq_api_key, self.google_api_key, self.openai_api_key, self.anthropic_api_key]):
                raise ValueError(
                    "llm_provider='auto' requiere al menos una clave de LLM "
                    "(GROQ_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY o ANTHROPIC_API_KEY). Añade al menos una a tu .env."
                )
        else:
            raise ValueError(
                f"llm_provider='{self.llm_provider}' no es válido. "
                "Usa 'auto', 'groq', 'gemini', 'openai' o 'anthropic'."
            )

        return self

    # ------------------------------------------------------------------
    # Helpers públicos
    # ------------------------------------------------------------------
    def get_active_provider(self) -> str:
        """Devuelve el proveedor de LLM activo ('groq', 'gemini', 'openai' o 'anthropic').

        En modo ``auto`` se prefiere Groq → Gemini → OpenAI → Anthropic
        según las claves disponibles.

        Returns:
            ``'groq'``, ``'gemini'``, ``'openai'`` o ``'anthropic'``.

        Raises:
            RuntimeError: Si no hay ninguna clave disponible para el proveedor.
        """
        provider = self.llm_provider.lower()

        if provider in ("groq", "gemini", "openai", "anthropic"):
            return provider

        # Modo auto: preferir groq → gemini → openai → anthropic
        if self.groq_api_key:
            return "groq"
        if self.google_api_key:
            return "gemini"
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"

        # Esto no debería alcanzarse gracias al validador, pero por seguridad:
        raise RuntimeError(
            "No se encontró ninguna clave de LLM válida para el modo 'auto'."
        )

    def get_active_model(self) -> str:
        """Devuelve el nombre del modelo correspondiente al proveedor activo."""
        provider = self.get_active_provider()
        if provider == "groq":
            return self.llm_model_groq
        elif provider == "gemini":
            return self.llm_model_gemini
        elif provider == "openai":
            return self.llm_model_openai
        elif provider == "anthropic":
            return self.llm_model_anthropic
        return self.llm_model_groq

    def get_active_api_key(self) -> str:
        """Devuelve la API key correspondiente al proveedor activo."""
        provider = self.get_active_provider()
        if provider == "groq":
            key = self.groq_api_key
        elif provider == "gemini":
            key = self.google_api_key
        elif provider == "openai":
            key = self.openai_api_key
        else:
            key = self.anthropic_api_key

        if not key:
            raise RuntimeError(
                f"No se encontró API key para el proveedor activo '{provider}'."
            )
        return key


# ======================================================================
# Singleton — importar como: from src.config.settings import settings
# ======================================================================
settings = Settings()
