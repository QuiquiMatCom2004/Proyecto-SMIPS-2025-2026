# Guía de Conexión de Cachés en S-MIPS

**Fecha**: 2025-12-13
**Estado**: 📋 Guía de Implementación

---

## 📌 RESUMEN EJECUTIVO

Tu procesador **YA TIENE** las cachés implementadas en `s-mips.circ`:
- **Instruction Cache** en posición (510,1210)
- **Data Cache** en posición (940,1200)

Esta guía te explica **cómo conectarlas correctamente** con Control Unit, Data Path y Memory Control.

---

## 🔍 COMPONENTES DE CACHÉ DETECTADOS

### Instruction Cache (s-mips.circ)

**Ubicación**: (510, 1210)
**Label**: "InstructionCache"

**Pines identificados**:
- `PC` (32 bits, entrada): Dirección de instrucción a buscar
- `Start` (1 bit, entrada): Solicitud de fetch desde Control Unit
- `W0`, `W2`, `W3` (32 bits cada uno, entrada): Palabras de bloque desde Memory Control
- Salidas hacia Data Path e indicadores de estado

### Data Cache (s-mips.circ)

**Ubicación**: (940, 1200)
**Label**: "DataCache"
**Nota**: Usa el mismo componente "Instruction Cache" internamente

---

## 🔌 ESQUEMA GENERAL DE CONEXIONES

```
┌──────────────────────────────────────────────────────────────┐
│                        S-MIPS CPU                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │Control Unit │──┐                                         │
│  │    (FSM)    │  │ Señales de control                      │
│  └─────────────┘  │                                         │
│       ↓           ↓                                         │
│  ┌────────────────────────────────────────────────┐         │
│  │            DATA PATH                            │         │
│  │  ┌──────────┐  ┌─────┐  ┌──────────┐          │         │
│  │  │ Inst Reg │  │ ALU │  │ Reg File │          │         │
│  │  └──────────┘  └─────┘  └──────────┘          │         │
│  └────────────────────────────────────────────────┘         │
│       │ PC                    │ ALU_RESULT                  │
│       │ I_FETCH_REQ           │ READ_DATA_2                 │
│       ↓                       ↓                             │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │ INSTRUCTION  │        │  DATA CACHE  │                  │
│  │    CACHE     │        │              │                  │
│  │ @ (510,1210) │        │ @ (940,1200) │                  │
│  └──────────────┘        └──────────────┘                  │
│       │ MC_START_I            │ MC_START_D                  │
│       │ MC_ADDRESS_I          │ MC_ADDRESS_D                │
│       ↓                       ↓                             │
│         ┌────────────────────────────────┐                  │
│         │    MEMORY CONTROL              │                  │
│         │  (con multiplexor I/D)         │                  │
│         └────────────────────────────────┘                  │
│                     ↓                                       │
└─────────────────────┼───────────────────────────────────────┘
                      ↓
                  ┌───────┐
                  │  RAM  │
                  └───────┘
```

---

## 📋 PASO 1: CONEXIONES DE INSTRUCTION CACHE

### 1.1 Entradas desde Data Path / Control Unit

| Señal | Ancho | Origen | Túnel a crear | Descripción |
|-------|-------|--------|---------------|-------------|
| `PC` | 32 bits | Program Counter | `PC` | Dirección de instrucción (ya existe) |
| `FETCH_REQ` | 1 bit | Control Unit (estado START_FETCH) | `I_FETCH_REQ` | Solicitud de fetch |
| `CLK` | 1 bit | Sistema | `CLK` | Clock global (ya existe) |
| `RESET` | 1 bit | Sistema | `CLR` | Reset global (ya existe) |

**Acción**:
1. El túnel `PC` ya debe existir en el Data Path
2. Conectar pin `PC` de Instruction Cache al túnel `PC`
3. Crear nuevo túnel `I_FETCH_REQ` desde Control Unit
4. Conectar pines `CLK` y `RESET` a los túneles globales existentes

### 1.2 Salidas hacia Data Path / Control Unit

| Señal | Ancho | Destino | Túnel a crear | Descripción |
|-------|-------|---------|---------------|-------------|
| `INSTRUCTION` | 32 bits | Instruction Register | `INST_IN` | Instrucción leída |
| `I_CACHE_READY` | 1 bit | Control Unit | `I_READY` | Dato listo (hit o miss completado) |

**Acción**:
1. Actualmente el Instruction Register recibe instrucción desde Memory Control
2. **CAMBIAR**: Conectar Instruction Register al túnel `INST_IN` que viene de Instruction Cache
3. Crear túnel `I_READY` hacia Control Unit (nuevo estado WAIT_INST_CACHE)

### 1.3 Conexiones con Memory Control (on cache miss)

| Señal | Ancho | Dirección | Túnel a crear | Descripción |
|-------|-------|-----------|---------------|-------------|
| `MC_START` | 1 bit | I-Cache → MC | `MC_START_I` | Iniciar lectura de bloque |
| `MC_ADDRESS` | 32 bits | I-Cache → MC | `MC_ADDR_I` | Dirección del bloque |
| `MC_READ_WRITE` | 1 bit | I-Cache → MC | `MC_RW_I` (siempre 0) | Tipo de operación |
| `MC_BLOCK_DATA` | 128 bits | MC → I-Cache | `MC_BLOCK` (compartido) | Bloque de 4 palabras |
| `MC_END` | 1 bit | MC → I-Cache | `MC_END_I` | Operación completada |

**Acción**:
1. Crear túneles `MC_START_I`, `MC_ADDR_I` desde Instruction Cache
2. Estos se conectan al **multiplexor de Memory Control** (ver Paso 3)
3. Memory Control debe retornar `MC_BLOCK` (128 bits) y `MC_END_I`

---

## 📋 PASO 2: CONEXIONES DE DATA CACHE

### 2.1 Entradas desde Data Path / Control Unit

| Señal | Ancho | Origen | Túnel existente/nuevo | Descripción |
|-------|-------|--------|----------------------|-------------|
| `ADDRESS` | 32 bits | ALU RESULT | `mem_address` ✅ | Dirección efectiva (ya existe) |
| `DATA_WRITE` | 32 bits | Register File READ_DATA_2 | `mem_write_Data` ✅ | Dato a escribir (ya existe) |
| `READ_REQ` | 1 bit | Control Unit (START_MEM_READ) | `D_READ_REQ` 🆕 | Solicitud LW |
| `WRITE_REQ` | 1 bit | Control Unit (START_MEM_WRITE) | `D_WRITE_REQ` 🆕 | Solicitud SW |
| `CLK` | 1 bit | Sistema | `CLK` ✅ | Clock |
| `RESET` | 1 bit | Sistema | `CLR` ✅ | Reset |

**Acción**:
1. Los túneles `mem_address` y `mem_write_Data` ya existen
2. Conectar Data Cache a estos túneles
3. Crear túneles `D_READ_REQ` y `D_WRITE_REQ` desde Control Unit

### 2.2 Salidas hacia Data Path / Control Unit

| Señal | Ancho | Destino | Túnel a crear | Descripción |
|-------|-------|---------|---------------|-------------|
| `DATA_READ` | 32 bits | MUX Writeback (Data Path) | `mem_data_out` 🔄 | Dato leído (reemplaza conexión directa de MC) |
| `D_CACHE_READY` | 1 bit | Control Unit | `D_READY` 🆕 | Operación completa |

**Acción**:
1. Actualmente MUX Writeback recibe datos desde Memory Control
2. **CAMBIAR**: MUX Writeback debe recibir desde Data Cache vía túnel `mem_data_out`
3. Crear túnel `D_READY` hacia Control Unit (nuevo estado WAIT_DATA_CACHE)

### 2.3 Conexiones con Memory Control

| Señal | Ancho | Dirección | Túnel a crear | Descripción |
|-------|-------|-----------|---------------|-------------|
| `MC_START` | 1 bit | D-Cache → MC | `MC_START_D` | Iniciar operación |
| `MC_ADDRESS` | 32 bits | D-Cache → MC | `MC_ADDR_D` | Dirección del bloque |
| `MC_READ_WRITE` | 1 bit | D-Cache → MC | `MC_RW_D` | 0=read, 1=write |
| `MC_DATA_WRITE` | 32 bits | D-Cache → MC | `MC_DATA_WR` | Dato a escribir (word) |
| `MC_BLOCK_DATA` | 128 bits | MC → D-Cache | `MC_BLOCK` (compartido con I-Cache) | Bloque leído |
| `MC_END` | 1 bit | MC → D-Cache | `MC_END_D` | Operación completada |

---

## 📋 PASO 3: MODIFICAR MEMORY CONTROL (MULTIPLEXOR)

Memory Control **actualmente** recibe requests directos de Control Unit. Con cachés, debe **multiplexar** entre requests de **Instruction Cache** y **Data Cache**.

### 3.1 Entradas Multiplexadas

**ANTES** (sin cachés):
```
Control Unit → MC_START → Memory Control
Control Unit → MC_ADDRESS → Memory Control
Control Unit → MC_R/W → Memory Control
```

**DESPUÉS** (con cachés):
```
Instruction Cache → MC_START_I ─┐
                  → MC_ADDRESS_I  ├─→ [MUX] → Memory Control
Data Cache → MC_START_D ─────────┤
           → MC_ADDRESS_D         │
           → MC_RW_D ─────────────┘
```

### 3.2 Lógica de Arbitraje

```verilog
// Prioridad: Data Cache > Instruction Cache
// (datos son más críticos para ejecución)

if (MC_START_D == 1) begin
    // Servir Data Cache
    MC_ADDRESS_selected = MC_ADDRESS_D;
    MC_RW_selected = MC_RW_D;
    MC_DATA_WRITE_selected = MC_DATA_WR;
    // Cuando termine: MC_END_D = 1, MC_END_I = 0
end
else if (MC_START_I == 1) begin
    // Servir Instruction Cache
    MC_ADDRESS_selected = MC_ADDRESS_I;
    MC_RW_selected = 0;  // Siempre lectura para instrucciones
    // Cuando termine: MC_END_I = 1, MC_END_D = 0
end
else begin
    // Idle, no hay requests
    MC_END_I = 0;
    MC_END_D = 0;
end
```

### 3.3 Implementación en Logisim

**Componentes necesarios**:
1. **OR Gate** (2 entradas): `MC_START_I OR MC_START_D → MC_START_internal`
2. **Multiplexor 2:1** (32 bits): Selecciona entre `MC_ADDRESS_I` y `MC_ADDRESS_D`
   - Select = `MC_START_D` (si D=1, selecciona D; si D=0, selecciona I)
3. **Multiplexor 2:1** (1 bit): Selecciona `MC_RW`
4. **Demultiplexor 1:2** (1 bit): Distribuye `MC_END` a `MC_END_I` o `MC_END_D`
   - Select = `MC_START_D`

**Conexión**:
```
MC_START_I ──┐
             ├── OR ──→ MC_START (hacia lógica interna de MC)
MC_START_D ──┘

MC_ADDRESS_I ──┐
               ├── MUX (select=MC_START_D) ──→ MC_ADDRESS_internal
MC_ADDRESS_D ──┘

MC_RW_I (0) ────┐
               ├── MUX (select=MC_START_D) ──→ MC_RW_internal
MC_RW_D ────────┘

MC_END_internal ──→ DEMUX (select=MC_START_D) ──┬──→ MC_END_I
                                                └──→ MC_END_D
```

---

## 📋 PASO 4: MODIFICAR CONTROL UNIT

### 4.1 Estados Nuevos

**ANTES** (sin cachés):
```
START_FETCH → WAIT_INST_READ → LOAD_INST → EXECUTE
```

**DESPUÉS** (con Instruction Cache):
```
START_FETCH → WAIT_INST_CACHE → LOAD_INST → EXECUTE
```

**Para LW/SW** (antes):
```
START_MEM_READ → WAIT_MEM_READ → ...
```

**Para LW/SW** (después):
```
START_MEM_READ → WAIT_DATA_CACHE → ...
START_MEM_WRITE → WAIT_DATA_CACHE → ...
```

### 4.2 Cambios en Señales de Control

#### Fetch de Instrucciones

**ANTES**:
```verilog
// Estado START_FETCH
START_FETCH:
    MC_START = 1;        // Request directo a Memory Control
    MC_ADDRESS = PC;
    state <= WAIT_INST_READ;

// Estado WAIT_INST_READ
WAIT_INST_READ:
    if (MC_END == 1)
        state <= LOAD_INST;
```

**DESPUÉS**:
```verilog
// Estado START_FETCH
START_FETCH:
    I_FETCH_REQ = 1;     // Request a Instruction Cache
    state <= WAIT_INST_CACHE;

// Estado WAIT_INST_CACHE (nuevo)
WAIT_INST_CACHE:
    if (I_CACHE_READY == 1)  // Puede ser hit (1 ciclo) o miss (1+RT ciclos)
        state <= LOAD_INST;
```

#### Lectura de Datos (LW)

**ANTES**:
```verilog
START_MEM_READ:
    MC_START = 1;
    MC_ADDRESS = mem_address;
    MC_R/W = 0;
    state <= WAIT_MEM_READ;

WAIT_MEM_READ:
    if (MC_END == 1)
        state <= CHECK_STACK;
```

**DESPUÉS**:
```verilog
START_MEM_READ:
    D_READ_REQ = 1;      // Request a Data Cache
    state <= WAIT_DATA_CACHE;

WAIT_DATA_CACHE:
    if (D_CACHE_READY == 1)
        state <= CHECK_STACK;
```

#### Escritura de Datos (SW)

**ANTES**:
```verilog
START_MEM_WRITE:
    MC_START = 1;
    MC_ADDRESS = mem_address;
    MC_R/W = 1;
    state <= WAIT_MEM_WRITE;

WAIT_MEM_WRITE:
    if (MC_END == 1)
        state <= CHECK_STACK;
```

**DESPUÉS**:
```verilog
START_MEM_WRITE:
    D_WRITE_REQ = 1;     // Request a Data Cache
    state <= WAIT_DATA_CACHE;

WAIT_DATA_CACHE:  // Mismo estado que para LW
    if (D_CACHE_READY == 1)
        state <= CHECK_STACK;
```

### 4.3 Nuevas Señales de Control Unit

**Salidas a agregar**:
- `I_FETCH_REQ` → Instruction Cache
- `D_READ_REQ` → Data Cache
- `D_WRITE_REQ` → Data Cache

**Entradas a agregar**:
- `I_CACHE_READY` ← Instruction Cache
- `D_CACHE_READY` ← Data Cache

---

## 📋 PASO 5: VERIFICACIÓN DE CONEXIONES

### Checklist de Instruction Cache

- [ ] Pin `PC` → Túnel `PC` (desde Program Counter)
- [ ] Pin `FETCH_REQ` → Túnel `I_FETCH_REQ` (desde Control Unit)
- [ ] Pin `CLK` → Túnel `CLK` (global)
- [ ] Pin `RESET` → Túnel `CLR` (global)
- [ ] Pin `INSTRUCTION` → Túnel `INST_IN` (hacia Instruction Register)
- [ ] Pin `I_CACHE_READY` → Túnel `I_READY` (hacia Control Unit)
- [ ] Pin `MC_START` → Túnel `MC_START_I` (hacia Memory Control MUX)
- [ ] Pin `MC_ADDRESS` → Túnel `MC_ADDR_I` (hacia Memory Control MUX)
- [ ] Pin `MC_BLOCK_DATA` ← Túnel `MC_BLOCK` (desde Memory Control)
- [ ] Pin `MC_END` ← Túnel `MC_END_I` (desde Memory Control DEMUX)

### Checklist de Data Cache

- [ ] Pin `ADDRESS` → Túnel `mem_address` (desde ALU RESULT)
- [ ] Pin `DATA_WRITE` → Túnel `mem_write_Data` (desde READ_DATA_2)
- [ ] Pin `READ_REQ` → Túnel `D_READ_REQ` (desde Control Unit)
- [ ] Pin `WRITE_REQ` → Túnel `D_WRITE_REQ` (desde Control Unit)
- [ ] Pin `CLK` → Túnel `CLK` (global)
- [ ] Pin `RESET` → Túnel `CLR` (global)
- [ ] Pin `DATA_READ` → Túnel `mem_data_out` (hacia MUX Writeback)
- [ ] Pin `D_CACHE_READY` → Túnel `D_READY` (hacia Control Unit)
- [ ] Pin `MC_START` → Túnel `MC_START_D` (hacia Memory Control MUX)
- [ ] Pin `MC_ADDRESS` → Túnel `MC_ADDR_D` (hacia Memory Control MUX)
- [ ] Pin `MC_RW` → Túnel `MC_RW_D` (hacia Memory Control MUX)
- [ ] Pin `MC_DATA_WRITE` → Túnel `MC_DATA_WR` (hacia Memory Control)
- [ ] Pin `MC_BLOCK_DATA` ← Túnel `MC_BLOCK` (desde Memory Control, compartido)
- [ ] Pin `MC_END` ← Túnel `MC_END_D` (desde Memory Control DEMUX)

### Checklist de Memory Control

- [ ] Entrada `MC_START_I` desde Instruction Cache
- [ ] Entrada `MC_START_D` desde Data Cache
- [ ] MUX de addresses: selecciona `MC_ADDR_I` o `MC_ADDR_D`
- [ ] MUX de R/W: selecciona 0 (I-Cache) o `MC_RW_D` (D-Cache)
- [ ] Salida `MC_BLOCK` (128 bits) compartida hacia ambas cachés
- [ ] DEMUX de END: `MC_END_I` o `MC_END_D` según cuál se sirvió
- [ ] Lógica de prioridad: Data Cache > Instruction Cache

### Checklist de Control Unit

- [ ] Nueva salida `I_FETCH_REQ` conectada a Instruction Cache
- [ ] Nueva entrada `I_CACHE_READY` desde Instruction Cache
- [ ] Nueva salida `D_READ_REQ` conectada a Data Cache
- [ ] Nueva salida `D_WRITE_REQ` conectada a Data Cache
- [ ] Nueva entrada `D_CACHE_READY` desde Data Cache
- [ ] Estado `WAIT_INST_CACHE` implementado
- [ ] Estado `WAIT_DATA_CACHE` implementado
- [ ] Transiciones actualizadas para usar señales de caché

---

## 🔄 FLUJO DE DATOS COMPLETO

### Ejemplo: Fetch con HIT en Instruction Cache

```
Ciclo 1: Control Unit (START_FETCH)
         → I_FETCH_REQ = 1
         → State = WAIT_INST_CACHE

Ciclo 2: Instruction Cache
         → Recibe PC
         → Extrae Tag, Index
         → Compara con cache_line[Index].tag
         → HIT! Retorna instrucción
         → I_CACHE_READY = 1

Ciclo 3: Control Unit (WAIT_INST_CACHE)
         → Lee I_CACHE_READY = 1
         → State = LOAD_INST

Ciclo 4: Instruction Register
         → Carga INST_IN desde Instruction Cache
         → Instrucción disponible para Decoder
```

**Latencia total**: 3 ciclos (vs 3+RT sin caché)

### Ejemplo: Fetch con MISS en Instruction Cache

```
Ciclo 1: Control Unit (START_FETCH)
         → I_FETCH_REQ = 1

Ciclo 2: Instruction Cache
         → MISS! Tag no coincide
         → MC_START_I = 1
         → MC_ADDRESS_I = PC
         → I_CACHE_READY = 0

Ciclo 3-N: Memory Control
         → Arbitraje: servir Instruction Cache
         → MC_ADDRESS = MC_ADDRESS_I
         → Espera RT cycles
         → Lee bloque de RAM
         → MC_BLOCK_DATA disponible
         → MC_END_I = 1

Ciclo N+1: Instruction Cache
         → Recibe MC_BLOCK_DATA
         → Carga bloque en cache_line[Index]
         → Extrae palabra solicitada
         → I_CACHE_READY = 1

Ciclo N+2: Control Unit
         → Lee I_CACHE_READY = 1
         → State = LOAD_INST
```

**Latencia total**: 2 + RT ciclos (primera vez), luego hits en 1 ciclo

---

## ⚠️ PUNTOS CRÍTICOS

### 1. Túneles Compartidos

**`MC_BLOCK`**: Ambas cachés reciben el mismo túnel de 128 bits desde Memory Control.
**Solución**: No hay conflicto porque Memory Control solo sirve una caché a la vez (arbitraje secuencial).

### 2. Sincronización de END Signals

**Problema**: ¿Cómo sabe cada caché cuándo `MC_END` es para ella?

**Solución**: Usar señales separadas `MC_END_I` y `MC_END_D` mediante demultiplexor controlado por cuál caché está siendo servida.

### 3. Prioridad en Arbitraje

**Data Cache tiene prioridad sobre Instruction Cache** porque:
- Datos son críticos para la instrucción actual
- Instruction fetch puede esperar (pipeline stall es aceptable)

### 4. Write-Through Policy

Si Data Cache usa **write-through** (recomendado para simplicidad):
- En SW: Data Cache actualiza su línea Y escribe a RAM
- `D_CACHE_READY` se activa solo después de que Memory Control complete la escritura
- Latencia de SW: 1 + WT cycles (igual que sin caché)

---

## 🎯 RESUMEN DE IMPLEMENTACIÓN

1. ✅ **Componentes de caché ya existen** en el circuito
2. 🔧 **Conectar Instruction Cache** siguiendo tabla de pines (Paso 1)
3. 🔧 **Conectar Data Cache** siguiendo tabla de pines (Paso 2)
4. 🔧 **Modificar Memory Control** para multiplexar requests (Paso 3)
5. 🔧 **Modificar Control Unit** para usar señales de caché (Paso 4)
6. ✅ **Verificar** todas las conexiones con checklists (Paso 5)

**Tiempo estimado**: 1-2 semanas de implementación y testing.

---

## 📚 REFERENCIAS

- `CONEXIONES-CACHE-CPU.md`: Especificación detallada original
- `SMIPS-Obsidian-Vault/06-Memory/Memory Control.md`: Interfaz de Memory Control
- `SMIPS-Obsidian-Vault/04-Control-Unit/Control Unit.md`: FSM de Control Unit
- Vault corregido: Señales consistentes entre componentes

---

**Con estas conexiones, las cachés estarán completamente integradas y funcionales en tu procesador S-MIPS.**
