# Word Selector (Selector de Palabra)

**Tipo**: Lógica Combinacional Personalizada
**Estado**: 🔴 #faltante **BLOQUEANTE**
**Ubicación**: **NO EXISTE** (debe estar dentro de [[Memory Control]])
**Complejidad**: ⭐⭐ Moderada
**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 2-3 horas

## Descripción

El Word Selector selecciona una palabra específica de 32 bits de las 4 palabras (128 bits totales) que devuelve la RAM en cada lectura de bloque. Usa los bits [3:2] de la dirección para determinar qué palabra seleccionar.

## Problema que Resuelve

### Organización de la RAM

La RAM devuelve **bloques completos de 16 bytes = 4 palabras**:

```
RAM Block (16 bytes = 128 bits):
┌─────────┬─────────┬─────────┬─────────┐
│   O0    │   O1    │   O2    │   O3    │
│ Word 0  │ Word 1  │ Word 2  │ Word 3  │
│ [31:0]  │ [31:0]  │ [31:0]  │ [31:0]  │
│Bytes 0-3│Bytes 4-7│Bytes 8-B│Bytes C-F│
└─────────┴─────────┴─────────┴─────────┘
```

### Dirección de Byte del CPU

```
Address (32 bits):
┌───────────┬─────────────┬────┬────┐
│ [31:20]   │   [19:4]    │[3:2│[1:0│
│  Unused   │Block Address│Word│Byte│
└───────────┴─────────────┴────┴────┘
              16 bits      2bit  2bit
                           │     │
                           │     └─→ Siempre 00 (alineación 4 bytes)
                           │
                           └─→ Selecciona palabra dentro del bloque
```

### Mapeo Word Offset → Palabra

| Bits [3:2] | Palabra | Bytes | Salida RAM |
|------------|---------|-------|------------|
| 00 | Word 0 | 0-3 | O0 |
| 01 | Word 1 | 4-7 | O1 |
| 10 | Word 2 | 8-11 | O2 |
| 11 | Word 3 | 12-15 | O3 |

## Arquitectura

```
┌────────────────────────────────────────────────────┐
│              WORD SELECTOR                         │
│                                                    │
│  Address[3:2] = Word Offset                        │
│        │                                           │
│        ▼                                           │
│  ┌──────────┐                                      │
│  │   MUX    │                                      │
│  │   4:1    │                                      │
│  │  32-bit  │                                      │
│  └──────────┘                                      │
│     ▲  ▲  ▲  ▲                                     │
│     │  │  │  │                                     │
│    O0 O1 O2 O3  (después de Little-Endian Conv)    │
│                                                    │
│        │                                           │
│        ▼                                           │
│  Selected Word (32 bits) → DATA_READ               │
└────────────────────────────────────────────────────┘
```

## Entradas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `O0_converted` | 32 bits | Palabra 0 (después de conversión endian) |
| `O1_converted` | 32 bits | Palabra 1 (después de conversión endian) |
| `O2_converted` | 32 bits | Palabra 2 (después de conversión endian) |
| `O3_converted` | 32 bits | Palabra 3 (después de conversión endian) |
| `WORD_OFFSET` | 2 bits | Bits [3:2] de la dirección |

## Salidas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `DATA_READ` | 32 bits | Palabra seleccionada para el CPU |

## Lógica de Selección

### Tabla de Verdad

| WORD_OFFSET[1] | WORD_OFFSET[0] | DATA_READ |
|----------------|----------------|-----------|
| 0 | 0 | O0_converted |
| 0 | 1 | O1_converted |
| 1 | 0 | O2_converted |
| 1 | 1 | O3_converted |

### Pseudocódigo

```verilog
module word_selector (
    input wire [31:0] O0_conv,
    input wire [31:0] O1_conv,
    input wire [31:0] O2_conv,
    input wire [31:0] O3_conv,
    input wire [1:0] word_offset,
    output reg [31:0] data_read
);

always @(*) begin
    case (word_offset)
        2'b00: data_read = O0_conv;
        2'b01: data_read = O1_conv;
        2'b10: data_read = O2_conv;
        2'b11: data_read = O3_conv;
        default: data_read = 32'h00000000;
    endcase
end

endmodule
```

## Implementación en Logisim

### Opción 1: Multiplexer Nativo

```
Componente: Multiplexer
├─ Data Bits: 32
├─ Select Bits: 2
├─ Inputs: 4
└─ Conexiones:
   ├─ Input 0: O0_converted
   ├─ Input 1: O1_converted
   ├─ Input 2: O2_converted
   ├─ Input 3: O3_converted
   ├─ Select: WORD_OFFSET (bits [3:2] de ADDRESS)
   └─ Output: DATA_READ
```

### Opción 2: Lógica con Demux + AND + OR

```
1. Decoder 2:4
   ├─ Input: WORD_OFFSET[1:0]
   └─ Outputs: enable[0], enable[1], enable[2], enable[3]

2. AND Gates (4 × 32-bit)
   ├─ O0_conv AND enable[0] (broadcasted)
   ├─ O1_conv AND enable[1]
   ├─ O2_conv AND enable[2]
   └─ O3_conv AND enable[3]

3. OR Gate (4-input, 32-bit)
   └─ Combina todos los resultados AND
```

**Recomendación**: Usar Multiplexer nativo (Opción 1) - más simple y eficiente.

## Ejemplos de Uso

### Ejemplo 1: LW R1, 0(R0)

```
Dirección solicitada: 0x00000000
└─ Block address: 0x0000 (bits [19:4])
└─ Word offset: 0b00 (bits [3:2])

RAM devuelve bloque 0:
├─ O0 = 0x12345678
├─ O1 = 0xAABBCCDD
├─ O2 = 0xDEADBEEF
└─ O3 = 0xCAFEBABE

Después de Little-Endian Conversion:
├─ O0_conv = 0x1E6A2C48
├─ O1_conv = 0xBB33DD57
├─ O2_conv = 0xF77DB57B
└─ O3_conv = 0x5D7F5F53

Word Selector:
├─ WORD_OFFSET = 0b00
└─ DATA_READ = O0_conv = 0x1E6A2C48 ✓

R1 recibe: 0x1E6A2C48
```

### Ejemplo 2: LW R2, 4(R0)

```
Dirección solicitada: 0x00000004
└─ Block address: 0x0000 (mismo bloque)
└─ Word offset: 0b01 (bits [3:2])

RAM devuelve mismo bloque 0 (ya en caché idealmente):
├─ O0_conv = 0x1E6A2C48
├─ O1_conv = 0xBB33DD57
├─ O2_conv = 0xF77DB57B
└─ O3_conv = 0x5D7F5F53

Word Selector:
├─ WORD_OFFSET = 0b01
└─ DATA_READ = O1_conv = 0xBB33DD57 ✓

R2 recibe: 0xBB33DD57
```

### Ejemplo 3: LW R3, 8(R0)

```
Dirección: 0x00000008
└─ Word offset: 0b10

Word Selector:
├─ WORD_OFFSET = 0b10
└─ DATA_READ = O2_conv = 0xF77DB57B ✓

R3 recibe: 0xF77DB57B
```

### Ejemplo 4: LW R4, 12(R0)

```
Dirección: 0x0000000C
└─ Word offset: 0b11

Word Selector:
├─ WORD_OFFSET = 0b11
└─ DATA_READ = O3_conv = 0x5D7F5F53 ✓

R4 recibe: 0x5D7F5F53
```

### Ejemplo 5: Direcciones en Diferentes Bloques

```
Dirección: 0x00000010 (16 decimal)
└─ Block address: 0x0001 (bloque 1)
└─ Word offset: 0b00 (palabra 0 del bloque 1)

RAM devuelve bloque 1:
├─ O0_conv = 0x11111111
├─ O1_conv = 0x22222222
├─ O2_conv = 0x33333333
└─ O3_conv = 0x44444444

Word Selector:
├─ WORD_OFFSET = 0b00
└─ DATA_READ = 0x11111111 ✓
```

## Integración en Memory Control

### Flujo Completo de Lectura

```
1. Control Unit solicita lectura en ADDRESS

2. Address Translator extrae:
   ├─ Block Address (bits [19:4]) → a RAM
   └─ Word Offset (bits [3:2]) → a Word Selector

3. Memory State Machine espera RT cycles

4. RAM devuelve O0, O1, O2, O3 (big-endian)

5. Little-Endian Converter (×4) convierte:
   ├─ O0 → O0_conv
   ├─ O1 → O1_conv
   ├─ O2 → O2_conv
   └─ O3 → O3_conv

6. Word Selector selecciona:
   ├─ Input: O0_conv, O1_conv, O2_conv, O3_conv
   ├─ Select: Word Offset (bits [3:2])
   └─ Output: DATA_READ (palabra correcta)

7. DATA_READ va al Data Path/Cache
```

### Diagrama de Conexiones

```
Memory Control
│
├─ Address Translator
│  ├─ ADDRESS[19:4] → RAM (ADDR)
│  └─ ADDRESS[3:2] → Word Selector (WORD_OFFSET)
│
├─ RAM Interface
│  ├─ O0 (32-bit, big-endian)
│  ├─ O1 (32-bit, big-endian)
│  ├─ O2 (32-bit, big-endian)
│  └─ O3 (32-bit, big-endian)
│
├─ Little-Endian Converters (×4)
│  ├─ O0 → O0_conv
│  ├─ O1 → O1_conv
│  ├─ O2 → O2_conv
│  └─ O3 → O3_conv
│
└─ Word Selector ⭐
   ├─ Inputs: O0_conv, O1_conv, O2_conv, O3_conv
   ├─ Select: WORD_OFFSET (ADDRESS[3:2])
   └─ Output: DATA_READ → Data Path
```

## Para Escrituras (SW)

Para escrituras, el Word Selector NO se usa directamente. En su lugar:

1. El dato a escribir (DATA_WRITE) va a UNA de las 4 palabras (I0-I3)
2. [[MASK Generator]] determina cuál(es) palabra(s) escribir
3. El Word Offset se usa para seleccionar qué I0/I1/I2/I3 recibe el dato

**Ver**: [[MASK Generator]] para detalles de escritura.

## Tests de Validación

### Test 1: Lectura de 4 Palabras Consecutivas

```assembly
# Escribir patrón conocido
addi r1, r0, 0x1111
sw r1, 0(r0)    # Word 0 del bloque 0

addi r2, r0, 0x2222
sw r2, 4(r0)    # Word 1 del bloque 0

addi r3, r0, 0x3333
sw r3, 8(r0)    # Word 2 del bloque 0

addi r4, r0, 0x4444
sw r4, 12(r0)   # Word 3 del bloque 0

# Leer de vuelta
lw r5, 0(r0)    # Debe ser 0x1111
lw r6, 4(r0)    # Debe ser 0x2222
lw r7, 8(r0)    # Debe ser 0x3333
lw r8, 12(r0)   # Debe ser 0x4444

# Verificar
beq r5, r1, test1_ok
halt
test1_ok:
beq r6, r2, test2_ok
halt
test2_ok:
beq r7, r3, test3_ok
halt
test3_ok:
beq r8, r4, success
halt

success:
addi r10, r0, 99  # PASS
halt
```

### Test 2: Offset Correcto

```assembly
# Escribir valor único en cada posición
addi r1, r0, 0xAAAA
sw r1, 0(r0)

addi r2, r0, 0xBBBB
sw r2, 4(r0)

# Verificar que NO se confunden
lw r3, 0(r0)
beq r3, r1, ok1
halt
ok1:

lw r4, 4(r0)
beq r4, r2, ok2
halt
ok2:

# Verificar que 0 != 4
beq r3, r4, fail   # Si son iguales, algo mal
addi r10, r0, 99   # PASS
halt

fail:
addi r10, r0, 1    # FAIL
halt
```

## Troubleshooting

### Problema: LW siempre devuelve O0

**Síntoma**: Todas las lecturas devuelven la misma palabra (O0)

**Causa**: Word Selector no conectado correctamente
- WORD_OFFSET no llega al selector
- Selector siempre en 00

**Solución**: Verificar que ADDRESS[3:2] se extrae y conecta al MUX select

### Problema: Lecturas incorrectas pero consistentes

**Síntoma**: LW devuelve valores incorrectos pero reproducibles

**Causa**: Word Offset mal extraído
- Usando bits incorrectos (ej: [2:1] en vez de [3:2])
- Off-by-one en selección

**Solución**: Verificar Address Translator

### Problema: Valores aleatorios

**Síntoma**: Cada LW devuelve valor diferente e impredecible

**Causa**: Word Selector recibe datos inestables
- Little-Endian Converter no completo
- Timing incorrecto

**Solución**: Verificar pipeline completo: RAM → Converter → Selector

## Optimización para Cache

Cuando se implementa cache, el Word Selector se usa de forma similar:

```
Cache Line (4 palabras):
├─ Word 0
├─ Word 1
├─ Word 2
└─ Word 3

Cache Hit:
├─ Word Offset (bits [3:2]) → Word Selector
└─ Selecciona palabra de la línea de cache
```

**Ventaja**: Mismo Word Selector puede usarse tanto para:
- Lecturas directas de RAM (sin cache)
- Lecturas de líneas de cache (con cache)

## Costo en Logisim

### Usando MUX Nativo

```
Componentes:
└─ 1 Multiplexer (4:1, 32-bit)

Costo estimado: ~2 unidades
```

### Usando Lógica Discreta

```
Componentes:
├─ 1 Decoder (2:4)
├─ 4 AND gates (32-bit)
└─ 1 OR gate (4-input, 32-bit)

Costo estimado: ~5-6 unidades
```

**Recomendación**: MUX nativo (más eficiente)

## Enlaces Relacionados

- [[Memory Control]] - Componente padre
- [[Address Translator]] - Proporciona WORD_OFFSET
- [[Little-Endian Converter]] - Prepara datos antes de selección
- [[MASK Generator]] - Equivalente para escrituras
- [[Memory State Machine]] - Coordina timing

---

**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 2-3 horas
**Complejidad**: Baja (es un MUX 4:1)
**Bloquea**: Lecturas de memoria (LW)
**Tests afectados**: tests/mem.asm, tests/sw-lw.asm, tests/push-pop.asm
