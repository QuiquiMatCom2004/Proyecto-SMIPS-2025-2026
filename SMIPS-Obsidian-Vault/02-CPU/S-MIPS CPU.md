# S-MIPS CPU (Central Processing Unit)

**Tipo**: Componente Integrador Superior
**Estado**: 🟡 #parcial **52% IMPLEMENTADO**
**Ubicación**: `s-mips.circ` → CPU
**Complejidad**: ⭐⭐⭐⭐⭐ Máxima Complejidad (integra todo el sistema)
**Prioridad**: 🔴 CRÍTICA

## Descripción

El CPU es el componente de nivel superior que integra TODOS los elementos del procesador S-MIPS. Contiene tres grandes bloques: Control Unit, Memory Control, y Data Path, coordinando la ejecución completa del ciclo de instrucción.

## Razón por la que esta carpeta existe

La carpeta `02-CPU/` representa el **nivel jerárquico superior** del procesador en Logisim. En el archivo `s-mips.circ`, existe un componente llamado "CPU" que contiene dentro:
- Control Unit
- Memory Control
- Data Path

Este archivo documenta cómo estos tres componentes principales se **integran** y **comunican** entre sí para formar el procesador completo.

## Arquitectura del CPU

```
┌───────────────────────────────────────────────────────────────────┐
│                          S-MIPS CPU                               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    CONTROL UNIT 🔴                          │ │
│  │  • FSM de 12 estados                                        │ │
│  │  • Coordina fetch-decode-execute-writeback                  │ │
│  │  • Genera señales de control para Data Path                │ │
│  │  • Maneja timing del ciclo de instrucción                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│         │                    │                    │               │
│         │ (señales control)  │ (START/END)        │ (OPCODE)      │
│         ↓                    ↓                    ↓               │
│  ┌─────────────────┐  ┌────────────────────────────────────┐     │
│  │ MEMORY CONTROL  │  │         DATA PATH                  │     │
│  │      🔴         │  │            🟡                      │     │
│  │                 │  │                                    │     │
│  │ • State Machine │  │  ┌──────────────────────────┐     │     │
│  │ • Address Trans │  │  │  Instruction Register    │     │     │
│  │ • Endian Conv   │  │  └──────────────────────────┘     │     │
│  │ • Word Selector │  │              ↓                    │     │
│  │ • MASK Gen      │  │  ┌──────────────────────────┐     │     │
│  └─────────────────┘  │  │  Instruction Decoder ✅  │     │     │
│         ↓             │  └──────────────────────────┘     │     │
│     (hacia RAM)       │     ↓         ↓         ↓         │     │
│                       │  ┌────┐   ┌────┐   ┌──────┐      │     │
│                       │  │Reg │   │ALU │   │Branch│      │     │
│                       │  │File│   │ ✅ │   │Ctrl ✅│     │     │
│                       │  │ ✅ │   └────┘   └──────┘      │     │
│                       │  └────┘                           │     │
│                       └────────────────────────────────────┘     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
            ↓                                       ↑
            │ (ADDR, DATA_WRITE, R/W, CS)          │ (DATA_READ)
            └───────────────────────────────────────┘
                            RAM (externo)
```

## Interfaz Externa del CPU

### Entradas desde S-MIPS Board

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `CLK` | 1 bit | Sistema | Reloj del sistema (todos los componentes) |
| `RESET` | 1 bit | Sistema | Reset global del CPU |
| `RAM_DATA_IN` | 128 bits | RAM | Bloque de 4 words leído de RAM (O0-O3) |
| `RT` | N bits | RAM | Read Time - ciclos de lectura |
| `WT` | N bits | RAM | Write Time - ciclos de escritura |

### Salidas hacia S-MIPS Board

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `RAM_ADDR` | 16 bits | RAM | Dirección de bloque en RAM |
| `RAM_CS` | 1 bit | RAM | Chip Select (activar RAM) |
| `RAM_RW` | 1 bit | RAM | Read/Write (0=read, 1=write) |
| `RAM_DATA_OUT` | 128 bits | RAM | Bloque a escribir (I0-I3) |
| `RAM_MASK` | 4 bits | RAM | Máscara de bancos activos |
| `TTY_OUT` | 7 bits | Terminal | Output para instrucción TTY |
| `KBD_IN` | 8 bits | Teclado | Input de teclado |
| `HALT` | 1 bit | Sistema | Señal de detención |

## Tres Bloques Principales

### 1. [[Control Unit]] - El Cerebro 🔴

**Ubicación**: `s-mips.circ` → CPU → Control Unit

**Función**: Orquestar todo el ciclo de instrucción mediante un FSM.

**Estados**:
```
IDLE → START_FETCH → WAIT_INST_READ → LOAD_INST →
DECODE → EXECUTE → CHECK_MEM → WAIT_MEM_READ →
WAIT_MEM_WRITE → WRITEBACK → UPDATE_PC → HALT
```

**Señales que genera**:
- `LOAD_INST`: Cargar instrucción en IR
- `REG_WRITE`: Escribir en Register File
- `MEM_READ`, `MEM_WRITE`: Operaciones de memoria
- `ALU_SRC`, `REG_DST`, `MEM_TO_REG`: Control de multiplexores
- `MC_START`: Iniciar Memory Control
- `BRANCH`, `JUMP`: Control de flujo

**Señales que recibe**:
- `OPCODE`, `FUNCT`: Para decidir qué hacer
- `MC_END`: Memory Control completó operación
- `ZERO`, `NEGATIVE`: Flags de ALU para branches

**Estado**: 🔴 **NO IMPLEMENTADO** (bloqueante crítico)

**Archivo**: [[Control Unit]]

---

### 2. [[Memory Control]] - Interfaz con RAM 🔴

**Ubicación**: `s-mips.circ` → CPU → Memory Control

**Función**: Manejar el acceso asíncrono a RAM con timing correcto.

**Subcomponentes**:

1. **Memory State Machine**:
   - IDLE → LOAD_ADDR → WAIT_CYCLE → COMPLETE
   - Cuenta RT/WT cycles

2. **Address Translator**:
   - 32-bit byte address → 16-bit block address
   - `block_addr = ADDRESS[19:4]`
   - `word_offset = ADDRESS[3:2]`

3. **Little-Endian Converter**:
   - CPU (little-endian) ↔ RAM (big-endian)
   - Bit-reverse: swap bit 0↔31, 1↔30, ..., 15↔16

4. **Word Selector**:
   - Seleccionar palabra correcta de bloque (4 words)
   - Basado en word_offset [3:2]

5. **MASK Generator**:
   - Generar máscara de 4 bits para bancos
   - 1 bit por banco (Bank0-Bank3)

**Señales de control**:
- `MC_START`: Iniciar operación
- `MC_RW`: Read (0) o Write (1)
- `MC_ADDRESS`: Dirección de 32 bits
- `MC_END`: Operación completada

**Estado**: 🔴 **NO IMPLEMENTADO** (bloqueante)

**Archivo**: [[Memory Control]]

---

### 3. [[Data Path]] - Procesamiento de Datos 🟡

**Ubicación**: `s-mips.circ` → CPU → Data Path

**Función**: Ejecutar las operaciones sobre los datos.

**Subcomponentes**:
- ✅ [[Instruction Register]] - Almacenar instrucción actual
- ✅ [[Instruction Decoder]] - Decodificar 40+ instrucciones
- ✅ [[Register File]] - 32 registros + Hi/Lo
- ✅ [[ALU]] - Operaciones aritméticas/lógicas
- ✅ [[Branch Control]] - Cálculo de PC
- ✅ [[Program Counter]] - Contador de programa
- 🔴 [[Random Generator]] - LFSR para RND
- ✅ [[MUX Writeback]] - Selección de dato a escribir
- ✅ MUX ALU_B, MUX Rd/Rt
- ✅ Sign/Zero Extenders

**Estado**: 🟡 **90% IMPLEMENTADO** (solo falta Random Generator)

**Archivo**: [[Data Path]]

---

## Flujo de Ejecución del CPU

### Ciclo Completo de una Instrucción ADD

```
Ciclo 1-N: FETCH
┌─────────────────────────────────────────────────┐
│ Control Unit (START_FETCH)                      │
│   → Activa MC_START                             │
│                                                 │
│ Memory Control                                  │
│   → Traduce PC a block address                  │
│   → Envía RAM_ADDR, RAM_CS=1, RAM_RW=0         │
│   → Espera RT cycles                            │
│                                                 │
│ RAM                                             │
│   → Lee bloque (4 words)                        │
│   → Devuelve en RAM_DATA_IN                     │
│                                                 │
│ Memory Control                                  │
│   → Convierte big-endian → little-endian        │
│   → Selecciona palabra correcta                 │
│   → Activa MC_END                               │
│                                                 │
│ Control Unit (WAIT_INST_READ)                   │
│   → Detecta MC_END                              │
│   → Pasa a LOAD_INST                            │
└─────────────────────────────────────────────────┘

Ciclo N+1: DECODE
┌─────────────────────────────────────────────────┐
│ Control Unit (LOAD_INST)                        │
│   → Activa LOAD_INST = 1                        │
│                                                 │
│ Data Path - Instruction Register                │
│   → Carga instrucción: 0x00221820              │
│                                                 │
│ Control Unit (DECODE)                           │
│   → Lee OPCODE = 0x00                           │
│                                                 │
│ Data Path - Instruction Decoder                 │
│   → Extrae: opcode=0, rs=1, rt=2, rd=3, funct=0x20│
│   → Genera: ALU_OP=ADD, REG_WRITE=1, REG_DST=1 │
└─────────────────────────────────────────────────┘

Ciclo N+2: EXECUTE
┌─────────────────────────────────────────────────┐
│ Control Unit (EXECUTE)                          │
│   → Mantiene señales de control activas         │
│                                                 │
│ Data Path - Register File                       │
│   → READ_REG_1 = 1 → READ_DATA_1 = R1 = 10     │
│   → READ_REG_2 = 2 → READ_DATA_2 = R2 = 20     │
│                                                 │
│ Data Path - MUX ALU_B                           │
│   → ALU_SRC=0 → selecciona R2                   │
│                                                 │
│ Data Path - ALU                                 │
│   → A = 10, B = 20, ALU_OP = ADD                │
│   → RESULT = 30                                 │
│   → ZERO = 0, NEGATIVE = 0                      │
│                                                 │
│ Data Path - Branch Control                      │
│   → PC_NEXT = PC + 4 (secuencial)               │
└─────────────────────────────────────────────────┘

Ciclo N+3: CHECK_MEM
┌─────────────────────────────────────────────────┐
│ Control Unit (CHECK_MEM)                        │
│   → ADD no requiere memoria                     │
│   → Salta directamente a WRITEBACK              │
└─────────────────────────────────────────────────┘

Ciclo N+4: WRITEBACK
┌─────────────────────────────────────────────────┐
│ Control Unit (WRITEBACK)                        │
│   → Activa REG_WRITE = 1                        │
│                                                 │
│ Data Path - MUX Rd/Rt                           │
│   → REG_DST=1 → WRITE_REG = 3 (Rd)             │
│                                                 │
│ Data Path - MUX Writeback                       │
│   → Selecciona ALU_RESULT = 30                  │
│                                                 │
│ Data Path - Register File                       │
│   → R3 ← 30                                     │
│                                                 │
│ Control Unit (UPDATE_PC)                        │
│   → PC ← PC_NEXT = PC + 4                       │
│   → Vuelve a IDLE                               │
└─────────────────────────────────────────────────┘

Total: RT + 4 cycles (sin caché)
```

### Ciclo con Instruction Cache (Cuando se implemente)

```
Ciclo 1: FETCH (con I-Cache)
┌─────────────────────────────────────────────────┐
│ Control Unit (START_FETCH)                      │
│   → Activa I_CACHE_FETCH_REQ                    │
│                                                 │
│ Instruction Cache                               │
│   → Verifica hit/miss                           │
│                                                 │
│   CASO HIT (80% del tiempo):                    │
│   → I_CACHE_READY = 1 (mismo ciclo)             │
│   → Instrucción disponible                      │
│                                                 │
│   CASO MISS (20% del tiempo):                   │
│   → Solicita a Memory Control                   │
│   → Memory Control → RAM (RT cycles)            │
│   → Carga bloque en caché                       │
│   → I_CACHE_READY = 1 después de RT cycles      │
└─────────────────────────────────────────────────┘

Total con hit: 1 + 3 cycles = 4 cycles
Total con miss: RT + 4 cycles
Promedio con 80% hit: 0.8×4 + 0.2×(RT+4) ≈ 5 cycles (si RT=10)
Mejora: ~3x más rápido
```

## Señales Internas entre Bloques

### Control Unit → Data Path

| Señal | Descripción |
|-------|-------------|
| `LOAD_INST` | Cargar instrucción en IR |
| `REG_WRITE` | Escribir en Register File |
| `REG_DST` | Seleccionar Rd o Rt como destino |
| `ALU_SRC` | Seleccionar Rt o Immediate para ALU |
| `MEM_TO_REG` | Seleccionar ALU o Memory para writeback |
| `BRANCH` | Instrucción es branch |
| `JUMP` | Instrucción es jump |

### Data Path → Control Unit

| Señal | Descripción |
|-------|-------------|
| `OPCODE[5:0]` | Código de operación |
| `FUNCT[5:0]` | Function code (R-type) |
| `ZERO` | Flag: resultado ALU = 0 |
| `NEGATIVE` | Flag: resultado ALU < 0 |

### Control Unit → Memory Control

| Señal | Descripción |
|-------|-------------|
| `MC_START` | Iniciar operación de memoria |
| `MC_RW` | Read (0) o Write (1) |

### Memory Control → Control Unit

| Señal | Descripción |
|-------|-------------|
| `MC_END` | Operación completada |

### Data Path → Memory Control

| Señal | Descripción |
|-------|-------------|
| `PC` | Program Counter (para fetch) |
| `ADDRESS` | Dirección calculada (LW/SW) |
| `WRITE_DATA` | Dato a escribir (SW) |

### Memory Control → Data Path

| Señal | Descripción |
|-------|-------------|
| `INSTRUCTION` | Instrucción leída |
| `MEMORY_DATA` | Dato leído (LW) |

## Integración con Cache (Cuando se implemente)

### Sin Caché (Estado actual)

```
Control Unit → Memory Control → RAM
Data Path → Memory Control → RAM
```

Todas las operaciones de memoria van directo a Memory Control.

### Con Instruction Cache

```
Control Unit → Instruction Cache → Memory Control → RAM
                    ↓ (on hit)
               Instrucción (1 cycle)

Data Path → Memory Control → RAM (LW/SW sin caché aún)
```

Modificación en Control Unit:
- Reemplazar `MC_START` por `I_CACHE_FETCH_REQ`
- Esperar `I_CACHE_READY` en vez de `MC_END`

### Con Ambas Cachés

```
Control Unit → Instruction Cache → Memory Control → RAM
                    ↓ (on hit)
               Instrucción (1 cycle)

Data Path → Data Cache → Memory Control → RAM
               ↓ (on hit)
           Dato (1 cycle)
```

Modificación en Control Unit:
- Agregar señales `D_CACHE_READ_REQ`, `D_CACHE_WRITE_REQ`
- Esperar `D_CACHE_READY` para LW/SW

## Estado de Implementación del CPU

### Componentes Implementados (11/21)

```
CPU
├── Control Unit         🔴 NO IMPLEMENTADO (0%)
├── Memory Control       🔴 NO IMPLEMENTADO (0%)
│   ├── State Machine    🔴
│   ├── Address Trans    🔴
│   ├── Endian Conv      🔴
│   ├── Word Selector    🔴
│   └── MASK Generator   🔴
└── Data Path            🟡 PARCIAL (90%)
    ├── IR               ✅ IMPLEMENTADO
    ├── Decoder          ✅ IMPLEMENTADO (40+ inst)
    ├── Register File    ✅ IMPLEMENTADO (32+Hi/Lo)
    ├── ALU              ✅ IMPLEMENTADO (40+ ops)
    ├── Branch Control   ✅ IMPLEMENTADO
    ├── PC               ✅ IMPLEMENTADO
    ├── Random Gen       🔴 NO IMPLEMENTADO
    ├── MUX Writeback    ✅ IMPLEMENTADO
    ├── MUX ALU_B        ✅ IMPLEMENTADO
    ├── MUX Rd/Rt        ✅ IMPLEMENTADO
    └── Extenders        ✅ IMPLEMENTADO
```

### Progreso Total

```
┌─────────────────────────────────────────────────────┐
│ CPU S-MIPS                                          │
├─────────────────────────────────────────────────────┤
│ ████████████░░░░░░░░░░░░░░ 52%                     │
│                                                     │
│ ✅ Implementado:     11/21 componentes             │
│ 🔴 Faltante:         10/21 componentes             │
│                                                     │
│ FUNCIONALIDAD:       ❌ NO FUNCIONA                │
│ Razón:              Falta Control Unit + MC         │
└─────────────────────────────────────────────────────┘
```

## Timing del CPU

### Sin Caché

```
Instrucción típica (ADD):
    FETCH:      RT cycles (leer de RAM)
    DECODE:     1 cycle
    EXECUTE:    1 cycle
    WRITEBACK:  1 cycle
    Total:      RT + 3 cycles

LW:
    FETCH:      RT cycles
    DECODE:     1 cycle
    EXECUTE:    1 cycle (calc address)
    MEMORY:     RT cycles (leer dato)
    WRITEBACK:  1 cycle
    Total:      2×RT + 4 cycles
```

### Con Instruction Cache (80% hit rate)

```
Instrucción típica (ADD):
    FETCH (hit):    1 cycle
    FETCH (miss):   RT+1 cycles
    Promedio:       0.8×1 + 0.2×(RT+1) ≈ 3 cycles (si RT=10)

    DECODE:         1 cycle
    EXECUTE:        1 cycle
    WRITEBACK:      1 cycle
    Total promedio: 6 cycles

Mejora: RT+3 → 6 cycles (si RT=10: 13 → 6, ~2x más rápido)
```

### Con Ambas Cachés (80% hit rate)

```
LW:
    FETCH (hit):    1 cycle
    DECODE:         1 cycle
    EXECUTE:        1 cycle
    MEMORY (hit):   1 cycle
    WRITEBACK:      1 cycle
    Total:          5 cycles

Vs sin caché:       2×RT + 4 cycles = 24 cycles (si RT=10)
Mejora:             ~5x más rápido
```

## Verificación del CPU

### Tests de Integración

1. **Test básico - ADD**:
   ```assembly
   ADDI R1, R0, 10
   ADDI R2, R0, 20
   ADD R3, R1, R2
   TTY R3
   #prints 30
   ```
   Verifica: Fetch, Decode, Execute, Writeback

2. **Test memoria - LW/SW**:
   ```assembly
   ADDI R1, R0, 100
   SW R1, 0(R2)
   LW R3, 0(R2)
   TTY R3
   #prints 100
   ```
   Verifica: Memory Control funcionando

3. **Test branch - BEQ**:
   ```assembly
   ADDI R1, R0, 10
   ADDI R2, R0, 10
   BEQ R1, R2, skip
   ADDI R3, R0, 1
   skip:
   ADDI R4, R0, 2
   TTY R4
   #prints 2
   ```
   Verifica: Branch Control, flags ALU

## Problemas Conocidos

**Estado actual**: ❌ **CPU NO FUNCIONA**

**Bloqueantes críticos**:
1. 🚨🚨🚨 Control Unit no existe → No hay ciclo de instrucción
2. 🚨🚨 Memory Control no existe → No hay acceso a memoria
3. 🔴 Random Generator falta → Instrucción RND no funciona

**Impacto**: Imposible ejecutar ningún programa.

## Plan de Implementación

### Fase 1: Hacer Funcionar el CPU (Semanas 1-2)

1. **Control Unit** (7-10 días)
   - Implementar FSM de 12 estados
   - Conectar con Data Path y Memory Control

2. **Memory Control** (5-6 días)
   - Implementar 5 subcomponentes
   - Conectar con RAM

3. **Random Generator** (2-3 horas)
   - LFSR de 32 bits
   - Conectar con Data Path

4. **Testing** (2 días)
   - Tests básicos (ADD, LW, BEQ)

**Resultado**: CPU funcional (lento, sin caché)

### Fase 2: Optimizar con Caché (Semanas 3-4)

5. **Instruction Cache** (7-10 días)
6. **Data Cache** (5-7 días, opcional)

**Resultado**: CPU rápido, nota ≥ 5

## Referencias

- [[Control Unit]] - FSM principal del CPU
- [[Memory Control]] - Interfaz con RAM
- [[Data Path]] - Procesamiento de datos
- [[S-MIPS Complete Architecture]] - Arquitectura del sistema
- Documentación: `s-mips.pdf` - Especificación completa
- Código: `s-mips.circ` → CPU

---
**Última actualización**: 2025-12-09
**Estado**: 🟡 52% IMPLEMENTADO
**Bloqueante**: Control Unit y Memory Control
**Prioridad**: 🚨🚨🚨 MÁXIMA
