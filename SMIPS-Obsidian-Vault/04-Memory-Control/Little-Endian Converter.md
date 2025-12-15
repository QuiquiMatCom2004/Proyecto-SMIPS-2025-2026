# Little-Endian Converter (Conversor de Endianness)

**Tipo**: Circuito Combinacional
**Estado**: 🔴 #implementado 
**Ubicación**: **NO EXISTE** (debe estar dentro de [[Memory Control]])
**Complejidad**: ⭐ Simple
**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 3-4 horas

## Descripción

El Little-Endian Converter realiza la conversión de endianness entre el CPU (little-endian) y la RAM (big-endian). Invierte el orden de los bits en cada palabra de 32 bits mediante bit reversal.

## Problema que Resuelve

### CPU S-MIPS (Little-Endian)
```
Byte Order: [Byte 0][Byte 1][Byte 2][Byte 3]
            LSB                           MSB
Bit Order:  [7:0][15:8][23:16][31:24]
```

### RAM (Big-Endian)
```
Byte Order: [Byte 3][Byte 2][Byte 1][Byte 0]
            MSB                           LSB
Bit Order:  [31:24][23:16][15:8][7:0]
```

**Sin conversión**: Los datos se interpretan incorrectamente.

## Conversión Requerida

### Bit Reversal Completo

**Entrada (Big-Endian de RAM)**:
```
Bit:  31 30 29 ... 3  2  1  0
Val:  A  B  C  ... X  Y  Z  W
```

**Salida (Little-Endian para CPU)**:
```
Bit:  31 30 29 ... 3  2  1  0
Val:  W  Z  Y  ... C  B  A
```

**Mapeo**:
- Bit[0] ↔ Bit[31]
- Bit[1] ↔ Bit[30]
- Bit[2] ↔ Bit[29]
- ...
- Bit[15] ↔ Bit[16]

## Implementación

### Pseudocódigo

```verilog
module little_endian_converter (
    input wire [31:0] big_endian_in,
    output wire [31:0] little_endian_out
);

// Bit reversal directo
assign little_endian_out[0]  = big_endian_in[31];
assign little_endian_out[1]  = big_endian_in[30];
assign little_endian_out[2]  = big_endian_in[29];
// ...
assign little_endian_out[30] = big_endian_in[1];
assign little_endian_out[31] = big_endian_in[0];

// O en loop:
genvar i;
generate
    for (i = 0; i < 32; i = i + 1) begin
        assign little_endian_out[i] = big_endian_in[31-i];
    end
endgenerate

endmodule
```

### Implementación en Logisim

```
Componentes:
├─ Splitter "Split to Bits" (32 bits → 32 bits individuales)
│  ├─ Input: big_endian_in (32 bits)
│  └─ Outputs: bit[0], bit[1], ..., bit[31]
│
└─ Splitter "Combine Reversed" (32 bits individuales → 32 bits)
   ├─ Inputs (en orden invertido):
   │  ├─ bit[31] → posición 0
   │  ├─ bit[30] → posición 1
   │  ├─ ...
   │  ├─ bit[1] → posición 30
   │  └─ bit[0] → posición 31
   └─ Output: little_endian_out (32 bits)
```

## Ejemplo de Conversión

### Ejemplo 1: Número 0x12345678

**Big-Endian (RAM almacena así)**:
```
Hex:        0x12345678
Binary:     00010010 00110100 01010110 01111000
Bytes:      [0x12]   [0x34]   [0x56]   [0x78]
            MSB                          LSB
```

**Little-Endian (CPU necesita así)**:
```
Binary:     00011110 01101010 00101100 01001000
Hex:        0x1E6A2C48
Bytes:      [0x1E]   [0x6A]   [0x2C]   [0x48]
            LSB                          MSB
```

**Verificación bit a bit**:
```
Big[31]=0 → Little[0]=0
Big[30]=0 → Little[1]=0
Big[29]=0 → Little[2]=0
Big[28]=1 → Little[3]=1
Big[27]=0 → Little[4]=0
...
Big[0]=0 → Little[31]=0
```

### Ejemplo 2: Número 0xDEADBEEF

**Big-Endian**:
```
0xDEADBEEF
= 11011110 10101101 10111110 11101111
```

**Little-Endian**:
```
= 11110111 01111101 10110101 01111011
= 0xF77DB57B
```

## Instancias Necesarias en Memory Control

Memory Control requiere **5 instancias** del Little-Endian Converter:

### Para Lectura (RAM → CPU)
- **Converter 0**: O0_raw → O0_conv
- **Converter 1**: O1_raw → O1_conv
- **Converter 2**: O2_raw → O2_conv
- **Converter 3**: O3_raw → O3_conv

### Para Escritura (CPU → RAM)
- **Converter 4**: DATA_WRITE → DATA_WRITE_conv

### Diagrama de Conexión

```
Memory Control
├─ FROM RAM (Lectura):
│  ├─ O0_raw (32 bits) ──► Little-Endian Converter 0 ──► O0_conv
│  ├─ O1_raw (32 bits) ──► Little-Endian Converter 1 ──► O1_conv
│  ├─ O2_raw (32 bits) ──► Little-Endian Converter 2 ──► O2_conv
│  └─ O3_raw (32 bits) ──► Little-Endian Converter 3 ──► O3_conv
│      └─► Word Selector (selecciona 1 de 4)
│          └─► DATA_READ to CPU
│
└─ TO RAM (Escritura):
   └─ DATA_WRITE (CPU, little-endian)
       └─► Little-Endian Converter 4
           └─► DATA_WRITE_conv (big-endian)
               └─► I0/I1/I2/I3 (según MASK)
```

## Integración en Memory Control

### Para Lectura (RAM → CPU)

```
RAM outputs O0-O3 (big-endian)
      ↓
Little-Endian Converter (4 instancias paralelas)
      ├─ Converter 0: O0_raw → O0_little
      ├─ Converter 1: O1_raw → O1_little
      ├─ Converter 2: O2_raw → O2_little
      └─ Converter 3: O3_raw → O3_little
      ↓
Word Selector (selecciona según word_offset)
      ↓
DATA_READ to CPU (correcto)
```

### Para Escritura (CPU → RAM)

```
DATA_WRITE from CPU (little-endian)
      ↓
Little-Endian Converter (1 instancia)
      ↓
Converted data (big-endian)
      ↓
Distribuido a I0-I3 según MASK
      ↓
RAM (almacena correctamente)
```

## Conexión en Memory Control

```
Memory Control
├─ FROM RAM:
│  ├─ O0_raw, O1_raw, O2_raw, O3_raw (big-endian)
│  │
│  └─► Little-Endian Converter (4× instancias)
│      ├─ O0_conv = reverse(O0_raw)
│      ├─ O1_conv = reverse(O1_raw)
│      ├─ O2_conv = reverse(O2_raw)
│      └─ O3_conv = reverse(O3_raw)
│      │
│      └─► Word Selector
│          └─► DATA_READ (to CPU)
│
└─ TO RAM:
   ├─ DATA_WRITE (from CPU, little-endian)
   │
   └─► Little-Endian Converter (1× instancia)
       └─► I0/I1/I2/I3 (big-endian, según MASK)
```

## Test de Validación

### Test 1: Reversibilidad

```
Input:  0x12345678 (big-endian)
Convert to little-endian: 0x1E6A2C48
Convert back to big-endian: 0x12345678 ✓
```

### Test 2: Lectura de Memoria

```assembly
# Escribir 0xAABBCCDD en memoria
addi r1, r0, 0xAABB    # r1 = 0x0000AABB
sll r1, r1, 16         # r1 = 0xAABB0000
ori r1, r1, 0xCCDD     # r1 = 0xAABBCCDD
sw r1, 0(r0)           # Memory[0] = 0xAABBCCDD

# Leer de vuelta
lw r2, 0(r0)           # r2 debe ser 0xAABBCCDD

# Verificar
beq r1, r2, success    # Debe saltar
addi r3, r0, 1         # FAIL
halt
success:
addi r3, r0, 2         # PASS
halt
```

**Qué verifica**: Sin conversión correcta, r2 ≠ r1

### Test 3: Bytes Individuales

```assembly
# Escribir bytes específicos
addi r1, r0, 0x0102
sll r1, r1, 16
ori r1, r1, 0x0304     # r1 = 0x01020304
sw r1, 0(r0)

lw r2, 0(r0)

# Extraer bytes y verificar
andi r3, r2, 0xFF      # r3 = 0x04 (byte 0)
srl r4, r2, 8
andi r4, r4, 0xFF      # r4 = 0x03 (byte 1)
srl r5, r2, 16
andi r5, r5, 0xFF      # r5 = 0x02 (byte 2)
srl r6, r2, 24         # r6 = 0x01 (byte 3)

halt
# Verificar: r3=4, r4=3, r5=2, r6=1
```

## Caso Sin Conversión (ERROR)

### Sin Converter

```
CPU escribe: 0xDEADBEEF
RAM almacena: 0xDEADBEEF (como está)
CPU lee: 0xDEADBEEF
```

**Problema**: RAM es big-endian internamente, pero bits no se reordenan.
**Resultado**: Datos corruptos.

### Con Converter

```
CPU escribe: 0xDEADBEEF (little-endian en su vista)
→ Converter: 0xF77DB57B (big-endian para RAM)
RAM almacena: 0xF77DB57B
CPU lee: RAM devuelve 0xF77DB57B
→ Converter: 0xDEADBEEF (de vuelta a little-endian)
CPU recibe: 0xDEADBEEF ✓
```

## Implementación Logisim Detallada

### Subcircuito "Little Endian Converter 32"

**Entradas**:
- `IN[31:0]` - Dato en un formato

**Salidas**:
- `OUT[31:0]` - Dato en formato opuesto

**Implementación**:
```
1. Splitter de entrada
   ├─ Bit Width: 32
   ├─ Fan Out: 32
   └─ Outputs: 32 bits individuales

2. Splitter de salida (reordenado)
   ├─ Bit Width: 32
   ├─ Fan Out: 32
   └─ Inputs conectados en orden inverso:
      ├─ Input 0 ← bit 31 de entrada
      ├─ Input 1 ← bit 30 de entrada
      ├─ ...
      ├─ Input 30 ← bit 1 de entrada
      └─ Input 31 ← bit 0 de entrada
```

**Costo**: ~34 componentes (2 splitters + conexiones)

### Resumen de Instancias Necesarias

| Instancia | Propósito | Entrada | Salida | Destino |
|-----------|-----------|---------|--------|---------|
| Converter 0 | Lectura | O0_raw (RAM) | O0_conv | Word Selector |
| Converter 1 | Lectura | O1_raw (RAM) | O1_conv | Word Selector |
| Converter 2 | Lectura | O2_raw (RAM) | O2_conv | Word Selector |
| Converter 3 | Lectura | O3_raw (RAM) | O3_conv | Word Selector |
| Converter 4 | Escritura | DATA_WRITE (CPU) | DATA_WRITE_conv | I0-I3 (según MASK) |

**Total**: 5 instancias del subcircuito Little-Endian Converter

**Nota**: Todas las instancias usan el mismo subcircuito, ya que bit reversal es una operación simétrica (reversible).

## Optimización (Avanzado)

### Converter Bidireccional

```
Converter bidireccional:
├─ Input: DATA_IN (32 bits)
├─ Output: DATA_OUT (32 bits)
└─ Nota: Bit reversal es simétrico
         reverse(reverse(x)) = x
         → Mismo circuito para ambas direcciones
```

**Ventaja**: Reutilizar mismo subcircuito para read y write.

## Troubleshooting

### Problema: Datos incorrectos después de LW

**Síntoma**: `sw r1, 0(r0)` seguido de `lw r2, 0(r0)` resulta en r1 ≠ r2

**Causa probable**: Little-Endian Converter faltante o mal conectado

**Solución**: Verificar conversión en ambas direcciones

### Problema: Tests de memoria fallan

**Síntoma**: tests/mem.asm, tests/sw-lw.asm fallan

**Causa**: Endianness incorrecto

**Solución**: Implementar este componente

### Problema: Valores "al revés"

**Síntoma**: Escribo 0x12345678, leo 0x1E6A2C48

**Causa**: Converter operando, pero datos se interpretan mal

**Solución**: Verificar que converter esté en ambos read y write paths

## Enlaces Relacionados

- [[Memory Control]] - Componente padre
- [[Memory State Machine]] - Coordina timing
- [[Word Selector]] - Selecciona palabra después de conversión
- [[Address Translator]] - Traduce direcciones

---

**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 3-4 horas
**Bloquea**: Correctitud de LW/SW
**Tests afectados**: tests/mem.asm, tests/sw-lw.asm, tests/push-pop.asm
