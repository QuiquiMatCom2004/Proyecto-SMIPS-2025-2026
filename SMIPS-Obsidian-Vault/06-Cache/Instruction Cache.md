# Instruction Cache (Caché de Instrucciones)

**Tipo**: Componente de Sistema de Memoria
**Estado**: 🔴 #faltante **OBLIGATORIO PARA APROBAR**
**Ubicación**: **NO EXISTE**
**Complejidad**: ⭐⭐⭐⭐ Muy Compleja
**Prioridad**: 🔴 ALTA (necesario para nota > 3)

## ⚠️ COMPONENTE OBLIGATORIO

**SIN INSTRUCTION CACHE = MÁXIMO 3 PUNTOS = SUSPENSO**

Este es el componente mínimo de caché requerido para aprobar el proyecto.

## Descripción

La Instruction Cache almacena bloques de instrucciones recientemente accedidas para reducir la latencia de fetch. En lugar de esperar RT cycles cada vez que se necesita una instrucción, la caché devuelve la instrucción en 1 ciclo si está presente (hit).

## Configuración Mínima (Para Aprobar)

```
┌─────────────────────────────────────────┐
│        INSTRUCTION CACHE                │
│                                         │
│  Tipo:   Direct-Mapped                  │
│  Líneas: 4 (mínimo requerido)           │
│  Tamaño: 4 líneas × 16 bytes = 64 bytes│
│  Bloque: 4 words (128 bits)            │
│                                         │
│  Política: Read-only (no writes)        │
│  Reemplazo: Automático (direct-mapped)  │
└─────────────────────────────────────────┘
```

## Estructura de una Línea de Caché

```
┌────────┬──────────────────┬──────────────────────────────────────────┐
│ Valid  │       Tag        │            Data Block                    │
│ 1 bit  │    26 bits       │        4 words × 32 bits = 128 bits     │
└────────┴──────────────────┴──────────────────────────────────────────┘

Bits:     1         26                      128
Total por línea: 1 + 26 + 128 = 155 bits
Total caché (4 líneas): 155 × 4 = 620 bits
```

### Desglose de Dirección (PC de 32 bits)

```
┌────────────────────────┬──────────┬────────────┬────────┐
│        Tag             │  Index   │Word Offset │  Byte  │
│      26 bits           │  2 bits  │   2 bits   │ 2 bits │
│     bits [31:6]        │  [5:4]   │   [3:2]    │ [1:0]  │
└────────────────────────┴──────────┴────────────┴────────┘

Tag (26 bits):         Identifica bloque único en memoria
Index (2 bits):        Selecciona línea en caché (0-3)
Word Offset (2 bits):  Selecciona palabra dentro del bloque (0-3)
Byte Offset (2 bits):  Siempre 00 (instrucciones alineadas a 4 bytes)
```

**Ejemplo**:
```
PC = 0x00001048 = 0000 0000 0000 0000 0001 0000 0100 1000

Tag    = 0x000004 (bits 31:6) = 00 0000 0000 0000 0000 0001 00
Index  = 0x01     (bits 5:4)  = 01
Word   = 0x02     (bits 3:2)  = 10
Byte   = 0x00     (bits 1:0)  = 00

Línea: 1 (de 0-3)
Palabra: 2 (de 0-3) dentro del bloque
```

## Interfaz de Entradas/Salidas

### Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `PC` | 32 bits | [[Control Unit]] | Dirección de instrucción a buscar |
| `FETCH_REQ` | 1 bit | [[Control Unit]] | Solicitud de fetch (activa en START_FETCH) |
| `CLK` | 1 bit | Sistema | Señal de reloj |
| `RESET` | 1 bit | Sistema | Reset (invalida todas las líneas) |

### Salidas

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `INSTRUCTION` | 32 bits | [[Instruction Register]] (Data Path) | Instrucción leída |
| `I_CACHE_READY` | 1 bit | [[Control Unit]] | Indica dato disponible (1 = listo) |

### Conexión con Memory Control (on miss)

| Señal | Ancho | Dirección | Descripción |
|-------|-------|-----------|-------------|
| `MC_START` | 1 bit | I-Cache → MC | Iniciar lectura de bloque |
| `MC_ADDRESS` | 32 bits | I-Cache → MC | Dirección de bloque a leer |
| `MC_BLOCK_DATA` | 128 bits | MC → I-Cache | Bloque leído (4 words) |
| `MC_END` | 1 bit | MC → I-Cache | Lectura completada |

## Operación Detallada

### Caso 1: Cache Hit (Instrucción en caché)

```
Ciclo 1: Control Unit activa FETCH_REQ
         I-Cache extrae Tag, Index, Word Offset de PC

Ciclo 1 (mismo): Compara Tag con cache_line[Index].tag
         Si Valid=1 AND Tag match:
            → CACHE HIT
            → Selecciona palabra usando Word Offset
            → INSTRUCTION = cache_line[Index].data[word_offset]
            → I_CACHE_READY = 1

Ciclo 2: Control Unit lee INSTRUCTION, continúa a LOAD_INST

Latencia total: 1 ciclo
```

### Caso 2: Cache Miss (Instrucción NO en caché)

```
Ciclo 1: Control Unit activa FETCH_REQ
         I-Cache extrae Tag, Index, Word Offset de PC

Ciclo 1 (mismo): Compara Tag con cache_line[Index].tag
         Si Valid=0 OR Tag mismatch:
            → CACHE MISS
            → Activa MC_START = 1
            → MC_ADDRESS = PC (dirección del bloque)
            → I_CACHE_READY = 0

Ciclos 2 a N: Espera a Memory Control
              MC lee bloque completo de RAM (RT cycles)

Ciclo N+1: MC devuelve MC_BLOCK_DATA (128 bits = 4 words)
           MC_END = 1
           I-Cache carga bloque en cache_line[Index]:
              cache_line[Index].valid = 1
              cache_line[Index].tag = Tag
              cache_line[Index].data = MC_BLOCK_DATA
           I-Cache selecciona palabra usando Word Offset
           INSTRUCTION = cache_line[Index].data[word_offset]
           I_CACHE_READY = 1

Ciclo N+2: Control Unit lee INSTRUCTION, continúa a LOAD_INST

Latencia total: 1 + RT cycles
```

## Máquina de Estados (Opcional - recomendada)

```
┌────────┐  FETCH_REQ=1    ┌──────────┐  Hit    ┌──────────┐
│  IDLE  │ ───────────────→│  LOOKUP  │────────→│   HIT    │
└────────┘                  └──────────┘         └──────────┘
                                 │                     │
                                 │ Miss                │
                                 ↓                     │
                            ┌──────────┐              │
                            │WAIT_MEM  │              │
                            └──────────┘              │
                                 │ MC_END=1            │
                                 ↓                     │
                            ┌──────────┐              │
                            │ FILL     │              │
                            └──────────┘              │
                                 │                     │
                                 └─────────────────────┘
                                         │
                                         ↓
                                    (volver a IDLE)
```

### Estados

1. **IDLE**: Esperando solicitud de fetch
2. **LOOKUP**: Comparando Tag y Valid
3. **HIT**: Devolviendo instrucción (1 ciclo)
4. **WAIT_MEM**: Esperando Memory Control (RT cycles)
5. **FILL**: Cargando bloque en línea de caché

## Pseudocódigo Verilog

```verilog
module instruction_cache(
    input wire [31:0] PC,
    input wire FETCH_REQ,
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

// Estructura de línea de caché
typedef struct {
    bit valid;
    bit [25:0] tag;
    bit [127:0] data;  // 4 words × 32 bits
} cache_line_t;

cache_line_t cache[4];  // 4 líneas

// Extracción de campos de dirección
wire [25:0] pc_tag = PC[31:6];
wire [1:0]  pc_index = PC[5:4];
wire [1:0]  pc_word_offset = PC[3:2];

// Lógica de hit/miss
wire hit = cache[pc_index].valid &&
           (cache[pc_index].tag == pc_tag);

// Estados
typedef enum {IDLE, LOOKUP, HIT, WAIT_MEM, FILL} state_t;
state_t state;

always @(posedge CLK) begin
    if (RESET) begin
        // Invalidar todas las líneas
        for (int i = 0; i < 4; i++)
            cache[i].valid <= 0;
        state <= IDLE;
        I_CACHE_READY <= 0;
        MC_START <= 0;
    end else begin
        case (state)
            IDLE: begin
                if (FETCH_REQ) begin
                    state <= LOOKUP;
                end
                I_CACHE_READY <= 0;
            end

            LOOKUP: begin
                if (hit) begin
                    // CACHE HIT
                    state <= HIT;
                end else begin
                    // CACHE MISS
                    state <= WAIT_MEM;
                    MC_START <= 1;
                    MC_ADDRESS <= PC;
                end
            end

            HIT: begin
                // Seleccionar palabra del bloque
                case (pc_word_offset)
                    2'b00: INSTRUCTION <= cache[pc_index].data[31:0];
                    2'b01: INSTRUCTION <= cache[pc_index].data[63:32];
                    2'b10: INSTRUCTION <= cache[pc_index].data[95:64];
                    2'b11: INSTRUCTION <= cache[pc_index].data[127:96];
                endcase
                I_CACHE_READY <= 1;
                state <= IDLE;
            end

            WAIT_MEM: begin
                MC_START <= 0;
                if (MC_END) begin
                    state <= FILL;
                end
            end

            FILL: begin
                // Cargar bloque en caché
                cache[pc_index].valid <= 1;
                cache[pc_index].tag <= pc_tag;
                cache[pc_index].data <= MC_BLOCK_DATA;

                // Seleccionar palabra solicitada
                case (pc_word_offset)
                    2'b00: INSTRUCTION <= MC_BLOCK_DATA[31:0];
                    2'b01: INSTRUCTION <= MC_BLOCK_DATA[63:32];
                    2'b10: INSTRUCTION <= MC_BLOCK_DATA[95:64];
                    2'b11: INSTRUCTION <= MC_BLOCK_DATA[127:96];
                endcase
                I_CACHE_READY <= 1;
                state <= IDLE;
            end
        endcase
    end
end

endmodule
```

## Integración con Control Unit

### Modificaciones en Control Unit

**ANTES (sin caché)**:
```verilog
// En estado START_FETCH
MC_START <= 1;
MC_ADDRESS <= PC;
state <= WAIT_INST_READ;
```

**DESPUÉS (con instruction cache)**:
```verilog
// En estado START_FETCH
I_CACHE_FETCH_REQ <= 1;
state <= WAIT_INST_CACHE;

// Nuevo estado: WAIT_INST_CACHE
if (I_CACHE_READY) begin
    state <= LOAD_INST;
end
```

### Flujo de Fetch Actualizado

```
START_FETCH:
    Control Unit activa FETCH_REQ a I-Cache

WAIT_INST_CACHE:
    Espera I_CACHE_READY

    Si HIT (1 ciclo):
        I_CACHE_READY = 1 inmediatamente

    Si MISS (1 + RT cycles):
        I-Cache solicita a Memory Control
        Memory Control espera RT cycles
        I-Cache carga bloque
        I_CACHE_READY = 1

LOAD_INST:
    Instrucción cargada en Instruction Register
    Continúa con DECODE
```

## Estimación de Trabajo

**Tiempo total**: 7-10 días

### Desglose

1. **Diseñar estructura de línea** (1 día)
   - Definir campos: Valid, Tag, Data
   - Calcular tamaños de bits
   - Diseñar array de 4 líneas

2. **Implementar lógica de hit/miss** (2 días)
   - Extracción de campos de PC
   - Comparadores de Tag
   - Selector de palabra

3. **Implementar FSM de caché** (2 días)
   - Estados IDLE, LOOKUP, HIT, WAIT_MEM, FILL
   - Transiciones de estado
   - Señales de control

4. **Integrar con Memory Control** (1 día)
   - Conexión MC_START, MC_ADDRESS
   - Recepción de MC_BLOCK_DATA, MC_END
   - Carga de bloque en línea

5. **Integrar con Control Unit** (1 día)
   - Modificar estado START_FETCH
   - Agregar estado WAIT_INST_CACHE
   - Conectar señales FETCH_REQ, I_CACHE_READY

6. **Testing y depuración** (2-3 días)
   - Test 1: Cold start (todos misses)
   - Test 2: Loop pequeño (hits después de warm-up)
   - Test 3: Conflictos (instrucciones que mapean a misma línea)
   - Test 4: Programa largo (mix de hits y misses)

## Tests de Validación

### Test 1: Cold Start
```assembly
# Primera ejecución: todos misses
ADDI R1, R0, 1    # Miss, carga bloque
ADDI R2, R0, 2    # Hit (misma línea si contiguo)
ADDI R3, R0, 3    # Hit
ADDI R4, R0, 4    # Hit
```

**Esperado**:
- Primera instrucción: 1 + RT cycles
- Siguientes: 1 cycle cada una (hits)

### Test 2: Loop Pequeño
```assembly
loop:
    ADDI R1, R1, 1
    BEQ R1, R10, end
    J loop
end:
    HALT
```

**Esperado**:
- Primera iteración: misses en cada instrucción
- Iteraciones siguientes: todos hits (loop cabe en caché)

### Test 3: Conflictos
```assembly
# Instrucciones separadas por 64 bytes (mapean a misma línea)
# Dirección 0x0000
ADDI R1, R0, 1

# Dirección 0x0040 (bits [5:4] = 00, misma línea que 0x0000)
ADDI R2, R0, 2
```

**Esperado**:
- Primera instrucción: miss, carga en línea 0
- Segunda instrucción: miss, reemplaza línea 0
- Si vuelve a primera: miss de nuevo (conflict)

### Test 4: Programa Grande
```assembly
# Más de 16 instrucciones (más de 4 bloques)
# Verificar hit rate
```

**Métrica**: Hit Rate = hits / (hits + misses)
**Objetivo**: > 80% en programas típicos

## Mejoras Opcionales (Para Extraordinario/Mundial)

### Caché de 8 Líneas
```
Index: 3 bits (bits [5:3])
Tag: 25 bits (bits [31:6])
Total: 8 líneas × 155 bits = 1240 bits
```

**Ventaja**: Menos conflictos, mejor hit rate

### Caché 2-Way Set-Associative
```
4 sets × 2 ways = 8 líneas
Index: 2 bits (selecciona set)
Por cada set: 2 comparadores (2 vías)
Requiere política de reemplazo (LRU, Random)
```

**Ventaja**: Significativamente menos conflictos

## Problemas Conocidos

**Estado actual**: 🔴 NO IMPLEMENTADO

**Impacto**:
- ❌ Nota máxima: 3 puntos (SUSPENSO)
- ❌ Cada fetch espera RT cycles
- ❌ Performance extremadamente lenta en loops

**Prioridad**: 🔴 ALTA (tercera después de Control Unit y Memory Control)

## Referencias

- [[Cache System Overview]] - Visión general del sistema
- [[Control Unit]] - Integración con fetch
- [[Memory Control]] - Interfaz con RAM
- [[Data Cache]] - Caché de datos (similar)
- Documentación: `s-mips.pdf` requisitos de caché
- Teoría: Patterson-Hennessy Cap. 5.2 - Cache Basics

---
**Última actualización**: 2025-12-09
**Estado**: 🔴 NO IMPLEMENTADO - OBLIGATORIO PARA APROBAR
**Prioridad**: 🔴 ALTA
**Nota sin esto**: Máximo 3 puntos (SUSPENSO GARANTIZADO)
