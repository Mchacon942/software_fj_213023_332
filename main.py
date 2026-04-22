"""
main.py
=======
Punto de entrada principal del sistema Software FJ.

Ejecuta al menos 10 operaciones completas de simulación, incluyendo:
  - Registros válidos e inválidos de clientes
  - Creación correcta e incorrecta de servicios
  - Reservas exitosas y fallidas
  - Confirmaciones, cancelaciones y procesamientos
  - Manejo de todos los tipos de excepciones

Autores: Grupo 213023_332
Integrantes:
    - Juan Sebastian Bernal Bermudez
    - Juan Fernando Capitani Giraldo
    - Maribel Chacon Garzon
    - Cristian Camilo Galindo Barragan
    - Junior David Mancipe Castiblanco

Curso: Programación 213023
Universidad Nacional Abierta y a Distancia — UNAD
"""

import sys
import os

# Ajustamos el path para que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import log
from utils.excepciones import (
    SoftwareFJError,
    DatosClienteInvalidosError,
    ClienteYaExisteError,
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
    CapacidadExcedidaError,
    DuracionInvalidaError,
    ReservaYaCanceladaError,
    ReservaYaConfirmadaError,
    CalculoError,
)
from modelos.cliente import Cliente
from servicios.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from modelos.reserva import Reserva, EstadoReserva
from gestion.gestores import GestorClientes, GestorServicios, GestorReservas


# =============================================================================
# FUNCIONES AUXILIARES DE PRESENTACIÓN
# =============================================================================

def encabezado(titulo: str, numero: int = None) -> None:
    """Imprime un encabezado visual para separar operaciones."""
    prefijo = f"[OP {str(numero).zfill(2)}]" if numero else "[INFO]"
    separador = "─" * 65
    print(f"\n{separador}")
    print(f"  {prefijo} {titulo}")
    print(separador)


def resultado_ok(mensaje: str) -> None:
    """Imprime un mensaje de operación exitosa."""
    print(f"  ✅ {mensaje}")


def resultado_error(mensaje: str) -> None:
    """Imprime un mensaje de error controlado."""
    print(f"  ⚠️  ERROR CONTROLADO: {mensaje}")


def separador_seccion(titulo: str) -> None:
    """Imprime un separador de sección mayor."""
    print(f"\n{'═'*65}")
    print(f"  {titulo}")
    print(f"{'═'*65}")


# =============================================================================
# INICIALIZACIÓN DEL SISTEMA
# =============================================================================

def inicializar_sistema():
    """Crea e inicializa los gestores del sistema."""
    gestor_clientes = GestorClientes()
    gestor_servicios = GestorServicios()
    gestor_reservas = GestorReservas()
    log.info("Sistema Software FJ inicializado correctamente.")
    return gestor_clientes, gestor_servicios, gestor_reservas


# =============================================================================
# BLOQUE DE SIMULACIONES
# =============================================================================

def ejecutar_simulaciones():
    """
    Ejecuta las 10+ operaciones de simulación completas.

    Estructura de las simulaciones:
      OP 01-03: Registro de clientes (válidos e inválidos)
      OP 04-06: Creación de servicios (válidos e inválidos)
      OP 07-10: Reservas (exitosas y fallidas)
      OP 11-13: Confirmaciones, cancelaciones y procesamiento
    """

    separador_seccion("SISTEMA INTEGRAL — SOFTWARE FJ")
    print("  Gestión de Clientes, Servicios y Reservas")
    print("  Curso: Programación 213023 | Grupo: 213023_332")

    # Inicializamos gestores
    gestores = inicializar_sistema()
    gc, gs, gr = gestores  # Desempaquetamos para comodidad

    # ===========================================================
    # OP 01 — Registro de cliente VÁLIDO
    # ===========================================================
    encabezado("Registro de cliente VÁLIDO — Juan Sebastian Bernal", 1)
    try:
        cliente1 = Cliente(
            id_cliente="CLI001",
            nombre="Juan Sebastian Bernal Bermudez",
            email="jsbernal@unad.edu.co",
            telefono="3101234567",
            ciudad="Bogotá"
        )
        gc.registrar(cliente1)
        resultado_ok(f"Cliente registrado: {cliente1}")
        print(f"\n{cliente1.describir()}")

    except DatosClienteInvalidosError as e:
        resultado_error(f"Datos inválidos: {e}")
    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 02 — Registro de cliente VÁLIDO #2
    # ===========================================================
    encabezado("Registro de cliente VÁLIDO — Maribel Chacon", 2)
    try:
        cliente2 = Cliente(
            id_cliente="CLI002",
            nombre="Maribel Chacon Garzon",
            email="mchacon@empresa.com",
            telefono="3209876543",
            ciudad="Medellín"
        )
        gc.registrar(cliente2)
        resultado_ok(f"Cliente registrado: {cliente2}")

        # Registramos un tercer cliente para las simulaciones siguientes
        cliente3 = Cliente(
            id_cliente="CLI003",
            nombre="Junior David Mancipe Castiblanco",
            email="jmancipe@softwarefj.co",
            telefono="3154445566",
            ciudad="Cali"
        )
        gc.registrar(cliente3)
        resultado_ok(f"Cliente registrado: {cliente3}")

    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 03 — Registro de cliente INVÁLIDO (email mal formado)
    # ===========================================================
    encabezado("Registro de cliente INVÁLIDO — email incorrecto", 3)
    try:
        cliente_malo = Cliente(
            id_cliente="CLI999",
            nombre="Cliente Invalido",
            email="esto-no-es-un-email",   # ← Email inválido
            telefono="3001112233",
            ciudad="Bogotá"
        )
        gc.registrar(cliente_malo)
        resultado_ok("(Esto no debería ejecutarse)")

    except DatosClienteInvalidosError as e:
        # Capturamos el error específico de datos inválidos
        resultado_error(str(e))
        log.error(f"Intento de registro con datos inválidos: {e}")

    # OP 03b — Cliente duplicado
    encabezado("Registro de cliente DUPLICADO — ID ya existe", "3b")
    try:
        cliente_dup = Cliente(
            id_cliente="CLI001",   # ← ID ya registrado
            nombre="Cristian Camilo Galindo Barragan",
            email="cgalindo@unad.edu.co",
            telefono="3177778888",
            ciudad="Bucaramanga"
        )
        gc.registrar(cliente_dup)

    except ClienteYaExisteError as e:
        resultado_error(str(e))
    except DatosClienteInvalidosError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 04 — Creación de servicios VÁLIDOS
    # ===========================================================
    encabezado("Creación de servicios VÁLIDOS", 4)
    try:
        # Servicio 1: Sala de conferencias
        sala_conf = ReservaSala(
            id_servicio="SAL001",
            nombre="Sala de Conferencias A",
            tarifa_base=80_000,          # $80,000 COP/hora
            capacidad_maxima=20,
            tiene_proyector=True
        )
        gs.agregar(sala_conf)
        resultado_ok(f"Servicio agregado: {sala_conf}")
        print(f"\n{sala_conf.describir()}")

        # Servicio 2: Alquiler de laptop
        laptop = AlquilerEquipo(
            id_servicio="EQU001",
            nombre="Laptop HP ProBook 450",
            tarifa_base=25_000,          # $25,000 COP/hora
            tipo_equipo="Laptop",
            requiere_capacitacion=False
        )
        gs.agregar(laptop)
        resultado_ok(f"Servicio agregado: {laptop}")

        # Servicio 3: Asesoría en Sistemas
        asesoria_sistemas = AsesoriaEspecializada(
            id_servicio="ASE001",
            nombre="Asesoría en Arquitectura de Software",
            tarifa_base=120_000,         # $120,000 COP/hora
            nivel_asesor="expert",
            area_especialidad="Arquitectura de Software"
        )
        gs.agregar(asesoria_sistemas)
        resultado_ok(f"Servicio agregado: {asesoria_sistemas}")
        print(f"\n{asesoria_sistemas.describir()}")

        # Servicio 4: Sala pequeña (para pruebas de capacidad)
        sala_pequena = ReservaSala(
            id_servicio="SAL002",
            nombre="Sala Ejecutiva B",
            tarifa_base=50_000,
            capacidad_maxima=4,
            tiene_proyector=False
        )
        gs.agregar(sala_pequena)
        resultado_ok(f"Servicio agregado: {sala_pequena}")

    except ParametroServicioInvalidoError as e:
        resultado_error(str(e))
    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 05 — Creación de servicio con tarifa INVÁLIDA
    # ===========================================================
    encabezado("Creación de servicio con tarifa INVÁLIDA (negativa)", 5)
    try:
        servicio_invalido = AlquilerEquipo(
            id_servicio="EQU999",
            nombre="Proyector Roto",
            tarifa_base=-5000,           # ← Tarifa negativa, inválida
            tipo_equipo="Proyector"
        )
        gs.agregar(servicio_invalido)

    except ParametroServicioInvalidoError as e:
        resultado_error(str(e))
        log.error(f"Intento de crear servicio con parámetros inválidos: {e}")

    # ===========================================================
    # OP 06 — Creación de asesoría con nivel INVÁLIDO
    # ===========================================================
    encabezado("Creación de asesoría con nivel de asesor INVÁLIDO", 6)
    try:
        asesoria_invalida = AsesoriaEspecializada(
            id_servicio="ASE999",
            nombre="Asesoría Fantasma",
            tarifa_base=100_000,
            nivel_asesor="dios",         # ← Nivel no reconocido
            area_especialidad="Misterio"
        )
        gs.agregar(asesoria_invalida)

    except ParametroServicioInvalidoError as e:
        resultado_error(str(e))
        log.warning(f"Servicio rechazado por nivel inválido: {e}")

    # ===========================================================
    # OP 07 — Reserva EXITOSA con cálculo de costo completo
    # ===========================================================
    encabezado("Reserva EXITOSA — Sala de Conferencias (5 horas, videoconferencia)", 7)
    try:
        reserva1 = Reserva(
            id_reserva=gr.generar_id(),
            cliente=cliente1,
            servicio=sala_conf,
            duracion_horas=5,
            numero_personas=15,
            con_videoconferencia=True,
            descuento_adicional=0.05    # 5% de descuento corporativo
        )
        gr.registrar(reserva1)

        # Confirmamos y obtenemos el costo
        costo = reserva1.confirmar()
        resultado_ok(f"Reserva confirmada. Costo total: ${costo:,.2f} COP")
        print(f"\n{reserva1.describir()}")

    except ServicioNoDisponibleError as e:
        resultado_error(str(e))
    except CapacidadExcedidaError as e:
        resultado_error(str(e))
    except DuracionInvalidaError as e:
        resultado_error(str(e))
    except CalculoError as e:
        resultado_error(str(e))
    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 08 — Reserva FALLIDA por capacidad excedida
    # ===========================================================
    encabezado("Reserva FALLIDA — Sala Ejecutiva B (capacidad excedida)", 8)
    try:
        reserva_cap = Reserva(
            id_reserva="RES_CAP",
            cliente=cliente2,
            servicio=sala_pequena,     # Sala con máximo 4 personas
            duracion_horas=2,
            numero_personas=10         # ← 10 personas, excede el máximo de 4
        )
        gr.registrar(reserva_cap)
        reserva_cap.confirmar()

    except CapacidadExcedidaError as e:
        resultado_error(str(e))
        log.error(f"Reserva rechazada por capacidad excedida: {e}")
    except CalculoError as e:
        resultado_error(str(e))
        log.error(f"Error de cálculo en reserva: {e}")

    # ===========================================================
    # OP 09 — Reserva FALLIDA por duración inválida
    # ===========================================================
    encabezado("Reserva FALLIDA — Duración de cero horas", 9)
    try:
        reserva_dur = Reserva(
            id_reserva="RES_DUR",
            cliente=cliente1,
            servicio=laptop,
            duracion_horas=0            # ← Duración de 0 no es válida
        )
        gr.registrar(reserva_dur)

    except DuracionInvalidaError as e:
        resultado_error(str(e))
        log.error(f"Reserva rechazada por duración inválida: {e}")

    # ===========================================================
    # OP 10 — Reserva EXITOSA de alquiler de equipo (full-day)
    # ===========================================================
    encabezado("Reserva EXITOSA — Alquiler laptop 8 horas con descuento full-day", 10)
    try:
        reserva2 = Reserva(
            id_reserva=gr.generar_id(),
            cliente=cliente2,
            servicio=laptop,
            duracion_horas=8,
            con_seguro=True,
            descuento_corporativo=0.10,  # 10% corporativo
            con_impuesto=True
        )
        gr.registrar(reserva2)

        # Usamos procesar() en lugar de confirmar() para ver el resumen completo
        resumen = reserva2.procesar()
        resultado_ok(resumen["mensaje"])
        print(f"\n{reserva2.describir()}")

    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 11 — Reserva EXITOSA de asesoría especializada (virtual)
    # ===========================================================
    encabezado("Reserva EXITOSA — Asesoría Expert 3 sesiones virtuales con informe", 11)
    try:
        reserva3 = Reserva(
            id_reserva=gr.generar_id(),
            cliente=cliente3,
            servicio=asesoria_sistemas,
            duracion_horas=2,
            modalidad="virtual",
            numero_sesiones=3,
            con_informe=True
        )
        gr.registrar(reserva3)
        costo = reserva3.confirmar()
        resultado_ok(f"Asesoría confirmada — 3 sesiones de 2h c/u. Total: ${costo:,.2f} COP")
        print(f"\n{reserva3.describir()}")

    except SoftwareFJError as e:
        resultado_error(str(e))

    # ===========================================================
    # OP 12 — Cancelación de reserva y manejo de doble cancelación
    # ===========================================================
    encabezado("Cancelación de reserva y manejo de doble cancelación", 12)
    try:
        # Creamos una reserva para cancelar
        reserva_cancelar = Reserva(
            id_reserva=gr.generar_id(),
            cliente=cliente1,
            servicio=sala_conf,
            duracion_horas=2,
            numero_personas=5
        )
        gr.registrar(reserva_cancelar)
        reserva_cancelar.confirmar()

        # Primera cancelación → EXITOSA
        reserva_cancelar.cancelar("Cliente solicitó reprogramación")
        resultado_ok(f"Reserva cancelada correctamente. Estado: {reserva_cancelar.estado.value}")

        # Segunda cancelación → debe lanzar excepción
        reserva_cancelar.cancelar("Intentando cancelar de nuevo")
        resultado_ok("(Esto no debería ejecutarse)")

    except ReservaYaCanceladaError as e:
        resultado_error(str(e))
        log.warning(f"Doble cancelación detectada: {e}")

    # ===========================================================
    # OP 13 — Intento de confirmar reserva ya confirmada
    # ===========================================================
    encabezado("Intento de confirmar reserva ya CONFIRMADA", 13)
    try:
        # reserva1 ya fue confirmada en OP 07
        reserva1.confirmar()           # ← Debe lanzar excepción
        resultado_ok("(Esto no debería ejecutarse)")

    except ReservaYaConfirmadaError as e:
        resultado_error(str(e))
        log.info(f"Segundo intento de confirmación manejado correctamente: {e}")

    # ===========================================================
    # OP 14 — Reserva sobre servicio NO DISPONIBLE
    # ===========================================================
    encabezado("Reserva FALLIDA — Servicio desactivado", 14)
    try:
        # Desactivamos el servicio de laptop
        laptop.disponible = False
        resultado_ok("Servicio 'laptop' desactivado temporalmente.")

        # Intentamos reservar sobre el servicio desactivado
        reserva_no_disp = Reserva(
            id_reserva="RES_ND",
            cliente=cliente2,
            servicio=laptop,           # ← No disponible
            duracion_horas=3
        )
        gr.registrar(reserva_no_disp)

    except ServicioNoDisponibleError as e:
        resultado_error(str(e))
        log.warning(f"Reserva sobre servicio no disponible: {e}")
    finally:
        # Reactivamos el servicio (bloque finally garantiza que siempre se ejecute)
        laptop.disponible = True
        print("  🔄 Servicio 'laptop' reactivado en bloque finally.")

    # ===========================================================
    # OP 15 — Encadenamiento de excepciones
    # ===========================================================
    encabezado("Encadenamiento de excepciones — Cálculo con parámetros imposibles", 15)
    try:
        # Intentamos calcular costo con modalidad inválida en asesoría
        costo_malo = asesoria_sistemas.calcular_costo(
            duracion_horas=2,
            modalidad="holografica",   # ← Modalidad no válida
            numero_sesiones=1
        )

    except ParametroServicioInvalidoError as e:
        resultado_error(str(e))
        # Encadenamos: lanzamos CalculoError que referencia la excepción original
        try:
            raise CalculoError("simulacion_15", "Fallo provocado por modalidad inválida") from e
        except CalculoError as ce:
            print(f"  🔗 Excepción encadenada capturada: {ce}")
            print(f"     Causa original: {ce.__cause__}")
            log.error(f"Excepción encadenada: {ce} | Causa: {ce.__cause__}")

    # ===========================================================
    # RESUMEN FINAL DEL SISTEMA
    # ===========================================================
    separador_seccion("RESUMEN FINAL DEL SISTEMA")

    print(f"\n  {'Clientes registrados':<30}: {gc.total()}")
    print(f"  {'Servicios disponibles':<30}: {len(gs.listar_disponibles())}/{gs.total()}")
    print(f"  {'Total de reservas':<30}: {gr.total()}")

    print("\n  Reservas por estado:")
    resumen_estados = gr.resumen()
    for estado, cantidad in resumen_estados.items():
        print(f"    • {estado:<15}: {cantidad}")

    print("\n  Listado completo de reservas:")
    for r in gr.listar_todas():
        print(f"    • {r}")

    print("\n  Clientes con sus reservas:")
    for cliente in gc.listar_todos():
        print(f"    • {cliente} — {cliente.total_reservas()} reserva(s)")

    separador_seccion("SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print("  El sistema Software FJ operó de forma estable ante todos los")
    print("  errores presentados. Revisar archivo de logs para detalles.")
    print(f"  {'─'*55}\n")

    log.info("Simulación completa finalizada. Sistema estable.")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    try:
        ejecutar_simulaciones()

    except KeyboardInterrupt:
        # El usuario interrumpió con Ctrl+C
        print("\n\n  ⚠️  Ejecución interrumpida por el usuario.")
        log.warning("Ejecución interrumpida por el usuario (KeyboardInterrupt).")

    except Exception as e:
        # Cualquier error no controlado que llegue hasta aquí
        print(f"\n  ❌ Error crítico no controlado: {e}")
        log.critical(f"Error crítico en main: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Se ejecuta siempre, haya o no error
        log.info("Proceso principal finalizado.")
