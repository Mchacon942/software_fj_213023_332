"""
logger.py
=========
Módulo de registro de eventos y errores del sistema Software FJ.

Configura un logger centralizado que escribe tanto en consola como en un
archivo de logs persistente, garantizando trazabilidad de todas las
operaciones y errores del sistema.

Autores: Grupo 213023_332
"""

import logging          # Módulo estándar de Python para logging
import os               # Para manejo de rutas de archivos
from datetime import datetime  # Para timestamps en nombres de archivo


def configurar_logger(nombre: str = "SoftwareFJ") -> logging.Logger:
    """
    Crea y configura el logger principal del sistema.

    Crea dos handlers:
      1. FileHandler  → escribe en archivo .log con fecha en el nombre
      2. StreamHandler → imprime en consola (para depuración en tiempo real)

    Args:
        nombre: Nombre identificador del logger (aparece en cada línea del log).

    Returns:
        logging.Logger: Instancia del logger ya configurada.
    """

    # Creamos el directorio de logs si no existe
    carpeta_logs = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(carpeta_logs, exist_ok=True)

    # Nombre del archivo incluye la fecha para organizar por día
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ruta_archivo = os.path.join(carpeta_logs, f"software_fj_{fecha_hoy}.log")

    # Obtenemos (o creamos) el logger con el nombre dado
    logger = logging.getLogger(nombre)

    # Evitamos agregar handlers duplicados si la función se llama varias veces
    if logger.handlers:
        return logger

    # Nivel mínimo: DEBUG captura todo (DEBUG < INFO < WARNING < ERROR < CRITICAL)
    logger.setLevel(logging.DEBUG)

    # -------------------------------------------------------------------
    # FORMATO de cada línea del log
    # Ejemplo: 2026-04-20 10:35:22 | ERROR    | SoftwareFJ | Mensaje aquí
    # -------------------------------------------------------------------
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # -------------------------------------------------------------------
    # HANDLER 1: Archivo de logs (nivel DEBUG → guarda absolutamente todo)
    # -------------------------------------------------------------------
    handler_archivo = logging.FileHandler(ruta_archivo, encoding="utf-8")
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    # -------------------------------------------------------------------
    # HANDLER 2: Consola (nivel INFO → solo mensajes importantes en pantalla)
    # -------------------------------------------------------------------
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    # Agregamos ambos handlers al logger
    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)

    # Primera línea del log: marca de inicio de sesión
    logger.info("=" * 70)
    logger.info("SISTEMA SOFTWARE FJ — SESIÓN INICIADA")
    logger.info(f"Archivo de log: {os.path.abspath(ruta_archivo)}")
    logger.info("=" * 70)

    return logger


# =============================================================================
# INSTANCIA GLOBAL DEL LOGGER
# Importar 'log' desde cualquier módulo del proyecto para usarlo directamente
# =============================================================================
log = configurar_logger("SoftwareFJ")
