"""
Módulo de caché basado en SQLite para el proyecto SteamAgent.

Proporciona un sistema de caché key-value con expiración automática,
serialización JSON y un decorador para cachear resultados de funciones.
"""

import json
import logging
import sqlite3
import time
import functools
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Ruta al archivo de base de datos SQLite
DB_PATH: Path = Path(__file__).resolve().parent.parent.parent / "data" / "cache.db"


class CacheManager:
    """Gestor de caché basado en SQLite con soporte de expiración automática."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        """Inicializa el gestor de caché y crea la tabla si no existe.

        Args:
            db_path: Ruta al archivo de base de datos SQLite.
        """
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info("CacheManager inicializado con DB en: %s", self._db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Crea y devuelve una conexión a la base de datos SQLite.

        Returns:
            Conexión activa a SQLite.
        """
        return sqlite3.connect(str(self._db_path))

    def _init_db(self) -> None:
        """Crea la tabla de caché si no existe."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at REAL
                )
                """
            )
            conn.commit()
        logger.debug("Tabla 'cache' verificada/creada correctamente.")

    def get(self, key: str) -> Any | None:
        """Obtiene un valor del caché por su clave.

        Si la entrada ha expirado, se elimina automáticamente y se devuelve None.

        Args:
            key: Clave de la entrada en el caché.

        Returns:
            El valor deserializado o None si no existe o ha expirado.
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
            ).fetchone()

        if row is None:
            logger.debug("Cache MISS (no encontrado): %s", key)
            return None

        value_str, expires_at = row

        if expires_at < time.time():
            logger.debug("Cache MISS (expirado): %s", key)
            self.delete(key)
            return None

        logger.debug("Cache HIT: %s", key)
        return json.loads(value_str)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Almacena un valor en el caché con un tiempo de vida (TTL).

        El valor se serializa a JSON antes de almacenarse. Si el valor no
        es serializable, se registra una advertencia y no se almacena.

        Args:
            key: Clave de la entrada.
            value: Valor a almacenar (debe ser serializable a JSON).
            ttl: Tiempo de vida en segundos (por defecto 300).
        """
        try:
            value_str = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logger.warning(
                "No se pudo serializar el valor para la clave '%s': %s", key, e
            )
            return

        expires_at = time.time() + ttl

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
                """,
                (key, value_str, expires_at),
            )
            conn.commit()
        logger.debug("Cache SET: %s (TTL=%ds)", key, ttl)

    def delete(self, key: str) -> None:
        """Elimina una entrada específica del caché.

        Args:
            key: Clave de la entrada a eliminar.
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
        logger.debug("Cache DELETE: %s", key)

    def clear(self) -> None:
        """Elimina todas las entradas del caché."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
        logger.info("Cache limpiado completamente.")

    def cleanup(self) -> None:
        """Elimina todas las entradas expiradas del caché."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at < ?", (now,)
            )
            deleted = cursor.rowcount
            conn.commit()
        if deleted:
            logger.info("Cleanup: %d entradas expiradas eliminadas.", deleted)
        else:
            logger.debug("Cleanup: no se encontraron entradas expiradas.")


# Singleton a nivel de módulo
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorador que cachea el resultado de una función.

    Genera una clave de caché a partir del prefijo, nombre de la función,
    argumentos y keyword arguments. Si el resultado ya existe en caché y
    no ha expirado, se devuelve directamente sin ejecutar la función.

    Args:
        ttl: Tiempo de vida en segundos para la entrada cacheada.
        key_prefix: Prefijo opcional para la clave de caché.

    Returns:
        Decorador que envuelve la función con lógica de caché.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache_manager.get(cache_key)

            if result is not None:
                logger.debug(
                    "Decorador @cached: resultado obtenido del caché para '%s'.",
                    func.__name__,
                )
                return result

            result = func(*args, **kwargs)

            cache_manager.set(cache_key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
