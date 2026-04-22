"""Paquete de utilidades del sistema Software FJ."""
from .excepciones import (
    SoftwareFJError,
    ClienteError, ClienteYaExisteError, ClienteNoEncontradoError, DatosClienteInvalidosError,
    ServicioError, ServicioNoDisponibleError, ServicioNoEncontradoError,
    ParametroServicioInvalidoError, CapacidadExcedidaError,
    ReservaError, ReservaNoEncontradaError, ReservaYaCanceladaError,
    ReservaYaConfirmadaError, DuracionInvalidaError,
    CalculoError, LogError,
)
from .logger import log
