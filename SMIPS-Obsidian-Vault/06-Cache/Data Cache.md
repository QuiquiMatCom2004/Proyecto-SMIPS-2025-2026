# Data Cache (Caché de Datos)

**Tipo**: Componente de Sistema de Memoria
**Estado**: 🔴 #faltante **PARA EXTRAORDINARIO**
**Ubicación**: **NO EXISTE**
**Complejidad**: ⭐⭐⭐⭐⭐ Muy Compleja (requiere write policy)
**Prioridad**: 🟡 MEDIA (después de Instruction Cache)

## Requisito para Nota Alta

**Con Instruction Cache + Data Cache**: 5 puntos (Segunda Convocatoria)

La Data Cache es similar a la Instruction Cache, pero más compleja porque debe manejar tanto lecturas (LW) como escrituras (SW).

## Descripción

La Data Cache almacena bloques de datos recientemente accedidos para reducir la latencia de operaciones LW/SW. En lugar de esperar RT/WT cycles cada vez, la caché devuelve el dato en 1 ciclo si está presente (hit).

## Configuración Recomendada

```
┌─────────────────────────────────────────┐
│           DATA CACHE                    │
│                                         │
│  Tipo:   Direct-Mapped                  │
│  Líneas: 4 (mínimo) - 8 (recomendado)  │
│  Tamaño: 4 líneas × 16 bytes = 64 bytes│
│  Bloque: 4 words (128 bits)            │
│                                         │
│  Política: Write-Through (simple)       │
│            o Write-Back (eficiente)     │
│  Reemplazo: Automático (direct-mapped)  │
└─────────────────────────────────────────┘
```

## Estructura de una Línea de Caché

### Versión Write-Through (Más Simple)
```
┌────────┬──────────────────┬──────────────────────────────────────────┐
│ Valid  │       Tag        │            Data Block                    │
│ 1 bit  │    26 bits       │        4 words × 32 bits = 128 bits     │
└────────┴──────────────────┴──────────────────────────────────────────┘

Bits:     1         26                      128
Total por línea: 155 bits
```

### Versión Write-Back (Más Eficiente)
```
┌────────┬────────┬──────────────────┬───────────────────────────────────┐
│ Valid  │ Dirty  │       Tag        │         Data Block                │
│ 1 bit  │ 1 bit  │    26 bits       │   4 words × 32 bits = 128 bits   │
└────────┴────────┴──────────────────┴───────────────────────────────────┘

Bits:     1        1         26                     128
Total por línea: 156 bits

Dirty bit:
    0 = bloque NO modificado (igual a RAM)
    1 = bloque modificado (debe escribirse a RAM antes de reemplazo)
```

### Desglose de Dirección (Igual que Instruction Cache)

```
┌────────────────────────┬──────────┬────────────┬────────┐
│        Tag             │  Index   │Word Offset │  Byte  │
│      26 bits           │  2 bits  │   2 bits   │ 2 bits │
│     bits [31:6]        │  [5:4]   │   [3:2]    │ [1:0]  │
└────────────────────────┴──────────┴────────────┴────────┘
```

## Interfaz de Entradas/Salidas

### Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `ADDRESS` | 32 bits | [[Data Path]] | Dirección de dato (de ALU Result) |
| `DATA_WRITE` | 32 bits | [[Data Path]] | Dato a escribir (SW, de Register File) |
| `READ_REQ` | 1 bit | [[Control Unit]] | Solicitud de lectura (LW) |
| `WRITE_REQ` | 1 bit | [[Control Unit]] | Solicitud de escritura (SW) |
| `CLK` | 1 bit | Sistema | Señal de reloj |
| `RESET` | 1 bit | Sistema | Reset (invalida todas las líneas) |

### Salidas

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `DATA_READ` | 32 bits | [[Data Path]] (MUX Writeback) | Dato leído (LW) |
| `D_CACHE_READY` | 1 bit | [[Control Unit]] | Operación completada |

### Conexión con Memory Control

| Señal | Ancho | Dirección | Descripción |
|-------|-------|-----------|-------------|
| `MC_START` | 1 bit | D-Cache → MC | Iniciar operación de memoria |
| `MC_READ_WRITE` | 1 bit | D-Cache → MC | 0=read, 1=write |
| `MC_ADDRESS` | 32 bits | D-Cache → MC | Dirección de bloque |
| `MC_DATA_WRITE` | 32 bits | D-Cache → MC | Dato a escribir (solo write) |
| `MC_BLOCK_DATA` | 128 bits | MC → D-Cache | Bloque leído (solo read) |
| `MC_END` | 1 bit | MC → D-Cache | Operación completada |

## Operación Detallada

### Lectura (LW) - Write-Through Policy

#### Caso 1: Read Hit
```
Ciclo 1: Control Unit activa READ_REQ
         D-Cache extrae Tag, Index, Word Offset de ADDRESS

Ciclo 1 (mismo): Compara Tag con cache_line[Index].tag
         Si Valid=1 AND Tag match:
            → CACHE HIT
            → Selecciona palabra usando Word Offset
            → DATA_READ = cache_line[Index].data[word_offset]
            → D_CACHE_READY = 1

Latencia: 1 ciclo
```

#### Caso 2: Read Miss
```
Ciclo 1: Control Unit activa READ_REQ
         D-Cache: Valid=0 OR Tag mismatch
            → CACHE MISS
            → MC_START = 1, MC_READ_WRITE = 0
            → MC_ADDRESS = ADDRESS
            → D_CACHE_READY = 0

Ciclos 2 a N: Espera Memory Control (RT cycles)

Ciclo N+1: MC_END = 1, MC_BLOCK_DATA disponible
           D-Cache carga bloque:
              cache_line[Index].valid = 1
              cache_line[Index].tag = Tag
              cache_line[Index].data = MC_BLOCK_DATA
           DATA_READ = cache_line[Index].data[word_offset]
           D_CACHE_READY = 1

Latencia: 1 + RT cycles
```

### Escritura (SW) - Write-Through Policy

#### Caso 1: Write Hit (Write-Through)
```
Ciclo 1: Control Unit activa WRITE_REQ
         D-Cache: Valid=1 AND Tag match
            → CACHE HIT
            → Actualiza palabra en bloque:
               cache_line[Index].data[word_offset] = DATA_WRITE
            → Inicia escritura a RAM:
               MC_START = 1, MC_READ_WRITE = 1
               MC_ADDRESS = ADDRESS
               MC_DATA_WRITE = DATA_WRITE
            → D_CACHE_READY = 0

Ciclos 2 a N: Espera Memory Control (WT cycles)

Ciclo N+1: MC_END = 1
           D_CACHE_READY = 1

Latencia: 1 + WT cycles
```

#### Caso 2: Write Miss (Write-Through, No Allocate)
```
Ciclo 1: Control Unit activa WRITE_REQ
         D-Cache: Valid=0 OR Tag mismatch
            → CACHE MISS
            → NO cargar bloque (no allocate)
            → Escribir directamente a RAM:
               MC_START = 1, MC_READ_WRITE = 1
               MC_ADDRESS = ADDRESS
               MC_DATA_WRITE = DATA_WRITE
            → D_CACHE_READY = 0

Ciclos 2 a N: Espera Memory Control (WT cycles)

Ciclo N+1: MC_END = 1
           D_CACHE_READY = 1

Latencia: WT cycles
```

### Escritura (SW) - Write-Back Policy (Más Eficiente)

#### Caso 1: Write Hit (Write-Back)
```
Ciclo 1: Control Unit activa WRITE_REQ
         D-Cache: Valid=1 AND Tag match
            → CACHE HIT
            → Actualiza palabra en bloque:
               cache_line[Index].data[word_offset] = DATA_WRITE
            → Marca dirty:
               cache_line[Index].dirty = 1
            → NO escribir a RAM aún
            → D_CACHE_READY = 1

Latencia: 1 ciclo (MUY RÁPIDO!)
```

#### Caso 2: Write Miss (Write-Back, con reemplazo)
```
Ciclo 1: Control Unit activa WRITE_REQ
         D-Cache: Valid=0 OR Tag mismatch
            → CACHE MISS

         Si cache_line[Index].dirty = 1:
            → Debe escribir bloque viejo a RAM primero
            → MC_START = 1, MC_READ_WRITE = 1
            → MC_ADDRESS = {cache_line[Index].tag, Index, 4'b0000}
            → MC_BLOCK_DATA_WRITE = cache_line[Index].data
            → Estado: WRITE_BACK_OLD

Ciclos 2 a N: Espera write-back (WT cycles)

         Si cache_line[Index].dirty = 0:
            → Saltar write-back, ir directo a cargar bloque

Ciclo N+1: Cargar bloque nuevo:
           MC_START = 1, MC_READ_WRITE = 0
           MC_ADDRESS = ADDRESS
           Estado: LOAD_NEW

Ciclos N+2 a M: Espera lectura (RT cycles)

Ciclo M+1: cache_line[Index].valid = 1
           cache_line[Index].tag = Tag
           cache_line[Index].data = MC_BLOCK_DATA
           cache_line[Index].dirty = 0
           Actualizar palabra:
              cache_line[Index].data[word_offset] = DATA_WRITE
              cache_line[Index].dirty = 1
           D_CACHE_READY = 1

Latencia: Variable (WT + RT cycles si dirty, RT cycles si clean)
```

## Máquina de Estados (Write-Through)

```
┌────────┐  READ_REQ=1     ┌──────────┐  Hit    ┌──────────┐
│  IDLE  │ ───────────────→│  LOOKUP  │────────→│  R_HIT   │→ IDLE
└────────┘                  └──────────┘         └──────────┘
    ↑                            │
    │                            │ Miss
    │                            ↓
    │                       ┌──────────┐
    │                       │WAIT_READ │
    │                       └──────────┘
    │                            │ MC_END=1
    │                            ↓
    │                       ┌──────────┐
    │                       │  FILL    │
    │                       └──────────┘
    │                            │
    └────────────────────────────┘

    ↓ WRITE_REQ=1

┌────────┐                  ┌──────────┐
│  IDLE  │ ───────────────→│  LOOKUP  │
└────────┘                  └──────────┘
    ↑                            │
    │                            │ Hit or Miss
    │                            ↓
    │                       ┌──────────┐
    │                       │WAIT_WRITE│
    │                       └──────────┘
    │                            │ MC_END=1
    │                            │
    └────────────────────────────┘
```

## Máquina de Estados (Write-Back)

```
Más complejo, requiere estados adicionales:

- WRITE_BACK_OLD: Escribir bloque dirty a RAM
- LOAD_NEW: Cargar bloque nuevo de RAM
- FILL: Actualizar línea con bloque nuevo
```

## Pseudocódigo Verilog (Write-Through)

```verilog
module data_cache(
    input wire [31:0] ADDRESS,
    input wire [31:0] DATA_WRITE,
    input wire READ_REQ,
    input wire WRITE_REQ,
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
    input wire MC_END
);

// Estructura de línea de caché
typedef struct {
    bit valid;
    bit [25:0] tag;
    bit [127:0] data;
} cache_line_t;

cache_line_t cache[4];

// Extracción de campos
wire [25:0] addr_tag = ADDRESS[31:6];
wire [1:0]  addr_index = ADDRESS[5:4];
wire [1:0]  addr_word_offset = ADDRESS[3:2];

// Hit detection
wire hit = cache[addr_index].valid &&
           (cache[addr_index].tag == addr_tag);

// Estados
typedef enum {
    IDLE,
    LOOKUP,
    R_HIT,
    WAIT_READ,
    FILL,
    WAIT_WRITE
} state_t;

state_t state;

always @(posedge CLK) begin
    if (RESET) begin
        for (int i = 0; i < 4; i++)
            cache[i].valid <= 0;
        state <= IDLE;
        D_CACHE_READY <= 0;
        MC_START <= 0;
    end else begin
        case (state)
            IDLE: begin
                if (READ_REQ) begin
                    state <= LOOKUP;
                end else if (WRITE_REQ) begin
                    state <= LOOKUP;
                end
                D_CACHE_READY <= 0;
            end

            LOOKUP: begin
                if (READ_REQ) begin
                    if (hit) begin
                        state <= R_HIT;
                    end else begin
                        // Read miss: cargar bloque
                        state <= WAIT_READ;
                        MC_START <= 1;
                        MC_READ_WRITE <= 0;
                        MC_ADDRESS <= ADDRESS;
                    end
                end else if (WRITE_REQ) begin
                    // Write hit o miss: ambos escriben a RAM (write-through)
                    if (hit) begin
                        // Actualizar caché
                        case (addr_word_offset)
                            2'b00: cache[addr_index].data[31:0] <= DATA_WRITE;
                            2'b01: cache[addr_index].data[63:32] <= DATA_WRITE;
                            2'b10: cache[addr_index].data[95:64] <= DATA_WRITE;
                            2'b11: cache[addr_index].data[127:96] <= DATA_WRITE;
                        endcase
                    end
                    // Escribir a RAM (siempre, write-through)
                    state <= WAIT_WRITE;
                    MC_START <= 1;
                    MC_READ_WRITE <= 1;
                    MC_ADDRESS <= ADDRESS;
                    MC_DATA_WRITE <= DATA_WRITE;
                end
            end

            R_HIT: begin
                // Leer palabra de caché
                case (addr_word_offset)
                    2'b00: DATA_READ <= cache[addr_index].data[31:0];
                    2'b01: DATA_READ <= cache[addr_index].data[63:32];
                    2'b10: DATA_READ <= cache[addr_index].data[95:64];
                    2'b11: DATA_READ <= cache[addr_index].data[127:96];
                endcase
                D_CACHE_READY <= 1;
                state <= IDLE;
            end

            WAIT_READ: begin
                MC_START <= 0;
                if (MC_END) begin
                    state <= FILL;
                end
            end

            FILL: begin
                // Cargar bloque en caché
                cache[addr_index].valid <= 1;
                cache[addr_index].tag <= addr_tag;
                cache[addr_index].data <= MC_BLOCK_DATA;

                // Devolver palabra solicitada
                case (addr_word_offset)
                    2'b00: DATA_READ <= MC_BLOCK_DATA[31:0];
                    2'b01: DATA_READ <= MC_BLOCK_DATA[63:32];
                    2'b10: DATA_READ <= MC_BLOCK_DATA[95:64];
                    2'b11: DATA_READ <= MC_BLOCK_DATA[127:96];
                endcase
                D_CACHE_READY <= 1;
                state <= IDLE;
            end

            WAIT_WRITE: begin
                MC_START <= 0;
                if (MC_END) begin
                    D_CACHE_READY <= 1;
                    state <= IDLE;
                end
            end
        endcase
    end
end

endmodule
```

## Comparación: Write-Through vs Write-Back

| Aspecto | Write-Through | Write-Back |
|---------|---------------|------------|
| **Complejidad** | 🟢 Simple | 🔴 Compleja (requiere dirty bit) |
| **Latencia (write hit)** | 1 + WT cycles | 🟢 1 cycle |
| **Coherencia RAM** | 🟢 Siempre actualizada | 🔴 RAM puede estar desactualizada |
| **Tráfico a RAM** | 🔴 Alto (cada write va a RAM) | 🟢 Bajo (solo write-back on eviction) |
| **Recomendación** | Para aprobar (más simple) | Para extraordinario (mejor performance) |

## Integración con Data Path

### Modificaciones en Data Path

**ANTES (sin caché)**:
```verilog
// LW/SW van directamente a Memory Control
if (LW or SW) begin
    MC_START <= 1;
    MC_ADDRESS <= ALU_RESULT;
end
```

**DESPUÉS (con data cache)**:
```verilog
// LW/SW van a Data Cache
if (LW) begin
    D_CACHE_READ_REQ <= 1;
    D_CACHE_ADDRESS <= ALU_RESULT;
end

if (SW) begin
    D_CACHE_WRITE_REQ <= 1;
    D_CACHE_ADDRESS <= ALU_RESULT;
    D_CACHE_DATA_WRITE <= Register_Read_Data_2;
end
```

### Modificaciones en Control Unit

Agregar estado para esperar Data Cache:

```verilog
WAIT_DATA_CACHE:
    if (D_CACHE_READY) begin
        state <= WRITEBACK;  // o siguiente estado
    end
```

## Estimación de Trabajo

**Tiempo total**: 5-7 días adicionales (si ya tienes Instruction Cache)

### Desglose

1. **Adaptar diseño de I-Cache** (2 días)
   - Copiar estructura de Instruction Cache
   - Modificar para manejar READ_REQ y WRITE_REQ

2. **Implementar write-through** (2 días)
   - Lógica de actualizar caché + escribir a RAM
   - Estados WAIT_WRITE

3. **Integrar con Data Path** (1 día)
   - Conectar señales de LW/SW
   - Modificar MUX Writeback para recibir de D-Cache

4. **Testing** (2 días)
   - Test LW repetido (hit después de primer miss)
   - Test SW + LW (coherencia)
   - Test array access (secuencial)
   - Test matrix access (no secuencial)

### Si implementas Write-Back (adicional)

5. **Agregar dirty bit** (+2 días)
   - Modificar estructura de línea
   - Lógica de write-back on eviction

6. **Testing write-back** (+1 día)

**Total con write-back**: 8-10 días

## Tests de Validación

### Test 1: LW Repetido
```assembly
# Primera vez: miss, segunda vez: hit
LW R1, 0(R2)      # Miss, carga bloque
LW R3, 0(R2)      # Hit, mismo bloque
```

### Test 2: SW + LW (Coherencia)
```assembly
SW R1, 0(R2)      # Escribe a caché y RAM
LW R3, 0(R2)      # Debe leer valor actualizado
```

### Test 3: Array Access
```assembly
# Acceso secuencial aprovecha bloque de 4 words
ADDI R2, R0, 0x1000
LW R3, 0(R2)      # Miss, carga bloque [0x1000, 0x1004, 0x1008, 0x100C]
LW R4, 4(R2)      # Hit
LW R5, 8(R2)      # Hit
LW R6, 12(R2)     # Hit
LW R7, 16(R2)     # Miss, nuevo bloque
```

## Problemas Conocidos

**Estado actual**: 🔴 NO IMPLEMENTADO

**Impacto**:
- 🟡 No crítico para aprobar (instruction cache es suficiente)
- 🔴 Performance lenta en operaciones LW/SW intensivas
- 🔴 Necesario para nota > 5 puntos (extraordinario)

**Prioridad**: 🟡 MEDIA (después de Instruction Cache)

## Referencias

- [[Cache System Overview]] - Visión general
- [[Instruction Cache]] - Diseño similar
- [[Memory Control]] - Interfaz con RAM
- [[Data Path]] - Integración
- Documentación: `s-mips.pdf` requisitos de caché
- Teoría: Patterson-Hennessy Cap. 5.3 - Cache Performance

---
**Última actualización**: 2025-12-09
**Estado**: 🔴 NO IMPLEMENTADO - PARA EXTRAORDINARIO
**Prioridad**: 🟡 MEDIA
**Requisito**: Instruction Cache debe implementarse primero
