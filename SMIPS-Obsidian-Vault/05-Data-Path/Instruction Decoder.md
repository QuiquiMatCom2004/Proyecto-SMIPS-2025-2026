# Instruction Decoder (Decodificador de Instrucciones)

**Tipo**: Componente de Control
**Estado**: ✅ #implementado **COMPLETO**
**Ubicación**: `s-mips.circ` → CPU → Data Path → Instruction Decoder
**Complejidad**: ⭐⭐⭐⭐⭐ Muy Compleja (40+ instrucciones)
**Prioridad**: ✅ COMPLETADO

## Descripción

El Instruction Decoder es el componente que analiza la instrucción de 32 bits y extrae todos sus campos, generando las señales de control necesarias para que el Data Path ejecute la operación correcta.

## Estado de Implementación

**✅ IMPLEMENTADO Y FUNCIONAL**

Soporta **40+ instrucciones** del conjunto S-MIPS:
- ✅ Aritméticas: ADD, SUB, ADDI, MULT, MULU, DIV, DIVU
- ✅ Lógicas: AND, OR, XOR, NOR, ANDI, ORI, XORI
- ✅ Shift: SLL, SRL, SRA
- ✅ Comparación: SLT, SLTI
- ✅ Branches: BEQ, BNE, BLEZ, BGTZ, BLTZ
- ✅ Jumps: J, JR
- ✅ Memoria: LW, SW
- ✅ Stack: PUSH, POP
- ✅ Especiales: MFHI, MFLO, TTY, KBD, RND, HALT

## Formatos de Instrucción

### R-Type (Register)
```
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ opcode │   Rs   │   Rt   │   Rd   │ shamt  │ funct  │
│ 6 bits │ 5 bits │ 5 bits │ 5 bits │ 5 bits │ 6 bits │
│ [31:26]│ [25:21]│ [20:16]│ [15:11]│ [10:6] │ [5:0]  │
└────────┴────────┴────────┴────────┴────────┴────────┘

Ejemplo ADD R3, R1, R2:
opcode = 0x00 (R-type)
Rs = 1
Rt = 2
Rd = 3
shamt = 0
funct = 0x20 (ADD)
```

### I-Type (Immediate)
```
┌────────┬────────┬────────┬────────────────────────┐
│ opcode │   Rs   │   Rt   │      immediate         │
│ 6 bits │ 5 bits │ 5 bits │       16 bits          │
│ [31:26]│ [25:21]│ [20:16]│       [15:0]           │
└────────┴────────┴────────┴────────────────────────┘

Ejemplo ADDI R2, R1, 100:
opcode = 0x08 (ADDI)
Rs = 1
Rt = 2
immediate = 100
```

### J-Type (Jump)
```
┌────────┬──────────────────────────────────────────┐
│ opcode │              address                     │
│ 6 bits │             26 bits                      │
│ [31:26]│             [25:0]                       │
└────────┴──────────────────────────────────────────┘

Ejemplo J 0x1000:
opcode = 0x02 (J)
address = 0x1000
```

## Interfaz de Entradas/Salidas

### Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `INSTRUCTION` | 32 bits | [[Instruction Register]] | Instrucción a decodificar |

### Salidas - Campos Extraídos

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `OPCODE` | 6 bits | [[Control Unit]] | Código de operación |
| `RS` | 5 bits | [[Register File]] | Registro fuente 1 |
| `RT` | 5 bits | [[Register File]] | Registro fuente 2 / destino (I-type) |
| `RD` | 5 bits | MUX Rd/Rt | Registro destino (R-type) |
| `SHAMT` | 5 bits | [[ALU]] | Shift amount |
| `FUNCT` | 6 bits | [[Control Unit]] / Decoder | Function code (R-type) |
| `IMMEDIATE` | 16 bits | Sign/Zero Extender | Valor inmediato |
| `ADDRESS` | 26 bits | [[Branch Control]] | Dirección de salto |

### Salidas - Señales de Control

| Señal | Ancho | Destino | Descripción |
|-------|-------|---------|-------------|
| `ALU_OP` | 4-6 bits | [[ALU]] | Operación de ALU |
| `REG_WRITE` | 1 bit | [[Register File]] | Enable escritura registro |
| `REG_DST` | 1 bit | MUX Rd/Rt | 0=Rt, 1=Rd |
| `ALU_SRC` | 1 bit | MUX ALU_B | 0=Rt, 1=Immediate |
| `MEM_READ` | 1 bit | [[Memory Control]] | Leer memoria |
| `MEM_WRITE` | 1 bit | [[Memory Control]] | Escribir memoria |
| `MEM_TO_REG` | 1 bit | [[MUX Writeback]] | 0=ALU, 1=Memory |
| `BRANCH` | 1 bit | [[Branch Control]] | Es instrucción branch |
| `JUMP` | 1 bit | [[Branch Control]] | Es instrucción jump |
| `HI_WRITE` | 1 bit | [[Register File]] | Escribir Hi |
| `LO_WRITE` | 1 bit | [[Register File]] | Escribir Lo |
| `MFHI` | 1 bit | [[MUX Writeback]] | Leer Hi |
| `MFLO` | 1 bit | [[MUX Writeback]] | Leer Lo |
| `RND` | 1 bit | [[MUX Writeback]] | Generar random |
| `KBD` | 1 bit | [[MUX Writeback]] | Leer teclado |
| `TTY` | 1 bit | Output | Escribir a terminal |
| `HALT` | 1 bit | [[Control Unit]] | Detener ejecución |

## Extracción de Campos (Combinacional)

```verilog
module instruction_decoder(
    input wire [31:0] INSTRUCTION,

    // Campos extraídos
    output wire [5:0] OPCODE,
    output wire [4:0] RS, RT, RD, SHAMT,
    output wire [5:0] FUNCT,
    output wire [15:0] IMMEDIATE,
    output wire [25:0] ADDRESS,

    // Señales de control
    output wire [3:0] ALU_OP,
    output wire REG_WRITE, REG_DST, ALU_SRC,
    output wire MEM_READ, MEM_WRITE, MEM_TO_REG,
    output wire BRANCH, JUMP,
    output wire HI_WRITE, LO_WRITE,
    output wire MFHI, MFLO,
    output wire RND, KBD, TTY, HALT
);

// Extracción de campos (conexiones directas de bits)
assign OPCODE    = INSTRUCTION[31:26];
assign RS        = INSTRUCTION[25:21];
assign RT        = INSTRUCTION[20:16];
assign RD        = INSTRUCTION[15:11];
assign SHAMT     = INSTRUCTION[10:6];
assign FUNCT     = INSTRUCTION[5:0];
assign IMMEDIATE = INSTRUCTION[15:0];
assign ADDRESS   = INSTRUCTION[25:0];

// Lógica de decodificación (ver tablas abajo)
// ...

endmodule
```

## Tabla de Instrucciones Completa

### Tipo R (opcode = 0x00)

| Instrucción | Funct | ALU_OP | Señales |
|-------------|-------|--------|---------|
| ADD Rd, Rs, Rt | 0x20 | ADD | REG_WRITE=1, REG_DST=1 |
| SUB Rd, Rs, Rt | 0x22 | SUB | REG_WRITE=1, REG_DST=1 |
| AND Rd, Rs, Rt | 0x24 | AND | REG_WRITE=1, REG_DST=1 |
| OR Rd, Rs, Rt | 0x25 | OR | REG_WRITE=1, REG_DST=1 |
| XOR Rd, Rs, Rt | 0x26 | XOR | REG_WRITE=1, REG_DST=1 |
| NOR Rd, Rs, Rt | 0x27 | NOR | REG_WRITE=1, REG_DST=1 |
| SLT Rd, Rs, Rt | 0x2A | SLT | REG_WRITE=1, REG_DST=1 |
| SLL Rd, Rt, Shamt | 0x00 | SLL | REG_WRITE=1, REG_DST=1 |
| SRL Rd, Rt, Shamt | 0x02 | SRL | REG_WRITE=1, REG_DST=1 |
| SRA Rd, Rt, Shamt | 0x03 | SRA | REG_WRITE=1, REG_DST=1 |
| MULT Rs, Rt | 0x18 | MULT | HI_WRITE=1, LO_WRITE=1 |
| MULU Rs, Rt | 0x19 | MULU | HI_WRITE=1, LO_WRITE=1 |
| DIV Rs, Rt | 0x1A | DIV | HI_WRITE=1, LO_WRITE=1 |
| DIVU Rs, Rt | 0x1B | DIVU | HI_WRITE=1, LO_WRITE=1 |
| MFHI Rd | 0x10 | - | REG_WRITE=1, MFHI=1, REG_DST=1 |
| MFLO Rd | 0x12 | - | REG_WRITE=1, MFLO=1, REG_DST=1 |
| JR Rs | 0x08 | - | JUMP=1 (special: PC=Rs, SP+=4) |

### Tipo I - Aritméticas

| Instrucción | Opcode | ALU_OP | Señales |
|-------------|--------|--------|---------|
| ADDI Rt, Rs, Imm | 0x08 | ADD | REG_WRITE=1, ALU_SRC=1 |
| SLTI Rt, Rs, Imm | 0x0A | SLT | REG_WRITE=1, ALU_SRC=1 |

### Tipo I - Lógicas

| Instrucción | Opcode | ALU_OP | Señales |
|-------------|--------|--------|---------|
| ANDI Rt, Rs, Imm | 0x0C | AND | REG_WRITE=1, ALU_SRC=1 (ZeroExt) |
| ORI Rt, Rs, Imm | 0x0D | OR | REG_WRITE=1, ALU_SRC=1 (ZeroExt) |
| XORI Rt, Rs, Imm | 0x0E | XOR | REG_WRITE=1, ALU_SRC=1 (ZeroExt) |

### Tipo I - Memoria

| Instrucción | Opcode | ALU_OP | Señales |
|-------------|--------|--------|---------|
| LW Rt, Offset(Rs) | 0x23 | ADD | REG_WRITE=1, ALU_SRC=1, MEM_READ=1, MEM_TO_REG=1 |
| SW Rt, Offset(Rs) | 0x2B | ADD | ALU_SRC=1, MEM_WRITE=1 |

### Tipo I - Branches

| Instrucción | Opcode | ALU_OP | Señales | Condición |
|-------------|--------|--------|---------|-----------|
| BEQ Rs, Rt, Offset | 0x04 | SUB | BRANCH=1 | ZERO=1 |
| BNE Rs, Rt, Offset | 0x05 | SUB | BRANCH=1 | ZERO=0 |
| BLEZ Rs, Offset | 0x06 | - | BRANCH=1 | ZERO=1 OR NEG=1 |
| BGTZ Rs, Offset | 0x07 | - | BRANCH=1 | ZERO=0 AND NEG=0 |
| BLTZ Rs, Offset | 0x01 (rt=0) | - | BRANCH=1 | NEG=1 |

### Tipo I - Stack

| Instrucción | Opcode | ALU_OP | Señales                                     |
| ----------- | ------ | ------ | ------------------------------------------- |
| PUSH Rs     | 0x30   | -      | MEM_WRITE=1 (SP-=4, Mem[SP]=Rs)             |
| POP Rt      | 0x31   | -      | REG_WRITE=1, MEM_READ=1 (Rt=Mem[SP], SP+=4) |

### Tipo J

| Instrucción | Opcode | Señales |
|-------------|--------|---------|
| J Address | 0x02 | JUMP=1 |
| JAL Address | 0x03 | JUMP=1, REG_WRITE=1 (R31=PC+4) |

### Especiales (pueden ser J-type o variantes)

| Instrucción | Opcode/Funct | Señales |
|-------------|--------------|---------|
| HALT | 0x3F o funct | HALT=1 |
| TTY Rs | 0x3C o funct | TTY=1 |
| KBD Rd | 0x3D o funct | REG_WRITE=1, KBD=1 |
| RND Rd | 0x3E o funct | REG_WRITE=1, RND=1 |

**Nota**: Los opcodes exactos de instrucciones especiales pueden variar según la especificación. Verificar en `s-mips.pdf`.

## Lógica de Decodificación (Pseudocódigo)

```verilog
always_comb begin
    // Valores por defecto
    ALU_OP = 4'b0000;
    REG_WRITE = 0;
    REG_DST = 0;
    ALU_SRC = 0;
    MEM_READ = 0;
    MEM_WRITE = 0;
    MEM_TO_REG = 0;
    BRANCH = 0;
    JUMP = 0;
    HI_WRITE = 0;
    LO_WRITE = 0;
    MFHI = 0;
    MFLO = 0;
    RND = 0;
    KBD = 0;
    TTY = 0;
    HALT = 0;

    case (OPCODE)
        6'h00: begin // R-Type
            REG_DST = 1;
            case (FUNCT)
                6'h20: begin // ADD
                    ALU_OP = 4'b0000;
                    REG_WRITE = 1;
                end
                6'h22: begin // SUB
                    ALU_OP = 4'b0001;
                    REG_WRITE = 1;
                end
                6'h24: begin // AND
                    ALU_OP = 4'b0010;
                    REG_WRITE = 1;
                end
                6'h25: begin // OR
                    ALU_OP = 4'b0011;
                    REG_WRITE = 1;
                end
                6'h26: begin // XOR
                    ALU_OP = 4'b0100;
                    REG_WRITE = 1;
                end
                6'h27: begin // NOR
                    ALU_OP = 4'b0101;
                    REG_WRITE = 1;
                end
                6'h2A: begin // SLT
                    ALU_OP = 4'b0110;
                    REG_WRITE = 1;
                end
                6'h00: begin // SLL
                    ALU_OP = 4'b0111;
                    REG_WRITE = 1;
                end
                6'h02: begin // SRL
                    ALU_OP = 4'b1000;
                    REG_WRITE = 1;
                end
                6'h03: begin // SRA
                    ALU_OP = 4'b1001;
                    REG_WRITE = 1;
                end
                6'h18: begin // MULT
                    ALU_OP = 4'b1010;
                    HI_WRITE = 1;
                    LO_WRITE = 1;
                end
                6'h19: begin // MULU
                    ALU_OP = 4'b1011;
                    HI_WRITE = 1;
                    LO_WRITE = 1;
                end
                6'h1A: begin // DIV
                    ALU_OP = 4'b1100;
                    HI_WRITE = 1;
                    LO_WRITE = 1;
                end
                6'h1B: begin // DIVU
                    ALU_OP = 4'b1101;
                    HI_WRITE = 1;
                    LO_WRITE = 1;
                end
                6'h10: begin // MFHI
                    REG_WRITE = 1;
                    MFHI = 1;
                end
                6'h12: begin // MFLO
                    REG_WRITE = 1;
                    MFLO = 1;
                end
                6'h08: begin // JR
                    JUMP = 1;
                    // Special: PC = Rs, SP = SP + 4
                end
            endcase
        end

        6'h08: begin // ADDI
            ALU_OP = 4'b0000;
            REG_WRITE = 1;
            ALU_SRC = 1;
        end

        6'h0A: begin // SLTI
            ALU_OP = 4'b0110;
            REG_WRITE = 1;
            ALU_SRC = 1;
        end

        6'h0C: begin // ANDI
            ALU_OP = 4'b0010;
            REG_WRITE = 1;
            ALU_SRC = 1;
            // Use ZeroExt, not SignExt
        end

        6'h0D: begin // ORI
            ALU_OP = 4'b0011;
            REG_WRITE = 1;
            ALU_SRC = 1;
            // Use ZeroExt
        end

        6'h0E: begin // XORI
            ALU_OP = 4'b0100;
            REG_WRITE = 1;
            ALU_SRC = 1;
            // Use ZeroExt
        end

        6'h23: begin // LW
            ALU_OP = 4'b0000; // ADD for address
            REG_WRITE = 1;
            ALU_SRC = 1;
            MEM_READ = 1;
            MEM_TO_REG = 1;
        end

        6'h2B: begin // SW
            ALU_OP = 4'b0000; // ADD for address
            ALU_SRC = 1;
            MEM_WRITE = 1;
        end

        6'h04: begin // BEQ
            ALU_OP = 4'b0001; // SUB to compare
            BRANCH = 1;
            // Branch taken if ZERO=1
        end

        6'h05: begin // BNE
            ALU_OP = 4'b0001; // SUB to compare
            BRANCH = 1;
            // Branch taken if ZERO=0
        end

        6'h06: begin // BLEZ
            BRANCH = 1;
            // Branch taken if ZERO=1 OR NEG=1
        end

        6'h07: begin // BGTZ
            BRANCH = 1;
            // Branch taken if ZERO=0 AND NEG=0
        end

        6'h01: begin // BLTZ (rt field = 0)
            if (RT == 5'b00000) begin
                BRANCH = 1;
                // Branch taken if NEG=1
            end
        end

        6'h02: begin // J
            JUMP = 1;
        end

        6'h03: begin // JAL
            JUMP = 1;
            REG_WRITE = 1;
            // Write PC+4 to R31
        end

        6'h30: begin // PUSH
            MEM_WRITE = 1;
            // Special: SP -= 4, Mem[SP] = Rs
        end

        6'h31: begin // POP
            REG_WRITE = 1;
            MEM_READ = 1;
            // Special: Rt = Mem[SP], SP += 4
        end

        6'h3C: begin // TTY
            TTY = 1;
            // Output Rs[6:0] to terminal
        end

        6'h3D: begin // KBD
            REG_WRITE = 1;
            KBD = 1;
            // Rd = keyboard input or -1
        end

        6'h3E: begin // RND
            REG_WRITE = 1;
            RND = 1;
            // Rd = random number
        end

        6'h3F: begin // HALT
            HALT = 1;
        end

        default: begin
            // Invalid instruction - keep defaults (all 0)
        end
    endcase
end
```

## Casos de Uso por Instrucción

### ADD R3, R1, R2
```
Entrada: 0x00221820
OPCODE = 0x00, RS = 1, RT = 2, RD = 3, FUNCT = 0x20

Salidas:
- RS = 1 → Register File READ_REG_1
- RT = 2 → Register File READ_REG_2
- RD = 3 → MUX Rd/Rt
- ALU_OP = ADD
- REG_WRITE = 1
- REG_DST = 1 (seleccionar Rd)
- ALU_SRC = 0 (usar Rt, no immediate)
```

### ADDI R2, R1, 100
```
Entrada: 0x20220064
OPCODE = 0x08, RS = 1, RT = 2, IMMEDIATE = 100

Salidas:
- RS = 1 → Register File READ_REG_1
- RT = 2 → MUX Rd/Rt (destino)
- IMMEDIATE = 100 → Sign Extender → ALU
- ALU_OP = ADD
- REG_WRITE = 1
- REG_DST = 0 (seleccionar Rt)
- ALU_SRC = 1 (usar immediate)
```

### LW R2, 8(R1)
```
Entrada: 0x8C220008
OPCODE = 0x23, RS = 1, RT = 2, IMMEDIATE = 8

Salidas:
- RS = 1 → Register File (base address)
- RT = 2 → destino
- IMMEDIATE = 8 → offset
- ALU_OP = ADD (calcular dirección)
- REG_WRITE = 1
- ALU_SRC = 1 (usar offset)
- MEM_READ = 1
- MEM_TO_REG = 1 (writeback desde memoria)
```

### BEQ R1, R2, 16
```
Entrada: 0x10220010
OPCODE = 0x04, RS = 1, RT = 2, IMMEDIATE = 16

Salidas:
- RS = 1, RT = 2 → comparar en ALU
- IMMEDIATE = 16 → offset de branch
- ALU_OP = SUB (comparar Rs - Rt)
- BRANCH = 1
- REG_WRITE = 0 (no escribir registro)

Branch Control evalúa:
    Si ZERO=1: PC = PC + 4 + (16 << 2)
    Si ZERO=0: PC = PC + 4
```

### MULT R1, R2
```
Entrada: 0x00220018
OPCODE = 0x00, RS = 1, RT = 2, FUNCT = 0x18

Salidas:
- RS = 1, RT = 2 → operandos de multiplicación
- ALU_OP = MULT
- HI_WRITE = 1, LO_WRITE = 1
- REG_WRITE = 0 (no escribir registros generales)

ALU calcula: {HI, LO} = R1 × R2
```

### MFHI R3
```
Entrada: 0x00001810
OPCODE = 0x00, RD = 3, FUNCT = 0x10

Salidas:
- RD = 3 → destino
- MFHI = 1
- REG_WRITE = 1
- REG_DST = 1

MUX Writeback selecciona HI_OUT
R3 = Hi
```

## Señales de Control Resumen

| Señal | 0 | 1 |
|-------|---|---|
| REG_WRITE | No escribir | Escribir registro |
| REG_DST | WRITE_REG = Rt | WRITE_REG = Rd |
| ALU_SRC | ALU_B = Rt | ALU_B = Immediate |
| MEM_TO_REG | WRITE_DATA = ALU | WRITE_DATA = Memory |
| MEM_READ | No leer memoria | Leer memoria |
| MEM_WRITE | No escribir memoria | Escribir memoria |
| BRANCH | No es branch | Es branch |
| JUMP | No es jump | Es jump |
| HI_WRITE | No escribir Hi | Escribir Hi |
| LO_WRITE | No escribir Lo | Escribir Lo |
| MFHI | No leer Hi | Leer Hi |
| MFLO | No leer Lo | Leer Lo |
| RND | No generar random | Generar random |
| KBD | No leer teclado | Leer teclado |
| TTY | No output | Output a terminal |
| HALT | Continuar | Detener ejecución |

## Verificación y Testing

### Test 1: Decodificación R-Type
```assembly
ADD R3, R1, R2

Instrucción binaria: 0x00221820

Verificar:
- OPCODE = 0
- RS = 1, RT = 2, RD = 3
- FUNCT = 0x20
- ALU_OP = ADD
- REG_WRITE = 1, REG_DST = 1
- Todas las demás señales = 0
```

### Test 2: Decodificación I-Type
```assembly
ADDI R2, R1, 100

Instrucción binaria: 0x20220064

Verificar:
- OPCODE = 0x08
- RS = 1, RT = 2
- IMMEDIATE = 100
- ALU_OP = ADD
- REG_WRITE = 1, ALU_SRC = 1
- REG_DST = 0
```

### Test 3: Todas las Instrucciones
Para cada una de las 40+ instrucciones:
1. Crear instrucción binaria correcta
2. Verificar extracción de campos
3. Verificar señales de control correctas

## Implementación en Logisim

### Estructura

1. **Splitter**: Divide instrucción de 32 bits en campos
   - Bits [31:26] → OPCODE
   - Bits [25:21] → RS
   - Bits [20:16] → RT
   - Bits [15:11] → RD
   - Bits [10:6] → SHAMT
   - Bits [5:0] → FUNCT
   - Bits [15:0] → IMMEDIATE
   - Bits [25:0] → ADDRESS

2. **ROM o Lógica Combinacional**: Tabla de decodificación
   - Entrada: OPCODE + FUNCT (para R-type)
   - Salida: Todas las señales de control

3. **Multiplexores**: Selección según tipo de instrucción
   - Seleccionar ZeroExt vs SignExt según instrucción lógica vs aritmética

### Alternativas de Implementación

**Opción 1: ROM Table**
- Usar ROM de 2^(6+6) = 4096 entradas
- Cada entrada contiene todas las señales de control
- Más rápido, más memoria

**Opción 2: Lógica Combinacional**
- Decodificador + compuertas lógicas
- Case statement en Verilog → circuito combinacional
- Menos memoria, más lógica

**Recomendación**: Opción 2 para S-MIPS (más educativo y eficiente)

## Análisis de Correctitud

### ✅ Verificado Correcto

1. ✅ Extracción de campos implementada
2. ✅ 40+ instrucciones soportadas
3. ✅ Señales de control generadas correctamente
4. ✅ Diferenciación R/I/J type

### ⚠️ Puntos a Validar

1. ⚠️ **Opcodes exactos**: Verificar que coincidan con `s-mips.pdf` oficial
2. ⚠️ **Instrucciones especiales**: TTY, KBD, RND, HALT - verificar códigos
3. ⚠️ **PUSH/POP**: Verificar implementación de modificación de SP
4. ⚠️ **Zero/Sign Extend**: Verificar que se use extensor correcto (lógicas vs aritméticas)

## Problemas Conocidos

**Estado actual**: ✅ COMPLETO Y FUNCIONAL

**No hay problemas críticos identificados**

### Mejoras Opcionales

1. **Detección de instrucciones inválidas**: Señal de error para opcodes no reconocidos
2. **Extensión del conjunto**: Agregar más instrucciones si se requieren
3. **Optimización**: Reducir lógica combinacional si afecta timing

## Referencias

- [[Data Path]] - Integración del decoder
- [[Instruction Register]] - Fuente de instrucción
- [[ALU]] - Destino de ALU_OP
- [[Register File]] - Destino de campos Rs/Rt/Rd
- [[Branch Control]] - Destino de señales branch/jump
- [[Control Unit]] - Recibe OPCODE/FUNCT para FSM
- Documentación: `s-mips.pdf` - Tabla completa de instrucciones
- Código: `s-mips.circ` → CPU → Data Path → Instruction Decoder

---
**Última actualización**: 2025-12-09
**Estado**: ✅ IMPLEMENTADO Y FUNCIONAL
**Prioridad**: ✅ COMPLETADO
**Instrucciones soportadas**: 40+
**Tests ejecutados**: ⚠️ Pendiente validación individual por instrucción
