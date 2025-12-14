# Correcciones de Conectividad - S-MIPS Processor

**Versión**: 1.0  
**Fecha**: 2025-12-13  
**Estado**: Revisión completa de conectividad  
**Autor**: Análisis de Vault Obsidian S-MIPS

---

## Tabla de Contenidos

1. [Análisis de Inconsistencias Detectadas](#1-análisis-de-inconsistencias-detectadas)
2. [Integración de Cachés con Bypass](#2-integración-de-cachés-con-bypass)
3. [Tabla Resumen de Correcciones](#3-tabla-resumen-de-correcciones)
4. [Checklist de Validación](#4-checklist-de-validación-post-corrección)
5. [Prioridades de Implementación](#5-prioridades-de-implementación)
6. [Notas Finales](#6-notas-finales)

---

## 1. Análisis de Inconsistencias Detectadas

### 1.1 Control Unit ↔ Data Path

#### **Problema 1: Nomenclatura de señales**

**Control Unit genera (Document 3):**
- `LOAD_I` → Carga instrucción en IR

**Data Path espera (Document 12):**
- `LOAD_INST` → Mismo propósito

**✅ Solución:**
```markdown
Son el mismo pin físico, diferente nombre en documentación.
No requiere cambio de hardware.

Aclaración a agregar en ambos documentos:
- Control Unit genera: LOAD_I
- Data Path recibe como: LOAD_INST
- Mismo pin, nomenclatura diferente por claridad
```

---

#### **Problema 2: Pin EN faltante**

**Data Path espera (Document 12):**
```markdown
| `EN` | 1 bit | Control Unit | Data Path Enable (habilitar ejecución) |
```

**Control Unit NO documenta** esta salida.

**🔧 Solución - AGREGAR a Document 3:**
```markdown
### Hacia Data Path
| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `LOAD_I` | 1 bit | Data Path | Carga instrucción en IR |
| `EXECUTE` | 1 bit | Data Path | Habilita ejecución |
| `EN` | 1 bit | Data Path | Enable general del Data Path |
| `RESET` | 1 bit | Data Path | Reset sincrónico |
```

**Lógica de generación:**
```verilog
assign EN = (state == EXECUTE_INST) || 
            (state == CHECK_INST) || 
            (state == WRITEBACK);
```

---

#### **Problema 3: CLK_DP innecesario**

**Data Path documenta:**
```markdown
| `CLK_DP` | 1 bit | Control Unit | Clock del Data Path |
```

**🔧 Solución:**
```markdown
❌ ELIMINAR CLK_DP de Document 12
✅ Usar CLK global del sistema
✅ Todos los componentes reciben mismo CLK
```

---

#### **Problema 4: Señales faltantes Data Path → Control Unit**

**Control Unit espera (Document 3):**
```markdown
- HALT ✅
- MC_NEEDED ✅
- IS_WRITE ⚠️
- PUSH ⚠️
- POP ⚠️
```

**Data Path solo documenta:**
```markdown
- HALT
- MC_NEEDED
```

**🔧 Solución - AGREGAR a Document 12:**
```markdown
### Salidas a Control Unit
| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `HALT` | 1 bit | [[Control Unit]] | Señal de instrucción HALT |
| `MC_NEEDED` | 1 bit | [[Control Unit]] | Requiere acceso a memoria (LW/SW/PUSH/POP) |
| `IS_WRITE` | 1 bit | [[Control Unit]] | 1=Escritura (SW/PUSH), 0=Lectura (LW/POP) |
| `PUSH` | 1 bit | [[Control Unit]] | Instrucción PUSH (para 2º ciclo) |
| `POP` | 1 bit | [[Control Unit]] | Instrucción POP (para 2º ciclo) |
```

**Generación interna (en Instruction Decoder):**
```verilog
// Estas señales se generan en Instruction Decoder
// pero se exponen como salidas del Data Path

assign MC_NEEDED = (opcode == LW) || (opcode == SW) || 
                   (opcode == PUSH) || (opcode == POP);

assign IS_WRITE = (opcode == SW) || (opcode == PUSH);

assign PUSH = (opcode == PUSH_OPCODE);
assign POP = (opcode == POP_OPCODE);

assign HALT = (opcode == HALT_OPCODE);
```

---

### 1.2 Data Path → Memory Control

#### **Problema: Ambigüedad en ADDRESS**

**Data Path genera:**
```markdown
- PC_OUT (32 bits) - para fetch
- ADDRESS (32 bits) - para LW/SW
```

**Memory Control recibe:**
```markdown
- ADDRESS (32 bits) - ¿Cuál de los dos?
```

**🔧 Solución - ACLARAR en Document 7:**

**Opción A (Recomendada): Dos pines separados**
```markdown
### Entradas desde [[Data Path]]
| Puerto | Ancho | Fuente | Descripción |
|--------|-------|---------|-------------|
| `PC` | 32 bits | Program Counter | Dirección para fetch de instrucciones |
| `MEM_ADDRESS` | 32 bits | ALU Result | Dirección para LW/SW |
| `DATA_WRITE` | 32 bits | Register File | Dato a escribir (SW/PUSH) |
```

**MUX interno en Memory Control:**
```verilog
wire [31:0] final_address;
assign final_address = is_fetch ? PC : MEM_ADDRESS;
```

**Opción B (Alternativa): Un solo ADDRESS con control**
```markdown
### Entradas desde [[Data Path]]
| `ADDRESS` | 32 bits | Data Path | PC (si fetch) o ALU Result (si LW/SW) |
| `DATA_WRITE` | 32 bits | Register File | Dato a escribir |
```

Donde Data Path usa un MUX para seleccionar:
```verilog
assign ADDRESS = (state == FETCH) ? PC : ALU_RESULT;
```

**Recomendación:** Usar **Opción A** (dos pines) para mayor claridad.

---

### 1.3 Branch Control - Pin innecesario

#### **Problema: SP_INCREMENT no existe**

**Branch Control genera (Document 11):**
```markdown
| `SP_INCREMENT` | 1 bit | [[Register File]] | Incrementar SP (JR) |
```

**Register File NO tiene** entrada `SP_INCREMENT`.

**🔧 Solución - ELIMINAR de Document 11:**
```markdown
❌ ELIMINAR:
| `SP_INCREMENT` | 1 bit | Register File |

✅ AGREGAR NOTA:
**Modificación del Stack Pointer:**
El SP (R31) se modifica usando los puertos normales del Register File:
- WRITE_REG = 31
- WRITE_DATA = ALU_RESULT (SP ± 4)
- REG_WRITE = 1

Ver [[Register File]] Document 17 sección "Modificación del Stack Pointer"
para detalles completos de PUSH/POP/JR.
```

---

### 1.4 Memory State Machine - Pin innecesario

#### **Problema: CAPTURE_DATA no utilizado**

**Memory State Machine genera (Document 8):**
```markdown
| `CAPTURE_DATA` | 1 bit | Señal para capturar O0-O3 (lectura) |
```

**Memory Control NO usa** esta señal.

**🔧 Solución - ELIMINAR de Document 8:**
```markdown
❌ ELIMINAR de Salidas:
| `CAPTURE_DATA` | 1 bit |

✅ JUSTIFICACIÓN:
En Logisim, los registros capturan datos automáticamente en el
flanco de reloj cuando están habilitados. La captura ocurre
implícitamente en estado COMPLETE sin necesidad de señal especial.
```

---

### 1.5 Nomenclatura Random Generator

#### **Problema: Inconsistencia de nombres**

**Random Generator genera:**
```markdown
Salida: RANDOM_VALUE (según código Logisim)
```

**MUX Writeback espera:**
```markdown
Entrada: RND_VALUE (según Document 12)
```

**🔧 Solución - UNIFICAR en Document 12 y 16:**
```markdown
✅ Nombre correcto: RANDOM_VALUE
✅ Actualizar MUX Writeback (Document 12):
   - Cambiar RND_VALUE → RANDOM_VALUE

✅ Mantener en Random Generator (Document 16):
   - RANDOM_VALUE (ya correcto)
```

---

### 1.6 Little-Endian Converter - Instancias

#### **Problema: No especifica cuántas instancias**

**🔧 Solución - AGREGAR a Document 5:**
```markdown
## Instancias Necesarias en Memory Control

Memory Control requiere **5 instancias** del Little-Endian Converter:

### Para Lectura (RAM → CPU)
- **Converter 0**: O0_raw → O0_conv
- **Converter 1**: O1_raw → O1_conv
- **Converter 2**: O2_raw → O2_conv
- **Converter 3**: O3_raw → O3_conv

### Para Escritura (CPU → RAM)
- **Converter 4**: DATA_WRITE → DATA_WRITE_conv

### Conexión
```
Memory Control
├─ FROM RAM:
│  └─► Little-Endian Converter × 4
│      └─► Word Selector
│
└─ TO RAM:
   └─► Little-Endian Converter × 1
       └─► MASK Generator + Data Distributor
```
```

---

## 2. Integración de Cachés con Bypass

### 2.1 Principio de Diseño: Cache as Optional Layer

El sistema debe funcionar **con o sin cachés** mediante bypass automático.
```
┌─────────────────────────────────────────────────────┐
│           DISEÑO CON BYPASS AUTOMÁTICO              │
│                                                     │
│  Control Unit ──→ I-Cache ──→ Memory Control       │
│       │              │              ↑               │
│       │              └──────────────┘               │
│       │            (bypass on disable)              │
│       │                                             │
│       └──→ Data Path ──→ D-Cache ──→ Memory Control│
│                             │              ↑        │
│                             └──────────────┘        │
│                          (bypass on disable)        │
└─────────────────────────────────────────────────────┘
```

---

### 2.2 Instruction Cache - Conexión con Bypass

#### **Señales de Control**

**AGREGAR a Control Unit (Document 3):**
```markdown
### Configuración de Cache
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `I_CACHE_ENABLE` | 1 bit | Enable de Instruction Cache (0=bypass) |
```

#### **Nueva Interfaz: Control Unit ↔ I-Cache**
```markdown
### Control Unit → I-Cache
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `PC` | 32 bits | Dirección de instrucción |
| `FETCH_REQ` | 1 bit | Solicitud de fetch |
| `I_CACHE_ENABLE` | 1 bit | 1=Usar cache, 0=Bypass a Memory Control |
| `CLK` | 1 bit | Reloj del sistema |
| `RESET` | 1 bit | Reset (invalida todas las líneas) |

### I-Cache → Control Unit
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `INSTRUCTION` | 32 bits | Instrucción leída |
| `I_CACHE_READY` | 1 bit | Dato disponible |

### I-Cache ↔ Memory Control (on miss o bypass)
| Puerto | Ancho | Dirección | Descripción |
|--------|-------|-----------|-------------|
| `MC_START` | 1 bit | I-Cache → MC | Solicitud de lectura |
| `MC_ADDRESS` | 32 bits | I-Cache → MC | Dirección de bloque |
| `MC_BLOCK_DATA` | 128 bits | MC → I-Cache | Bloque leído |
| `MC_END` | 1 bit | MC → I-Cache | Operación completa |
```

#### **Lógica de Bypass en I-Cache**
```verilog
module instruction_cache(
    input wire [31:0] PC,
    input wire FETCH_REQ,
    input wire I_CACHE_ENABLE,  // ← PIN DE BYPASS
    input wire CLK,
    input wire RESET,
    
    output reg [31:0] INSTRUCTION,
    output reg I_CACHE_READY,
    
    // Conexión con Memory Control
    output reg MC_START,
    output reg [31:0] MC_ADDRESS,
    input wire [127:0] MC_BLOCK_DATA,
    input wire MC_END
);

// Estados
typedef enum {IDLE, LOOKUP, HIT, WAIT_MEM, FILL, BYPASS} state_t;
state_t state;

always @(posedge CLK) begin
    if (RESET) begin
        // Invalidar caché
        state <= IDLE;
    end 
    else begin
        case (state)
            IDLE: begin
                if (FETCH_REQ) begin
                    if (I_CACHE_ENABLE) begin
                        state <= LOOKUP;  // Usar caché
                    end else begin
                        state <= BYPASS;  // Bypass directo
                    end
                end
            end
            
            BYPASS: begin
                // Bypass: pasar directamente a Memory Control
                MC_START <= 1;
                MC_ADDRESS <= PC;
                state <= WAIT_MEM;
                // I_CACHE_READY se activará cuando MC_END=1
            end
            
            LOOKUP: begin
                // Lógica normal de caché
                if (hit) begin
                    state <= HIT;
                end else begin
                    state <= WAIT_MEM;
                    MC_START <= 1;
                    MC_ADDRESS <= PC;
                end
            end
            
            // ... resto de estados normales
        endcase
    end
end

endmodule
```

#### **Configuración del Bypass**
```verilog
// En Control Unit o configuración global
parameter I_CACHE_ENABLED = 1'b1;  // 0 = desactivar caché, 1 = activar

assign I_CACHE_ENABLE = I_CACHE_ENABLED;
```

---

### 2.3 Data Cache - Conexión con Bypass

#### **Señales de Control**

**AGREGAR a Control Unit (Document 3):**
```markdown
### Configuración de Cache
| `D_CACHE_ENABLE` | 1 bit | Enable de Data Cache (0=bypass) |
```

#### **Nueva Interfaz: Data Path ↔ D-Cache**
```markdown
### Data Path → D-Cache
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `ADDRESS` | 32 bits | Dirección de dato (de ALU) |
| `DATA_WRITE` | 32 bits | Dato a escribir (SW/PUSH) |
| `READ_REQ` | 1 bit | Solicitud de lectura (LW/POP) |
| `WRITE_REQ` | 1 bit | Solicitud de escritura (SW/PUSH) |
| `D_CACHE_ENABLE` | 1 bit | 1=Usar cache, 0=Bypass |
| `CLK` | 1 bit | Reloj |
| `RESET` | 1 bit | Reset |

### D-Cache → Data Path
| Porto | Ancho | Descripción |
|-------|-------|-------------|
| `DATA_READ` | 32 bits | Dato leído (LW/POP) |
| `D_CACHE_READY` | 1 bit | Operación completa |

### D-Cache ↔ Memory Control
| Porto | Ancho | Dirección | Descripción |
|-------|-------|-----------|-------------|
| `MC_START` | 1 bit | D-Cache → MC | Solicitud |
| `MC_READ_WRITE` | 1 bit | D-Cache → MC | 0=Read, 1=Write |
| `MC_ADDRESS` | 32 bits | D-Cache → MC | Dirección |
| `MC_DATA_WRITE` | 32 bits | D-Cache → MC | Dato (write) |
| `MC_BLOCK_DATA` | 128 bits | MC → D-Cache | Bloque (read) |
| `MC_DATA_READ` | 32 bits | MC → D-Cache | Palabra (read) |
| `MC_END` | 1 bit | MC → D-Cache | Completo |
```

#### **Lógica de Bypass en D-Cache**
```verilog
module data_cache(
    input wire [31:0] ADDRESS,
    input wire [31:0] DATA_WRITE,
    input wire READ_REQ,
    input wire WRITE_REQ,
    input wire D_CACHE_ENABLE,  // ← PIN DE BYPASS
    input wire CLK,
    input wire RESET,
    
    output reg [31:0] DATA_READ,
    output reg D_CACHE_READY,
    
    // Conexión con Memory Control
    output reg MC_START,
    output reg MC_READ_WRITE,
    output reg [31:0] MC_ADDRESS,
    output reg [31:0] MC_DATA_WRITE,
    input wire [127:0] MC_BLOCK_DATA,
    input wire [31:0] MC_DATA_READ,
    input wire MC_END
);

typedef enum {
    IDLE, 
    LOOKUP, 
    R_HIT, 
    WAIT_MEM, 
    FILL, 
    BYPASS_READ,
    BYPASS_WRITE
} state_t;

state_t state;

always @(posedge CLK) begin
    if (RESET) begin
        state <= IDLE;
    end 
    else begin
        case (state)
            IDLE: begin
                if (READ_REQ) begin
                    if (D_CACHE_ENABLE) begin
                        state <= LOOKUP;
                    end else begin
                        state <= BYPASS_READ;
                    end
                end 
                else if (WRITE_REQ) begin
                    if (D_CACHE_ENABLE) begin
                        state <= LOOKUP;
                    end else begin
                        state <= BYPASS_WRITE;
                    end
                end
            end
            
            BYPASS_READ: begin
                // Bypass: lectura directa de Memory Control
                MC_START <= 1;
                MC_READ_WRITE <= 0;
                MC_ADDRESS <= ADDRESS;
                state <= WAIT_MEM;
            end
            
            BYPASS_WRITE: begin
                // Bypass: escritura directa a Memory Control
                MC_START <= 1;
                MC_READ_WRITE <= 1;
                MC_ADDRESS <= ADDRESS;
                MC_DATA_WRITE <= DATA_WRITE;
                state <= WAIT_MEM;
            end
            
            WAIT_MEM: begin
                MC_START <= 0;
                if (MC_END) begin
                    if (MC_READ_WRITE == 0) begin
                        // Read completo
                        DATA_READ <= MC_DATA_READ;
                    end
                    D_CACHE_READY <= 1;
                    state <= IDLE;
                end
            end
            
            LOOKUP: begin
                // Lógica normal de caché
                // ...
            end
            
            // ... resto de estados
        endcase
    end
end

endmodule
```

---

### 2.4 Memory Control - Modificaciones para Cachés

**Memory Control NO necesita modificaciones** si las cachés se implementan correctamente.

#### **Interfaz actualizada (sin cambios en lógica)**
```markdown
### Entradas (ahora puede venir de CPU o Cachés)
| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `START` | 1 bit | Control Unit / I-Cache / D-Cache | Iniciar op |
| `R/W` | 1 bit | Control Unit / Cachés | 0=Read, 1=Write |
| `ADDRESS` | 32 bits | PC / ALU / Cachés | Dirección |
| `DATA_WRITE` | 32 bits | Data Path / D-Cache | Dato a escribir |

### Salidas (ahora puede ir a CPU o Cachés)
| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `BLOCK_DATA` | 128 bits | I-Cache / D-Cache | Bloque completo |
| `DATA_READ` | 32 bits | Data Path / D-Cache | Palabra única |
| `END` | 1 bit | Control Unit / Cachés | Operación completa |
```

**Nota:** Memory Control es **agnóstico** a si hay cachés o no.

---

### 2.5 Arbitraje entre I-Cache y D-Cache

Si ambas cachés solicitan Memory Control simultáneamente, se necesita **arbitraje**.

#### **Opción A: Prioridad Fija**
```verilog
// En Memory Control o módulo separado
always @(*) begin
    if (I_CACHE_MC_START) begin
        // Prioridad a fetch de instrucciones
        MC_START_internal = I_CACHE_MC_START;
        MC_ADDRESS_internal = I_CACHE_MC_ADDRESS;
        MC_RW_internal = 0;  // Siempre read
    end 
    else if (D_CACHE_MC_START) begin
        MC_START_internal = D_CACHE_MC_START;
        MC_ADDRESS_internal = D_CACHE_MC_ADDRESS;
        MC_RW_internal = D_CACHE_MC_RW;
    end 
    else begin
        // Direct from Control Unit (sin cachés)
        MC_START_internal = CU_START;
        MC_ADDRESS_internal = CU_ADDRESS;
        MC_RW_internal = CU_RW;
    end
end
```

#### **Opción B: Round-Robin (más justo)**
```verilog
reg last_served;  // 0=I-Cache, 1=D-Cache

always @(*) begin
    if (I_CACHE_MC_START && D_CACHE_MC_START) begin
        // Ambos solicitan: round-robin
        if (last_served == 0) begin
            // Servir D-Cache
            MC_START_internal = D_CACHE_MC_START;
            // ...
        end else begin
            // Servir I-Cache
            MC_START_internal = I_CACHE_MC_START;
            // ...
        end
    end 
    else if (I_CACHE_MC_START) begin
        MC_START_internal = I_CACHE_MC_START;
        last_served <= 0;
    end 
    else if (D_CACHE_MC_START) begin
        MC_START_internal = D_CACHE_MC_START;
        last_served <= 1;
    end
    // ...
end
```

**Recomendación:** Usar **Opción A** (prioridad fija a I-Cache) por simplicidad.

---

### 2.6 Diagrama de Conexión Completo con Cachés
```
┌────────────────────────────────────────────────────────────┐
│                      CONTROL UNIT                          │
│                                                            │
│  Configuración:                                            │
│    - I_CACHE_ENABLE (1 bit, parámetro)                    │
│    - D_CACHE_ENABLE (1 bit, parámetro)                    │
│                                                            │
│  Salidas:                                                  │
│    - PC → I-Cache                                          │
│    - FETCH_REQ → I-Cache                                   │
│    - READ_REQ → D-Cache (vía Data Path)                   │
│    - WRITE_REQ → D-Cache (vía Data Path)                  │
└────────────────────────────────────────────────────────────┘
         │                                    │
         ↓                                    ↓
┌──────────────────────┐          ┌──────────────────────┐
│  INSTRUCTION CACHE   │          │     DATA PATH        │
│                      │          │                      │
│  IF I_CACHE_ENABLE:  │          │  Genera:             │
│    - Lookup          │          │    - ADDRESS         │
│    - Hit: 1 ciclo   │          │    - DATA_WRITE      │
│    - Miss: → MC     │          │    - READ_REQ        │
│  ELSE:               │          │    - WRITE_REQ       │
│    - Bypass → MC    │          └──────────────────────┘
└──────────────────────┘                    │
         │                                  ↓
         │                      ┌──────────────────────┐
         │                      │     DATA CACHE       │
         │                      │                      │
         │                      │  IF D_CACHE_ENABLE:  │
         │                      │    - Lookup          │
         │                      │    - Hit: 1 ciclo   │
         │                      │    - Miss: → MC     │
         │                      │  ELSE:               │
         │                      │    - Bypass → MC    │
         │                      └──────────────────────┘
         │                                  │
         └──────────┬───────────────────────┘
                    ↓
         ┌────────────────────────┐
         │   MEMORY CONTROL       │
         │   (Arbitraje interno)  │
         │                        │
         │  Acepta de:            │
         │    - I-Cache (miss)    │
         │    - D-Cache (miss)    │
         │    - Control Unit      │
         │      (bypass mode)     │
         └────────────────────────┘
                    ↓
         ┌────────────────────────┐
         │         RAM            │
         │       (1 MB)           │
         └────────────────────────┘
```

---

### 2.7 Flujos de Operación

#### **Caso 1: I-Cache habilitada, D-Cache deshabilitada**
```
FETCH:
  Control Unit → I-Cache (FETCH_REQ)
  I-Cache hit → INSTRUCTION (1 ciclo)
  I-Cache miss → Memory Control → RAM (RT ciclos)

LOAD (LW):
  Data Path → D-Cache (READ_REQ, D_CACHE_ENABLE=0)
  D-Cache → BYPASS_READ → Memory Control → RAM (RT ciclos)
```

#### **Caso 2: Ambas cachés habilitadas**
```
FETCH:
  I-Cache hit → 1 ciclo
  I-Cache miss → MC → RT ciclos

LOAD:
  D-Cache hit → 1 ciclo
  D-Cache miss → MC → RT ciclos
  
(Arbitraje en MC si ambos miss simultáneos)
```

#### **Caso 3: Ambas cachés deshabilitadas (fallback)**
```
FETCH:
  Control Unit → I-Cache (I_CACHE_ENABLE=0)
  I-Cache → BYPASS → Memory Control → RAM
  
LOAD:
  Data Path → D-Cache (D_CACHE_ENABLE=0)
  D-Cache → BYPASS → Memory Control → RAM

Sistema funciona igual que sin cachés ✅
```

---

## 3. Tabla Resumen de Correcciones

| Documento | Sección | Acción | Prioridad |
|-----------|---------|--------|-----------|
| **Document 3** | Salidas → Data Path | AGREGAR: `EN` (1 bit) | ALTA |
| **Document 3** | Salidas → Data Path | CAMBIAR: `CLR` → `RESET` | MEDIA |
| **Document 3** | Configuración | AGREGAR: `I_CACHE_ENABLE`, `D_CACHE_ENABLE` | ALTA |
| **Document 12** | Entradas | ELIMINAR: `CLK_DP` | ALTA |
| **Document 12** | Entradas | ACLARAR: `LOAD_INST` = `LOAD_I` | BAJA |
| **Document 12** | Salidas → Control Unit | AGREGAR: `IS_WRITE`, `PUSH`, `POP` | ALTA |
| **Document 12** | MUX Writeback | CAMBIAR: `RND_VALUE` → `RANDOM_VALUE` | BAJA |
| **Document 7** | Entradas | ACLARAR o SEPARAR: `PC` vs `MEM_ADDRESS` | MEDIA |
| **Document 11** | Salidas | ELIMINAR: `SP_INCREMENT` | ALTA |
| **Document 11** | Notas | AGREGAR: Aclaración sobre modificación de SP | MEDIA |
| **Document 8** | Salidas | ELIMINAR: `CAPTURE_DATA` | MEDIA |
| **Document 5** | Instancias | AGREGAR: Sección de 5 instancias | BAJA |
| **Document 16** | Salidas | CONFIRMAR: `RANDOM_VALUE` (ya correcto) | BAJA |
| **Document 21** | Interfaz | AGREGAR: Lógica de bypass con `I_CACHE_ENABLE` | ALTA |
| **Document 19** | Interfaz | AGREGAR: Lógica de bypass con `D_CACHE_ENABLE` | ALTA |

---

## 4. Checklist de Validación Post-Corrección

### 4.1 Validación de Interfaces CPU-Level

- [ ] Control Unit genera todos los pines que Data Path espera
- [ ] Data Path genera todos los pines que Control Unit espera
- [ ] Memory Control recibe direcciones claras (PC vs MEM_ADDRESS)
- [ ] Nomenclatura `CLK` unificada (sin `CLK_DP`)
- [ ] Nomenclatura `RESET` unificada (sin `CLR`)

### 4.2 Validación de Pines Innecesarios

- [ ] `SP_INCREMENT` eliminado de Branch Control
- [ ] `CAPTURE_DATA` eliminado de Memory State Machine
- [ ] Todos los pines documentados tienen destino real

### 4.3 Validación de Cachés con Bypass

- [ ] I-Cache puede deshabilitarse (bypass a MC)
- [ ] D-Cache puede deshabilitarse (bypass a MC)
- [ ] Sistema funciona con ambas cachés off
- [ ] Sistema funciona con solo I-Cache on
- [ ] Sistema funciona con ambas cachés on
- [ ] Arbitraje resuelve conflictos entre cachés

### 4.4 Validación de Nomenclatura

- [ ] `LOAD_I` (Control Unit) = `LOAD_INST` (Data Path) documentado
- [ ] `HI`/`LO` (ALU) → `HI_IN`/`LO_IN` (Register File) documentado
- [ ] `RANDOM_VALUE` unificado en todos los documentos

---

## 5. Prioridades de Implementación

### Fase 1: Correcciones Críticas (AHORA)
1. ✅ Agregar `EN` a Control Unit
2. ✅ Agregar `IS_WRITE`, `PUSH`, `POP` a salidas de Data Path
3. ✅ Eliminar `SP_INCREMENT` de Branch Control
4. ✅ Eliminar `CLK_DP` de Data Path
5. ✅ Aclarar ADDRESS en Memory Control

### Fase 2: Implementación de Cachés con Bypass (SIGUIENTE)
1. ✅ Agregar `I_CACHE_ENABLE` / `D_CACHE_ENABLE` a Control Unit
2. ✅ Implementar lógica de bypass en I-Cache
3. ✅ Implementar lógica de bypass en D-Cache
4. ✅ Implementar arbitraje en Memory Control (si necesario)

### Fase 3: Validación (DESPUÉS)
1. ✅ Test con cachés deshabilitadas (modo bypass)
2. ✅ Test con solo I-Cache habilitada
3. ✅ Test con ambas cachés habilitadas
4. ✅ Test de conflictos simultáneos

---

## 6. Notas Finales

### Principios de Diseño Aplicados

1. **Modularidad**: Cada componente puede funcionar independientemente
2. **Robustez**: Sistema funciona con o sin cachés
3. **Claridad**: Pines tienen propósito claro y documentado
4. **Simplicidad**: Sin pines innecesarios o ambiguos

### Riesgos Mitigados

- ✅ Fallo de caché no colapsa el sistema (bypass)
- ✅ Debugging facilitado (desactivar cachés individualmente)
- ✅ Desarrollo incremental posible (agregar cachés después)
- ✅ Compatibilidad con tests sin cachés

### Beneficios del Diseño con Bypass

1. **Desarrollo incremental**: Implementar CPU primero, cachés después
2. **Testing simplificado**: Aislar problemas (CPU vs Cache)
3. **Flexibilidad**: Ajustar configuración sin rehacer hardware
4. **Robustez**: Fallback automático si caché falla

---

**Fin del documento**

**Próximos pasos:**
1. Revisar este documento con el equipo
2. Implementar correcciones en orden de prioridad
3. Actualizar documentos del vault
4. Validar conexiones en Logisim
5. Ejecutar checklist de validación

**Contacto para consultas:** [Tu información]

---

**Versión**: 1.0  
**Última actualización**: 2025-12-13  
**Estado**: Listo para implementación