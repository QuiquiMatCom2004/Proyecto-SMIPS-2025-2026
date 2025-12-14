# Data Path (Camino de Datos)

**Tipo**: Componente Integrador Central
**Estado**: 🟡 #implementado 
**Ubicación**: `s-mips.circ` → CPU → Data Path
**Complejidad**: ⭐⭐⭐⭐⭐ Muy Compleja (integra todos los componentes)
**Prioridad**: COMPLETO

## Descripción

El Data Path es el componente central que integra todos los elementos de procesamiento de datos del CPU. Maneja el flujo de datos desde las instrucciones hasta los resultados, coordinando operaciones entre registros, ALU, memoria y control de branches.

## Estado de Implementación

**🟡 90% IMPLEMENTADO**

### ✅ Componentes Implementados (11/11)

1. ✅ [[Instruction Register]] - Almacena instrucción actual
2. ✅ [[Instruction Decoder]] - Decodifica 40+ instrucciones
3. ✅ [[Register File]] - 32 registros + Hi/Lo
4. ✅ [[ALU]] - Operaciones aritméticas/lógicas
5. ✅ [[Branch Control]] - Cálculo de PC
6. ✅ [[Program Counter]] - Contador de programa
7. ✅ [[MUX Writeback]] - Selección de dato a escribir
8. ✅ MUX ALU_B - Selección operando B (Rt o Immediate)
9. ✅ MUX Rd/Rt - Selección registro destino
10. ✅ Sign/Zero Extenders - Extensión de inmediatos
11. ✅ [[Random Generator]] - Generador LFSR para instrucción RND

## Arquitectura del Data Path

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA PATH                                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              INSTRUCTION REGISTER (IR)                       │   │
│  │  • 32 bits                                                   │   │
│  │  • Cargado desde Memory Control                              │   │
│  │  • Salida a Instruction Decoder                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │           INSTRUCTION DECODER                                │   │
│  │  • Extrae: opcode, Rs, Rt, Rd, shamt, funct, immediate       │   │
│  │  • Genera: ALU_OP, REG_WRITE, MEM_READ, MEM_WRITE, etc.      │   │
│  │  • 40+ instrucciones soportadas                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│         │        │        │         │          │                    │
│         │        │        │         │          │                    │
│       Rs(5)   Rt(5)    Rd(5)   Imm(16)    ALU_OP                    │
│         │        │        │         │          │                    │
│         ↓        ↓        │         ↓          ↓                    │
│  ┌─────────────────┐     │    ┌────────┐  ┌─────────────────┐       │
│  │ REGISTER FILE   │     │    │Sign/   │  │      ALU        │       │
│  │ • 32 regs (R0-R31)    │    │Zero    │  │ • ADD/SUB/etc.  │       │
│  │ • R0 = 0        │     │    │Extend  │  │ • 40+ ops       │       │
│  │ • Hi/Lo special │     │    └────────┘  │ • Hi/Lo output  │       │
│  │                 │     │         │       │ • ZERO flag     │      │
│  │ READ_REG_1 = Rs │     │         │       │ • NEG flag      │      │
│  │ READ_REG_2 = Rt │     │         │       └─────────────────┘      │
│  │                 │     │         │                 ↑              │
│  │ READ_DATA_1 ────┼─────┼─────────┼─────────────→ A                │
│  │                 │     │         │                                │
│  │ READ_DATA_2 ────┼─────┼─────────┼──→ MUX_B ──→ B                 │
│  │                 │     │         │      ↑                         │
│  └─────────────────┘     │         └──────┘                         │
│         ↑                │           (Rt o Imm)                     │
│         │                │                                          │
│         │                ↓                                          │
│    WRITE_REG ←─── MUX_RD_RT                                         │
│         │           ↑     ↑                                         │
│         │           Rd    Rt                                        │
│         │                                                           │
│    WRITE_DATA ←── MUX_WRITEBACK ←─┬─ ALU_RESULT                     │
│                        ↑           ├─ MEMORY_DATA                   │
│                        │           ├─ HI_OUT                        │
│                        │           ├─ LO_OUT                        │
│                        │           ├─ PC+4                          │
│                        │           ├─ RND_VALUE                     │
│                        │           └─ KBD_VALUE                     │
│                        │                                            │
│                     Control                                         │
│                     Signals                                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              BRANCH CONTROL                                  │   │
│  │  • Calcula next PC                                           │   │
│  │  • PC+4 (secuencial)                                         │   │
│  │  • PC+4+offset×4 (branch)                                    │   │
│  │  • {PC[31:28], addr[25:0], 00} (jump)                        │   │
│  │  • Register value (JR)                                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              PROGRAM COUNTER (PC)                            │   │
│  │  • 32 bits                                                   │   │
│  │  • Incrementa cada ciclo de instrucción                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Interfaz de Entradas/Salidas

### Entradas desde Control Unit

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `LOAD_INST` | 1 bit | Cargar instrucción en IR |
| `REG_WRITE` | 1 bit | Enable escritura en Register File |
| `MEM_TO_REG` | 1 bit | Seleccionar dato de memoria para writeback |
| `ALU_SRC` | 1 bit | Seleccionar Rt o Immediate para ALU |
| `REG_DST` | 1 bit | Seleccionar Rd o Rt como destino |
| `BRANCH` | 1 bit | Instrucción es branch |
| `JUMP` | 1 bit | Instrucción es jump |
| `CLK` | 1 bit | Reloj del sistema |
| `RESET` | 1 bit | Reset del sistema |

### Entradas desde Memory Control

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `INSTRUCTION_IN` | 32 bits | Instrucción leída de memoria |
| `MEMORY_DATA` | 32 bits | Dato leído de memoria (LW) |

### Salidas a Control Unit

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `OPCODE` | 6 bits | Opcode de instrucción actual |
| `FUNCT` | 6 bits | Function code (R-type) |
| `ZERO` | 1 bit | Flag: resultado ALU = 0 |
| `NEGATIVE` | 1 bit | Flag: resultado ALU < 0 |

### Salidas a Memory Control

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `ADDRESS` | 32 bits | Dirección de memoria (LW/SW) |
| `WRITE_DATA` | 32 bits | Dato a escribir (SW) |
| `PC_OUT` | 32 bits | Program Counter para fetch |

## Subcomponentes Detallados

### 1. [[Instruction Register]] (IR)

**Función**: Almacenar la instrucción actual durante su ejecución.

**Implementación**:
```verilog
module instruction_register(
    input wire [31:0] INSTRUCTION_IN,
    input wire LOAD_INST,
    input wire CLK,
    output reg [31:0] INSTRUCTION_OUT
);

always @(posedge CLK) begin
    if (LOAD_INST) begin
        INSTRUCTION_OUT <= INSTRUCTION_IN;
    end
end

endmodule
```

**Estado**: ✅ IMPLEMENTADO

---

### 2. [[Instruction Decoder]]

**Función**: Decodificar instrucción y generar señales de control.

**Extracción de campos**:
```verilog
wire [5:0]  opcode    = INSTRUCTION[31:26];
wire [4:0]  rs        = INSTRUCTION[25:21];
wire [4:0]  rt        = INSTRUCTION[20:16];
wire [4:0]  rd        = INSTRUCTION[15:11];
wire [4:0]  shamt     = INSTRUCTION[10:6];
wire [5:0]  funct     = INSTRUCTION[5:0];
wire [15:0] immediate = INSTRUCTION[15:0];
wire [25:0] address   = INSTRUCTION[25:0];
```

**Generación de señales**:
- `ALU_OP`: Operación de ALU (4-6 bits)
- `REG_WRITE`: Escribir registro
- `MEM_READ`: Leer memoria
- `MEM_WRITE`: Escribir memoria
- `BRANCH`: Es branch
- `JUMP`: Es jump
- `ALU_SRC`: Usar immediate
- `REG_DST`: Destino Rd o Rt

**Estado**: ✅ IMPLEMENTADO (40+ instrucciones)

**Archivo detallado**: [[Instruction Decoder]]

---

### 3. [[Register File]]

**Función**: Banco de 32 registros + Hi/Lo.

**Características**:
- Lectura dual (2 puertos)
- Escritura single (1 puerto)
- R0 hardwired a 0
- Hi/Lo para MULT/DIV

**Interfaz**:
```verilog
input  [4:0]  READ_REG_1, READ_REG_2, WRITE_REG
output [31:0] READ_DATA_1, READ_DATA_2
input  [31:0] WRITE_DATA
input  REG_WRITE
```

**Estado**: ✅ IMPLEMENTADO

**Archivo detallado**: [[Register File]]

---

### 4. [[ALU]]

**Función**: Unidad aritmético-lógica.

**Operaciones soportadas**:
- Aritméticas: ADD, SUB, MULT, DIV
- Lógicas: AND, OR, XOR, NOR
- Shift: SLL, SRL, SRA
- Comparación: SLT

**Interfaz**:
```verilog
input  [31:0] A, B
input  [3:0]  ALU_OP
output [31:0] RESULT
output ZERO, NEGATIVE
output [31:0] HI, LO
```

**Estado**: ✅ IMPLEMENTADO

**Archivo detallado**: [[ALU]]

---

### 5. [[Branch Control]]

**Función**: Calcular siguiente PC.

**Cálculos**:
1. **Secuencial**: `PC_NEXT = PC + 4`
2. **Branch**: `PC_NEXT = PC + 4 + (SignExt(offset) << 2)`
3. **Jump**: `PC_NEXT = {PC[31:28], address[25:0], 2'b00}`
4. **Jump Register**: `PC_NEXT = Rs, SP = SP + 4`

**Condiciones de branch**:
- BEQ: `ZERO == 1`
- BNE: `ZERO == 0`
- BLEZ: `ZERO == 1 OR NEGATIVE == 1`
- BGTZ: `ZERO == 0 AND NEGATIVE == 0`
- BLTZ: `NEGATIVE == 1`

**Estado**: ✅ IMPLEMENTADO

**Archivo detallado**: [[Branch Control]]

---

### 6. [[Program Counter]] (PC)

**Función**: Mantener dirección de instrucción actual.

**Implementación**:
```verilog
module program_counter(
    input wire [31:0] PC_NEXT,
    input wire CLK,
    input wire RESET,
    output reg [31:0] PC
);

always @(posedge CLK) begin
    if (RESET)
        PC <= 32'h00000000;
    else
        PC <= PC_NEXT;
end

endmodule
```

**Estado**: ✅ IMPLEMENTADO

---

### 7. [[Random Generator]]

**Función**: Generar número pseudoaleatorio para instrucción RND.

**Implementación requerida**: LFSR de 32 bits

**Estado**: 🔴 NO IMPLEMENTADO

**Archivo detallado**: [[Random Generator]]

---

### 8. Multiplexores

#### MUX ALU_B (Selección operando B)
```verilog
assign ALU_B = ALU_SRC ? SignExt(immediate) : READ_DATA_2;

ALU_SRC = 0 → ALU_B = Rt (R-type: ADD, SUB, etc.)
ALU_SRC = 1 → ALU_B = Immediate (I-type: ADDI, ORI, etc.)
```

**Estado**: ✅ IMPLEMENTADO

---

#### MUX Rd/Rt (Selección registro destino)
```verilog
assign WRITE_REG = REG_DST ? rd : rt;

REG_DST = 0 → WRITE_REG = Rt (I-type: ADDI, LW, etc.)
REG_DST = 1 → WRITE_REG = Rd (R-type: ADD, SUB, etc.)
```

**Estado**: ✅ IMPLEMENTADO

---

#### [[MUX Writeback]] (Selección dato a escribir)

**Entradas (8 fuentes)**:
1. `ALU_RESULT` - Resultado de operación ALU
2. `MEMORY_DATA` - Dato leído de memoria (LW)
3. `HI_OUT` - Registro Hi (MFHI)
4. `LO_OUT` - Registro Lo (MFLO)
5. `PC_PLUS_4` - PC+4 (para JAL/JALR si existieran)
6. `RND_VALUE` - Número aleatorio (RND) 🔴
7. `KBD_VALUE` - Input de teclado (KBD)
8. `IMMEDIATE` - Immediate directo (si necesario)

**Lógica de selección**:
```verilog
case (WB_SEL)
    3'b000: WRITE_DATA = ALU_RESULT;
    3'b001: WRITE_DATA = MEMORY_DATA;
    3'b010: WRITE_DATA = HI_OUT;
    3'b011: WRITE_DATA = LO_OUT;
    3'b100: WRITE_DATA = PC_PLUS_4;
    3'b101: WRITE_DATA = RND_VALUE;
    3'b110: WRITE_DATA = KBD_VALUE;
    3'b111: WRITE_DATA = IMMEDIATE;
endcase
```

**Estado**: ✅ IMPLEMENTADO (excepto RND_VALUE)

**Archivo detallado**: [[MUX Writeback]]

---

### 9. Extenders

#### Sign Extender (16→32 bits)
```verilog
assign SignExt = {{16{immediate[15]}}, immediate};

Ejemplo:
immediate = 0xFFFF (-1 en 16 bits)
SignExt   = 0xFFFFFFFF (-1 en 32 bits)

immediate = 0x0005 (5 en 16 bits)
SignExt   = 0x00000005 (5 en 32 bits)
```

**Usado por**: ADDI, SLTI, LW, SW, BEQ, BNE, etc.

**Estado**: ✅ IMPLEMENTADO

---

#### Zero Extender (16→32 bits)
```verilog
assign ZeroExt = {16'h0000, immediate};

Ejemplo:
immediate = 0xFFFF
ZeroExt   = 0x0000FFFF (65535 unsigned)
```

**Usado por**: ANDI, ORI, XORI

**Estado**: ✅ IMPLEMENTADO

---

## Flujo de Datos por Tipo de Instrucción

### R-Type (ADD R3, R1, R2)

```
1. IR carga instrucción: 0x00221820
   opcode=0, rs=1, rt=2, rd=3, shamt=0, funct=0x20

2. Instruction Decoder:
   - Extrae rs=1, rt=2, rd=3
   - Genera ALU_OP=ADD, REG_DST=1, REG_WRITE=1

3. Register File:
   - READ_REG_1 = 1 → READ_DATA_1 = R1
   - READ_REG_2 = 2 → READ_DATA_2 = R2

4. MUX ALU_B:
   - ALU_SRC=0 → ALU_B = READ_DATA_2 (R2)

5. ALU:
   - A = R1, B = R2
   - RESULT = R1 + R2

6. MUX Rd/Rt:
   - REG_DST=1 → WRITE_REG = 3 (Rd)

7. MUX Writeback:
   - WB_SEL=ALU → WRITE_DATA = ALU_RESULT

8. Register File:
   - R3 = WRITE_DATA (R1 + R2)
```

---

### I-Type Aritmético (ADDI R2, R1, 100)

```
1. IR: opcode=0x08, rs=1, rt=2, immediate=100

2. Decoder:
   - ALU_OP=ADD, REG_DST=0, REG_WRITE=1, ALU_SRC=1

3. Register File:
   - READ_DATA_1 = R1

4. Sign Extender:
   - SignExt(100) = 0x00000064

5. MUX ALU_B:
   - ALU_SRC=1 → ALU_B = SignExt(immediate) = 100

6. ALU:
   - RESULT = R1 + 100

7. MUX Rd/Rt:
   - REG_DST=0 → WRITE_REG = 2 (Rt)

8. MUX Writeback:
   - WRITE_DATA = ALU_RESULT

9. Register File:
   - R2 = R1 + 100
```

---

### Load (LW R2, 8(R1))

```
1. IR: opcode=LW, rs=1, rt=2, offset=8

2. Decoder:
   - ALU_OP=ADD, MEM_READ=1, REG_WRITE=1, MEM_TO_REG=1

3. ALU:
   - A = R1, B = SignExt(8)
   - ADDRESS = R1 + 8

4. Memory Control:
   - Lee memoria en ADDRESS
   - Retorna MEMORY_DATA

5. MUX Writeback:
   - MEM_TO_REG=1 → WRITE_DATA = MEMORY_DATA

6. Register File:
   - R2 = MEMORY_DATA
```

---

### Store (SW R2, 8(R1))

```
1. IR: opcode=SW, rs=1, rt=2, offset=8

2. Decoder:
   - ALU_OP=ADD, MEM_WRITE=1, REG_WRITE=0

3. ALU:
   - ADDRESS = R1 + 8

4. Register File:
   - READ_DATA_2 = R2

5. Memory Control:
   - Escribe READ_DATA_2 en memoria[ADDRESS]

6. No writeback (REG_WRITE=0)
```

---

### Branch (BEQ R1, R2, offset)

```
1. Decoder:
   - ALU_OP=SUB, BRANCH=1

2. ALU:
   - RESULT = R1 - R2
   - ZERO = (RESULT == 0)

3. Branch Control:
   - Si ZERO==1 AND BRANCH==1:
       PC_NEXT = PC + 4 + (SignExt(offset) << 2)
   - Si no:
       PC_NEXT = PC + 4
```

---

### Jump (J address)

```
1. Decoder:
   - JUMP=1

2. Branch Control:
   - PC_NEXT = {PC[31:28], address[25:0], 2'b00}
```

---

### MULT (MULT R1, R2)

```
1. ALU:
   - {HI, LO} = R1 × R2

2. Register File:
   - Hi ← HI, Lo ← LO
   - No writeback a registros generales
```

---

### MFHI (MFHI R3)

```
1. Register File:
   - HI_OUT = Hi

2. MUX Writeback:
   - WRITE_DATA = HI_OUT

3. Register File:
   - R3 = Hi
```

---

### RND (RND R5)

```
1. Random Generator: 🔴 FALTANTE
   - RND_VALUE = LFSR output

2. MUX Writeback:
   - WRITE_DATA = RND_VALUE

3. Register File:
   - R5 = RND_VALUE
```

---

## 📊 Flujo de Señales Completo (Todas las Conexiones)

### De Memory Control → Data Path
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `INST_IN` | 32 bits | Instrucción leída de memoria → Instruction Register |

### De Control Unit → Data Path
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `LOAD_I` | 1 bit | Cargar instrucción en Instruction Register |
| `EN` | 1 bit | Data Path Enable (habilitar ejecución) |
| `CLK_DP` | 1 bit | Clock del Data Path |
| `CLR` | 1 bit | Clear/Reset global del Data Path |

### De Instruction Register → Instruction Decoder
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `IR` | 32 bits | Instrucción completa para decodificar |

### De Instruction Decoder → Register File
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `READ_REG_1` | 5 bits | Dirección de Rs (registro fuente 1) |
| `READ_REG_2` | 5 bits | Dirección de Rt (registro fuente 2) |
| `WRITE_REG` | 5 bits | Dirección de Rd o Rt (destino, vía MUX) |
| `REG_WRITE` | 1 bit | Enable de escritura en Register File |

### De Register File → ALU
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `READ_DATA_1` | 32 bits | Contenido de Rs → Operando A de ALU |
| `READ_DATA_2` | 32 bits | Contenido de Rt → MUX_B → Operando B (o immediate) |

### De ALU → Register File
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `RESULT` | 32 bits | Resultado de operación → MUX Writeback → WRITE_DATA |
| `HI` | 32 bits | Upper 32 bits (MULT/DIV) → HI_IN |
| `LO` | 32 bits | Lower 32 bits (MULT/DIV) → LO_IN |

### De ALU → Branch Control
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `ZERO` | 1 bit | Flag: resultado = 0 (para BEQ) |
| `NEGATIVE` | 1 bit | Flag: resultado < 0 (para BLEZ, BLTZ, BGTZ) |

### De Branch Control → Program Counter
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `PC_NEXT` | 32 bits | Próximo valor de PC (secuencial/branch/jump) |

### De Register File → Memory Control
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `READ_DATA_2` | 32 bits | Dato a escribir en memoria (para SW/PUSH) |

### De ALU → Memory Control
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `RESULT` | 32 bits | Dirección efectiva para LW/SW (base + offset) |

### De Data Path → Control Unit
| Señal | Ancho | Descripción |
|-------|-------|-------------|
| `HALT` | 1 bit | Señal de instrucción HALT |
| `MC_NEEDED` | 1 bit | Indica si necesita acceso a memoria (LW/SW/PUSH/POP) |

### Multiplexores Internos Detallados

#### MUX ALU_B (2 entradas)
**Selector**: `ALU_SRC` [1 bit]
```
ALU_SRC = 0 → ALU_B = READ_DATA_2 (Rt) - Para R-type
ALU_SRC = 1 → ALU_B = SignExt(immediate) - Para I-type arithmetic
```

#### MUX Rd/Rt (2 entradas)
**Selector**: `REG_DST` [1 bit]
```
REG_DST = 0 → WRITE_REG = Rt - Para I-type (ADDI, LW)
REG_DST = 1 → WRITE_REG = Rd - Para R-type (ADD, SUB)

Excepción para PUSH/POP/JR:
  WRITE_REG = 31 (SP) - Forzado directamente, no via MUX
```

#### MUX Writeback (8 entradas)
**Selector**: `WB_SEL` [3 bits]
```
000 → WRITE_DATA = ALU_RESULT       - ADD, SUB, AND, OR, etc.
001 → WRITE_DATA = MEMORY_DATA      - LW, POP
010 → WRITE_DATA = HI_OUT           - MFHI
011 → WRITE_DATA = LO_OUT           - MFLO
100 → WRITE_DATA = PC_PLUS_4        - JAL (si existe)
101 → WRITE_DATA = RND_VALUE        - RND
110 → WRITE_DATA = KBD_VALUE        - KBD
111 → WRITE_DATA = IMMEDIATE        - (Si necesario)
```

## Conexión con Otros Componentes

### Con Control Unit

**Señales de entrada (Control → Data Path)**:
- `LOAD_INST`: Cargar instrucción en IR
- `REG_WRITE`: Enable escritura registros
- `MEM_TO_REG`: Seleccionar memoria en writeback
- `ALU_SRC`: Usar immediate en ALU
- `REG_DST`: Destino Rd o Rt
- `BRANCH`, `JUMP`: Tipo de instrucción

**Señales de salida (Data Path → Control)**:
- `OPCODE`, `FUNCT`: Para decodificación en Control Unit
- `ZERO`, `NEGATIVE`: Flags para branches

---

### Con Memory Control

**Señales de salida (Data Path → Memory)**:
- `PC_OUT`: Dirección de fetch
- `ADDRESS`: Dirección para LW/SW
- `WRITE_DATA`: Dato a escribir (SW)

**Señales de entrada (Memory → Data Path)**:
- `INSTRUCTION_IN`: Instrucción fetched
- `MEMORY_DATA`: Dato leído (LW)

---

### Con Caché (cuando se implemente)

**Instruction Cache**:
```
PC_OUT → I-Cache → Memory Control
         I-Cache hit → INSTRUCTION_IN (1 cycle)
         I-Cache miss → Memory Control (RT cycles)
```

**Data Cache**:
```
ADDRESS, WRITE_DATA → D-Cache → Memory Control
                      D-Cache hit (1 cycle)
                      D-Cache miss (RT/WT cycles)
```

---

## Timing del Data Path

### Sin Pipeline (Estado actual)

Cada instrucción se ejecuta completamente antes de la siguiente:

```
Ciclo 1-N:   FETCH (RT cycles)
Ciclo N+1:   DECODE (1 cycle)
Ciclo N+2:   EXECUTE (1 cycle)
Ciclo N+3:   MEMORY (RT/WT cycles, si aplica)
Ciclo N+4:   WRITEBACK (1 cycle)

Total: RT + 3 a 4 cycles (sin caché)
       4 a 5 cycles (con I-Cache, hit)
```

### Potencial con Pipeline (Opcional, no requerido)

Si se implementara pipeline de 5 etapas:
```
IF | ID | EX | MEM | WB
   | IF | ID | EX  | MEM | WB
       | IF | ID  | EX  | MEM | WB

Throughput: 1 instrucción/ciclo (después de llenado)
```

**Nota**: S-MIPS no requiere pipeline. Implementación actual es single-cycle multi-cycle.

---

## Hazards (Riesgos)

### Data Hazards

#### RAW (Read-After-Write)
```assembly
ADDI R1, R0, 10    # Escribe R1
ADD R2, R1, R0     # Lee R1
```

**Problema**: Si ADD lee R1 antes de que ADDI escriba, valor incorrecto.

**Solución**:
1. **Forwarding**: Pasar WRITE_DATA directamente a READ_DATA si hay match
2. **Stalling**: Control Unit inserta ciclos de espera
3. **Manual**: Programador inserta NOPs

**Estado actual**: ⚠️ Verificar si hay forwarding implementado

---

### Control Hazards

#### Branch Hazard
```assembly
BEQ R1, R2, label
ADD R3, R4, R5      # ¿Se ejecuta o no?
label: ...
```

**Problema**: No se sabe si branch será tomado hasta después de EXECUTE.

**Solución**:
1. **Branch delay slot**: Siempre ejecutar siguiente instrucción
2. **Branch prediction**: Predecir tomado/no tomado
3. **Stalling**: Esperar hasta resolución

**Estado actual**: ⚠️ Verificar estrategia implementada

---

## Verificación y Testing

### Tests por Componente

| Componente | Test | Verificación |
|------------|------|--------------|
| IR | Cargar instrucción | IR debe contener instrucción correcta |
| Decoder | Todas las 40+ instrucciones | Señales de control correctas |
| Register File | Lectura/escritura, R0=0, Hi/Lo | Valores correctos |
| ALU | Todas las operaciones | RESULT, ZERO, NEG correctos |
| Branch Control | BEQ, BNE, BLEZ, BGTZ, J, JR | PC_NEXT correcto |
| Extenders | Sign/Zero extend | Valores extendidos correctos |
| Multiplexores | Todas las selecciones | Salida correcta según control |

### Tests de Integración

1. **Instrucción R-type completa**: ADD, verificar flujo completo
2. **Instrucción I-type completa**: ADDI, verificar immediate
3. **Load/Store**: LW/SW, verificar acceso a memoria
4. **Branch taken/not taken**: BEQ, verificar PC
5. **MULT/DIV + MFHI/MFLO**: Verificar Hi/Lo
6. **Programa completo**: Múltiples instrucciones secuenciales

---

## Análisis de Correctitud

### ✅ Componentes Verificados Correctos

1. ✅ Instruction Register - Implementado
2. ✅ Instruction Decoder - 40+ instrucciones
3. ✅ Register File - R0=0, Hi/Lo funcional
4. ✅ ALU - Todas las operaciones
5. ✅ Branch Control - Todos los tipos
6. ✅ Program Counter - Funcionamiento básico
7. ✅ Multiplexores - Implementados
8. ✅ Extenders - Sign/Zero correctos

### 🔴 Componentes Faltantes

1. 🔴 Random Generator - Instrucción RND no funciona

### ⚠️ Verificaciones Pendientes

1. ⚠️ **Forwarding**: ¿Hay detección de data hazards?
2. ⚠️ **Branch delay**: ¿Cómo se manejan branches?
3. ⚠️ **Timing**: ¿Todos los componentes sincronizan correctamente?

---

## Estimación de Trabajo Restante

### Random Generator (ÚNICA TAREA PENDIENTE)

**Tiempo**: 2-3 horas

**Tareas**:
1. Implementar LFSR de 32 bits (1 hora)
2. Conectar a MUX Writeback (30 min)
3. Conectar señales de control (30 min)
4. Testing (1 hora)

**Después de esto**: Data Path 100% completo ✅

---

## Referencias

- [[Instruction Register]] - Almacenamiento de instrucción
- [[Instruction Decoder]] - Decodificación completa
- [[Register File]] - Banco de registros
- [[ALU]] - Operaciones aritméticas/lógicas
- [[Branch Control]] - Control de PC
- [[Random Generator]] - LFSR (faltante)
- [[MUX Writeback]] - Selección de writeback
- [[Control Unit]] - Orquestador externo
- [[Memory Control]] - Interfaz con RAM
- Documentación: `s-mips.pdf` - Especificación completa
- Código: `s-mips.circ` líneas 8882-9970

---
**Última actualización**: 2025-12-09
**Estado**: 🟡 90% IMPLEMENTADO
**Faltante**: Random Generator (2-3 horas)
**Prioridad**: 🟢 BAJA (completar después de Control Unit y Memory Control)
