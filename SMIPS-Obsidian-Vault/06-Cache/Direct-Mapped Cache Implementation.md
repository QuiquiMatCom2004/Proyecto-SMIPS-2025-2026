# Direct-Mapped Cache - Implementación Detallada

**Tipo**: Sistema de Cache Completo
**Estado**: 🔴 #faltante **CRÍTICO PARA APROBAR**
**Ubicación**: **NO EXISTE**
**Complejidad**: ⭐⭐⭐ Compleja
**Prioridad**: 🔴 ALTA (para nota > 3)
**Tiempo estimado**: 7-10 días

## Descripción

Direct-Mapped Cache es la implementación más simple de cache. Cada dirección de memoria mapea a exactamente UNA línea de cache. Requerido mínimo: 4 líneas para [[Instruction Cache]] y [[Data Cache]].

## Importancia

**Sin cache**: Máximo 3 puntos (**SUSPENSO**)
**Con cache direct-mapped**: 5 puntos (**APROBADO**)

## Arquitectura General

```
┌────────────────────────────────────────────────────┐
│        DIRECT-MAPPED CACHE (4 líneas mínimo)       │
│                                                    │
│  Address (20 bits usados):                         │
│  ┌────────┬───────┬──────┬────┐                   │
│  │ Tag    │ Index │ Word │Byte│                   │
│  │ 16 bit │ 2 bit │ 2 bit│2bit│                   │
│  └────────┴───────┴──────┴────┘                   │
│      │        │      │     │                       │
│      │        │      │     └─→ Siempre 00         │
│      │        │      └─→ Selección dentro línea   │
│      │        └─→ Selección de línea (0-3)        │
│      └─→ Comparación para hit/miss                │
│                                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │ Cache Lines (4 líneas):                     │  │
│  │                                             │  │
│  │ Line 0: [V][Tag 16][Data 128 bits]         │  │
│  │ Line 1: [V][Tag 16][Data 128 bits]         │  │
│  │ Line 2: [V][Tag 16][Data 128 bits]         │  │
│  │ Line 3: [V][Tag 16][Data 128 bits]         │  │
│  │                                             │  │
│  │ V = Valid bit (1 bit)                       │  │
│  │ Tag = Tag bits (16 bits)                    │  │
│  │ Data = 4 words × 32 bits = 128 bits        │  │
│  └─────────────────────────────────────────────┘  │
│                     ↓                              │
│          ┌──────────────────────┐                  │
│          │   Tag Comparator     │                  │
│          │   Valid & Tag Match? │                  │
│          └──────────────────────┘                  │
│                     ↓                              │
│              ┌──────┴──────┐                       │
│              │             │                       │
│          HIT (1 cycle)   MISS (fetch)             │
└────────────────────────────────────────────────────┘
```

## Estructura de Dirección (Cache de 4 Líneas)

```
Address de CPU (20 bits usados de 32):
┌──────────────────┬────────┬────────┬────────┐
│   Tag            │ Index  │ Word   │ Byte   │
│   16 bits        │ 2 bits │ 2 bits │ 2 bits │
│  [19:4]          │ [3:2]  │ [1:0]  │        │
└──────────────────┴────────┴────────┴────────┘
       │               │        │        │
       │               │        │        └─→ Offset byte (ignorado, siempre alineado)
       │               │        └─→ Offset palabra dentro línea (0-3)
       │               └─→ Selecciona línea de cache (0-3)
       └─→ Para comparación hit/miss

Index bits determinan línea:
├─ 00 → Line 0
├─ 01 → Line 1
├─ 10 → Line 2
└─ 11 → Line 3
```

## Estructura de Línea de Cache

```
Cache Line (149 bits total):
┌──────┬─────────────────┬──────────────────────────────────┐
│Valid │      Tag        │           Data Block             │
│1 bit │    16 bits      │          128 bits                │
└──────┴─────────────────┴──────────────────────────────────┘
   │          │                        │
   │          │                        └─→ 4 words (W0, W1, W2, W3)
   │          └─→ Address bits [19:4]
   └─→ 1 = Valid, 0 = Invalid

Desglose Data Block:
├─ W0: bits [31:0]   - palabra en offset 00
├─ W1: bits [63:32]  - palabra en offset 01
├─ W2: bits [95:64]  - palabra en offset 10
└─ W3: bits [127:96] - palabra en offset 11
```

## Componentes de la Cache

### 1. Cache Line Storage (×4 líneas)

```
Cada línea necesita:
├─ 1 Flip-flop (Valid bit)
├─ 16 Flip-flops o 1 Register 16-bit (Tag)
└─ 128 Flip-flops o 1 Register 128-bit (Data)

Total por línea: 145 bits de almacenamiento
Total 4 líneas: 580 bits (73 bytes)
```

### 2. Index Decoder

```
Input: Index (2 bits)
Output: Line select (one-hot, 4 bits)

Decoder 2:4:
├─ 00 → 0001 (selecciona línea 0)
├─ 01 → 0010 (selecciona línea 1)
├─ 10 → 0100 (selecciona línea 2)
└─ 11 → 1000 (selecciona línea 3)
```

### 3. Tag Comparator

```
Para cada línea:
├─ Comparator 16-bit:
│  ├─ Input A: Stored Tag (de línea)
│  ├─ Input B: Address Tag (bits [19:4])
│  └─ Output: Tags Match?
│
└─ AND Gate:
   ├─ Input A: Valid bit
   ├─ Input B: Tags Match
   └─ Output: Line Hit
```

### 4. Hit/Miss Logic

```
Hit Detector:
├─ OR Gate (4-input):
│  ├─ Input: Line 0 hit
│  ├─ Input: Line 1 hit
│  ├─ Input: Line 2 hit
│  └─ Input: Line 3 hit
│
├─ Output: CACHE_HIT (1 = hit, 0 = miss)
```

### 5. Data Output Multiplexer

```
Data Selector:
├─ MUX 4:1 (128 bits):
│  ├─ Input 0: Line 0 data
│  ├─ Input 1: Line 1 data
│  ├─ Input 2: Line 2 data
│  ├─ Input 3: Line 3 data
│  ├─ Select: Index (2 bits)
│  └─ Output: Selected Data Block (128 bits)
│
└─ Word Selector (MUX 4:1, 32 bits):
   ├─ Input: Data Block (4 words)
   ├─ Select: Word offset (bits [3:2])
   └─ Output: DATA_OUT (32 bits)
```

## Pseudocódigo Verilog

```verilog
module direct_mapped_cache #(
    parameter NUM_LINES = 4,
    parameter INDEX_BITS = 2,  // log2(NUM_LINES)
    parameter TAG_BITS = 16,
    parameter BLOCK_SIZE = 128 // 4 words × 32 bits
)(
    input wire CLK,
    input wire RESET,
    input wire [19:0] ADDRESS,  // 20 bits usados
    input wire READ_ENABLE,
    input wire WRITE_ENABLE,
    input wire [31:0] DATA_IN,  // Para write-through
    input wire [127:0] BLOCK_IN, // Para cache fill
    input wire FILL_ENABLE,     // De Memory Control
    output wire CACHE_HIT,
    output wire [31:0] DATA_OUT,
    output wire MISS_REQUEST,
    output wire [15:0] MISS_ADDR // Block address para fetch
);

// Extraer campos de dirección
wire [TAG_BITS-1:0] tag = ADDRESS[19:4];
wire [INDEX_BITS-1:0] index = ADDRESS[3:2];
wire [1:0] word_offset = ADDRESS[3:2]; // Reuso para selección palabra

// Cache lines storage
reg valid [0:NUM_LINES-1];
reg [TAG_BITS-1:0] tags [0:NUM_LINES-1];
reg [BLOCK_SIZE-1:0] data [0:NUM_LINES-1];

// Hit detection
wire [NUM_LINES-1:0] line_hit;
genvar i;
generate
    for (i = 0; i < NUM_LINES; i = i + 1) begin: hit_check
        assign line_hit[i] = valid[i] && (tags[i] == tag);
    end
endgenerate

assign CACHE_HIT = |line_hit; // OR de todos los hits

// Miss request
assign MISS_REQUEST = (READ_ENABLE || WRITE_ENABLE) && !CACHE_HIT;
assign MISS_ADDR = ADDRESS[19:4]; // Block address

// Data output (si hit)
wire [BLOCK_SIZE-1:0] selected_block = data[index];

// Word selector dentro del bloque
reg [31:0] selected_word;
always @(*) begin
    case (word_offset)
        2'b00: selected_word = selected_block[31:0];
        2'b01: selected_word = selected_block[63:32];
        2'b10: selected_word = selected_block[95:64];
        2'b11: selected_word = selected_block[127:96];
    endcase
end

assign DATA_OUT = CACHE_HIT ? selected_word : 32'h00000000;

// Cache fill (on miss)
integer j;
always @(posedge CLK) begin
    if (RESET) begin
        for (j = 0; j < NUM_LINES; j = j + 1) begin
            valid[j] <= 1'b0;
            tags[j] <= {TAG_BITS{1'b0}};
            data[j] <= {BLOCK_SIZE{1'b0}};
        end
    end
    else if (FILL_ENABLE) begin
        // Fill cache line on miss
        valid[index] <= 1'b1;
        tags[index] <= tag;
        data[index] <= BLOCK_IN;
    end
    else if (WRITE_ENABLE && CACHE_HIT) begin
        // Write-through: actualizar cache
        case (word_offset)
            2'b00: data[index][31:0] <= DATA_IN;
            2'b01: data[index][63:32] <= DATA_IN;
            2'b10: data[index][95:64] <= DATA_IN;
            2'b11: data[index][127:96] <= DATA_IN;
        endcase
    end
end

endmodule
```

## Flujo de Operación

### Caso 1: Cache Hit (Lectura)

```
1. CPU solicita lectura en ADDRESS

2. Cache extrae:
   ├─ Index = ADDRESS[3:2] → selecciona línea
   ├─ Tag = ADDRESS[19:4] → para comparación
   └─ Word offset = ADDRESS[3:2] → selecciona palabra

3. Cache comprueba línea seleccionada:
   ├─ Valid = 1? ✓
   ├─ Stored Tag == Address Tag? ✓
   └─ HIT!

4. Cache devuelve dato:
   ├─ Selecciona bloque de línea (index)
   ├─ Selecciona palabra de bloque (word offset)
   └─ DATA_OUT → CPU (1 ciclo)

Total: 1 ciclo ⚡
```

### Caso 2: Cache Miss (Lectura)

```
1. CPU solicita lectura

2. Cache comprueba:
   ├─ Valid = 0? O
   ├─ Stored Tag ≠ Address Tag?
   └─ MISS!

3. Cache solicita a Memory Control:
   ├─ MISS_REQUEST = 1
   └─ MISS_ADDR = ADDRESS[19:4] (block address)

4. Memory Control hace fetch de RAM:
   ├─ Espera RT cycles
   └─ Devuelve bloque completo (4 words)

5. Cache almacena bloque (fill):
   ├─ valid[index] = 1
   ├─ tags[index] = tag
   └─ data[index] = bloque de RAM

6. Cache devuelve dato solicitado

Total: 1 + RT + fill cycles (~5-8 ciclos)
```

### Caso 3: Cache Hit (Escritura, Write-Through)

```
1. CPU solicita escritura

2. Cache comprueba: HIT ✓

3. Cache actualiza:
   ├─ Actualiza palabra en línea
   └─ (Write-through: también a RAM vía Memory Control)

4. Memory Control escribe a RAM (WT cycles)

Total: 1 + WT cycles (para consistencia)
```

## Integración con Control Unit

### Sin Cache (Estado Actual)

```
Control Unit → Memory Control → RAM
      (cada fetch = RT cycles)
```

### Con Instruction Cache

```
Control Unit → I-Cache → Memory Control → RAM
                   ↓ hit             ↓ miss
               1 ciclo          1+RT ciclos
```

**Speedup esperado**: 2-5× para programas con localidad

## Mapeo de Direcciones

### Ejemplo: Cache de 4 Líneas

```
Direcciones que mapean a Line 0 (index=00):
├─ 0x00000 (bits [3:2] = 00)
├─ 0x00004 (bits [3:2] = 01) ← NO, este es Line 1
│
Corrección: Index son bits [5:4] para 4 líneas:
├─ Line 0: direcciones con bits [5:4] = 00
│  └─ 0x00, 0x10, 0x20, 0x30, ...
├─ Line 1: direcciones con bits [5:4] = 01
│  └─ 0x10, 0x30, 0x50, 0x70, ...
├─ Line 2: direcciones con bits [5:4] = 10
└─ Line 3: direcciones con bits [5:4] = 11
```

**IMPORTANTE**: Ajustar bits de index según número de líneas:
- 4 líneas: index = ADDRESS[5:4]
- 8 líneas: index = ADDRESS[6:4]
- 16 líneas: index = ADDRESS[7:4]

## Performance Metrics

### Hit Rate

```
Hit Rate = Hits / (Hits + Misses)

Ejemplo:
100 accesos a memoria
85 hits
15 misses

Hit Rate = 85 / 100 = 85%
```

### Average Access Time

```
AMAT = Hit Time + (Miss Rate × Miss Penalty)

Ejemplo:
├─ Hit Time = 1 ciclo
├─ Miss Penalty = 5 ciclos (RT)
├─ Hit Rate = 85%
└─ Miss Rate = 15%

AMAT = 1 + (0.15 × 5) = 1.75 ciclos promedio
```

**Sin cache**: Cada acceso = 5 ciclos
**Con cache**: Promedio = 1.75 ciclos
**Speedup**: 5 / 1.75 = 2.86×

## Tests de Validación

### Test 1: Cold Miss → Hit

```assembly
# Primera lectura: miss (cache vacía)
lw r1, 0(r0)    # MISS → fetch de RAM (~5 ciclos)

# Segunda lectura misma dirección: hit
lw r2, 0(r0)    # HIT → 1 ciclo

# Verificar mismo valor
beq r1, r2, pass

fail:
addi r10, r0, 1
halt

pass:
addi r10, r0, 99
halt
```

### Test 2: Spatial Locality

```assembly
# Leer 4 palabras consecutivas del mismo bloque
lw r1, 0(r0)    # MISS → trae bloque completo
lw r2, 4(r0)    # HIT (mismo bloque, word 1)
lw r3, 8(r0)    # HIT (mismo bloque, word 2)
lw r4, 12(r0)   # HIT (mismo bloque, word 3)

# Total: 1 miss + 3 hits
# Sin cache: 4 misses
```

### Test 3: Conflict Miss

```assembly
# Direcciones que mapean a misma línea
# Asumiendo cache 4 líneas, index = bits [5:4]

lw r1, 0(r0)      # Address 0x00 → line 0, MISS
lw r2, 64(r0)     # Address 0x40 → line 0, CONFLICT MISS
                  # (0x40 bits [5:4] = 01, diferente! Corregir)

# Ejemplo correcto para Line 0:
lw r1, 0(r0)      # 0x00 → line 0
lw r2, 256(r0)    # 0x100 → line 0 (si index correcto)
                  # Segundo acceso expulsa primero (replacement)
```

## Limitaciones de Direct-Mapped

### Problema: Conflict Misses

```
Dos direcciones diferentes que mapean a la misma línea:
├─ Address A: tag=0x123, index=0
└─ Address B: tag=0x456, index=0

Acceso alternado A, B, A, B:
├─ A: miss (fill line 0)
├─ B: miss (expulsa A, fill line 0)
├─ A: miss (expulsa B, fill line 0)
└─ B: miss (expulsa A, fill line 0)

Hit rate: 0% (terrible!)
```

**Solución**: Set-associative cache (permite múltiples tags por index)

## Implementación en Logisim

### Estructura Recomendada

```
Subcircuito "Instruction Cache" (o "Data Cache")
├─ Inputs:
│  ├─ ADDRESS (20 bits)
│  ├─ READ_EN (1 bit)
│  ├─ WRITE_EN (1 bit)
│  ├─ DATA_IN (32 bits, para write)
│  ├─ BLOCK_IN (128 bits, para fill)
│  └─ FILL_EN (1 bit, desde Memory Control)
│
├─ Components:
│  ├─ 4 × Cache Line Registers (145 bits each)
│  ├─ Index Decoder (2:4)
│  ├─ 4 × Tag Comparators (16-bit)
│  ├─ Hit Detector (OR gate)
│  ├─ Data MUX (4:1, 128-bit)
│  └─ Word Selector (4:1, 32-bit)
│
└─ Outputs:
   ├─ CACHE_HIT (1 bit)
   ├─ DATA_OUT (32 bits)
   └─ MISS_ADDR (16 bits)
```

### Cost Estimado

```
Por cache (4 líneas):
├─ Registers: ~20 unidades
├─ Comparators: ~5 unidades
├─ Multiplexers: ~3 unidades
├─ Logic gates: ~2 unidades
└─ Total: ~30 unidades

Ambas caches (I + D): ~60 unidades
Resto del CPU: ~40 unidades
TOTAL: ~100 unidades ✓ (dentro del límite)
```

## Enlaces Relacionados

- [[Cache System Overview]] - Visión general del sistema
- [[Instruction Cache]] - Especificación de I-Cache
- [[Data Cache]] - Especificación de D-Cache
- [[Memory Control]] - Para miss handling
- [[Set-Associative Cache Implementation]] - Versión avanzada

---

**Prioridad**: 🔴 ALTA (para aprobar)
**Tiempo**: 7-10 días (ambas caches)
**Complejidad**: Alta pero alcanzable
**Reward**: +2 puntos (de 3 a 5)
**Bloquea**: Aprobado del proyecto
