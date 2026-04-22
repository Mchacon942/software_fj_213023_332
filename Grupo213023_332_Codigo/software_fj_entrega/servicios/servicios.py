"""
servicios.py
============
Define la clase abstracta Servicio y los tres servicios especializados:
  1. ReservaSala        — Reserva de salas de reuniones
  2. AlquilerEquipo     — Alquiler de equipos tecnológicos
  3. AsesoriaEspecializada — Asesorías con expertos

Implementa herencia, polimorfismo y métodos con parámetros opcionales
para simular sobrecarga de métodos (Python no soporta sobrecarga nativa).

Autores: Grupo 213023_332
"""

from abc import ABC, abstractmethod
from datetime import datetime

from utils.excepciones import (
    ParametroServicioInvalidoError,
    ServicioNoDisponibleError,
    CapacidadExcedidaError,
    CalculoError,
)
from utils.logger import log


# =============================================================================
# CLASE ABSTRACTA: SERVICIO
# =============================================================================

class Servicio(ABC):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.

    Establece el contrato que deben cumplir todos los servicios:
    - calcular_costo(): debe ser implementado por cada servicio
    - describir(): descripción específica de cada servicio
    - validar_parametros(): verifica que los parámetros sean correctos

    Principios aplicados:
      - Abstracción: define interfaz sin implementación concreta
      - Polimorfismo: cada subclase implementa los métodos a su manera
      - Herencia: todos los servicios comparten atributos base
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float,
                 disponible: bool = True):
        """
        Args:
            id_servicio: Identificador único del servicio.
            nombre: Nombre descriptivo del servicio.
            tarifa_base: Precio base en pesos colombianos (COP) por hora.
            disponible: Si el servicio está activo para reservas.

        Raises:
            ParametroServicioInvalidoError: Si la tarifa base es negativa o cero.
        """
        # Validación de la tarifa antes de asignarla
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ParametroServicioInvalidoError(
                "tarifa_base", tarifa_base,
                "La tarifa base debe ser un número mayor a cero."
            )

        self._id = id_servicio
        self._nombre = nombre
        self._tarifa_base = float(tarifa_base)   # Aseguramos tipo float
        self._disponible = disponible
        self._fecha_creacion = datetime.now()

        log.debug(f"Servicio creado: '{nombre}' (ID: {id_servicio}) | Tarifa base: ${tarifa_base:,.0f}")

    # -------------------------------------------------------------------------
    # PROPIEDADES
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        """Permite activar o desactivar el servicio."""
        self._disponible = valor
        estado = "ACTIVADO" if valor else "DESACTIVADO"
        log.info(f"Servicio '{self._nombre}' → {estado}")

    # -------------------------------------------------------------------------
    # MÉTODOS ABSTRACTOS (contrato obligatorio para subclases)
    # -------------------------------------------------------------------------

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """
        Calcula el costo total del servicio.

        Args:
            duracion_horas: Duración de uso en horas.
            **kwargs: Parámetros opcionales específicos de cada servicio
                      (ej: descuento, impuesto, numero_personas).

        Returns:
            float: Costo total calculado en COP.
        """
        pass

    @abstractmethod
    def describir(self) -> str:
        """Retorna descripción detallada del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, **kwargs) -> None:
        """
        Valida que los parámetros sean correctos antes de procesar.

        Raises:
            ParametroServicioInvalidoError: Si algún parámetro es inválido.
            CapacidadExcedidaError: Si se supera la capacidad máxima.
        """
        pass

    # -------------------------------------------------------------------------
    # MÉTODO CONCRETO COMPARTIDO (no abstracto)
    # -------------------------------------------------------------------------

    def verificar_disponibilidad(self) -> None:
        """
        Verifica que el servicio esté disponible antes de usarlo.

        Raises:
            ServicioNoDisponibleError: Si el servicio está inactivo.
        """
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)

    def _calcular_con_impuesto(self, subtotal: float, tasa_iva: float = 0.19) -> float:
        """
        Método auxiliar protegido: aplica IVA al subtotal.

        Args:
            subtotal: Valor antes de impuestos.
            tasa_iva: Porcentaje de IVA (por defecto 19% colombiano).

        Returns:
            float: Subtotal + IVA
        """
        try:
            if tasa_iva < 0 or tasa_iva > 1:
                raise CalculoError("IVA", f"La tasa {tasa_iva} está fuera del rango [0, 1]")
            return subtotal * (1 + tasa_iva)
        except CalculoError:
            raise  # Re-lanzamos la excepción sin modificarla
        except Exception as e:
            # Encadenamiento de excepciones: from e preserva el traceback original
            raise CalculoError("IVA", str(e)) from e

    def __str__(self) -> str:
        estado = "✓ Disponible" if self._disponible else "✗ No disponible"
        return f"Servicio[{self._id}] — {self._nombre} | ${self._tarifa_base:,.0f}/h | {estado}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self._id}', tarifa={self._tarifa_base})"


# =============================================================================
# SERVICIO 1: RESERVA DE SALA
# =============================================================================

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones.

    Características:
    - Tarifa base por hora según capacidad de la sala
    - Descuento por reservas de más de 4 horas
    - Capacidad máxima configurable
    - Equipamiento adicional (proyector, videoconferencia) con costo extra
    """

    # Constante de clase: descuento para reservas largas (más de 4 horas)
    DESCUENTO_LARGA_DURACION = 0.10   # 10% de descuento
    HORAS_MINIMAS_PARA_DESCUENTO = 4  # A partir de cuántas horas aplica

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float,
                 capacidad_maxima: int = 10, tiene_proyector: bool = True):
        """
        Args:
            capacidad_maxima: Número máximo de personas en la sala.
            tiene_proyector: Si la sala tiene proyector disponible.
        """
        super().__init__(id_servicio, nombre, tarifa_base)

        # Validación de capacidad
        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0:
            raise ParametroServicioInvalidoError(
                "capacidad_maxima", capacidad_maxima,
                "La capacidad debe ser un entero positivo."
            )

        self._capacidad_maxima = capacidad_maxima
        self._tiene_proyector = tiene_proyector

    @property
    def capacidad_maxima(self) -> int:
        return self._capacidad_maxima

    def calcular_costo(self, duracion_horas: float, numero_personas: int = 1,
                       con_videoconferencia: bool = False,
                       descuento_adicional: float = 0.0) -> float:
        """
        Calcula el costo de la reserva de sala.

        Simula sobrecarga de método usando parámetros opcionales:
          - Sin extras:         tarifa_base × horas
          - Con descuento:      aplica 10% si duración > 4h
          - Con videoconf:      suma $50,000 adicionales por hora
          - Con desc. adicional: aplica descuento extra (0.0 a 1.0)

        Args:
            duracion_horas: Horas de uso.
            numero_personas: Cantidad de asistentes.
            con_videoconferencia: Si se requiere equipo de videoconferencia.
            descuento_adicional: Porcentaje adicional de descuento (0.0 = sin descuento).

        Returns:
            float: Costo total en COP.
        """
        try:
            # Primero validamos todos los parámetros
            self.validar_parametros(duracion_horas, numero_personas=numero_personas,
                                    descuento_adicional=descuento_adicional)

            # Cálculo base: tarifa × horas
            costo = self._tarifa_base * duracion_horas

            # Extra por videoconferencia: $50,000/hora adicionales
            if con_videoconferencia:
                costo += 50_000 * duracion_horas
                log.debug(f"ReservaSala: cargo videoconferencia aplicado")

            # Descuento por duración larga (>= 4 horas)
            if duracion_horas >= self.HORAS_MINIMAS_PARA_DESCUENTO:
                costo *= (1 - self.DESCUENTO_LARGA_DURACION)
                log.debug(f"ReservaSala: descuento larga duración ({self.DESCUENTO_LARGA_DURACION*100:.0f}%) aplicado")

            # Descuento adicional (ej: cliente corporativo)
            if descuento_adicional > 0:
                costo *= (1 - descuento_adicional)
                log.debug(f"ReservaSala: descuento adicional ({descuento_adicional*100:.0f}%) aplicado")

            log.info(f"Costo calculado — {self._nombre}: ${costo:,.2f} COP ({duracion_horas}h, {numero_personas} personas)")
            return round(costo, 2)

        except (ParametroServicioInvalidoError, CapacidadExcedidaError):
            raise  # Re-lanzamos excepciones propias sin modificar
        except Exception as e:
            raise CalculoError("ReservaSala.calcular_costo", str(e)) from e

    def validar_parametros(self, duracion_horas: float, numero_personas: int = 1,
                           descuento_adicional: float = 0.0, **kwargs) -> None:
        """Valida duración, número de personas y descuento."""

        # Validar duración
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "La duración debe ser un número mayor a cero."
            )
        if duracion_horas > 24:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "La duración no puede superar 24 horas continuas."
            )

        # Validar número de personas
        if not isinstance(numero_personas, int) or numero_personas <= 0:
            raise ParametroServicioInvalidoError(
                "numero_personas", numero_personas,
                "El número de personas debe ser un entero positivo."
            )
        if numero_personas > self._capacidad_maxima:
            raise CapacidadExcedidaError(self._nombre, self._capacidad_maxima, numero_personas)

        # Validar descuento adicional
        if not isinstance(descuento_adicional, (int, float)) or not (0.0 <= descuento_adicional < 1.0):
            raise ParametroServicioInvalidoError(
                "descuento_adicional", descuento_adicional,
                "El descuento debe estar entre 0.0 (sin descuento) y 0.99 (máximo)."
            )

    def describir(self) -> str:
        proyector_str = "Sí" if self._tiene_proyector else "No"
        return (
            f"[ RESERVA DE SALA ]\n"
            f"  ID            : {self._id}\n"
            f"  Nombre        : {self._nombre}\n"
            f"  Tarifa base   : ${self._tarifa_base:,.0f} COP/hora\n"
            f"  Capacidad máx.: {self._capacidad_maxima} personas\n"
            f"  Proyector     : {proyector_str}\n"
            f"  Descuento +4h : {self.DESCUENTO_LARGA_DURACION*100:.0f}%\n"
            f"  Estado        : {'Disponible' if self._disponible else 'No disponible'}"
        )


# =============================================================================
# SERVICIO 2: ALQUILER DE EQUIPO
# =============================================================================

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.

    Características:
    - Tarifa base por hora según tipo de equipo
    - Cargo adicional por seguro del equipo
    - Penalización si se supera el tiempo acordado
    - Descuento para alquileres de más de 8 horas
    """

    DESCUENTO_FULL_DAY = 0.15        # 15% de descuento si alquila 8+ horas
    HORAS_FULL_DAY = 8               # Umbral para el descuento de día completo
    FACTOR_SEGURO = 0.05             # 5% del valor como costo de seguro

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float,
                 tipo_equipo: str, requiere_capacitacion: bool = False):
        """
        Args:
            tipo_equipo: Categoría del equipo (ej: "Laptop", "Proyector", "Drone").
            requiere_capacitacion: Si el usuario debe recibir capacitación previa.
        """
        super().__init__(id_servicio, nombre, tarifa_base)

        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ParametroServicioInvalidoError(
                "tipo_equipo", tipo_equipo,
                "El tipo de equipo no puede estar vacío."
            )

        self._tipo_equipo = tipo_equipo
        self._requiere_capacitacion = requiere_capacitacion

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    def calcular_costo(self, duracion_horas: float, con_seguro: bool = True,
                       descuento_corporativo: float = 0.0,
                       con_impuesto: bool = True) -> float:
        """
        Calcula el costo del alquiler.

        Variantes (simulación de sobrecarga):
          - Sin seguro:    solo tarifa × horas
          - Con seguro:    suma 5% como costo de seguro
          - Con descuento: aplica descuento corporativo
          - Con impuesto:  aplica IVA 19% al total

        Args:
            duracion_horas: Horas de alquiler.
            con_seguro: Si se incluye seguro del equipo.
            descuento_corporativo: Porcentaje de descuento para empresas.
            con_impuesto: Si se aplica IVA al total.

        Returns:
            float: Costo total en COP.
        """
        try:
            self.validar_parametros(duracion_horas,
                                    descuento_corporativo=descuento_corporativo)

            # Cálculo base
            costo = self._tarifa_base * duracion_horas

            # Seguro del equipo: 5% del valor base
            if con_seguro:
                costo_seguro = costo * self.FACTOR_SEGURO
                costo += costo_seguro
                log.debug(f"AlquilerEquipo: seguro aplicado +${costo_seguro:,.2f}")

            # Descuento full-day (8+ horas)
            if duracion_horas >= self.HORAS_FULL_DAY:
                costo *= (1 - self.DESCUENTO_FULL_DAY)
                log.debug(f"AlquilerEquipo: descuento full-day aplicado")

            # Descuento corporativo adicional
            if descuento_corporativo > 0:
                costo *= (1 - descuento_corporativo)
                log.debug(f"AlquilerEquipo: descuento corporativo {descuento_corporativo*100:.0f}% aplicado")

            # IVA (usando método heredado de Servicio)
            if con_impuesto:
                costo = self._calcular_con_impuesto(costo)
                log.debug(f"AlquilerEquipo: IVA 19% aplicado")

            log.info(f"Costo calculado — {self._nombre}: ${costo:,.2f} COP ({duracion_horas}h)")
            return round(costo, 2)

        except (ParametroServicioInvalidoError, CalculoError):
            raise
        except Exception as e:
            raise CalculoError("AlquilerEquipo.calcular_costo", str(e)) from e

    def validar_parametros(self, duracion_horas: float,
                           descuento_corporativo: float = 0.0, **kwargs) -> None:
        """Valida duración y descuento corporativo."""

        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "La duración debe ser un número positivo."
            )
        if duracion_horas > 72:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "El alquiler no puede superar 72 horas (3 días)."
            )
        if not (0.0 <= descuento_corporativo < 1.0):
            raise ParametroServicioInvalidoError(
                "descuento_corporativo", descuento_corporativo,
                "El descuento corporativo debe estar entre 0.0 y 0.99."
            )

    def describir(self) -> str:
        capacitacion_str = "Requerida" if self._requiere_capacitacion else "No requerida"
        return (
            f"[ ALQUILER DE EQUIPO ]\n"
            f"  ID              : {self._id}\n"
            f"  Nombre          : {self._nombre}\n"
            f"  Tipo de equipo  : {self._tipo_equipo}\n"
            f"  Tarifa base     : ${self._tarifa_base:,.0f} COP/hora\n"
            f"  Seguro          : {self.FACTOR_SEGURO*100:.0f}% del valor base\n"
            f"  Descuento 8h+   : {self.DESCUENTO_FULL_DAY*100:.0f}%\n"
            f"  Capacitación    : {capacitacion_str}\n"
            f"  Estado          : {'Disponible' if self._disponible else 'No disponible'}"
        )


# =============================================================================
# SERVICIO 3: ASESORÍA ESPECIALIZADA
# =============================================================================

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesorías con expertos de Software FJ.

    Características:
    - Tarifa varía según nivel del asesor (Junior, Senior, Expert)
    - Modalidad: presencial o virtual (virtual tiene 10% de descuento)
    - Paquetes de horas con tarifas especiales
    - IVA aplicable según tipo de cliente
    """

    # Multiplicadores de tarifa según nivel del asesor
    MULTIPLICADORES_NIVEL = {
        "junior": 1.0,    # Tarifa base sin modificación
        "senior": 1.5,    # 50% más caro que Junior
        "expert": 2.0,    # El doble que Junior
    }

    DESCUENTO_VIRTUAL = 0.10   # 10% si la asesoría es virtual

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float,
                 nivel_asesor: str = "senior", area_especialidad: str = "General"):
        """
        Args:
            nivel_asesor: Nivel del asesor ('junior', 'senior', 'expert').
            area_especialidad: Área temática (ej: "Sistemas", "Redes", "IA").
        """
        super().__init__(id_servicio, nombre, tarifa_base)

        nivel_lower = nivel_asesor.lower().strip()
        if nivel_lower not in self.MULTIPLICADORES_NIVEL:
            raise ParametroServicioInvalidoError(
                "nivel_asesor", nivel_asesor,
                f"Nivel inválido. Opciones: {list(self.MULTIPLICADORES_NIVEL.keys())}"
            )

        self._nivel_asesor = nivel_lower
        self._area_especialidad = area_especialidad

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    def calcular_costo(self, duracion_horas: float, modalidad: str = "presencial",
                       numero_sesiones: int = 1, con_informe: bool = False) -> float:
        """
        Calcula el costo de la asesoría.

        Variantes (simulación de sobrecarga):
          - Básica:          tarifa × multiplicador_nivel × horas
          - Virtual:         aplica 10% de descuento
          - Multi-sesión:    multiplica por número de sesiones
          - Con informe:     suma $100,000 fijo por informe final

        Args:
            duracion_horas: Horas por sesión.
            modalidad: 'presencial' o 'virtual'.
            numero_sesiones: Cantidad de sesiones de asesoría.
            con_informe: Si se requiere informe escrito al final.

        Returns:
            float: Costo total en COP.
        """
        try:
            self.validar_parametros(duracion_horas, modalidad=modalidad,
                                    numero_sesiones=numero_sesiones)

            # Tarifa ajustada según nivel del asesor
            multiplicador = self.MULTIPLICADORES_NIVEL[self._nivel_asesor]
            tarifa_ajustada = self._tarifa_base * multiplicador

            # Cálculo base: tarifa ajustada × horas × número de sesiones
            costo = tarifa_ajustada * duracion_horas * numero_sesiones

            # Descuento por modalidad virtual
            if modalidad.lower() == "virtual":
                costo *= (1 - self.DESCUENTO_VIRTUAL)
                log.debug(f"Asesoria: descuento virtual {self.DESCUENTO_VIRTUAL*100:.0f}% aplicado")

            # Cargo fijo por informe escrito
            if con_informe:
                costo += 100_000
                log.debug("Asesoria: cargo por informe final +$100,000")

            log.info(f"Costo calculado — {self._nombre} ({self._nivel_asesor.title()}): "
                     f"${costo:,.2f} COP ({duracion_horas}h × {numero_sesiones} sesión(es))")
            return round(costo, 2)

        except (ParametroServicioInvalidoError,):
            raise
        except Exception as e:
            raise CalculoError("AsesoriaEspecializada.calcular_costo", str(e)) from e

    def validar_parametros(self, duracion_horas: float, modalidad: str = "presencial",
                           numero_sesiones: int = 1, **kwargs) -> None:
        """Valida duración, modalidad y número de sesiones."""

        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "La duración debe ser un número positivo."
            )
        if duracion_horas > 8:
            raise ParametroServicioInvalidoError(
                "duracion_horas", duracion_horas,
                "Una sesión de asesoría no puede superar 8 horas."
            )

        modalidades_validas = ["presencial", "virtual"]
        if modalidad.lower() not in modalidades_validas:
            raise ParametroServicioInvalidoError(
                "modalidad", modalidad,
                f"Modalidad inválida. Opciones: {modalidades_validas}"
            )

        if not isinstance(numero_sesiones, int) or numero_sesiones <= 0:
            raise ParametroServicioInvalidoError(
                "numero_sesiones", numero_sesiones,
                "El número de sesiones debe ser un entero positivo."
            )
        if numero_sesiones > 20:
            raise ParametroServicioInvalidoError(
                "numero_sesiones", numero_sesiones,
                "No se pueden programar más de 20 sesiones a la vez."
            )

    def describir(self) -> str:
        mult = self.MULTIPLICADORES_NIVEL[self._nivel_asesor]
        tarifa_real = self._tarifa_base * mult
        return (
            f"[ ASESORÍA ESPECIALIZADA ]\n"
            f"  ID              : {self._id}\n"
            f"  Nombre          : {self._nombre}\n"
            f"  Área            : {self._area_especialidad}\n"
            f"  Nivel asesor    : {self._nivel_asesor.title()}\n"
            f"  Tarifa base     : ${self._tarifa_base:,.0f} COP/hora\n"
            f"  Tarifa efectiva : ${tarifa_real:,.0f} COP/hora\n"
            f"  Desc. virtual   : {self.DESCUENTO_VIRTUAL*100:.0f}%\n"
            f"  Estado          : {'Disponible' if self._disponible else 'No disponible'}"
        )
