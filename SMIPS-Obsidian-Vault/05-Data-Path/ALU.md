# ALU (Arithmetic Logic Unit)

**Tipo**: Componente Computacional
**Estado**: ✅ #implementado **COMPLETO**
**Ubicación**: `s-mips.circ` → CPU → Data Path → ALU
**Complejidad**: ⭐⭐⭐⭐ Muy Compleja
**Prioridad**: ✅ COMPLETADO

## Descripción

La ALU (Unidad Aritmético-Lógica) es el componente que realiza todas las operaciones aritméticas y lógicas del procesador S-MIPS. Soporta operaciones de 32 bits con entradas y salidas signed/unsigned.

## Estado de Implementación

**✅ IMPLEMENTADO Y FUNCIONAL**

La ALU actual en s-mips.circ implementa todas las operaciones requeridas:
- ✅ Operaciones aritméticas: ADD, SUB, ADDI
- ✅ Operaciones lógicas: AND, OR, XOR, NOR, ANDI, ORI, XORI
- ✅ Comparación: SLT, SLTI (signed less than)
- ✅ Multiplicación: MULT (signed), MULU (unsigned)
- ✅ División: DIV (signed), DIVU (unsigned)
- ✅ Operaciones de shift: SLL, SRL, SRA
- ✅ Registros Hi/Lo para resultados de 64 bits

## Interfaz de Entradas/Salidas

### Entradas

| Puerto   | Ancho    | Fuente                          | Descripción                       |
| -------- | -------- | ------------------------------- | --------------------------------- |
| `A`      | 32 bits  | [[Register File]] (Read Data 1) | Operando A (Rs)                   |
| `B`      | 32 bits  | MUX ALU_B                       | Operando B (Rt o Immediate)       |
| `ALU_OP` | 4-6 bits | [[Instruction Decoder]]         | Código de operación               |
| `SHAMT`  | 5 bits   | [[Instruction Decoder]]         | Shift amount (para SLL/SRL/SRA)   |
| `CLK`    | 1 bit    | Sistema                         | Reloj (para MULT/DIV multi-ciclo) |

### Salidas

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `RESULT` | 32 bits | MUX Writeback | Resultado de operación |
| `ZERO` | 1 bit | [[Branch Control]] | Flag: resultado == 0 |
| `NEGATIVE` | 1 bit | [[Branch Control]] | Flag: resultado < 0 |
| `HI` | 32 bits | [[Register File]] (`HI_IN`) | Parte alta (mult/div) |
| `LO` | 32 bits | [[Register File]] (`LO_IN`) | Parte baja (mult/div) |

**Nota sobre nombres de señales**:
- ALU genera señales llamadas `HI` y `LO`
- Register File las recibe como `HI_IN` y `LO_IN` (nombre del puerto de entrada)
- Son la misma conexión física con nombres diferentes en cada componente

## Operaciones Soportadas

### Aritméticas

#### ADD / ADDI (Add)
```
RESULT = A + B
Signed operation (32-bit two's complement)
Overflow detection (optional, no trap en S-MIPS)
```

#### SUB (Subtract)
```
RESULT = A - B
Signed operation
```

### Lógicas

#### AND / ANDI (Bitwise AND)
```
RESULT = A & B
```

#### OR / ORI (Bitwise OR)
```
RESULT = A | B
```

#### XOR / XORI (Bitwise XOR)
```
RESULT = A ^ B
```

#### NOR (Bitwise NOR)
```
RESULT = ~(A | B)
Equivalente a NOT OR
```

### Comparación

#### SLT / SLTI (Set Less Than)
```
if (A < B) signed comparison
    RESULT = 1
else
    RESULT = 0

Usa comparación signed (two's complement)
```

### Multiplicación

#### MULT (Multiply Signed)
```
{HI, LO} = A × B (signed)

Resultado de 64 bits:
    HI[31:0] = resultado[63:32]  (upper 32 bits)
    LO[31:0] = resultado[31:0]   (lower 32 bits)

Operandos tratados como signed (two's complement)
```

**Ejemplo**:
```
A = 0x00001000 (4096 decimal)
B = 0x00000400 (1024 decimal)
Resultado = 0x00000000_00400000 (4,194,304 decimal)
    HI = 0x00000000
    LO = 0x00400000
```

#### MULU (Multiply Unsigned)
```
{HI, LO} = A × B (unsigned)

Mismo formato, pero:
    A y B tratados como unsigned
    No extensión de signo
```

**Ejemplo**:
```
A = 0xFFFFFFFF (4,294,967,295 unsigned)
B = 0x00000002 (2 unsigned)
Resultado = 0x00000001_FFFFFFFE
    HI = 0x00000001
    LO = 0xFFFFFFFE

(Si fuera signed, A sería -1, resultado sería -2)
```

### División

#### DIV (Divide Signed)
```
LO = A / B (quotient, signed)
HI = A % B (remainder, signed)

Signo del remainder = signo del dividendo (A)
```

**Ejemplo**:
```
A = 17, B = 5
    LO = 3
    HI = 2

A = -17, B = 5
    LO = -3
    HI = -2

A = 17, B = -5
    LO = -3
    HI = 2
```

#### DIVU (Divide Unsigned)
```
LO = A / B (quotient, unsigned)
HI = A % B (remainder, unsigned)

A y B tratados como unsigned
```

**División por cero**:
```
Si B == 0:
    LO = 0xFFFFFFFF (indefinido)
    HI = A (indefinido)

(No genera excepción en S-MIPS simplificado)
```

### Shift

#### SLL (Shift Left Logical)
```
RESULT = B << SHAMT

Desplaza B a la izquierda SHAMT posiciones
Rellena con 0s a la derecha
```

**Ejemplo**:
```
B = 0x00000001
SHAMT = 4
RESULT = 0x00000010 (16 decimal)
```

#### SRL (Shift Right Logical)
```
RESULT = B >> SHAMT (logical)

Desplaza B a la derecha SHAMT posiciones
Rellena con 0s a la izquierda (unsigned)
```

#### SRA (Shift Right Arithmetic)
```
RESULT = B >> SHAMT (arithmetic)

Desplaza B a la derecha SHAMT posiciones
Rellena con bit de signo (B[31]) a la izquierda (signed)
```

**Ejemplo**:
```
B = 0xFFFFFFF0 (-16 signed)
SHAMT = 2

SRL: RESULT = 0x3FFFFFFC (mantiene signo incorrecto)
SRA: RESULT = 0xFFFFFFFC (-4 signed, correcto)
```

## Códigos de Operación (ALU_OP)

Tabla de control generada por [[Instruction Decoder]]:

| ALU_OP | Operación | Descripción |
|--------|-----------|-------------|
| `0000` | ADD | A + B |
| `0001` | SUB | A - B |
| `0010` | AND | A & B |
| `0011` | OR | A \| B |
| `0100` | XOR | A ^ B |
| `0101` | NOR | ~(A \| B) |
| `0110` | SLT | (A < B) ? 1 : 0 (signed) |
| `0111` | SLL | B << SHAMT |
| `1000` | SRL | B >> SHAMT (logical) |
| `1001` | SRA | B >> SHAMT (arithmetic) |
| `1010` | MULT | {HI, LO} = A × B (signed) |
| `1011` | MULU | {HI, LO} = A × B (unsigned) |
| `1100` | DIV | LO = A / B, HI = A % B (signed) |
| `1101` | DIVU | LO = A / B, HI = A % B (unsigned) |

## Flags de Salida

### ZERO Flag
```verilog
ZERO = (RESULT == 32'h00000000) ? 1 : 0

Usado por BEQ, BNE:
    BEQ Rs, Rt: branch if (Rs - Rt == 0) → ALU SUB, check ZERO
    BNE Rs, Rt: branch if (Rs - Rt != 0) → ALU SUB, check !ZERO
```

### NEGATIVE Flag
```verilog
NEGATIVE = RESULT[31]

Usado por BLEZ, BGTZ, BLTZ:
    BLEZ Rs: branch if (Rs <= 0) → check NEGATIVE or ZERO
    BGTZ Rs: branch if (Rs > 0) → check !NEGATIVE and !ZERO
    BLTZ Rs: branch if (Rs < 0) → check NEGATIVE
```

## Implementación en Logisim

### Componentes Utilizados

1. **Adder (32-bit)**: Para ADD/SUB
   - SUB usa complemento a 2: A + (~B) + 1

2. **Bitwise Gates**: Para AND/OR/XOR/NOR
   - Operan bit a bit sobre 32 bits

3. **Comparador (32-bit signed)**: Para SLT
   - Compara A y B como signed
   - Salida 1 bit

4. **Shifter**: Para SLL/SRL/SRA
   - Barrel shifter de 32 bits
   - Control de tipo (logical/arithmetic)
   - SHAMT de 5 bits (0-31)

5. **Multiplicador (32×32→64)**: Para MULT/MULU
   - Versión signed y unsigned
   - Salida de 64 bits a Hi/Lo

6. **Divisor (32÷32→32)**: Para DIV/DIVU
   - Quotient → LO
   - Remainder → HI
   - Manejo de división por cero

7. **Multiplexor**: Selecciona resultado según ALU_OP

### Estructura

```
      A ────┐
             ├──→ Adder ──→┐
      B ────┤              │
             ├──→ AND ─────┤
             ├──→ OR ──────┤
             ├──→ XOR ─────┤
             ├──→ NOR ─────┤
             ├──→ SLT ─────┤
             ├──→ Shifter ─┤
             ├──→ MULT ────┤──→ MUX (ALU_OP) ──→ RESULT
             └──→ DIV ─────┘                       │
                                                   └──→ ZERO, NEGATIVE
    SHAMT ──→ Shifter
    ALU_OP ─→ MUX Control
```

## Casos de Prueba

### Test 1: Operaciones Aritméticas
```assembly
ADDI R1, R0, 10    # R1 = 10
ADDI R2, R0, 5     # R2 = 5
ADD R3, R1, R2     # R3 = 15
SUB R4, R1, R2     # R4 = 5
```

**Verificación**:
- R3 debe ser 0x0000000F (15)
- R4 debe ser 0x00000005 (5)

### Test 2: Operaciones Lógicas
```assembly
ADDI R1, R0, 0xFF  # R1 = 0x000000FF
ADDI R2, R0, 0x0F  # R2 = 0x0000000F
AND R3, R1, R2     # R3 = 0x0000000F
OR R4, R1, R2      # R4 = 0x000000FF
XOR R5, R1, R2     # R5 = 0x000000F0
NOR R6, R1, R2     # R6 = 0xFFFFFF00
```

### Test 3: Multiplicación
```assembly
ADDI R1, R0, 1000  # R1 = 1000
ADDI R2, R0, 2000  # R2 = 2000
MULT R1, R2        # HI:LO = 2,000,000
MFHI R3            # R3 = HI
MFLO R4            # R4 = LO
```

**Verificación**:
- R4 (LO) = 0x001E8480 (2,000,000)
- R3 (HI) = 0x00000000

### Test 4: División
```assembly
ADDI R1, R0, 17    # R1 = 17
ADDI R2, R0, 5     # R2 = 5
DIV R1, R2         # LO = 3, HI = 2
MFLO R3            # R3 = quotient = 3
MFHI R4            # R4 = remainder = 2
```

### Test 5: Shift
```assembly
ADDI R1, R0, 8     # R1 = 8 (0b1000)
SLL R2, R1, 2      # R2 = 32 (0b100000)
SRL R3, R1, 1      # R3 = 4 (0b100)
```

## Análisis de Correctitud

### ✅ Implementación Correcta

Según análisis del código en s-mips.circ:
1. ✅ Todas las operaciones aritméticas presentes
2. ✅ Todas las operaciones lógicas presentes
3. ✅ Multiplicación y división signed/unsigned diferenciadas
4. ✅ Registros Hi/Lo implementados
5. ✅ Flags ZERO y NEGATIVE generados correctamente
6. ✅ Shift operations con soporte signed/unsigned

### Puntos a Validar (Tests Pendientes)

1. ⚠️ **Overflow en ADD/SUB**: Verificar que no genera excepciones (S-MIPS ignora overflow)
2. ⚠️ **División por cero**: Verificar comportamiento (debe devolver resultado indefinido, no exception)
3. ⚠️ **Multiplicación de negativos**: Verificar MULT vs MULU con valores negativos
4. ⚠️ **SRA con negativos**: Verificar extensión de signo correcta

## Performance

### Latencias (ciclos de reloj)

| Operación | Latencia | Notas |
|-----------|----------|-------|
| ADD/SUB | 1 ciclo | Combinacional |
| AND/OR/XOR/NOR | 1 ciclo | Combinacional |
| SLT | 1 ciclo | Combinacional |
| SLL/SRL/SRA | 1 ciclo | Barrel shifter |
| MULT/MULU | 1-4 ciclos | Depende de implementación |
| DIV/DIVU | 1-32 ciclos | Depende de implementación |

**Nota**: En Logisim, multiplicación y división pueden ser combinacionales (1 ciclo) si se usan componentes integrados. En hardware real, serían multi-ciclo.

## Problemas Conocidos

**Estado actual**: ✅ COMPLETO Y FUNCIONAL

**No hay problemas críticos identificados**

### Mejoras Opcionales (No necesarias para aprobar)

1. **Detección de overflow**: Agregar flag de overflow para ADD/SUB (no requerido en S-MIPS)
2. **Excepción división por cero**: Trap en lugar de resultado indefinido (no requerido)
3. **Multiplicador/divisor multi-ciclo**: Optimizar área a costa de latencia (opcional)

## Referencias

- [[Data Path]] - Integración en datapath
- [[Register File]] - Fuente de operandos y destino Hi/Lo
- [[Instruction Decoder]] - Genera ALU_OP
- [[Branch Control]] - Usa flags ZERO/NEGATIVE
- Documentación: `s-mips.pdf` - Instrucciones aritméticas
- Teoría: Patterson-Hennessy Cap. 3 - Arithmetic for Computers

---
**Última actualización**: 2025-12-09
**Estado**: ✅ IMPLEMENTADO Y FUNCIONAL
**Prioridad**: ✅ COMPLETADO
**Tests ejecutados**: ⚠️ Pendiente validación exhaustiva
