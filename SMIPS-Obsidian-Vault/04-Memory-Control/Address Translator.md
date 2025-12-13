# Address Translator (Traductor de Direcciones)

**Tipo**: Subcomponente de Memory Control
**Estado**: 🔴 #implementado 
**Ubicación**: `s-mips.circ` → CPU → Memory Control → Address Translator
**Complejidad**: ⭐⭐ Moderada
**Prioridad**: 🔴 ALTA (parte de Memory Control)

## Descripción

El Address Translator es el subcomponente del Memory Control responsable de convertir direcciones de bytes de 32 bits (usadas por el CPU) en direcciones de bloques de 16 bits (usadas por la RAM), además de extraer el word offset y validar la alineación.

## Función

La RAM de S-MIPS está organizada en **bloques de 16 bytes** (4 palabras de 32 bits cada una). El CPU trabaja con direcciones de bytes, pero la RAM necesita:
- **Block address**: 16 bits para seleccionar uno de 65,536 bloques
- **Word offset**: 2 bits para seleccionar una de 4 palabras dentro del bloque
- **Alineación**: Verificar que bits [1:0] = 00 (múltiplo de 4)

## Interfaz de Entradas/Salidas

### Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `ADDRESS` | 32 bits | Data Path | Dirección de byte completa |

### Salidas

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `BLOCK_ADDR` | 16 bits | RAM | Dirección de bloque [19:4] |
| `WORD_OFFSET` | 2 bits | [[Word Selector]] | Palabra dentro del bloque [3:2] |
| `IS_ALIGNED` | 1 bit | Memory State Machine | 1 si alineado (bits [1:0] = 00) |
| `ALIGNMENT_ERROR` | 1 bit | [[Control Unit]] | 1 si no alineado (error) |

## Desglose de Dirección de 32 Bits

```
Dirección de byte (32 bits):
┌──────────────────┬──────────┬────────────┬────────┐
│  Block Address   │  Word    │   Byte     │ Align  │
│    16 bits       │ Offset   │  Offset    │        │
│   bits [19:4]    │  [3:2]   │   [1:0]    │  =00   │
└──────────────────┴──────────┴────────────┴────────┘

Bits [31:20]: No usados (0x00000 - solo 1 MB de RAM)
Bits [19:4]:  Block address (16 bits) → 2^16 = 65,536 bloques
Bits [3:2]:   Word offset (2 bits) → 4 palabras por bloque
Bits [1:0]:   Deben ser 00 (alineación a 4 bytes)
```

## Cálculos de Traducción

### Extracción de Block Address

```verilog
assign BLOCK_ADDR = ADDRESS[19:4];
```

**Ejemplo**:
```
ADDRESS = 0x00001048 = 0000 0000 0000 0000 0001 0000 0100 1000

BLOCK_ADDR = bits [19:4] = 0000 0000 0001 0000 0100 = 0x0104 (260 decimal)

RAM recibe: ADDR input = 0x0104
RAM devuelve: Bloque 260 (16 bytes = 4 words)
```

### Extracción de Word Offset

```verilog
assign WORD_OFFSET = ADDRESS[3:2];
```

**Ejemplo**:
```
ADDRESS = 0x00001048

WORD_OFFSET = bits [3:2] = 10 = 2

Significa: Seleccionar palabra 2 (de 0-3) dentro del bloque
```

### Verificación de Alineación

```verilog
assign IS_ALIGNED = (ADDRESS[1:0] == 2'b00);
assign ALIGNMENT_ERROR = (ADDRESS[1:0] != 2'b00);
```

**Ejemplo válido**:
```
ADDRESS = 0x00001048
bits [1:0] = 00
IS_ALIGNED = 1 (OK)
```

**Ejemplo inválido**:
```
ADDRESS = 0x00001049
bits [1:0] = 01
ALIGNMENT_ERROR = 1 (ERROR - no es múltiplo de 4)
```

## Rango de Memoria Válido

### Memoria Total

```
RAM: 1 MB = 2^20 bytes = 1,048,576 bytes

Bloques: 2^20 / 16 = 2^16 = 65,536 bloques
Direcciones válidas: 0x00000000 a 0x000FFFFF (1 MB)
```

### Direcciones Fuera de Rango

```verilog
// Verificar si dirección está fuera de 1 MB
wire OUT_OF_RANGE = (ADDRESS[31:20] != 12'h000);
```

**Ejemplo fuera de rango**:
```
ADDRESS = 0x00100000 (1 MB + 0)
bits [31:20] = 0x001 (no es 0x000)
OUT_OF_RANGE = 1 (ERROR)
```

## Pseudocódigo Verilog

```verilog
module address_translator(
    input wire [31:0] ADDRESS,

    output wire [15:0] BLOCK_ADDR,
    output wire [1:0]  WORD_OFFSET,
    output wire IS_ALIGNED,
    output wire ALIGNMENT_ERROR,
    output wire OUT_OF_RANGE
);

// Extracción de campos (combinacional - 0 ciclos)
assign BLOCK_ADDR = ADDRESS[19:4];
assign WORD_OFFSET = ADDRESS[3:2];

// Verificación de alineación
assign IS_ALIGNED = (ADDRESS[1:0] == 2'b00);
assign ALIGNMENT_ERROR = (ADDRESS[1:0] != 2'b00);

// Verificación de rango válido (0x000000 - 0x0FFFFF)
assign OUT_OF_RANGE = (ADDRESS[31:20] != 12'h000);

endmodule
```

## Integración con Memory Control

### Flujo de Uso

```
1. CPU calcula dirección:
   - ADD: ADDRESS = Rs + offset
   - LW/SW: ADDRESS = base + offset

2. Data Path envía ADDRESS a Memory Control

3. Address Translator:
   - Extrae BLOCK_ADDR → enviar a RAM
   - Extrae WORD_OFFSET → usar en Word Selector
   - Verifica IS_ALIGNED → continuar o error

4. Si IS_ALIGNED:
   - Memory State Machine usa BLOCK_ADDR
   - Word Selector usa WORD_OFFSET

5. Si ALIGNMENT_ERROR:
   - Memory Control detiene operación
   - Control Unit maneja error (opcional: trap o ignorar)
```

## Ejemplos de Traducción

### Ejemplo 1: Dirección Alineada Válida

```
Instrucción: LW R2, 8(R1)
R1 = 0x00001000

ADDRESS = R1 + 8 = 0x00001008

Traducción:
    BLOCK_ADDR = 0x00001008[19:4] = 0x0100 (256)
    WORD_OFFSET = 0x00001008[3:2] = 10 (2)
    IS_ALIGNED = 1 (bits [1:0] = 00)
    OUT_OF_RANGE = 0

RAM lee bloque 256:
    Devuelve 4 words: W0, W1, W2, W3
    Word Selector escoge W2 (offset = 2)
```

### Ejemplo 2: Acceso Secuencial

```
Base = 0x00001000

ADDRESS      BLOCK_ADDR  WORD_OFFSET  Mismo Bloque?
0x00001000   0x0100      00           Bloque 256
0x00001004   0x0100      01           Bloque 256 ✓
0x00001008   0x0100      10           Bloque 256 ✓
0x0000100C   0x0100      11           Bloque 256 ✓
0x00001010   0x0101      00           Bloque 257 (nuevo)

Observación: Primeras 4 direcciones están en el mismo bloque
Optimización: Caché puede aprovechar esto
```

### Ejemplo 3: Error de Alineación

```
Instrucción: LW R2, 1(R1)  // offset = 1 (ERROR!)
R1 = 0x00001000

ADDRESS = 0x00001001

Traducción:
    BLOCK_ADDR = 0x0100
    WORD_OFFSET = 00
    IS_ALIGNED = 0
    ALIGNMENT_ERROR = 1 (bits [1:0] = 01, no es 00)

Memory Control debe:
    - No ejecutar operación
    - Señalar error a Control Unit
    - (Opcional) Generar trap/exception
```

### Ejemplo 4: Fuera de Rango

```
ADDRESS = 0x00100000  // 1 MB (fuera de rango)

Traducción:
    BLOCK_ADDR = 0x0000 (bits [19:4])
    OUT_OF_RANGE = 1 (bits [31:20] = 0x001, no 0x000)

Memory Control debe:
    - No acceder a RAM
    - Retornar error
```

## Mapa de Memoria

```
┌────────────────────────────────────────────┐
│  Direcciones (byte addresses)             │
├────────────────────────────────────────────┤
│  0x00000000 - 0x0000000F  │ Bloque 0      │ 16 bytes
│  0x00000010 - 0x0000001F  │ Bloque 1      │
│  0x00000020 - 0x0000002F  │ Bloque 2      │
│  ...                      │ ...           │
│  0x000FFFF0 - 0x000FFFFF  │ Bloque 65535  │
├────────────────────────────────────────────┤
│  Total: 1 MB (2^20 bytes)                 │
│  Bloques: 65,536 (2^16)                   │
└────────────────────────────────────────────┘
```

### Estructura de un Bloque

```
Bloque N en RAM:
┌────────┬────────┬────────┬────────┐
│  W0    │  W1    │  W2    │  W3    │
│ 32 bits│ 32 bits│ 32 bits│ 32 bits│
└────────┴────────┴────────┴────────┘
  byte 0    byte 4   byte 8   byte 12

Dirección base del bloque: N × 16
Word 0: base + 0
Word 1: base + 4
Word 2: base + 8
Word 3: base + 12
```

## Timing

### Latencia

**0 ciclos** (combinacional puro)

El Address Translator es solo lógica combinacional:
- Extracción de bits: conexiones directas (0 delay)
- Comparadores: 1 gate delay
- Total: 1 gate delay

### Ruta Crítica

```
ADDRESS[31:0] → Comparador (bits [1:0] == 00) → IS_ALIGNED

Tiempo: ~1 gate delay (XOR + AND)
```

## Casos de Prueba

### Test 1: Direcciones Alineadas

```verilog
// Test básico
ADDRESS = 32'h00001000
assert(BLOCK_ADDR == 16'h0100);
assert(WORD_OFFSET == 2'b00);
assert(IS_ALIGNED == 1'b1);
assert(OUT_OF_RANGE == 1'b0);

// Test con offset
ADDRESS = 32'h0000100C
assert(BLOCK_ADDR == 16'h0100);
assert(WORD_OFFSET == 2'b11);
assert(IS_ALIGNED == 1'b1);
```

### Test 2: Errores de Alineación

```verilog
ADDRESS = 32'h00001001  // +1 byte
assert(ALIGNMENT_ERROR == 1'b1);

ADDRESS = 32'h00001002  // +2 bytes
assert(ALIGNMENT_ERROR == 1'b1);

ADDRESS = 32'h00001003  // +3 bytes
assert(ALIGNMENT_ERROR == 1'b1);

ADDRESS = 32'h00001004  // +4 bytes (OK)
assert(IS_ALIGNED == 1'b1);
```

### Test 3: Límites de Memoria

```verilog
// Inicio de memoria
ADDRESS = 32'h00000000
assert(BLOCK_ADDR == 16'h0000);
assert(OUT_OF_RANGE == 1'b0);

// Final de memoria (1 MB - 4 bytes)
ADDRESS = 32'h000FFFFC
assert(BLOCK_ADDR == 16'hFFFF);
assert(WORD_OFFSET == 2'b11);
assert(OUT_OF_RANGE == 1'b0);

// Fuera de rango
ADDRESS = 32'h00100000  // 1 MB
assert(OUT_OF_RANGE == 1'b1);

ADDRESS = 32'h12345678  // muy fuera
assert(OUT_OF_RANGE == 1'b1);
```

## Implementación en Logisim

### Componentes Necesarios

1. **Splitter**: Dividir ADDRESS[31:0] en:
   - Bits [31:20] → comparador para OUT_OF_RANGE
   - Bits [19:4] → BLOCK_ADDR (salida directa)
   - Bits [3:2] → WORD_OFFSET (salida directa)
   - Bits [1:0] → comparador para alineación

2. **Comparadores**:
   - Comparador de 2 bits: ADDRESS[1:0] == 00
   - Comparador de 12 bits: ADDRESS[31:20] == 0x000

3. **Puertas lógicas**:
   - NOT para ALIGNMENT_ERROR

### Diagrama en Logisim

```
ADDRESS[31:0]
    │
    ├─[31:20]─→ [Comparador == 0x000] ──→ NOT ──→ OUT_OF_RANGE
    │
    ├─[19:4]──────────────────────────────────→ BLOCK_ADDR[15:0]
    │
    ├─[3:2]───────────────────────────────────→ WORD_OFFSET[1:0]
    │
    └─[1:0]──→ [Comparador == 00] ────────────→ IS_ALIGNED
                        │
                       NOT
                        │
                        └────────────────────→ ALIGNMENT_ERROR
```

## Integración con Otros Subcomponentes

### Con Memory State Machine

```verilog
if (IS_ALIGNED && !OUT_OF_RANGE) begin
    // Usar BLOCK_ADDR para acceder a RAM
    RAM_ADDR <= BLOCK_ADDR;
    RAM_CS <= 1;
end else begin
    // Error - no acceder a RAM
    ERROR <= 1;
end
```

### Con Word Selector

```verilog
// Word Selector usa WORD_OFFSET para seleccionar palabra
case (WORD_OFFSET)
    2'b00: WORD_OUT = BLOCK_DATA[31:0];
    2'b01: WORD_OUT = BLOCK_DATA[63:32];
    2'b10: WORD_OUT = BLOCK_DATA[95:64];
    2'b11: WORD_OUT = BLOCK_DATA[127:96];
endcase
```

### Con MASK Generator

```verilog
// MASK Generator puede usar WORD_OFFSET para generar máscara
assign MASK = (1 << WORD_OFFSET);  // 0001, 0010, 0100, 1000
```

## Optimizaciones Opcionales

### 1. Cache Tag Extraction

Si hay caché, Address Translator también puede extraer tag e index:

```verilog
// Para caché de 4 líneas
wire [25:0] CACHE_TAG = ADDRESS[31:6];
wire [1:0]  CACHE_INDEX = ADDRESS[5:4];
wire [1:0]  CACHE_WORD_OFFSET = ADDRESS[3:2];
```

### 2. Bank Selection

Para acceso a bancos específicos:

```verilog
// Determinar qué banco contiene la palabra
wire [1:0] BANK = WORD_OFFSET;  // Bank 0-3 corresponde a word 0-3
```

## Referencias

- [[Memory Control]] - Componente padre
- [[Word Selector]] - Usa WORD_OFFSET
- [[MASK Generator]] - Puede usar WORD_OFFSET
- [[Memory State Machine]] - Usa BLOCK_ADDR e IS_ALIGNED
- [[Data Path]] - Fuente de ADDRESS
- Documentación: `s-mips.pdf` - Organización de memoria

---
**Última actualización**: 2025-12-09
**Estado**: 🔴 NO IMPLEMENTADO (parte de Memory Control)
**Complejidad**: ⭐⭐ Moderada (lógica combinacional simple)
**Tiempo estimado**: 1-2 horas (parte de los 5-6 días de Memory Control)
