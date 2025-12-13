# MASK Generator (Generador de Máscara)

**Tipo**: Lógica Combinacional Personalizada
**Estado**: 🔴 #implementado 
**Ubicación**: **NO EXISTE** (debe estar dentro de [[Memory Control]])
**Complejidad**: ⭐⭐ Moderada
**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 2-3 horas

## Descripción

El MASK Generator genera una máscara de 4 bits que indica a la RAM cuál(es) de las 4 palabras (I0, I1, I2, I3) debe escribir. Cada bit de la máscara habilita la escritura de una palabra específica, permitiendo escrituras parciales del bloque.

## Problema que Resuelve

### Escrituras en RAM

La RAM organiza datos en bloques de 16 bytes (4 palabras):

```
RAM Block Write Interface:
┌─────────┬─────────┬─────────┬─────────┐
│   I0    │   I1    │   I2    │   I3    │
│ Word 0  │ Word 1  │ Word 2  │ Word 3  │
│ [31:0]  │ [31:0]  │ [31:0]  │ [31:0]  │
│Bytes 0-3│Bytes 4-7│Bytes 8-B│Bytes C-F│
└─────────┴─────────┴─────────┴─────────┘
    │         │         │         │
    └─────────┴─────────┴─────────┴─ MASK[3:0]
   Bit 0     Bit 1     Bit 2     Bit 3
```

### Problema: CPU Escribe Solo 1 Palabra

Cuando el CPU hace `SW R1, 0(R0)`:
- Solo quiere escribir 4 bytes (1 palabra)
- RAM recibe 16 bytes (4 palabras)
- ¿Cómo decirle a RAM que solo escriba 1 palabra?

**Solución**: MASK de 4 bits

## Funcionamiento del MASK

### Bits de la Máscara

```
MASK[3:0]:
├─ Bit 0: Habilita escritura de I0 (Word 0, bytes 0-3)
├─ Bit 1: Habilita escritura de I1 (Word 1, bytes 4-7)
├─ Bit 2: Habilita escritura de I2 (Word 2, bytes 8-11)
└─ Bit 3: Habilita escritura de I3 (Word 3, bytes 12-15)

Bit = 1: Escribir esta palabra
Bit = 0: NO escribir esta palabra (mantener valor anterior)
```

### Mapeo Word Offset → MASK

| Address[3:2] | Palabra Target | MASK[3:0] | Descripción |
|--------------|----------------|-----------|-------------|
| 00 | Word 0 | 0001 | Escribir solo I0 |
| 01 | Word 1 | 0010 | Escribir solo I1 |
| 10 | Word 2 | 0100 | Escribir solo I2 |
| 11 | Word 3 | 1000 | Escribir solo I3 |

## Arquitectura

```
┌────────────────────────────────────────────────────┐
│              MASK GENERATOR                        │
│                                                    │
│  Address[3:2] = Word Offset                        │
│        │                                           │
│        ▼                                           │
│  ┌──────────┐                                      │
│  │ Decoder  │                                      │
│  │   2:4    │                                      │
│  │(one-hot) │                                      │
│  └──────────┘                                      │
│    │  │  │  │                                      │
│    ▼  ▼  ▼  ▼                                      │
│  [ 0][ 1][ 2][ 3]                                  │
│    │  │  │  │                                      │
│    └──┴──┴──┴─→ MASK[3:0] → RAM                   │
└────────────────────────────────────────────────────┘
```

## Entradas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `WORD_OFFSET` | 2 bits | Bits [3:2] de la dirección |
| `IS_WRITE` | 1 bit | 1=Operación de escritura, 0=Lectura |

## Salidas

| Porto | Ancho | Descripción |
|--------|-------|-------------|
| `MASK` | 4 bits | Máscara para RAM (bit i habilita escritura de Ii) |

## Lógica de Generación

### Tabla de Verdad

| IS_WRITE | WORD_OFFSET[1:0] | MASK[3] | MASK[2] | MASK[1] | MASK[0] |
|----------|------------------|---------|---------|---------|---------|
| 0 | XX | 0 | 0 | 0 | 0 |
| 1 | 00 | 0 | 0 | 0 | 1 |
| 1 | 01 | 0 | 0 | 1 | 0 |
| 1 | 10 | 0 | 1 | 0 | 0 |
| 1 | 11 | 1 | 0 | 0 | 0 |

**Nota**: En lectura (IS_WRITE=0), MASK=0000 (no escribir nada)

### Pseudocódigo

```verilog
module mask_generator (
    input wire [1:0] word_offset,
    input wire is_write,
    output reg [3:0] mask
);

always @(*) begin
    if (!is_write) begin
        // Lectura: no escribir nada
        mask = 4'b0000;
    end
    else begin
        // Escritura: habilitar solo la palabra target
        case (word_offset)
            2'b00: mask = 4'b0001;  // Escribir I0
            2'b01: mask = 4'b0010;  // Escribir I1
            2'b10: mask = 4'b0100;  // Escribir I2
            2'b11: mask = 4'b1000;  // Escribir I3
            default: mask = 4'b0000;
        endcase
    end
end

endmodule
```

### Implementación Simplificada (One-Hot Decoder)

```verilog
// Más eficiente: Decoder 2:4 + enable
assign mask[0] = is_write & (word_offset == 2'b00);
assign mask[1] = is_write & (word_offset == 2'b01);
assign mask[2] = is_write & (word_offset == 2'b10);
assign mask[3] = is_write & (word_offset == 2'b11);
```

## Implementación en Logisim

### Opción 1: Decoder + AND Gates

```
Componentes:
├─ Decoder 2:4
│  ├─ Input: WORD_OFFSET[1:0]
│  └─ Outputs: decode[0], decode[1], decode[2], decode[3]
│              (one-hot encoding)
│
├─ AND Gates (4 × 2-input)
│  ├─ MASK[0] = decode[0] AND IS_WRITE
│  ├─ MASK[1] = decode[1] AND IS_WRITE
│  ├─ MASK[2] = decode[2] AND IS_WRITE
│  └─ MASK[3] = decode[3] AND IS_WRITE
│
└─ Output: MASK[3:0]
```

### Opción 2: ROM Lookup Table

```
ROM (4 × 4 bits):
├─ Address: {IS_WRITE, WORD_OFFSET[1:0]} (3 bits)
└─ Data: MASK[3:0]

Contents:
├─ Address 000 (Read, offset 00): 0000
├─ Address 001 (Read, offset 01): 0000
├─ Address 010 (Read, offset 10): 0000
├─ Address 011 (Read, offset 11): 0000
├─ Address 100 (Write, offset 00): 0001
├─ Address 101 (Write, offset 01): 0010
├─ Address 110 (Write, offset 10): 0100
└─ Address 111 (Write, offset 11): 1000
```

**Recomendación**: Opción 1 (Decoder + AND) - más clara y eficiente

## Ejemplos de Uso

### Ejemplo 1: SW R1, 0(R0) - Escribir Word 0

```
Dirección: 0x00000000
├─ Block address: 0x0000
└─ Word offset: 0b00

IS_WRITE = 1
WORD_OFFSET = 0b00

MASK Generator:
└─ MASK = 0b0001

Efecto en RAM:
├─ I0 = DATA_WRITE → RAM actualiza Word 0 ✓
├─ I1 = (ignorado)  → RAM mantiene Word 1
├─ I2 = (ignorado)  → RAM mantiene Word 2
└─ I3 = (ignorado)  → RAM mantiene Word 3
```

### Ejemplo 2: SW R2, 4(R0) - Escribir Word 1

```
Dirección: 0x00000004
└─ Word offset: 0b01

MASK = 0b0010

Efecto en RAM:
├─ I0 = (ignorado)  → RAM mantiene Word 0
├─ I1 = DATA_WRITE → RAM actualiza Word 1 ✓
├─ I2 = (ignorado)  → RAM mantiene Word 2
└─ I3 = (ignorado)  → RAM mantiene Word 3
```

### Ejemplo 3: SW R3, 8(R0) - Escribir Word 2

```
Dirección: 0x00000008
└─ Word offset: 0b10

MASK = 0b0100

Efecto: Solo Word 2 se actualiza
```

### Ejemplo 4: SW R4, 12(R0) - Escribir Word 3

```
Dirección: 0x0000000C
└─ Word offset: 0b11

MASK = 0b1000

Efecto: Solo Word 3 se actualiza
```

### Ejemplo 5: LW (Lectura) - No Escribir

```
Dirección: 0x00000000 (cualquiera)
IS_WRITE = 0

MASK = 0b0000

Efecto: RAM no escribe nada (modo lectura)
```

## Integración en Memory Control

### Flujo Completo de Escritura

```
1. Control Unit solicita escritura (SW)

2. Address Translator extrae:
   ├─ Block Address → RAM ADDR
   └─ Word Offset → MASK Generator

3. MASK Generator genera:
   ├─ Input: WORD_OFFSET, IS_WRITE=1
   └─ Output: MASK (ej: 0b0001 para offset 00)

4. Data Distributor coloca DATA_WRITE en:
   ├─ I0, I1, I2, I3 (todas reciben mismo dato)
   └─ RAM solo escribe la indicada por MASK

5. Memory State Machine espera WT cycles

6. Escritura completa
```

### Routing de Datos de Escritura

```
Memory Control (Write Path)
│
├─ DATA_WRITE (from CPU) → Little-Endian Converter
│                         ↓
│                      DATA_BE (big-endian)
│                         │
│                         ├─→ I0 (broadcast)
│                         ├─→ I1 (broadcast)
│                         ├─→ I2 (broadcast)
│                         └─→ I3 (broadcast)
│
├─ WORD_OFFSET → MASK Generator
│                ↓
│              MASK[3:0] → RAM
│                         │
│                         └─→ RAM decide qué Ii escribir
└─ Control: R/W=1, CS=1
```

**Clave**: Todas las I0-I3 reciben el mismo dato, pero RAM solo escribe las habilitadas por MASK.

## Casos Especiales

### Escrituras Múltiples (Avanzado)

En configuraciones avanzadas, podrías querer escribir múltiples palabras:

```
MASK = 0b0011: Escribir Word 0 y Word 1
MASK = 0b1111: Escribir todas las 4 palabras (bloque completo)
```

**Para S-MIPS básico**: Solo escrituras de 1 palabra (SW, PUSH)
**MASK siempre**: Exactamente 1 bit en 1

### Direcciones No-Alineadas (Error)

Si por error el CPU intenta escribir en dirección no-alineada:

```
Dirección: 0x00000001 (NO múltiplo de 4)
Bits [1:0] = 01 (ERROR)

Comportamiento:
├─ Address Translator debería detectar error
└─ O simplemente usar bits [3:2], ignorando [1:0]
```

**En S-MIPS**: Todas las direcciones deben ser múltiplo de 4.

## Tests de Validación

### Test 1: Escribir 4 Palabras Diferentes

```assembly
# Escribir valores únicos en cada palabra del bloque 0
addi r1, r0, 0xAAAA
sw r1, 0(r0)    # Word 0 = 0xAAAA

addi r2, r0, 0xBBBB
sw r2, 4(r0)    # Word 1 = 0xBBBB

addi r3, r0, 0xCCCC
sw r3, 8(r0)    # Word 2 = 0xCCCC

addi r4, r0, 0xDDDD
sw r4, 12(r0)   # Word 3 = 0xDDDD

# Leer de vuelta y verificar
lw r5, 0(r0)
bne r5, r1, fail

lw r6, 4(r0)
bne r6, r2, fail

lw r7, 8(r0)
bne r7, r3, fail

lw r8, 12(r0)
bne r8, r4, fail

addi r10, r0, 99  # PASS
halt

fail:
addi r10, r0, 1   # FAIL
halt
```

**Qué verifica**: MASK correcto permite escrituras independientes de cada palabra.

### Test 2: Sobrescritura

```assembly
# Escribir valor inicial
addi r1, r0, 0x1111
sw r1, 0(r0)

# Sobrescribir con nuevo valor
addi r2, r0, 0x2222
sw r2, 0(r0)

# Verificar que se sobrescribió
lw r3, 0(r0)
bne r3, r2, fail  # Debe ser 0x2222, no 0x1111

addi r10, r0, 99  # PASS
halt

fail:
addi r10, r0, 1   # FAIL
halt
```

### Test 3: No Afectar Otras Palabras

```assembly
# Escribir Word 0
addi r1, r0, 0xAAAA
sw r1, 0(r0)

# Escribir Word 1
addi r2, r0, 0xBBBB
sw r2, 4(r0)

# Verificar que Word 0 no cambió
lw r3, 0(r0)
bne r3, r1, fail  # Debe seguir siendo 0xAAAA

addi r10, r0, 99  # PASS
halt

fail:
addi r10, r0, 1   # FAIL - Word 0 fue afectada por escritura a Word 1
halt
```

**Qué verifica**: MASK correcta aísla escrituras.

## Troubleshooting

### Problema: Escribir una palabra afecta otras

**Síntoma**: `sw r1, 0(r0)` también modifica words 1, 2, 3

**Causa**: MASK incorrecto
- MASK = 1111 en vez de 0001
- Todas las palabras habilitadas

**Solución**: Verificar MASK Generator lógica

### Problema: Escrituras no tienen efecto

**Síntoma**: SW ejecuta pero datos no se escriben en RAM

**Causa**: MASK siempre = 0000
- IS_WRITE no llega al MASK Generator
- Generator siempre cree que es lectura

**Solución**: Verificar conexión IS_WRITE

### Problema: Escrituras en posiciones incorrectas

**Síntoma**: `sw r1, 0(r0)` escribe en Word 2 en vez de Word 0

**Causa**: WORD_OFFSET mal conectado
- Bits incorrectos de address
- Mapeo invertido

**Solución**: Verificar Address Translator y conexión a MASK Generator

## Relación con Word Selector

### Lectura vs Escritura

```
LECTURA (LW):
├─ RAM devuelve O0, O1, O2, O3
├─ Word Selector elige 1 de las 4
└─ MASK no usado (siempre 0000)

ESCRITURA (SW):
├─ CPU provee 1 dato (DATA_WRITE)
├─ Dato se replica a I0, I1, I2, I3
├─ MASK Generator elige cuál(es) escribir
└─ Word Selector no usado
```

**Son complementarios**: Word Selector (lectura), MASK Generator (escritura)

## Costo en Logisim

### Usando Decoder + AND

```
Componentes:
├─ 1 Decoder (2:4)
├─ 4 AND gates (2-input)
└─ Total: ~3-4 unidades

Costo estimado: 3-4 unidades
```

### Usando ROM

```
Componentes:
└─ 1 ROM (8×4 bits)

Costo estimado: ~2 unidades
```

**Recomendación**: Decoder + AND (más claro conceptualmente)

## Extensiones Futuras (Opcional)

### Escrituras de Byte (No Requerido para S-MIPS)

Para escribir bytes individuales (ej: SB en MIPS completo):

```
MASK extendido a 16 bits:
├─ Bit 0-3: Habilita bytes 0-3
├─ Bit 4-7: Habilita bytes 4-7
├─ Bit 8-11: Habilita bytes 8-11
└─ Bit 12-15: Habilita bytes 12-15
```

**Para S-MIPS**: No necesario (solo SW de 32 bits)

## Enlaces Relacionados

- [[Memory Control]] - Componente padre
- [[Word Selector]] - Equivalente para lecturas
- [[Address Translator]] - Proporciona WORD_OFFSET
- [[Little-Endian Converter]] - Convierte DATA_WRITE antes de routing
- [[Memory State Machine]] - Coordina timing de escritura

---

**Prioridad**: 🚨🚨 URGENTE
**Tiempo estimado**: 2-3 horas
**Complejidad**: Baja-Media (decoder + lógica simple)
**Bloquea**: Escrituras de memoria (SW, PUSH)
**Tests afectados**: tests/mem.asm, tests/sw-lw.asm, tests/push-pop.asm, tests/sw-push-pop.asm
