# 🏢 Sistema Integral de Gestión de Clientes, Servicios y Reservas
### Software FJ — Curso Programación 213023 | Grupo 213023_332

---

## 📋 Descripción del Proyecto

Sistema orientado a objetos desarrollado en **Python** para gestionar clientes, servicios y reservas de la empresa **Software FJ**, que ofrece:

- 🏠 Reservas de salas de reuniones
- 💻 Alquiler de equipos tecnológicos
- 🎓 Asesorías especializadas

El sistema implementa de forma rigurosa los principios de **POO** y **manejo avanzado de excepciones**, operando sin base de datos (gestión mediante objetos, listas y archivos de logs).

---

## 👥 Integrantes del Grupo 213023_332

| Nombre | Rol en GitHub |
|--------|---------------|
| Juan Sebastian Bernal Bermudez | Contribuidor |
| Juan Fernando Capitani Giraldo | Contribuidor |
| Maribel Chacon Garzon | Contribuidor |
| Cristian Camilo Galindo Barragan | Contribuidor |
| Junior David Mancipe Castiblanco | Contribuidor |

---

## 🏗️ Arquitectura del Proyecto

```
software_fj/
│
├── main.py                     # Punto de entrada — 15 operaciones de simulación
│
├── modelos/                    # Entidades del dominio
│   ├── __init__.py
│   ├── cliente.py              # EntidadBase (abstracta) + Cliente
│   └── reserva.py              # Reserva + EstadoReserva (Enum)
│
├── servicios/                  # Catálogo de servicios
│   ├── __init__.py
│   └── servicios.py            # Servicio (abstracta) + ReservaSala
│                               #   + AlquilerEquipo + AsesoriaEspecializada
│
├── gestion/                    # Repositorios en memoria
│   ├── __init__.py
│   └── gestores.py             # GestorClientes + GestorServicios + GestorReservas
│
├── utils/                      # Utilidades transversales
│   ├── __init__.py
│   ├── excepciones.py          # 15 excepciones personalizadas
│   └── logger.py               # Sistema de logging centralizado
│
└── logs/                       # Archivos de log generados automáticamente
    └── software_fj_YYYY-MM-DD.log
```

---

## 🧱 Principios POO Implementados

### Abstracción
- `EntidadBase` (ABC): contrato base para toda entidad del sistema
- `Servicio` (ABC): interfaz común para todos los servicios

### Herencia
```
EntidadBase  ──▶  Cliente
Servicio     ──▶  ReservaSala
             ──▶  AlquilerEquipo
             ──▶  AsesoriaEspecializada
```

### Polimorfismo
Cada servicio implementa `calcular_costo()`, `describir()` y `validar_parametros()` con comportamiento propio.

### Encapsulación
- Atributos privados (`_nombre`, `_email`, etc.)
- Acceso mediante `@property` con validación integrada
- Setters que lanzan excepciones en datos inválidos

---

## ⚠️ Manejo de Excepciones

### Jerarquía de Excepciones Personalizadas

```
SoftwareFJError
├── ClienteError
│   ├── ClienteYaExisteError
│   ├── ClienteNoEncontradoError
│   └── DatosClienteInvalidosError
├── ServicioError
│   ├── ServicioNoDisponibleError
│   ├── ServicioNoEncontradoError
│   ├── ParametroServicioInvalidoError
│   └── CapacidadExcedidaError
├── ReservaError
│   ├── ReservaNoEncontradaError
│   ├── ReservaYaCanceladaError
│   ├── ReservaYaConfirmadaError
│   └── DuracionInvalidaError
└── CalculoError
```

### Patrones de Manejo Usados

| Patrón | Dónde se usa |
|--------|-------------|
| `try/except` | Validaciones en gestores y servicios |
| `try/except/else` | Método `confirmar()` en Reserva |
| `try/except/finally` | Métodos `procesar()` y `cancelar()` en Reserva |
| Encadenamiento (`raise ... from e`) | OP-15 y cálculos de costo |

---

## 🚀 Cómo Ejecutar

### Requisitos
- Python 3.8 o superior
- No requiere librerías externas (solo módulos estándar)

### Ejecución

```bash
# Clonar el repositorio
git clone https://github.com/[usuario]/software_fj_213023_332.git
cd software_fj_213023_332

# Ejecutar la simulación completa
python main.py
```

El sistema generará automáticamente un archivo de log en `logs/software_fj_YYYY-MM-DD.log`.

---

## 📊 Operaciones Simuladas

| # | Operación | Resultado Esperado |
|---|-----------|-------------------|
| 01 | Registro de cliente válido | ✅ Éxito |
| 02 | Registro de 2 clientes válidos | ✅ Éxito |
| 03 | Registro con email inválido | ⚠️ DatosClienteInvalidosError |
| 3b | Registro de cliente duplicado | ⚠️ ClienteYaExisteError |
| 04 | Creación de 4 servicios válidos | ✅ Éxito |
| 05 | Servicio con tarifa negativa | ⚠️ ParametroServicioInvalidoError |
| 06 | Asesoría con nivel inválido | ⚠️ ParametroServicioInvalidoError |
| 07 | Reserva sala 5h + videoconf | ✅ $555,750 COP |
| 08 | Reserva con capacidad excedida | ⚠️ CapacidadExcedidaError |
| 09 | Reserva con duración 0 horas | ⚠️ DuracionInvalidaError |
| 10 | Alquiler laptop 8h full-day | ✅ $191,173.50 COP |
| 11 | Asesoría expert 3 sesiones virtual | ✅ $1,396,000 COP |
| 12 | Cancelación + doble cancelación | ✅ / ⚠️ ReservaYaCanceladaError |
| 13 | Confirmar reserva ya confirmada | ⚠️ ReservaYaConfirmadaError |
| 14 | Reserva sobre servicio inactivo | ⚠️ ServicioNoDisponibleError |
| 15 | Encadenamiento de excepciones | 🔗 CalculoError from ParametroError |

---

## 📁 Logs

Cada ejecución genera un archivo de log con formato:
```
2026-04-22 16:27:14 | INFO     | SoftwareFJ | Reserva 'RES0001' CONFIRMADA. Costo: $555,750.00
2026-04-22 16:27:14 | ERROR    | SoftwareFJ | [ERR_DATO_CLIENTE_INVALIDO] email inválido
2026-04-22 16:27:14 | WARNING  | SoftwareFJ | Doble cancelación detectada
```

---

## 📚 Referencias

- Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html
- Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RA-MA Editorial.
- Romano, F., Baka, B., & Phillips, D. (2019). *Getting Started with Python*. Packt Publishing.

---

**Universidad Nacional Abierta y a Distancia — UNAD**  
Escuela de Ciencias Básicas Tecnología e Ingeniería — ECBTI  
Curso: Programación 213023 | Fase 4
