# Conexiones de Cachés con CPU y Memory Control

**Fecha**: 2025-12-13
**Estado**: ✅ Cachés implementadas, conexiones por documentar

---

## 🔍 DESCUBRIMIENTO

Encontré que **SÍ tienes cachés implementadas** en `s-mips.circ`:
- `Instruction Cache` en posición (510,1210)
- `Data Cache` en posición (940,1200) etiquetada como "DataCache"

El Vault dice que no existen, pero **sí están en el circuito**.

---

## 📐 ARQUITECTURA COMPLETA CON CACHÉS

```
┌──────────────────────────────────────────────────────────────┐
│                        S-MIPS CPU                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │ Control Unit│                                            │
│  │  (FSM)      │                                            │
│  └─────────────┘                                            │
│       │    ↑                                                │
│       │    └─────────────────┐                              │
│       ↓                      │                              │
│  ┌─────────────────────────────────────┐                    │
│  │         DATA PATH                   │                    │
│  │  ┌────────┐  ┌─────┐  ┌──────────┐ │                    │
│  │  │Inst Reg│  │ ALU │  │Reg File  │ │                    │
│  │  └────────┘  └─────┘  └──────────┘ │                    │
│  │  ┌────────┐  ┌────────────────────┐│                    │
│  │  │Branch  │  │Instruction Decoder ││                    │
│  │  │Control │  └────────────────────┘│                    │
│  │  └────────┘                        │                    │
│  └─────────────────────────────────────┘                    │
│       │              │                                      │
│       │ PC          │ ALU_RESULT (address)                 │
│       │ FETCH_REQ   │ READ_DATA_2 (write data)             │
│       ↓              ↓                                      │
│  ┌──────────────┐   ┌──────────────┐                       │
│  │ INSTRUCTION  │   │  DATA CACHE  │                       │
│  │    CACHE     │   │              │                       │
│  │  4+ lines    │   │  4+ lines    │                       │
│  └──────────────┘   └──────────────┘                       │
│       │                   │                                │
│       └─────────┬─────────┘                                │
│                 ↓                                           │
│         ┌──────────────────┐                               │
│         │ MEMORY CONTROL   │                               │
│         │                  │                               │
│         └──────────────────┘                               │
│                 │                                           │
└─────────────────┼───────────────────────────────────────────┘
                  ↓
              ┌────────┐
              │  RAM   │
              │ 1 MB   │
              └────────┘
```

---

## 🔌 CONEXIONES DETALLADAS

### 1. INSTRUCTION CACHE

#### Entradas (desde Control Unit / Data Path)

| Señal | Ancho | Desde | Descripción |
|-------|-------|-------|-------------|
| `PC` | 32 bits | Program Counter (Data Path) | Dirección de instrucción |
| `FETCH_REQ` | 1 bit | Control Unit | Solicitud de fetch (estado START_FETCH) |
| `CLK` | 1 bit | Sistema | Clock |
| `RESET` | 1 bit | Sistema | Reset |

#### Salidas (hacia Data Path / Control Unit)

| Señal | Ancho | Hacia | Descripción |
|-------|-------|-------|-------------|
| `INSTRUCTION` | 32 bits | Instruction Register (Data Path) | Instrucción leída |
| `I_CACHE_READY` | 1 bit | Control Unit | Dato disponible (1 = listo) |

#### Conexión con Memory Control (on miss)

| Señal | Ancho | Dirección | Descripción |
|-------|-------|-----------|-------------|
| `MC_START` | 1 bit | I-Cache → MC | Iniciar lectura de bloque |
| `MC_ADDRESS` | 32 bits | I-Cache → MC | Dirección del bloque |
| `MC_READ_WRITE` | 1 bit | I-Cache → MC | 0 (siempre lectura) |
| `MC_BLOCK_DATA` | 128 bits | MC → I-Cache | Bloque leído (4 words) |
| `MC_END` | 1 bit | MC → I-Cache | Lectura completada |

---

### 2. DATA CACHE

#### Entradas (desde Data Path / Control Unit)

| Señal | Ancho | Desde | Descripción |
|-------|-------|-------|-------------|
| `ADDRESS` | 32 bits | ALU RESULT (Data Path) | Dirección efectiva (base + offset) |
| `DATA_WRITE` | 32 bits | Register File READ_DATA_2 | Dato a escribir (SW) |
| `READ_REQ` | 1 bit | Control Unit | Solicitud de lectura (LW) |
| `WRITE_REQ` | 1 bit | Control Unit | Solicitud de escritura (SW) |
| `CLK` | 1 bit | Sistema | Clock |
| `RESET` | 1 bit | Sistema | Reset |

#### Salidas (hacia Data Path / Control Unit)

| Señal | Ancho | Hacia | Descripción |
|-------|-------|-------|-------------|
| `DATA_READ` | 32 bits | MUX Writeback (Data Path) | Dato leído (LW) |
| `D_CACHE_READY` | 1 bit | Control Unit | Operación completada |

#### Conexión con Memory Control

| Señal | Ancho | Dirección | Descripción |
|-------|-------|-----------|-------------|
| `MC_START` | 1 bit | D-Cache → MC | Iniciar operación |
| `MC_ADDRESS` | 32 bits | D-Cache → MC | Dirección del bloque |
| `MC_READ_WRITE` | 1 bit | D-Cache → MC | 0=read, 1=write |
| `MC_DATA_WRITE` | 32 bits | D-Cache → MC | Dato a escribir (word) |
| `MC_BLOCK_DATA` | 128 bits | MC → D-Cache | Bloque leído |
| `MC_END` | 1 bit | MC → D-Cache | Operación completada |

---

### 3. MEMORY CONTROL (modificado para cachés)

Memory Control debe **multiplexar** entre requests de Instruction Cache y Data Cache.

#### Entradas (multiplexadas)

| Señal | Ancho | Desde | Descripción |
|-------|-------|-------|-------------|
| `MC_START_I` | 1 bit | Instruction Cache | Request de I-Cache |
| `MC_START_D` | 1 bit | Data Cache | Request de D-Cache |
| `MC_ADDRESS_I` | 32 bits | Instruction Cache | Dirección I-Cache |
| `MC_ADDRESS_D` | 32 bits | Data Cache | Dirección D-Cache |
| `MC_RW_D` | 1 bit | Data Cache | Read/Write de D-Cache |
| `MC_DATA_WRITE_D` | 32 bits | Data Cache | Dato a escribir |

#### Salidas (compartidas)

| Señal | Ancho | Hacia | Descripción |
|-------|-------|-------|-------------|
| `MC_BLOCK_DATA` | 128 bits | Ambas cachés | Bloque leído de RAM |
| `MC_END_I` | 1 bit | Instruction Cache | Operación I-Cache completada |
| `MC_END_D` | 1 bit | Data Cache | Operación D-Cache completada |

#### Lógica de Arbitraje

```verilog
// Prioridad: Data Cache > Instruction Cache
// (datos son más críticos que instrucciones)

if (MC_START_D) begin
    // Servir Data Cache
    MC_ADDRESS = MC_ADDRESS_D;
    MC_RW = MC_RW_D;
    MC_DATA_WRITE = MC_DATA_WRITE_D;
    // Cuando termine: MC_END_D = 1
end
else if (MC_START_I) begin
    // Servir Instruction Cache
    MC_ADDRESS = MC_ADDRESS_I;
    MC_RW = 0;  // Siempre lectura
    // Cuando termine: MC_END_I = 1
end
```

---

## 🔧 MODIFICACIONES EN CONTROL UNIT

### ANTES (sin cachés)

```verilog
// Estado START_FETCH
START_FETCH:
    MC_START = 1;
    MC_ADDRESS = PC;
    state <= WAIT_INST_READ;

// Estado WAIT_INST_READ
WAIT_INST_READ:
    if (MC_END)
        state <= LOAD_INST;
```

### DESPUÉS (con Instruction Cache)

```verilog
// Estado START_FETCH
START_FETCH:
    I_CACHE_FETCH_REQ = 1;  // Request a I-Cache en lugar de MC
    state <= WAIT_INST_CACHE;

// Nuevo estado: WAIT_INST_CACHE
WAIT_INST_CACHE:
    if (I_CACHE_READY) begin
        // Puede ser hit (1 ciclo) o miss (1 + RT cycles)
        state <= LOAD_INST;
    end
```

### Para LW (con Data Cache)

```verilog
// Estado START_MEM_READ
START_MEM_READ:
    D_CACHE_READ_REQ = 1;  // Request a D-Cache
    state <= WAIT_DATA_CACHE;

// Nuevo estado: WAIT_DATA_CACHE
WAIT_DATA_CACHE:
    if (D_CACHE_READY) begin
        state <= CHECK_STACK;
    end
```

### Para SW (con Data Cache)

```verilog
// Estado START_MEM_WRITE
START_MEM_WRITE:
    D_CACHE_WRITE_REQ = 1;  // Request a D-Cache
    state <= WAIT_DATA_CACHE;

// Estado WAIT_DATA_CACHE (mismo que para LW)
WAIT_DATA_CACHE:
    if (D_CACHE_READY) begin
        state <= CHECK_STACK;
    end
```

---

## 📊 FLUJO DE DATOS COMPLETO

### Caso 1: Fetch de Instrucción (HIT)

```
1. Control Unit → I_CACHE_FETCH_REQ = 1
2. Instruction Cache:
   - Extrae Tag, Index de PC
   - Compara con cache_line[Index].tag
   - HIT → Retorna instrucción en 1 ciclo
   - I_CACHE_READY = 1
3. Control Unit → LOAD_INST
4. Instruction Register ← INSTRUCTION
```

**Latencia**: 1 ciclo (vs 1 + RT sin caché)

---

### Caso 2: Fetch de Instrucción (MISS)

```
1. Control Unit → I_CACHE_FETCH_REQ = 1
2. Instruction Cache:
   - Tag mismatch → MISS
   - MC_START_I = 1, MC_ADDRESS_I = PC
   - I_CACHE_READY = 0
3. Memory Control:
   - Arbitraje: servir I-Cache
   - Lee bloque de RAM (RT cycles)
   - MC_BLOCK_DATA disponible
   - MC_END_I = 1
4. Instruction Cache:
   - Carga bloque en cache_line[Index]
   - Extrae palabra solicitada
   - I_CACHE_READY = 1
5. Control Unit → LOAD_INST
```

**Latencia**: 1 + RT cycles (igual que sin caché en primera vez, pero siguientes hits son 1 ciclo)

---

### Caso 3: LW (Data Cache HIT)

```
1. Control Unit → D_CACHE_READ_REQ = 1
2. Data Cache:
   - Extrae Tag, Index de ADDRESS
   - HIT → Retorna dato en 1 ciclo
   - D_CACHE_READY = 1
3. Control Unit → Continúa
4. MUX Writeback ← DATA_READ
5. Register File ← Dato
```

**Latencia**: 1 ciclo (vs 1 + RT sin caché)

---

### Caso 4: SW Write-Through (Data Cache HIT)

```
1. Control Unit → D_CACHE_WRITE_REQ = 1
2. Data Cache:
   - HIT → Actualiza palabra en caché
   - Inicia escritura a RAM:
     MC_START_D = 1
     MC_RW_D = 1
     MC_DATA_WRITE_D = dato
   - D_CACHE_READY = 0
3. Memory Control:
   - Escribe a RAM (WT cycles)
   - MC_END_D = 1
4. Data Cache:
   - D_CACHE_READY = 1
5. Control Unit → Continúa
```

**Latencia**: 1 + WT cycles (igual que sin caché, pero dato ya está en caché para futuras lecturas)

---

## 🎯 TABLA DE CONEXIONES FÍSICAS (Logisim)

### Instruction Cache

| Pin del componente | Conectar a | Notas |
|--------------------|------------|-------|
| `PC` (entrada 32 bits) | Túnel `PC` desde Program Counter | |
| `FETCH_REQ` (entrada 1 bit) | Señal de Control Unit (estado START_FETCH) | Crear túnel `I_FETCH_REQ` |
| `CLK` (entrada 1 bit) | Túnel `CLK` global | |
| `RESET` (entrada 1 bit) | Túnel `CLR` / `RESET` global | |
| `INSTRUCTION` (salida 32 bits) | Túnel `INST_IN` hacia Instruction Register | Reemplaza conexión directa desde Memory Control |
| `I_CACHE_READY` (salida 1 bit) | Control Unit (nuevo estado WAIT_INST_CACHE) | Crear túnel `I_READY` |
| `MC_START` (salida 1 bit) | Memory Control (multiplexado) | Túnel `MC_START_I` |
| `MC_ADDRESS` (salida 32 bits) | Memory Control (multiplexado) | Túnel `MC_ADDR_I` |
| `MC_BLOCK_DATA` (entrada 128 bits) | Memory Control salida | Túnel `MC_BLOCK` compartido |
| `MC_END` (entrada 1 bit) | Memory Control salida | Túnel `MC_END_I` |

### Data Cache

| Pin del componente | Conectar a | Notas |
|--------------------|------------|-------|
| `ADDRESS` (entrada 32 bits) | Túnel `mem_address` (ALU RESULT) | Ya existe |
| `DATA_WRITE` (entrada 32 bits) | Túnel `mem_write_Data` (READ_DATA_2) | Ya existe |
| `READ_REQ` (entrada 1 bit) | Control Unit (estado START_MEM_READ) | Crear túnel `D_READ_REQ` |
| `WRITE_REQ` (entrada 1 bit) | Control Unit (estado START_MEM_WRITE) | Crear túnel `D_WRITE_REQ` |
| `CLK` (entrada 1 bit) | Túnel `CLK` global | |
| `RESET` (entrada 1 bit) | Túnel `CLR` global | |
| `DATA_READ` (salida 32 bits) | Túnel hacia MUX Writeback | Reemplaza conexión desde Memory Control |
| `D_CACHE_READY` (salida 1 bit) | Control Unit (nuevo estado WAIT_DATA_CACHE) | Crear túnel `D_READY` |
| `MC_START` (salida 1 bit) | Memory Control (multiplexado) | Túnel `MC_START_D` |
| `MC_ADDRESS` (salida 32 bits) | Memory Control (multiplexado) | Túnel `MC_ADDR_D` |
| `MC_RW` (salida 1 bit) | Memory Control (multiplexado) | Túnel `MC_RW_D` |
| `MC_DATA_WRITE` (salida 32 bits) | Memory Control (entrada write) | Túnel `MC_DATA_WR` |
| `MC_BLOCK_DATA` (entrada 128 bits) | Memory Control salida | Túnel `MC_BLOCK` compartido |
| `MC_END` (entrada 1 bit) | Memory Control salida | Túnel `MC_END_D` |

---

## ⚠️ IMPORTANTE: Multiplexor en Memory Control

Memory Control debe decidir a cuál caché servir. Agregar lógica de arbitraje:

```
Entrada a Memory Control:
  - MC_START_I (desde I-Cache)
  - MC_START_D (desde D-Cache)
  - MC_ADDR_I, MC_ADDR_D
  - MC_RW_D

Lógica:
  if (MC_START_D):
      servir Data Cache (prioridad alta)
      usar MC_ADDR_D, MC_RW_D
      al terminar: MC_END_D = 1
  elif (MC_START_I):
      servir Instruction Cache
      usar MC_ADDR_I, MC_RW = 0
      al terminar: MC_END_I = 1
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Paso 1: Verificar componentes de caché
- [ ] Instruction Cache existe en s-mips.circ ✅ (encontrado en 510,1210)
- [ ] Data Cache existe en s-mips.circ ✅ (encontrado en 940,1200)
- [ ] Tienen todos los pines documentados arriba

### Paso 2: Conectar Instruction Cache
- [ ] PC → I-Cache (32 bits)
- [ ] FETCH_REQ desde Control Unit → I-Cache
- [ ] I-Cache INSTRUCTION → Instruction Register (reemplazar conexión directa de MC)
- [ ] I-Cache I_CACHE_READY → Control Unit
- [ ] I-Cache ↔ Memory Control (MC_START, MC_ADDRESS, MC_BLOCK_DATA, MC_END)

### Paso 3: Conectar Data Cache
- [ ] ADDRESS (ALU RESULT) → D-Cache
- [ ] DATA_WRITE (READ_DATA_2) → D-Cache
- [ ] READ_REQ, WRITE_REQ desde Control Unit → D-Cache
- [ ] D-Cache DATA_READ → MUX Writeback
- [ ] D-Cache D_CACHE_READY → Control Unit
- [ ] D-Cache ↔ Memory Control (multiplexado)

### Paso 4: Modificar Memory Control
- [ ] Agregar multiplexor de requests (I-Cache vs D-Cache)
- [ ] Lógica de arbitraje (Data tiene prioridad)
- [ ] Señales separadas MC_END_I y MC_END_D

### Paso 5: Modificar Control Unit
- [ ] Cambiar START_FETCH para usar I_CACHE_FETCH_REQ
- [ ] Agregar estado WAIT_INST_CACHE
- [ ] Cambiar START_MEM_READ para usar D_CACHE_READ_REQ
- [ ] Cambiar START_MEM_WRITE para usar D_CACHE_WRITE_REQ
- [ ] Agregar estado WAIT_DATA_CACHE

### Paso 6: Testing
- [ ] Test programa pequeño (verificar hits después de warm-up)
- [ ] Test loop (verificar hit rate > 80%)
- [ ] Test conflictos (verificar que misses funcionan correctamente)

---

**Con estas conexiones, las cachés estarán completamente integradas en tu CPU.**
