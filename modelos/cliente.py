"""
cliente.py
==========
Define la clase abstracta EntidadBase y la clase concreta Cliente.

La clase EntidadBase establece el contrato mínimo que deben cumplir todas
las entidades del sistema. La clase Cliente implementa ese contrato con
validaciones estrictas y encapsulación de datos personales.

Autores: Grupo 213023_332
"""

import re                          # Para validación de email y teléfono con expresiones regulares
from abc import ABC, abstractmethod  # ABC = Abstract Base Class
from datetime import datetime        # Para registrar cuándo se creó cada entidad

from utils.excepciones import DatosClienteInvalidosError
from utils.logger import log


# =============================================================================
# CLASE ABSTRACTA BASE
# =============================================================================

class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema.

    Define la interfaz mínima que deben implementar Cliente, Servicio, etc.
    Al ser abstracta, no puede instanciarse directamente.

    Principio de diseño: Abstracción — oculta detalles de implementación
    y expone solo lo esencial.
    """

    def __init__(self, id_entidad: str):
        """
        Args:
            id_entidad: Identificador único de la entidad (no puede estar vacío).
        """
        # Atributo protegido (convención: _nombre indica "no acceder directamente")
        self._id = id_entidad
        # Registro automático de cuándo se creó la entidad
        self._fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        """Propiedad de solo lectura para el identificador."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Propiedad de solo lectura para la fecha de creación."""
        return self._fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        """
        Método abstracto: cada entidad concreta debe implementar su propia
        descripción textual. Obliga a todas las subclases a definirlo.
        """
        pass

    @abstractmethod
    def validar(self) -> bool:
        """
        Método abstracto: cada entidad concreta debe implementar su propia
        lógica de validación interna.
        """
        pass

    def __repr__(self) -> str:
        """Representación técnica del objeto para depuración."""
        return f"{self.__class__.__name__}(id='{self._id}')"


# =============================================================================
# CLASE CONCRETA: CLIENTE
# =============================================================================

class Cliente(EntidadBase):
    """
    Representa un cliente del sistema Software FJ.

    Implementa encapsulación completa: todos los atributos son privados
    y se accede/modifica a través de propiedades con validación.

    Principios aplicados:
      - Encapsulación: atributos privados con getters/setters validados
      - Herencia: extiende EntidadBase
      - Polimorfismo: implementa describir() y validar() propios
    """

    # Expresión regular para validar emails (formato básico estándar)
    _PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")

    # Expresión regular para teléfonos: acepta +57, 57 o sin prefijo, 10 dígitos
    _PATRON_TELEFONO = re.compile(r"^(\+?57)?[0-9]{10}$")

    def __init__(self, id_cliente: str, nombre: str, email: str,
                 telefono: str, ciudad: str = "No especificada"):
        """
        Crea un cliente validando todos los datos antes de asignarlos.

        Args:
            id_cliente: Identificador único (ej: "CLI001").
            nombre: Nombre completo del cliente.
            email: Correo electrónico válido.
            telefono: Número de teléfono colombiano.
            ciudad: Ciudad de residencia (opcional).

        Raises:
            DatosClienteInvalidosError: Si algún campo no pasa la validación.
        """
        # Primero validamos el ID antes de llamar al constructor padre
        self._validar_id(id_cliente)

        # Llamamos al constructor de EntidadBase con el ID validado
        super().__init__(id_cliente)

        # Asignamos los demás atributos usando las propiedades (que validan)
        # El orden importa: primero asignamos con _ para evitar recursión
        self._nombre = None
        self._email = None
        self._telefono = None
        self._ciudad = None

        # Usamos los setters para aprovechar la validación encapsulada
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.ciudad = ciudad

        # Lista de reservas asociadas a este cliente (encapsulada)
        self._reservas: list = []

        log.info(f"Cliente registrado exitosamente: ID='{id_cliente}', Nombre='{nombre}'")

    # -------------------------------------------------------------------------
    # VALIDACIONES ESTÁTICAS (no necesitan instancia)
    # -------------------------------------------------------------------------

    @staticmethod
    def _validar_id(id_cliente: str) -> None:
        """Valida que el ID no esté vacío y tenga formato correcto."""
        if not id_cliente or not isinstance(id_cliente, str):
            raise DatosClienteInvalidosError("id_cliente", id_cliente,
                                             "El ID no puede estar vacío ni ser nulo.")
        if len(id_cliente.strip()) < 3:
            raise DatosClienteInvalidosError("id_cliente", id_cliente,
                                             "El ID debe tener al menos 3 caracteres.")

    @staticmethod
    def _validar_nombre(nombre: str) -> None:
        """Valida que el nombre tenga al menos 2 palabras y solo letras/espacios."""
        if not nombre or not isinstance(nombre, str):
            raise DatosClienteInvalidosError("nombre", nombre,
                                             "El nombre no puede estar vacío.")
        nombre_limpio = nombre.strip()
        if len(nombre_limpio) < 3:
            raise DatosClienteInvalidosError("nombre", nombre,
                                             "El nombre debe tener al menos 3 caracteres.")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", nombre_limpio):
            raise DatosClienteInvalidosError("nombre", nombre,
                                             "El nombre solo puede contener letras y espacios.")

    # -------------------------------------------------------------------------
    # PROPIEDADES (Getters y Setters con validación — Encapsulación)
    # -------------------------------------------------------------------------

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del cliente."""
        self._validar_nombre(valor)
        self._nombre = valor.strip().title()  # Formateamos con mayúscula en cada palabra

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        """Valida formato de email usando expresión regular."""
        if not valor or not isinstance(valor, str):
            raise DatosClienteInvalidosError("email", valor,
                                             "El email no puede estar vacío.")
        if not self._PATRON_EMAIL.match(valor.strip()):
            raise DatosClienteInvalidosError("email", valor,
                                             "Formato de email inválido. Ejemplo válido: usuario@dominio.com")
        self._email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida número de teléfono colombiano."""
        if not valor or not isinstance(valor, str):
            raise DatosClienteInvalidosError("telefono", valor,
                                             "El teléfono no puede estar vacío.")
        valor_limpio = valor.strip().replace(" ", "").replace("-", "")
        if not self._PATRON_TELEFONO.match(valor_limpio):
            raise DatosClienteInvalidosError("telefono", valor,
                                             "Teléfono inválido. Debe ser un número colombiano de 10 dígitos.")
        self._telefono = valor_limpio

    @property
    def ciudad(self) -> str:
        return self._ciudad

    @ciudad.setter
    def ciudad(self, valor: str) -> None:
        """Asigna la ciudad con un valor por defecto si está vacía."""
        self._ciudad = valor.strip().title() if valor and valor.strip() else "No especificada"

    @property
    def reservas(self) -> list:
        """Retorna copia de la lista de reservas (inmutabilidad externa)."""
        return list(self._reservas)

    # -------------------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # -------------------------------------------------------------------------

    def agregar_reserva(self, reserva) -> None:
        """
        Asocia una reserva a este cliente.

        Args:
            reserva: Objeto Reserva a agregar.
        """
        self._reservas.append(reserva)
        log.debug(f"Reserva '{reserva.id}' asociada al cliente '{self._id}'")

    def total_reservas(self) -> int:
        """Retorna la cantidad de reservas activas del cliente."""
        return len(self._reservas)

    # -------------------------------------------------------------------------
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS
    # -------------------------------------------------------------------------

    def describir(self) -> str:
        """Retorna descripción completa del cliente."""
        return (
            f"Cliente: {self._nombre}\n"
            f"  ID       : {self._id}\n"
            f"  Email    : {self._email}\n"
            f"  Teléfono : {self._telefono}\n"
            f"  Ciudad   : {self._ciudad}\n"
            f"  Reservas : {self.total_reservas()}\n"
            f"  Registrado: {self._fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
        )

    def validar(self) -> bool:
        """
        Verifica que el cliente tiene todos los datos requeridos correctamente
        asignados. Retorna True si todo está en orden.
        """
        return all([
            self._id is not None and len(self._id) >= 3,
            self._nombre is not None and len(self._nombre) >= 3,
            self._email is not None and self._PATRON_EMAIL.match(self._email),
            self._telefono is not None,
        ])

    def __str__(self) -> str:
        return f"Cliente[{self._id}] — {self._nombre} ({self._email})"
