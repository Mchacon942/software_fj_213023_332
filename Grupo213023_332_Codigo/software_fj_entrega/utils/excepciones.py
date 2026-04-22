"""
excepciones.py
==============
Módulo de excepciones personalizadas del sistema Software FJ.

Define todas las excepciones específicas del dominio para garantizar
un manejo robusto y descriptivo de errores en toda la aplicación.

Autores: Grupo 213023_332
Integrantes:
    - Juan Sebastian Bernal Bermudez
    - Juan Fernando Capitani Giraldo
    - Maribel Chacon Garzon
    - Cristian Camilo Galindo Barragan
    - Junior David Mancipe Castiblanco
"""


# =============================================================================
# EXCEPCIÓN BASE DEL SISTEMA
# =============================================================================

class SoftwareFJError(Exception):
    """
    Excepción base de la que heredan todas las excepciones del sistema.
    Permite capturar cualquier error propio de Software FJ con un solo bloque.
    """

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        # Llamamos al constructor de la clase padre (Exception)
        super().__init__(mensaje)
        self.mensaje = mensaje        # Descripción legible del error
        self.codigo = codigo          # Código único para identificar el tipo

    def __str__(self):
        # Representación en texto con código y mensaje
        return f"[{self.codigo}] {self.mensaje}"


# =============================================================================
# EXCEPCIONES DE CLIENTE
# =============================================================================

class ClienteError(SoftwareFJError):
    """Clase base para errores relacionados con la entidad Cliente."""
    pass


class ClienteYaExisteError(ClienteError):
    """Se lanza cuando se intenta registrar un cliente con un ID ya existente."""

    def __init__(self, id_cliente: str):
        super().__init__(
            f"El cliente con ID '{id_cliente}' ya se encuentra registrado en el sistema.",
            "ERR_CLIENTE_DUPLICADO"
        )
        self.id_cliente = id_cliente  # Guardamos el ID problemático


class ClienteNoEncontradoError(ClienteError):
    """Se lanza cuando se busca un cliente que no existe en el sistema."""

    def __init__(self, id_cliente: str):
        super().__init__(
            f"No se encontró ningún cliente con ID '{id_cliente}'.",
            "ERR_CLIENTE_NO_ENCONTRADO"
        )
        self.id_cliente = id_cliente


class DatosClienteInvalidosError(ClienteError):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones."""

    def __init__(self, campo: str, valor, razon: str):
        super().__init__(
            f"Dato inválido en campo '{campo}': valor='{valor}'. Razón: {razon}",
            "ERR_DATO_CLIENTE_INVALIDO"
        )
        self.campo = campo    # Nombre del campo problemático
        self.valor = valor    # Valor que causó el error
        self.razon = razon    # Explicación del porqué es inválido


# =============================================================================
# EXCEPCIONES DE SERVICIO
# =============================================================================

class ServicioError(SoftwareFJError):
    """Clase base para errores relacionados con la entidad Servicio."""
    pass


class ServicioNoDisponibleError(ServicioError):
    """Se lanza cuando el servicio solicitado no está activo o disponible."""

    def __init__(self, nombre_servicio: str):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible en este momento.",
            "ERR_SERVICIO_NO_DISPONIBLE"
        )
        self.nombre_servicio = nombre_servicio


class ServicioNoEncontradoError(ServicioError):
    """Se lanza cuando se busca un servicio que no existe."""

    def __init__(self, id_servicio: str):
        super().__init__(
            f"No existe ningún servicio con ID '{id_servicio}'.",
            "ERR_SERVICIO_NO_ENCONTRADO"
        )
        self.id_servicio = id_servicio


class ParametroServicioInvalidoError(ServicioError):
    """Se lanza cuando un parámetro enviado a un servicio no es válido."""

    def __init__(self, parametro: str, valor, razon: str):
        super().__init__(
            f"Parámetro inválido '{parametro}': valor='{valor}'. Razón: {razon}",
            "ERR_PARAMETRO_SERVICIO_INVALIDO"
        )
        self.parametro = parametro
        self.valor = valor
        self.razon = razon


class CapacidadExcedidaError(ServicioError):
    """Se lanza cuando se intenta reservar más de la capacidad permitida."""

    def __init__(self, servicio: str, capacidad_max: int, solicitado: int):
        super().__init__(
            f"El servicio '{servicio}' tiene capacidad máxima de {capacidad_max} "
            f"personas, pero se solicitaron {solicitado}.",
            "ERR_CAPACIDAD_EXCEDIDA"
        )
        self.servicio = servicio
        self.capacidad_max = capacidad_max
        self.solicitado = solicitado


# =============================================================================
# EXCEPCIONES DE RESERVA
# =============================================================================

class ReservaError(SoftwareFJError):
    """Clase base para errores relacionados con la entidad Reserva."""
    pass


class ReservaNoEncontradaError(ReservaError):
    """Se lanza cuando se busca una reserva que no existe."""

    def __init__(self, id_reserva: str):
        super().__init__(
            f"No se encontró la reserva con ID '{id_reserva}'.",
            "ERR_RESERVA_NO_ENCONTRADA"
        )
        self.id_reserva = id_reserva


class ReservaYaCanceladaError(ReservaError):
    """Se lanza cuando se intenta cancelar una reserva que ya fue cancelada."""

    def __init__(self, id_reserva: str):
        super().__init__(
            f"La reserva '{id_reserva}' ya se encuentra cancelada.",
            "ERR_RESERVA_YA_CANCELADA"
        )
        self.id_reserva = id_reserva


class ReservaYaConfirmadaError(ReservaError):
    """Se lanza cuando se intenta confirmar una reserva ya confirmada."""

    def __init__(self, id_reserva: str):
        super().__init__(
            f"La reserva '{id_reserva}' ya estaba confirmada previamente.",
            "ERR_RESERVA_YA_CONFIRMADA"
        )
        self.id_reserva = id_reserva


class DuracionInvalidaError(ReservaError):
    """Se lanza cuando la duración de una reserva no es válida."""

    def __init__(self, duracion, razon: str):
        super().__init__(
            f"Duración '{duracion}' inválida. Razón: {razon}",
            "ERR_DURACION_INVALIDA"
        )
        self.duracion = duracion
        self.razon = razon


# =============================================================================
# EXCEPCIONES DE CÁLCULO Y SISTEMA
# =============================================================================

class CalculoError(SoftwareFJError):
    """Se lanza cuando ocurre un error durante el cálculo de costos."""

    def __init__(self, operacion: str, detalle: str):
        super().__init__(
            f"Error en cálculo '{operacion}': {detalle}",
            "ERR_CALCULO"
        )
        self.operacion = operacion
        self.detalle = detalle


class LogError(SoftwareFJError):
    """Se lanza cuando el sistema de logging falla."""

    def __init__(self, detalle: str):
        super().__init__(
            f"Error en el sistema de logs: {detalle}",
            "ERR_LOG"
        )
