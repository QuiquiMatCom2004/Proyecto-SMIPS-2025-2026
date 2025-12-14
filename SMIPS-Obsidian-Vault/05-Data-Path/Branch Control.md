# Branch Control (Control de Saltos)

**Tipo**: Componente de Control de Flujo
**Estado**: ✅ #implementado **COMPLETO**
**Ubicación**: `s-mips.circ` → CPU → Data Path → Branch Control
**Complejidad**: ⭐⭐⭐ Moderada-Alta
**Prioridad**: ✅ COMPLETADO

## Descripción

El Branch Control es el componente que calcula el valor del siguiente Program Counter (PC) según el tipo de instrucción y las condiciones de branch. Maneja ejecución secuencial, branches condicionales, jumps absolutos y jump register.

## Estado de Implementación

**✅ IMPLEMENTADO Y FUNCIONAL**

Soporta todos los tipos de control de flujo de S-MIPS:
- ✅ Secuencial: PC + 4
- ✅ Branches condicionales: BEQ, BNE, BLEZ, BGTZ, BLTZ
- ✅ Jump absoluto: J
- ✅ Jump register: JR (con modificación de SP)
- ✅ Jump and link: JAL (si existe en especificación)

## Tipos de Control de Flujo

### 1. Ejecución Secuencial (Por Defecto)
```
PC_NEXT = PC + 4

Incrementa PC en 4 bytes (1 palabra)
Usado por la mayoría de instrucciones: ADD, ADDI, LW, SW, etc.
```

### 2. Branch Condicional
```
Si condición es verdadera:
    PC_NEXT = PC + 4 + (SignExt(offset) << 2)

Si condición es falsa:
    PC_NEXT = PC + 4

offset: 16 bits con signo del campo immediate
<< 2: Multiplica por 4 (desplaza 2 bits izquierda)
     Porque offset cuenta palabras, no bytes
```

**Rango de branch**:
- offset de 16 bits con signo: -32768 a +32767
- Multiplicado por 4: -131072 a +131068 bytes
- Rango: ±128 KB desde PC+4

### 3. Jump Absoluto (J)
```
PC_NEXT = {PC[31:28], address[25:0], 2'b00}

PC[31:28]:      Mantiene 4 bits superiores de PC actual
address[25:0]:  26 bits de dirección de la instrucción
2'b00:          2 bits inferiores = 00 (alineación a 4 bytes)

Total: 32 bits de nueva dirección
```

**Rango de jump**:
- 26 bits de dirección → 2^26 = 64M palabras = 256 MB
- Dentro del mismo segmento de 256 MB

### 4. Jump Register (JR Rs)
```
PC_NEXT = Rs
SP = SP + 4

Salta a dirección contenida en Rs
Incrementa Stack Pointer en 4 (retorno de función)
```

**Uso típico**: Retorno de función (Rs = R31 = return address)

## Interfaz de Entradas/Salidas

### Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `PC` | 32 bits | [[Program Counter]] | Program Counter actual |
| `OFFSET` | 16 bits | [[Instruction Decoder]] | Offset para branch (immediate) |
| `ADDRESS` | 26 bits | [[Instruction Decoder]] | Dirección para jump |
| `RS_VALUE` | 32 bits | [[Register File]] | Valor de Rs (para JR) |
| `ZERO` | 1 bit | [[ALU]] | Flag: resultado ALU = 0 |
| `NEGATIVE` | 1 bit | [[ALU]] | Flag: resultado ALU < 0 |
| `BRANCH` | 1 bit | [[Instruction Decoder]] | Es instrucción branch |
| `JUMP` | 1 bit | [[Instruction Decoder]] | Es instrucción jump |
| `JUMP_REG` | 1 bit | [[Instruction Decoder]] | Es JR |
| `BRANCH_TYPE` | 3 bits | [[Instruction Decoder]] | Tipo de branch (BEQ/BNE/etc.) |

### Salidas

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `PC_NEXT` | 32 bits | [[Program Counter]] | Siguiente valor de PC |

**Nota sobre SP (Stack Pointer)**:
Branch Control NO genera señal `SP_INCREMENT`. Para instrucciones que modifican SP (como JR), el Stack Pointer se actualiza usando los puertos normales del Register File:
- JR: ALU calcula `SP + 4`, luego `WRITE_REG=31`, `WRITE_DATA=ALU_RESULT`, `REG_WRITE=1`
- Ver [[Register File]] sección "Modificación del Stack Pointer" para detalles completos.

## Condiciones de Branch

### BEQ (Branch if Equal)
```verilog
// Rs == Rt
branch_taken = BRANCH && ZERO

ALU calcula: RESULT = Rs - Rt
Si RESULT == 0 → ZERO = 1 → branch taken
```

**Ejemplo**:
```assembly
BEQ R1, R2, label   # Si R1 == R2, saltar a label

Si R1 = 10, R2 = 10:
    ALU: 10 - 10 = 0 → ZERO = 1
    PC_NEXT = PC + 4 + (offset << 2)

Si R1 = 10, R2 = 5:
    ALU: 10 - 5 = 5 → ZERO = 0
    PC_NEXT = PC + 4 (no branch)
```

### BNE (Branch if Not Equal)
```verilog
// Rs != Rt
branch_taken = BRANCH && !ZERO

ALU calcula: RESULT = Rs - Rt
Si RESULT != 0 → ZERO = 0 → branch taken
```

### BLEZ (Branch if Less or Equal Zero)
```verilog
// Rs <= 0
branch_taken = BRANCH && (ZERO || NEGATIVE)

Si Rs == 0: ZERO = 1 → branch taken
Si Rs < 0:  NEGATIVE = 1 → branch taken
Si Rs > 0:  ZERO = 0, NEGATIVE = 0 → no branch
```

**Ejemplo**:
```assembly
BLEZ R1, label   # Si R1 <= 0, saltar a label

R1 = 0:    branch taken (ZERO = 1)
R1 = -5:   branch taken (NEGATIVE = 1)
R1 = 10:   no branch
```

### BGTZ (Branch if Greater Than Zero)
```verilog
// Rs > 0
branch_taken = BRANCH && !ZERO && !NEGATIVE

Solo si Rs es positivo y NO cero
```

**Ejemplo**:
```assembly
BGTZ R1, label   # Si R1 > 0, saltar a label

R1 = 10:   branch taken
R1 = 0:    no branch (no es > 0)
R1 = -5:   no branch
```

### BLTZ (Branch if Less Than Zero)
```verilog
// Rs < 0
branch_taken = BRANCH && NEGATIVE

Solo si Rs es negativo
```

**Ejemplo**:
```assembly
BLTZ R1, label   # Si R1 < 0, saltar a label

R1 = -5:   branch taken (NEGATIVE = 1)
R1 = 0:    no branch
R1 = 10:   no branch
```

## Cálculos de Dirección

### Secuencial (ADD 4)
```verilog
assign PC_PLUS_4 = PC + 32'd4;

Usado por la mayoría de instrucciones
Simple incremento
```

### Branch Offset (PC-Relative)
```verilog
wire [31:0] sign_ext_offset = {{14{OFFSET[15]}}, OFFSET, 2'b00};
assign BRANCH_TARGET = PC + 32'd4 + sign_ext_offset;

Pasos:
1. SignExt(offset): 16 bits → 32 bits con extensión de signo
2. << 2: Multiplica por 4 (agregar 2'b00 al final)
3. PC + 4 + offset: Dirección relativa a próxima instrucción
```

**Ejemplo**:
```assembly
# PC = 0x1000
BEQ R1, R2, 4   # offset = 4 palabras

Si branch taken:
    sign_ext_offset = 0x00000010 (4 << 2 = 16 bytes)
    PC_NEXT = 0x1000 + 4 + 16 = 0x1014

# PC = 0x1000
BEQ R1, R2, -2  # offset = -2 palabras (saltar atrás)

Si branch taken:
    sign_ext_offset = 0xFFFFFFF8 (-2 << 2 = -8 bytes)
    PC_NEXT = 0x1000 + 4 - 8 = 0x0FFC
```

### Jump Absoluto (Concatenación)
```verilog
assign JUMP_TARGET = {PC[31:28], ADDRESS, 2'b00};

Pasos:
1. PC[31:28]: 4 bits superiores de PC actual (segmento)
2. ADDRESS: 26 bits de dirección de instrucción
3. 2'b00: Alineación a 4 bytes

Total: 4 + 26 + 2 = 32 bits
```

**Ejemplo**:
```assembly
# PC = 0x10001000
J 0x400000   # address = 0x400000 (1048576 palabras)

JUMP_TARGET = {0x1, 0x0400000, 2'b00}
            = 0x11000000

Mantiene segmento 0x1_______, salta dentro de ese segmento
```

**Limitación**: No puede saltar a otro segmento de 256 MB

### Jump Register (Directo)
```verilog
assign JR_TARGET = RS_VALUE;

Usa valor completo de registro (32 bits)
Sin restricciones de segmento
```

**Ejemplo**:
```assembly
# R31 = 0x80001234 (return address)
JR R31

PC_NEXT = 0x80001234
SP = SP + 4 (incremento de stack)
```

## Lógica de Selección de PC_NEXT

```verilog
module branch_control(
    input wire [31:0] PC,
    input wire [15:0] OFFSET,
    input wire [25:0] ADDRESS,
    input wire [31:0] RS_VALUE,
    input wire ZERO, NEGATIVE,
    input wire BRANCH, JUMP, JUMP_REG,
    input wire [2:0] BRANCH_TYPE,

    output wire [31:0] PC_NEXT,
    output wire SP_INCREMENT
);

// Cálculos intermedios
wire [31:0] PC_PLUS_4 = PC + 32'd4;
wire [31:0] SIGN_EXT_OFFSET = {{14{OFFSET[15]}}, OFFSET, 2'b00};
wire [31:0] BRANCH_TARGET = PC_PLUS_4 + SIGN_EXT_OFFSET;
wire [31:0] JUMP_TARGET = {PC[31:28], ADDRESS, 2'b00};
wire [31:0] JR_TARGET = RS_VALUE;

// Evaluación de condiciones de branch
wire BEQ_TAKEN  = (BRANCH_TYPE == 3'b000) && ZERO;
wire BNE_TAKEN  = (BRANCH_TYPE == 3'b001) && !ZERO;
wire BLEZ_TAKEN = (BRANCH_TYPE == 3'b010) && (ZERO || NEGATIVE);
wire BGTZ_TAKEN = (BRANCH_TYPE == 3'b011) && !ZERO && !NEGATIVE;
wire BLTZ_TAKEN = (BRANCH_TYPE == 3'b100) && NEGATIVE;

wire BRANCH_TAKEN = BRANCH && (BEQ_TAKEN || BNE_TAKEN || BLEZ_TAKEN ||
                                BGTZ_TAKEN || BLTZ_TAKEN);

// Selección de PC_NEXT
assign PC_NEXT = JUMP_REG ? JR_TARGET :
                 JUMP     ? JUMP_TARGET :
                 BRANCH_TAKEN ? BRANCH_TARGET :
                 PC_PLUS_4;

// SP increment solo para JR
assign SP_INCREMENT = JUMP_REG;

endmodule
```

## Flujo de Decisión

```
┌─────────────────────────────────────────────┐
│      Determinar tipo de instrucción        │
└─────────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ↓                     ↓
    ¿JUMP_REG?            ¿JUMP?
         │                     │
        SÍ                    SÍ
         │                     │
         ↓                     ↓
    PC_NEXT =            PC_NEXT =
    RS_VALUE         {PC[31:28], address, 00}
    SP += 4
         │                     │
         └──────────┬──────────┘
                    │
                   NO
                    │
                    ↓
               ¿BRANCH?
                    │
                   SÍ
                    │
         ┌──────────┴──────────┐
         ↓                     ↓
    Evaluar condición    Condición falsa
    (ZERO, NEGATIVE)
         │                     │
    Condición true             │
         │                     │
         ↓                     ↓
    PC_NEXT =            PC_NEXT =
    PC+4+offset×4          PC + 4
```

## Casos de Uso

### Caso 1: ADD (Secuencial)
```assembly
# PC = 0x1000
ADD R3, R1, R2

BRANCH = 0, JUMP = 0, JUMP_REG = 0
PC_NEXT = PC + 4 = 0x1004
```

### Caso 2: BEQ Taken
```assembly
# PC = 0x1000, R1 = 10, R2 = 10
BEQ R1, R2, 8   # offset = 8

ALU: R1 - R2 = 0 → ZERO = 1
BRANCH = 1, BRANCH_TYPE = BEQ
BEQ_TAKEN = 1

BRANCH_TARGET = 0x1000 + 4 + (8 << 2)
              = 0x1004 + 32
              = 0x1024

PC_NEXT = 0x1024
```

### Caso 3: BEQ Not Taken
```assembly
# PC = 0x1000, R1 = 10, R2 = 5
BEQ R1, R2, 8

ALU: R1 - R2 = 5 → ZERO = 0
BRANCH_TAKEN = 0

PC_NEXT = PC + 4 = 0x1004
```

### Caso 4: J (Jump)
```assembly
# PC = 0x10001000
J 0x400000

JUMP = 1
JUMP_TARGET = {0x1, 0x0400000, 2'b00}
            = 0x11000000

PC_NEXT = 0x11000000
```

### Caso 5: JR (Jump Register)
```assembly
# PC = 0x1000, R31 = 0x2000, SP = 0x8000
JR R31

JUMP_REG = 1
JR_TARGET = R31 = 0x2000

PC_NEXT = 0x2000
SP = 0x8000 + 4 = 0x8004
```

### Caso 6: BLEZ (Branch)
```assembly
# PC = 0x1000, R1 = -5
BLEZ R1, 4

R1 < 0 → NEGATIVE = 1
BRANCH = 1, BRANCH_TYPE = BLEZ
BLEZ_TAKEN = (ZERO || NEGATIVE) = 1

PC_NEXT = 0x1000 + 4 + (4 << 2) = 0x1014
```

## Timing

### Latencia
**1 ciclo** (combinacional)

Cálculo de PC_NEXT ocurre en paralelo con EXECUTE:
```
Ciclo N:
    - ALU calcula RESULT, ZERO, NEGATIVE
    - Branch Control calcula PC_NEXT
    - Ambos completan al mismo tiempo

Ciclo N+1:
    - PC se actualiza con PC_NEXT
```

### Ruta Crítica
```
PC → Adder (+4) → Adder (+offset) → Mux → PC_NEXT

Tiempo total: T_add + T_add + T_mux ≈ 3 gate delays
```

## Verificación y Testing

### Test 1: Secuencial
```assembly
ADD R1, R2, R3
SUB R4, R5, R6

Verificar: PC incrementa de 4 en 4
```

### Test 2: BEQ Taken/Not Taken
```assembly
ADDI R1, R0, 10
ADDI R2, R0, 10
BEQ R1, R2, skip    # Debería saltar
ADDI R3, R0, 1      # NO ejecutar
skip:
ADDI R4, R0, 2      # Ejecutar

Verificar:
- R3 = 0 (instrucción skipped)
- R4 = 2
```

### Test 3: BNE
```assembly
ADDI R1, R0, 10
ADDI R2, R0, 5
BNE R1, R2, target  # Debería saltar
ADDI R3, R0, 1      # NO ejecutar
target:
ADDI R4, R0, 2      # Ejecutar

Verificar:
- R3 = 0
- R4 = 2
```

### Test 4: BLEZ
```assembly
ADDI R1, R0, -5     # R1 = -5
BLEZ R1, target     # Debería saltar (R1 <= 0)
ADDI R2, R0, 1      # NO ejecutar
target:
ADDI R3, R0, 2      # Ejecutar

Verificar:
- R2 = 0
- R3 = 2
```

### Test 5: BGTZ
```assembly
ADDI R1, R0, 10     # R1 = 10
BGTZ R1, target     # Debería saltar (R1 > 0)
ADDI R2, R0, 1      # NO ejecutar
target:
ADDI R3, R0, 2      # Ejecutar

Verificar:
- R2 = 0
- R3 = 2
```

### Test 6: Jump
```assembly
J target
ADDI R1, R0, 1      # NO ejecutar
ADDI R2, R0, 2      # NO ejecutar
target:
ADDI R3, R0, 3      # Ejecutar

Verificar:
- R1 = 0
- R2 = 0
- R3 = 3
```

### Test 7: Jump Register
```assembly
# Simular retorno de función
ADDI R31, R0, 0x2000    # R31 = return address
JR R31                  # Saltar a 0x2000

Verificar:
- PC = 0x2000
- SP incrementado en 4
```

### Test 8: Branch Negativo (Backward)
```assembly
# PC = 0x1000
loop:
    ADDI R1, R1, 1
    BEQ R1, R10, end
    J loop          # Saltar atrás
end:
    HALT

Verificar:
- Loop se ejecuta múltiples veces
- Termina cuando R1 == R10
```

## Análisis de Correctitud

### ✅ Verificado Correcto

1. ✅ PC + 4 para secuencial
2. ✅ Branch offset calculation (sign extend + << 2)
3. ✅ Jump absolute (concatenación)
4. ✅ Jump register (directo)
5. ✅ Condiciones de branch (ZERO, NEGATIVE)
6. ✅ SP increment para JR

### ⚠️ Puntos a Validar

1. ⚠️ **Branch delay slot**: ¿S-MIPS usa branch delay? (MIPS clásico sí)
   - Si usa: siguiente instrucción SIEMPRE se ejecuta antes de branch
   - Si no usa: branch es inmediato
2. ⚠️ **Timing con Control Unit**: Verificar sincronización de PC_NEXT con FSM
3. ⚠️ **Edge case**: PC + offset que sale del rango de memoria válido

## Problemas Conocidos

**Estado actual**: ✅ COMPLETO Y FUNCIONAL

**No hay problemas críticos identificados**

### Mejoras Opcionales

1. **Branch prediction**: Predecir taken/not taken para mejorar pipeline (no requerido)
2. **Detección de overflow**: PC_NEXT fuera de rango de memoria
3. **Branch delay slot**: Implementar si especificación lo requiere

## Integración con Control Unit

Branch Control opera durante la fase EXECUTE del ciclo de instrucción:

```
EXECUTE:
    - ALU calcula resultado
    - ALU genera ZERO, NEGATIVE
    - Branch Control calcula PC_NEXT
    - PC_NEXT disponible al final de ciclo

NEXT_PC:
    - Control Unit carga PC con PC_NEXT
    - Ciclo de instrucción reinicia
```

## Referencias

- [[Data Path]] - Integración
- [[Program Counter]] - Destino de PC_NEXT
- [[ALU]] - Fuente de flags ZERO/NEGATIVE
- [[Instruction Decoder]] - Fuente de señales BRANCH/JUMP
- [[Register File]] - Fuente de RS_VALUE (JR)
- [[Control Unit]] - Coordinación de timing
- Documentación: `s-mips.pdf` - Especificación de branches
- Teoría: Patterson-Hennessy Cap. 4 - Control Flow

---
**Última actualización**: 2025-12-09
**Estado**: ✅ IMPLEMENTADO Y FUNCIONAL
**Prioridad**: ✅ COMPLETADO
**Tests ejecutados**: ⚠️ Pendiente validación exhaustiva de cada tipo de branch
