import os
import sys
import threading
import logging
from pathlib import Path
from dotenv import dotenv_values, set_key

logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class BridgeAPI:
    """API puente expuesta a JavaScript en PyWebView."""

    def __init__(self):
        self._window = None
        self._voice_thread = None
        self._voice_bot_instance = None
        self._is_running = False

    def set_window(self, window):
        self._window = window

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def close_window(self):
        if self._window:
            self._window.destroy()

    def get_config(self) -> dict:
        """Obtiene la configuración actual del archivo .env y el perfil de Steam."""
        if not ENV_PATH.exists():
            return {
                "llm_provider": "openai",
                "openai_api_key": "",
                "groq_api_key": "",
                "google_api_key": "",
                "anthropic_api_key": "",
                "steam_api_key": "",
                "steam_user_id": "",
                "discord_token": "",
                "steam_profile": None,
                "is_running": self._is_running
            }

        env_vars = dotenv_values(ENV_PATH)
        provider = env_vars.get("LLM_PROVIDER", "openai").lower()
        
        # Intentar obtener info de perfil de Steam si están las credenciales
        steam_profile = self._fetch_steam_profile(
            env_vars.get("STEAM_API_KEY", ""),
            env_vars.get("STEAM_USER_ID", "")
        )

        return {
            "llm_provider": provider,
            "openai_api_key": env_vars.get("OPENAI_API_KEY", ""),
            "groq_api_key": env_vars.get("GROQ_API_KEY", ""),
            "google_api_key": env_vars.get("GOOGLE_API_KEY", ""),
            "anthropic_api_key": env_vars.get("ANTHROPIC_API_KEY", ""),
            "steam_api_key": env_vars.get("STEAM_API_KEY", ""),
            "steam_user_id": env_vars.get("STEAM_USER_ID", ""),
            "discord_token": env_vars.get("DISCORD_TOKEN", ""),
            "steam_profile": steam_profile,
            "is_running": self._is_running
        }

    def _fetch_steam_profile(self, api_key: str, user_id: str):
        if not api_key or not user_id:
            return None
        try:
            from src.api.steam_client import SteamAPI
            api = SteamAPI()
            summary = api.get_player_summary(user_id)
            if summary and "personaname" in summary:
                current_game = summary.get("gameextrainfo", "Ninguno (En línea)")
                return {
                    "personaname": summary.get("personaname", "Usuario Steam"),
                    "avatar": summary.get("avatarfull", summary.get("avatar", "")),
                    "current_game": current_game,
                    "profileurl": summary.get("profileurl", "")
                }
        except Exception as e:
            logger.debug("No se pudo obtener resumen de Steam: %s", e)
        return None

    def save_config(self, data: dict) -> dict:
        """Guarda los valores ingresados en el archivo .env."""
        try:
            if not ENV_PATH.exists():
                ENV_PATH.touch()

            provider = str(data.get("llm_provider", "openai")).lower()
            set_key(str(ENV_PATH), "LLM_PROVIDER", provider)

            if "openai_api_key" in data:
                set_key(str(ENV_PATH), "OPENAI_API_KEY", str(data.get("openai_api_key", "")).strip())
            if "groq_api_key" in data:
                set_key(str(ENV_PATH), "GROQ_API_KEY", str(data.get("groq_api_key", "")).strip())
            if "google_api_key" in data:
                set_key(str(ENV_PATH), "GOOGLE_API_KEY", str(data.get("google_api_key", "")).strip())
            if "anthropic_api_key" in data:
                set_key(str(ENV_PATH), "ANTHROPIC_API_KEY", str(data.get("anthropic_api_key", "")).strip())
            if "steam_api_key" in data:
                set_key(str(ENV_PATH), "STEAM_API_KEY", str(data.get("steam_api_key", "")).strip())
            if "steam_user_id" in data:
                set_key(str(ENV_PATH), "STEAM_USER_ID", str(data.get("steam_user_id", "")).strip())

            # Recargar en la configuración de la app
            from src.config.settings import settings
            settings.load_env()

            # Obtener datos actualizados de Steam si cambiaron
            steam_profile = self._fetch_steam_profile(
                data.get("steam_api_key", ""),
                data.get("steam_user_id", "")
            )

            return {
                "success": True,
                "message": "Configuración guardada en .env correctamente.",
                "steam_profile": steam_profile
            }
        except Exception as e:
            logger.error("Error al guardar config: %s", e)
            return {"success": False, "message": str(e)}

    def test_connection(self) -> dict:
        """Verifica que las credenciales actuales funcionen."""
        results = {"ai_ok": False, "steam_ok": False, "message": ""}
        messages = []

        # Test Steam API
        try:
            from src.api.steam_client import SteamAPI
            api = SteamAPI()
            summary = api.get_player_summary()
            if summary and "personaname" in summary:
                results["steam_ok"] = True
                messages.append(f"Steam OK ({summary['personaname']})")
            else:
                messages.append("Steam: Falló consulta de perfil")
        except Exception as e:
            messages.append(f"Steam Error: {e}")

        # Test IA
        try:
            from src.config.settings import settings
            provider = settings.get_active_provider()
            model = settings.get_active_model()
            results["ai_ok"] = True
            messages.append(f"IA OK ({provider.upper()} - {model})")
        except Exception as e:
            messages.append(f"IA Error: {e}")

        results["message"] = " | ".join(messages)
        return results

    def toggle_agent(self) -> dict:
        """Alterna el estado del asistente de voz (iniciar o detener)."""
        if self._is_running:
            self._is_running = False
            return {
                "running": False,
                "message": "Asistente de voz detenido."
            }
        else:
            try:
                from src.interfaces.voice_bot import SteamVoiceBot

                def run_bot():
                    try:
                        self._voice_bot_instance = SteamVoiceBot()
                        self._is_running = True
                        self._voice_bot_instance.start()
                    except Exception as ex:
                        logger.error("Excepción en hilo de voz: %s", ex)
                    finally:
                        self._is_running = False

                self._voice_thread = threading.Thread(target=run_bot, daemon=True)
                self._voice_thread.start()
                self._is_running = True
                return {
                    "running": True,
                    "message": "Asistente activo en segundo plano. Mantén [F9] para hablar."
                }
            except Exception as e:
                self._is_running = False
                return {
                    "running": False,
                    "message": f"Error al iniciar: {str(e)}"
                }
