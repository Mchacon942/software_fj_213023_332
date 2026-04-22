"""
reserva.py
==========
Define la clase Reserva, que integra Cliente, Servicio, duración y estado.

Implementa el ciclo de vida completo de una reserva:
  PENDIENTE → CONFIRMADA → (COMPLETADA | CANCELADA)

Incluye manejo exhaustivo de excepciones con try/except, try/except/else,
try/except/finally y encadenamiento de excepciones.

Autores: Grupo 213023_332
"""

from datetime import datetime
from enum import Enum           # Para representar estados de forma segura

from utils.excepciones import (
    CapacidadExcedidaError,
    ParametroServicioInvalidoError,
    DuracionInvalidaError,
    ReservaYaCanceladaError,
    ReservaYaConfirmadaError,
    ServicioNoDisponibleError,
    CalculoError,
)
from utils.logger import log


# =============================================================================
# ENUMERACIÓN DE ESTADOS
# =============================================================================

class EstadoReserva(Enum):
    """
    Enumeración de los posibles estados de una reserva.
    Usar Enum previene errores por strings mal escritos ("confiramda", etc.)
    """
    PENDIENTE   = "PENDIENTE"      # Estado inicial al crear la reserva
    CONFIRMADA  = "CONFIRMADA"     # Reserva aprobada y pagada
    CANCELADA   = "CANCELADA"      # Reserva anulada
    COMPLETADA  = "COMPLETADA"     # Servicio ya fue prestado


# =============================================================================
# CLASE RESERVA
# =============================================================================

class Reserva:
    """
    Representa una reserva de servicio para un cliente en Software FJ.

    Integra:
      - Cliente   → quién hace la reserva
      - Servicio  → qué servicio se reserva
      - Duración  → cuántas horas
      - Estado    → ciclo de vida de la reserva
      - Costo     → calculado automáticamente

    Principios aplicados:
      - Encapsulación: atributos privados, acceso por propiedades
      - Manejo de excepciones: try/except, try/except/else, try/finally
      - Encadenamiento: raise ... from e para preservar contexto del error
    """

    def __init__(self, id_reserva: str, cliente, servicio,
                 duracion_horas: float, **kwargs_servicio):
        """
        Crea una nueva reserva en estado PENDIENTE.

        Args:
            id_reserva: Identificador único de la reserva.
            cliente: Objeto Cliente que realiza la reserva.
            servicio: Objeto Servicio (ReservaSala, AlquilerEquipo, etc.).
            duracion_horas: Duración del servicio en horas.
            **kwargs_servicio: Parámetros adicionales para el cálculo del costo
                               (se pasan directamente al método calcular_costo del servicio).

        Raises:
            DuracionInvalidaError: Si la duración no es válida.
            ServicioNoDisponibleError: Si el servicio no está disponible.
            CalculoError: Si hay un problema al calcular el costo.
        """
        # --- Validación de duración ---
        try:
            self._validar_duracion(duracion_horas)
        except DuracionInvalidaError:
            # Re-lanzamos sin modificar para que el llamador la maneje
            raise

        # --- Verificamos disponibilidad del servicio ---
        try:
            servicio.verificar_disponibilidad()
        except ServicioNoDisponibleError:
            log.warning(f"Intento de reserva sobre servicio no disponible: '{servicio.nombre}'")
            raise

        # --- Asignación de atributos ---
        self._id = id_reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._kwargs_servicio = kwargs_servicio       # Parámetros extra para el costo
        self._estado = EstadoReserva.PENDIENTE        # Estado inicial
        self._fecha_creacion = datetime.now()
        self._fecha_confirmacion = None               # Se asigna al confirmar
        self._fecha_cancelacion = None                # Se asigna al cancelar
        self._costo_total = 0.0                       # Se calcula al confirmar
        self._notas = ""                              # Campo opcional para anotaciones

        log.info(f"Reserva CREADA: ID='{id_reserva}' | Cliente='{cliente.nombre}' "
                 f"| Servicio='{servicio.nombre}' | Duración={duracion_horas}h")

    # -------------------------------------------------------------------------
    # VALIDACIÓN ESTÁTICA
    # -------------------------------------------------------------------------

    @staticmethod
    def _validar_duracion(duracion: float) -> None:
        """
        Valida que la duración sea un número positivo razonable.

        Raises:
            DuracionInvalidaError: Si la duración es inválida.
        """
        if not isinstance(duracion, (int, float)):
            raise DuracionInvalidaError(duracion, "La duración debe ser un número.")
        if duracion <= 0:
            raise DuracionInvalidaError(duracion, "La duración debe ser mayor a cero.")
        if duracion > 168:  # 168 horas = 1 semana
            raise DuracionInvalidaError(duracion,
                                        "La duración no puede superar 168 horas (1 semana).")

    # -------------------------------------------------------------------------
    # PROPIEDADES
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def notas(self) -> str:
        return self._notas

    @notas.setter
    def notas(self, texto: str) -> None:
        self._notas = str(texto).strip()

    # -------------------------------------------------------------------------
    # MÉTODOS DEL CICLO DE VIDA
    # -------------------------------------------------------------------------

    def confirmar(self) -> float:
        """
        Confirma la reserva: valida, calcula el costo y cambia el estado.

        Demuestra uso de try/except/else/finally:
          - try:     intenta calcular el costo
          - except:  captura errores de cálculo
          - else:    se ejecuta SOLO si no hubo excepciones
          - finally: se ejecuta SIEMPRE (registro en log)

        Returns:
            float: Costo total de la reserva confirmada.

        Raises:
            ReservaYaConfirmadaError: Si la reserva ya fue confirmada.
            ReservaYaCanceladaError:  Si la reserva ya fue cancelada.
            CalculoError:             Si falla el cálculo del costo.
        """
        # Verificamos que el estado permita confirmar
        if self._estado == EstadoReserva.CONFIRMADA:
            raise ReservaYaConfirmadaError(self._id)
        if self._estado == EstadoReserva.CANCELADA:
            raise ReservaYaCanceladaError(self._id)

        log.info(f"Procesando confirmación de reserva '{self._id}'...")

        # --- Bloque try/except/else/finally ---
        try:
            # Intentamos calcular el costo pasando los parámetros opcionales
            costo = self._servicio.calcular_costo(
                self._duracion_horas,
                **self._kwargs_servicio
            )

            # Validación adicional: el costo no puede ser negativo
            if costo < 0:
                raise CalculoError("confirmar", "El costo calculado es negativo.")

        except (CapacidadExcedidaError, ParametroServicioInvalidoError) as e:
            # Excepciones de validación conocidas: las re-lanzamos sin envolver
            # para que el llamador las reciba con su tipo original exacto
            log.error(f"Error de validación al confirmar reserva '{self._id}': {e}")
            raise

        except CalculoError as e:
            # Capturamos error de cálculo, lo registramos y re-lanzamos
            log.error(f"Error al calcular costo de reserva '{self._id}': {e}")
            raise  # Re-lanzamos para que el llamador decida qué hacer

        except Exception as e:
            # Capturamos cualquier otro error verdaderamente inesperado
            log.critical(f"Error inesperado al confirmar reserva '{self._id}': {e}")
            # Encadenamiento: el error original queda accesible como __cause__
            raise CalculoError("confirmar", f"Error inesperado: {str(e)}") from e

        else:
            # Este bloque SOLO se ejecuta si NO hubo ninguna excepción en try
            self._costo_total = costo
            self._estado = EstadoReserva.CONFIRMADA
            self._fecha_confirmacion = datetime.now()
            log.info(f"Reserva '{self._id}' CONFIRMADA exitosamente. "
                     f"Costo total: ${costo:,.2f} COP")

        finally:
            # Este bloque se ejecuta SIEMPRE, haya o no excepción
            # Útil para liberar recursos, cerrar conexiones, etc.
            log.debug(f"Proceso de confirmación de reserva '{self._id}' finalizado. "
                      f"Estado actual: {self._estado.value}")

        return self._costo_total

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """
        Cancela la reserva registrando el motivo.

        Args:
            motivo: Razón de la cancelación.

        Raises:
            ReservaYaCanceladaError: Si la reserva ya estaba cancelada.
        """
        # Usamos try/except para manejar el estado inválido
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise ReservaYaCanceladaError(self._id)

            # Cambiamos estado y registramos fecha y motivo
            self._estado = EstadoReserva.CANCELADA
            self._fecha_cancelacion = datetime.now()
            self._notas = f"CANCELADA — Motivo: {motivo}"

            log.info(f"Reserva '{self._id}' CANCELADA. Motivo: {motivo}")

        except ReservaYaCanceladaError:
            log.warning(f"Intento de cancelar reserva '{self._id}' que ya estaba cancelada.")
            raise  # Re-lanzamos para que el llamador lo maneje

    def completar(self) -> None:
        """
        Marca la reserva como completada (servicio ya fue prestado).

        Raises:
            ValueError: Si la reserva no estaba en estado CONFIRMADA.
        """
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise ValueError(
                    f"Solo se pueden completar reservas CONFIRMADAS. "
                    f"Estado actual: {self._estado.value}"
                )
            self._estado = EstadoReserva.COMPLETADA
            log.info(f"Reserva '{self._id}' marcada como COMPLETADA.")

        except ValueError as e:
            log.error(f"Error al completar reserva '{self._id}': {e}")
            raise

    def procesar(self) -> dict:
        """
        Método de procesamiento integral: confirma y retorna resumen.

        Demuestra uso encadenado de try/except/finally.

        Returns:
            dict: Diccionario con todos los datos del procesamiento.
        """
        resumen = {
            "id_reserva": self._id,
            "cliente": self._cliente.nombre,
            "servicio": self._servicio.nombre,
            "duracion": self._duracion_horas,
            "estado": None,
            "costo": 0.0,
            "exitoso": False,
            "mensaje": "",
        }

        try:
            costo = self.confirmar()
            resumen["estado"] = self._estado.value
            resumen["costo"] = costo
            resumen["exitoso"] = True
            resumen["mensaje"] = f"Reserva procesada correctamente. Total: ${costo:,.2f} COP"

        except (ReservaYaConfirmadaError, ReservaYaCanceladaError) as e:
            # Error de estado: la reserva no estaba en un estado válido
            resumen["estado"] = self._estado.value
            resumen["mensaje"] = f"Error de estado: {e}"
            log.warning(f"Procesamiento de reserva '{self._id}' falló por estado: {e}")

        except CalculoError as e:
            # Error específico de cálculo
            resumen["estado"] = self._estado.value
            resumen["mensaje"] = f"Error de cálculo: {e}"
            log.error(f"Procesamiento de reserva '{self._id}' falló en cálculo: {e}")

        except Exception as e:
            # Captura general para errores no previstos
            resumen["estado"] = self._estado.value
            resumen["mensaje"] = f"Error inesperado: {e}"
            log.critical(f"Error crítico al procesar reserva '{self._id}': {e}")

        finally:
            # Registro final sin importar el resultado
            log.debug(f"Procesamiento de reserva '{self._id}' completado. "
                      f"Exitoso: {resumen['exitoso']}")

        return resumen

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------

    def describir(self) -> str:
        """Retorna descripción detallada de la reserva."""
        confirmada_str = (self._fecha_confirmacion.strftime('%d/%m/%Y %H:%M')
                          if self._fecha_confirmacion else "No confirmada aún")
        return (
            f"{'='*50}\n"
            f"RESERVA: {self._id}\n"
            f"{'='*50}\n"
            f"  Cliente       : {self._cliente.nombre}\n"
            f"  Servicio      : {self._servicio.nombre}\n"
            f"  Duración      : {self._duracion_horas} hora(s)\n"
            f"  Estado        : {self._estado.value}\n"
            f"  Costo total   : ${self._costo_total:,.2f} COP\n"
            f"  Creada el     : {self._fecha_creacion.strftime('%d/%m/%Y %H:%M')}\n"
            f"  Confirmada el : {confirmada_str}\n"
            f"  Notas         : {self._notas or 'Sin notas'}\n"
            f"{'='*50}"
        )

    def __str__(self) -> str:
        return (f"Reserva[{self._id}] — {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._duracion_horas}h | "
                f"{self._estado.value} | ${self._costo_total:,.2f} COP")
