"""
gestores.py
===========
Módulo de gestión centralizada de Clientes, Servicios y Reservas.

Cada gestor actúa como repositorio en memoria (sin base de datos):
almacena, busca y administra colecciones de entidades usando listas y
diccionarios de Python.

Autores: Grupo 213023_332
"""

from utils.excepciones import (
    ClienteYaExisteError,
    ClienteNoEncontradoError,
    ServicioNoEncontradoError,
    ReservaNoEncontradaError,
)
from utils.logger import log
    

    

# =============================================================================
# GESTOR DE CLIENTES
# =============================================================================

class GestorClientes:
    """
    Repositorio en memoria para gestionar clientes.

    Almacena clientes en un diccionario {id: Cliente} para búsquedas O(1).
    Implementa operaciones CRUD básicas con validaciones y logging.
    """

    def __init__(self):
        # Diccionario principal: clave = id_cliente, valor = objeto Cliente
        self._clientes: dict = {}
        self._contador_id = 1  # Para generar IDs automáticos
        log.debug("GestorClientes inicializado.")

    def generar_id(self) -> str:
        """Genera un ID único para un nuevo cliente."""
        id_generado = f"CLI{self._contador_id:03d}"
        self._contador_id += 1
        return id_generado

    def registrar(self, cliente) -> None:
        """
        Registra un nuevo cliente en el sistema.

        Args:
            cliente: Objeto Cliente a registrar.

        Raises:
            ClienteYaExisteError: Si ya existe un cliente con el mismo ID.
        """
        try:
            # Verificamos que no exista ya un cliente con ese ID
            if cliente.id in self._clientes:
                raise ClienteYaExisteError(cliente.id)

            # Registramos el cliente
            self._clientes[cliente.id] = cliente
            log.info(f"Cliente REGISTRADO: '{cliente.id}' — {cliente.nombre}")

        except ClienteYaExisteError:
            log.warning(f"Registro fallido: cliente '{cliente.id}' ya existe.")
            raise

    def buscar(self, id_cliente: str):
        """
        Busca un cliente por su ID.

        Args:
            id_cliente: ID del cliente a buscar.

        Returns:
            Cliente: El objeto cliente encontrado.

        Raises:
            ClienteNoEncontradoError: Si no existe el cliente.
        """
        try:
            if id_cliente not in self._clientes:
                raise ClienteNoEncontradoError(id_cliente)
            return self._clientes[id_cliente]

        except ClienteNoEncontradoError:
            log.warning(f"Búsqueda fallida: cliente '{id_cliente}' no encontrado.")
            raise

    def listar_todos(self) -> list:
        """Retorna lista de todos los clientes registrados."""
        return list(self._clientes.values())

    def total(self) -> int:
        """Retorna la cantidad de clientes registrados."""
        return len(self._clientes)

    def existe(self, id_cliente: str) -> bool:
        """Verifica si existe un cliente con el ID dado (sin lanzar excepción)."""
        return id_cliente in self._clientes

    def eliminar(self, id_cliente: str) -> None:
        """
        Elimina un cliente del sistema.

        Raises:
            ClienteNoEncontradoError: Si el cliente no existe.
        """
        try:
            cliente = self.buscar(id_cliente)  # Lanza excepción si no existe
            del self._clientes[id_cliente]
            log.info(f"Cliente ELIMINADO: '{id_cliente}' — {cliente.nombre}")
        except ClienteNoEncontradoError:
            raise

    def __len__(self) -> int:
        return len(self._clientes)

    def __str__(self) -> str:
        return f"GestorClientes({len(self._clientes)} clientes registrados)"


# =============================================================================
# GESTOR DE SERVICIOS
# =============================================================================

class GestorServicios:
    """
    Repositorio en memoria para gestionar servicios de Software FJ.

    Almacena servicios en un diccionario {id: Servicio}.
    Permite filtrar por tipo y verificar disponibilidad.
    """

    def __init__(self):
        self._servicios: dict = {}
        self._contador_id = 1  # Para generar IDs automáticos
        log.debug("GestorServicios inicializado.")

    def generar_id(self) -> str:
        """Genera un ID único para un nuevo servicio."""
        id_generado = f"SER{self._contador_id:03d}"
        self._contador_id += 1
        return id_generado

    def agregar(self, servicio) -> None:
        """
        Agrega un nuevo servicio al catálogo.

        Args:
            servicio: Objeto Servicio a agregar.
        """
        try:
            if servicio.id in self._servicios:
                log.warning(f"Servicio '{servicio.id}' ya existe. Se sobrescribe.")

            self._servicios[servicio.id] = servicio
            log.info(f"Servicio AGREGADO: '{servicio.id}' — {servicio.nombre} "
                     f"(Tipo: {type(servicio).__name__})")

        except Exception as e:
            log.error(f"Error al agregar servicio '{servicio.id}': {e}")
            raise

    def buscar(self, id_servicio: str):
        """
        Busca un servicio por ID.

        Raises:
            ServicioNoEncontradoError: Si el servicio no existe.
        """
        if id_servicio not in self._servicios:
            log.warning(f"Servicio '{id_servicio}' no encontrado.")
            raise ServicioNoEncontradoError(id_servicio)
        return self._servicios[id_servicio]

    def listar_disponibles(self) -> list:
        """Retorna solo los servicios marcados como disponibles."""
        return [s for s in self._servicios.values() if s.disponible]

    def listar_por_tipo(self, tipo_clase) -> list:
        """
        Filtra servicios por tipo (clase).

        Args:
            tipo_clase: Clase a filtrar (ej: ReservaSala, AlquilerEquipo).

        Returns:
            list: Servicios del tipo especificado.
        """
        return [s for s in self._servicios.values() if isinstance(s, tipo_clase)]

    def listar_todos(self) -> list:
        """Retorna todos los servicios registrados."""
        return list(self._servicios.values())

    def total(self) -> int:
        return len(self._servicios)

    def __len__(self) -> int:
        return len(self._servicios)

    def __str__(self) -> str:
        return f"GestorServicios({len(self._servicios)} servicios registrados)"


# =============================================================================
# GESTOR DE RESERVAS
# =============================================================================

class GestorReservas:
    """
    Repositorio en memoria para gestionar el ciclo de vida de las reservas.

    Almacena reservas y provee filtros por estado, cliente y servicio.
    """

    def __init__(self):
        self._reservas: dict = {}
        self._contador_id = 1   # Para generar IDs automáticos si se necesita
        log.debug("GestorReservas inicializado.")
    def generar_id(self) -> str:
        """Genera un ID único para una nueva reserva."""
        id_generado = f"RES{self._contador_id:04d}"
        self._contador_id += 1
        return id_generado
    def registrar(self, reserva) -> None:
        """
        Registra una nueva reserva en el sistema.

        Args:
            reserva: Objeto Reserva a registrar.
        """
        try:
            if reserva.id in self._reservas:
                log.warning(f"Reserva '{reserva.id}' ya existe. Se sobrescribe.")

            self._reservas[reserva.id] = reserva

            # Asociamos la reserva al cliente (relación bidireccional)
            reserva.cliente.agregar_reserva(reserva)

            log.info(f"Reserva REGISTRADA: '{reserva.id}'")

        except Exception as e:
            log.error(f"Error al registrar reserva '{reserva.id}': {e}")
            raise

    def buscar(self, id_reserva: str):
        """
        Busca una reserva por ID.

        Raises:
            ReservaNoEncontradaError: Si no existe la reserva.
        """
        if id_reserva not in self._reservas:
            log.warning(f"Reserva '{id_reserva}' no encontrada.")
            raise ReservaNoEncontradaError(id_reserva)
        return self._reservas[id_reserva]

    def listar_por_cliente(self, id_cliente: str) -> list:
        """Retorna todas las reservas de un cliente específico."""
        return [r for r in self._reservas.values()
                if r.cliente.id == id_cliente]

    def listar_por_estado(self, estado) -> list:
        """
        Filtra reservas por estado.

        Args:
            estado: Valor de EstadoReserva (ej: EstadoReserva.CONFIRMADA).
        """
        return [r for r in self._reservas.values() if r.estado == estado]

    def listar_todas(self) -> list:
        """Retorna todas las reservas registradas."""
        return list(self._reservas.values())

    def generar_id(self) -> str:
        """Genera un ID único para una nueva reserva."""
        id_nuevo = f"RES{self._contador_id:04d}"
        self._contador_id += 1
        return id_nuevo

    def total(self) -> int:
        return len(self._reservas)

    def resumen(self) -> dict:
        """Retorna conteo de reservas por estado."""
        from modelos.reserva import EstadoReserva
        conteos = {estado.value: 0 for estado in EstadoReserva}
        for reserva in self._reservas.values():
            conteos[reserva.estado.value] += 1
        return conteos

    def __len__(self) -> int:
        return len(self._reservas)

    def __str__(self) -> str:
        return f"GestorReservas({len(self._reservas)} reservas registradas)"
