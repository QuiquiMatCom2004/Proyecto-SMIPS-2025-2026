# Diagrama de Conexiones Físicas en Logisim

**Fecha**: 2025-12-13
**Propósito**: Visualización detallada de conexiones de caché para implementación en Logisim

---

## 🎨 INSTRUCTION CACHE - Diagrama de Conexiones

```
┌────────────────────────────────────────────────────────────────┐
│                     INSTRUCTION CACHE                          │
│                   @ posición (510, 1210)                       │
│                                                                │
│  ENTRADAS (lado izquierdo):                                   │
│                                                                │
│  PC (32 bits) ◄────────── [Túnel: PC]                        │
│                              ↑                                 │
│                              └─ Desde Program Counter          │
│                                                                │
│  FETCH_REQ (1 bit) ◄──────── [Túnel: I_FETCH_REQ] 🆕         │
│                              ↑                                 │
│                              └─ Desde Control Unit             │
│                                 (estado START_FETCH)           │
│                                                                │
│  CLK (1 bit) ◄───────────── [Túnel: CLK]                     │
│                              ↑                                 │
│                              └─ Clock global                   │
│                                                                │
│  RESET (1 bit) ◄─────────── [Túnel: CLR]                     │
│                              ↑                                 │
│                              └─ Reset global                   │
│                                                                │
│  W0 (32 bits) ◄──────────── [Túnel: MC_BLOCK[31:0]]          │
│  W1 (32 bits) ◄──────────── [Túnel: MC_BLOCK[63:32]]         │
│  W2 (32 bits) ◄──────────── [Túnel: MC_BLOCK[95:64]]         │
│  W3 (32 bits) ◄──────────── [Túnel: MC_BLOCK[127:96]]        │
│                              ↑                                 │
│                              └─ Desde Memory Control           │
│                                 (bloque de 4 palabras)         │
│                                                                │
│  MC_END (1 bit) ◄────────── [Túnel: MC_END_I] 🆕             │
│                              ↑                                 │
│                              └─ Desde Memory Control DEMUX     │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  SALIDAS (lado derecho):                                      │
│                                                                │
│  INSTRUCTION (32 bits) ──────► [Túnel: INST_IN] 🔄           │
│                                 │                              │
│                                 └─► Hacia Instruction Register │
│                                     (reemplaza conexión de MC) │
│                                                                │
│  I_CACHE_READY (1 bit) ──────► [Túnel: I_READY] 🆕           │
│                                 │                              │
│                                 └─► Hacia Control Unit         │
│                                     (estado WAIT_INST_CACHE)   │
│                                                                │
│  MC_START (1 bit) ────────────► [Túnel: MC_START_I] 🆕       │
│                                 │                              │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
│  MC_ADDRESS (32 bits) ────────► [Túnel: MC_ADDR_I] 🆕        │
│                                 │                              │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
│  MC_READ_WRITE (1 bit) ───────► [Túnel: MC_RW_I] 🆕          │
│                                 │   (siempre = 0)              │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Pasos para Conectar en Logisim:

1. **Seleccionar el componente** "InstructionCache" en (510, 1210)

2. **Conectar entradas** (lado izquierdo):
   - Usar herramienta "Tunnel" (túnel) del menú Wiring
   - Cada pin de entrada debe conectarse al túnel correspondiente
   - Si el túnel no existe (marcado 🆕), créalo primero

3. **Conectar salidas** (lado derecho):
   - Crear túneles nuevos (🆕) donde sea necesario
   - Modificar conexiones existentes (🔄) donde se indica

4. **Separar MC_BLOCK**:
   - Usar componente "Splitter" de 128 bits a 4×32 bits
   - Configurar: incoming=128, fanout=4, bit distribution: [31:0], [63:32], [95:64], [127:96]

---

## 🎨 DATA CACHE - Diagrama de Conexiones

```
┌────────────────────────────────────────────────────────────────┐
│                       DATA CACHE                               │
│                   @ posición (940, 1200)                       │
│                   Label: "DataCache"                           │
│                                                                │
│  ENTRADAS (lado izquierdo):                                   │
│                                                                │
│  ADDRESS (32 bits) ◄──────── [Túnel: mem_address] ✅         │
│                               ↑                                │
│                               └─ Desde ALU RESULT              │
│                                  (ya existe en Data Path)      │
│                                                                │
│  DATA_WRITE (32 bits) ◄────── [Túnel: mem_write_Data] ✅     │
│                               ↑                                │
│                               └─ Desde Register File           │
│                                  READ_DATA_2 (ya existe)       │
│                                                                │
│  READ_REQ (1 bit) ◄────────── [Túnel: D_READ_REQ] 🆕         │
│                               ↑                                │
│                               └─ Desde Control Unit            │
│                                  (estado START_MEM_READ)       │
│                                                                │
│  WRITE_REQ (1 bit) ◄───────── [Túnel: D_WRITE_REQ] 🆕        │
│                               ↑                                │
│                               └─ Desde Control Unit            │
│                                  (estado START_MEM_WRITE)      │
│                                                                │
│  CLK (1 bit) ◄────────────── [Túnel: CLK] ✅                 │
│                               ↑                                │
│                               └─ Clock global                  │
│                                                                │
│  RESET (1 bit) ◄──────────── [Túnel: CLR] ✅                 │
│                               ↑                                │
│                               └─ Reset global                  │
│                                                                │
│  W0 (32 bits) ◄───────────── [Túnel: MC_BLOCK[31:0]]         │
│  W1 (32 bits) ◄───────────── [Túnel: MC_BLOCK[63:32]]        │
│  W2 (32 bits) ◄───────────── [Túnel: MC_BLOCK[95:64]]        │
│  W3 (32 bits) ◄───────────── [Túnel: MC_BLOCK[127:96]]       │
│                               ↑                                │
│                               └─ Desde Memory Control          │
│                                  (mismo que I-Cache)           │
│                                                                │
│  MC_END (1 bit) ◄─────────── [Túnel: MC_END_D] 🆕            │
│                               ↑                                │
│                               └─ Desde Memory Control DEMUX    │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  SALIDAS (lado derecho):                                      │
│                                                                │
│  DATA_READ (32 bits) ────────► [Túnel: mem_data_out] 🔄      │
│                                 │                              │
│                                 └─► Hacia MUX Writeback        │
│                                     (reemplaza MC directo)     │
│                                                                │
│  D_CACHE_READY (1 bit) ──────► [Túnel: D_READY] 🆕           │
│                                 │                              │
│                                 └─► Hacia Control Unit         │
│                                     (estado WAIT_DATA_CACHE)   │
│                                                                │
│  MC_START (1 bit) ────────────► [Túnel: MC_START_D] 🆕       │
│                                 │                              │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
│  MC_ADDRESS (32 bits) ────────► [Túnel: MC_ADDR_D] 🆕        │
│                                 │                              │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
│  MC_READ_WRITE (1 bit) ───────► [Túnel: MC_RW_D] 🆕          │
│                                 │   (0=read, 1=write)          │
│                                 └─► Hacia Memory Control MUX   │
│                                                                │
│  MC_DATA_WRITE (32 bits) ─────► [Túnel: MC_DATA_WR] 🆕       │
│                                 │                              │
│                                 └─► Hacia Memory Control       │
│                                     (para SW)                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎨 MEMORY CONTROL - Modificaciones con Multiplexor

```
┌────────────────────────────────────────────────────────────────┐
│                    MEMORY CONTROL                              │
│                  (con arbitraje I/D)                           │
│                                                                │
│  ENTRADAS MULTIPLEXADAS:                                      │
│                                                                │
│  [Túnel: MC_START_I] ─────┐                                   │
│                           │                                    │
│  [Túnel: MC_START_D] ─────┼──► [OR GATE] ──► MC_START_int    │
│                           │         │                          │
│                           │         │                          │
│  [Túnel: MC_ADDR_I] ──────┤         │                         │
│  (32 bits)                │         │                         │
│                           ├─► [MUX 2:1] ──► MC_ADDRESS_int    │
│  [Túnel: MC_ADDR_D] ──────┤    32 bits                        │
│  (32 bits)                │    select = MC_START_D            │
│                           │                                    │
│  MC_RW_I (constante 0) ───┤                                   │
│                           │                                    │
│                           ├─► [MUX 2:1] ──► MC_RW_int         │
│  [Túnel: MC_RW_D] ────────┤    1 bit                          │
│  (1 bit)                  │    select = MC_START_D            │
│                           │                                    │
│  [Túnel: MC_DATA_WR] ─────┘ (solo para Data Cache writes)    │
│  (32 bits)                                                     │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  SALIDAS DEMULTIPLEXADAS:                                     │
│                                                                │
│  MC_BLOCK_DATA_int ──────────────┬─► [Túnel: MC_BLOCK]       │
│  (128 bits desde RAM)            │    (compartido)             │
│                                  │                             │
│                                  └─► Hacia I-Cache y D-Cache  │
│                                                                │
│                                                                │
│  MC_END_int ─────► [DEMUX 1:2] ─┬─► [Túnel: MC_END_I] 🆕    │
│                    select =      │                             │
│                    MC_START_D    └─► [Túnel: MC_END_D] 🆕    │
│                                                                │
│  Lógica de select del DEMUX:                                  │
│  - Si MC_START_D = 1 → salida va a MC_END_D                   │
│  - Si MC_START_D = 0 → salida va a MC_END_I                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  IMPLEMENTACIÓN DEL MULTIPLEXOR EN LOGISIM:                   │
│                                                                │
│  Componentes necesarios:                                      │
│  ─────────────────────────────────────────────────────────────│
│                                                                │
│  1. [OR Gate] (2 entradas, 1 salida)                          │
│     - Entrada 0: MC_START_I                                   │
│     - Entrada 1: MC_START_D                                   │
│     - Salida: MC_START_internal                               │
│                                                                │
│  2. [Multiplexer] (32 bits, 2 entradas, select 1 bit)         │
│     - Entrada 0: MC_ADDR_I                                    │
│     - Entrada 1: MC_ADDR_D                                    │
│     - Select: MC_START_D                                      │
│     - Salida: MC_ADDRESS_internal                             │
│                                                                │
│  3. [Multiplexer] (1 bit, 2 entradas, select 1 bit)           │
│     - Entrada 0: Constante 0 (MC_RW_I)                        │
│     - Entrada 1: MC_RW_D                                      │
│     - Select: MC_START_D                                      │
│     - Salida: MC_RW_internal                                  │
│                                                                │
│  4. [Demultiplexer] (1 bit, 1 entrada, 2 salidas)             │
│     - Entrada: MC_END_internal                                │
│     - Select: MC_START_D                                      │
│     - Salida 0: MC_END_I (cuando select=0)                    │
│     - Salida 1: MC_END_D (cuando select=1)                    │
│                                                                │
│  Ubicación sugerida:                                          │
│  - Agregar estos componentes en la entrada de Memory Control  │
│  - Antes de la lógica FSM existente                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎨 CONTROL UNIT - Nuevas Señales

```
┌────────────────────────────────────────────────────────────────┐
│                     CONTROL UNIT (FSM)                         │
│                                                                │
│  NUEVAS SALIDAS a agregar:                                    │
│                                                                │
│  I_FETCH_REQ ──────────────► [Túnel: I_FETCH_REQ] 🆕         │
│  (1 bit)                      │                                │
│                               └─► Hacia Instruction Cache      │
│                                   Pin FETCH_REQ                │
│                                                                │
│  D_READ_REQ ───────────────► [Túnel: D_READ_REQ] 🆕          │
│  (1 bit)                      │                                │
│                               └─► Hacia Data Cache             │
│                                   Pin READ_REQ                 │
│                                                                │
│  D_WRITE_REQ ──────────────► [Túnel: D_WRITE_REQ] 🆕         │
│  (1 bit)                      │                                │
│                               └─► Hacia Data Cache             │
│                                   Pin WRITE_REQ                │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  NUEVAS ENTRADAS a agregar:                                   │
│                                                                │
│  I_CACHE_READY ◄────────────── [Túnel: I_READY] 🆕           │
│  (1 bit)                        ↑                              │
│                                 └─ Desde Instruction Cache     │
│                                    Pin I_CACHE_READY           │
│                                                                │
│  D_CACHE_READY ◄────────────── [Túnel: D_READY] 🆕           │
│  (1 bit)                        ↑                              │
│                                 └─ Desde Data Cache            │
│                                    Pin D_CACHE_READY           │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  SEÑALES A REMOVER/MODIFICAR:                                 │
│                                                                │
│  MC_START ──────────────────► ❌ ELIMINAR                     │
│                                  (reemplazado por I/D_REQ)    │
│                                                                │
│  MC_END ◄───────────────────── ❌ ELIMINAR                    │
│                                  (reemplazado por I/D_READY)  │
│                                                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  DIAGRAMA DE ESTADOS MODIFICADO:                              │
│                                                                │
│  ANTES (sin cachés):                                          │
│  ────────────────                                             │
│                                                                │
│    ┌──────────────┐                                           │
│    │ START_FETCH  │                                           │
│    │ MC_START=1   │                                           │
│    └──────┬───────┘                                           │
│           │                                                    │
│           ↓                                                    │
│    ┌──────────────┐                                           │
│    │WAIT_INST_READ│                                           │
│    │if MC_END=1   │                                           │
│    └──────┬───────┘                                           │
│           │                                                    │
│           ↓                                                    │
│    ┌──────────────┐                                           │
│    │  LOAD_INST   │                                           │
│    └──────────────┘                                           │
│                                                                │
│  DESPUÉS (con Instruction Cache):                             │
│  ────────────────────────────                                 │
│                                                                │
│    ┌──────────────┐                                           │
│    │ START_FETCH  │                                           │
│    │ I_FETCH_REQ=1│ 🔄                                        │
│    └──────┬───────┘                                           │
│           │                                                    │
│           ↓                                                    │
│    ┌──────────────────┐                                       │
│    │WAIT_INST_CACHE   │ 🆕                                    │
│    │if I_READY=1      │ 🆕                                    │
│    └──────┬───────────┘                                       │
│           │                                                    │
│           ↓                                                    │
│    ┌──────────────┐                                           │
│    │  LOAD_INST   │                                           │
│    └──────────────┘                                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Fase 1: Preparar Túneles (30 min)

1. Crear todos los túneles nuevos (🆕) en el área de trabajo:
   - `I_FETCH_REQ`
   - `I_READY`
   - `D_READ_REQ`
   - `D_WRITE_REQ`
   - `D_READY`
   - `MC_START_I`
   - `MC_START_D`
   - `MC_ADDR_I`
   - `MC_ADDR_D`
   - `MC_RW_D`
   - `MC_DATA_WR`
   - `MC_END_I`
   - `MC_END_D`

### Fase 2: Conectar Instruction Cache (1-2 horas)

1. Localizar componente en (510, 1210)
2. Conectar entradas existentes: PC, CLK, CLR
3. Conectar entradas nuevas: I_FETCH_REQ
4. Conectar salidas: INSTRUCTION → INST_IN, I_CACHE_READY → I_READY
5. Conectar Memory Control: MC_START_I, MC_ADDR_I, MC_BLOCK, MC_END_I

### Fase 3: Conectar Data Cache (1-2 horas)

1. Localizar componente en (940, 1200)
2. Conectar entradas existentes: mem_address, mem_write_Data, CLK, CLR
3. Conectar entradas nuevas: D_READ_REQ, D_WRITE_REQ
4. Conectar salidas: DATA_READ → mem_data_out, D_CACHE_READY → D_READY
5. Conectar Memory Control: MC_START_D, MC_ADDR_D, MC_RW_D, MC_DATA_WR, MC_BLOCK, MC_END_D

### Fase 4: Modificar Memory Control (2-3 horas)

1. Agregar OR gate para MC_START
2. Agregar MUX para MC_ADDRESS (32 bits, select=MC_START_D)
3. Agregar MUX para MC_RW (1 bit, select=MC_START_D)
4. Agregar DEMUX para MC_END (1→2, select=MC_START_D)
5. Conectar túneles de entrada/salida

### Fase 5: Modificar Control Unit (3-4 horas)

1. Agregar salidas: I_FETCH_REQ, D_READ_REQ, D_WRITE_REQ
2. Agregar entradas: I_READY, D_READY
3. Modificar estado START_FETCH: usar I_FETCH_REQ en vez de MC_START
4. Crear estado WAIT_INST_CACHE: esperar I_READY
5. Crear estado WAIT_DATA_CACHE: esperar D_READY
6. Modificar START_MEM_READ/WRITE: usar D_READ_REQ/D_WRITE_REQ

### Fase 6: Testing (2-4 horas)

1. Test simple: ADDI (debe usar Instruction Cache)
2. Test LW/SW: verificar Data Cache funciona
3. Test loop: verificar hit rate > 50%
4. Test miss: verificar Memory Control se invoca correctamente

---

## 📝 NOTAS FINALES

### Leyenda de Símbolos

- ✅ = Túnel/conexión ya existe, no crear
- 🆕 = Túnel/conexión nueva, debe crearse
- 🔄 = Túnel/conexión existente que debe modificarse
- ❌ = Eliminar o reemplazar

### Errores Comunes a Evitar

1. **No compartir MC_BLOCK correctamente**: Ambas cachés deben leer del mismo túnel
2. **Olvidar el DEMUX de MC_END**: Cada caché necesita su propia señal END
3. **Prioridad incorrecta**: Data Cache debe tener prioridad sobre Instruction Cache
4. **Anchos de bus incorrectos**: MC_BLOCK es 128 bits, debe dividirse en 4×32 bits
5. **No usar Splitter para MC_BLOCK**: Necesitas separar 128 bits en W0, W1, W2, W3

---

**Con estos diagramas, puedes implementar las conexiones de caché en Logisim paso a paso.**
