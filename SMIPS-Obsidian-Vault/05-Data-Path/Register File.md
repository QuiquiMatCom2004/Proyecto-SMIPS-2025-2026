# Register File (Banco de Registros)

**Tipo**: Componente de Almacenamiento
**Estado**: ✅ #implementado **COMPLETO**
**Ubicación**: `s-mips.circ` → CPU → Data Path → Register File
**Complejidad**: ⭐⭐⭐ Moderada
**Prioridad**: ✅ COMPLETADO

## Descripción

El Register File es el banco de registros de propósito general del procesador S-MIPS. Contiene 32 registros de 32 bits (R0-R31) más dos registros especiales (Hi y Lo) para resultados de multiplicación y división.

## Estado de Implementación

**✅ IMPLEMENTADO Y FUNCIONAL**

El Register File actual implementa:
- ✅ 32 registros de propósito general (R0-R31)
- ✅ R0 hardwired a 0 (siempre retorna 0, no modificable)
- ✅ R31 usado como Stack Pointer (SP) por PUSH/POP/JR
- ✅ Registros especiales Hi y Lo
- ✅ Lectura dual (2 puertos de lectura simultánea)
- ✅ Escritura single (1 puerto de escritura)
- ✅ Write enable con control de reloj

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              REGISTER FILE                          │
│                                                     │
│  R0  = 0x00000000 (hardwired to 0)                 │
│  R1  = General Purpose                              │
│  R2  = General Purpose                              │
│  ...                                                │
│  R30 = General Purpose                              │
│  R31 = Stack Pointer (SP)                           │
│                                                     │
│  Hi  = Multiplication/Division High                 │
│  Lo  = Multiplication/Division Low                  │
│                                                     │
│  Ports:                                             │
│    - Read Port 1 (Rs)                               │
│    - Read Port 2 (Rt)                               │
│    - Write Port (Rd)                                │
└─────────────────────────────────────────────────────┘
```

## Interfaz de Entradas/Salidas

### Entradas de Lectura

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `READ_REG_1` | 5 bits | [[Instruction Decoder]] | Rs (registro fuente 1) |
| `READ_REG_2` | 5 bits | [[Instruction Decoder]] | Rt (registro fuente 2) |

### Salidas de Lectura

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `READ_DATA_1` | 32 bits | [[ALU]] (operando A) | Contenido de Rs |
| `READ_DATA_2` | 32 bits | MUX ALU_B / Memory | Contenido de Rt |

### Entradas de Escritura (Registros Generales)

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `WRITE_REG` | 5 bits | MUX Rd/Rt | Registro destino (Rd o Rt) |
| `WRITE_DATA` | 32 bits | MUX Writeback | Dato a escribir |
| `REG_WRITE` | 1 bit | [[Control Unit]] | Enable de escritura |
| `CLK` | 1 bit | Sistema | Reloj (escritura en flanco positivo) |

### Entradas de Escritura (Hi/Lo)

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `HI_IN` | 32 bits | [[ALU]] | Valor para Hi (MULT/DIV) |
| `LO_IN` | 32 bits | [[ALU]] | Valor para Lo (MULT/DIV) |
| `HI_WRITE` | 1 bit | [[Control Unit]] | Enable escritura Hi |
| `LO_WRITE` | 1 bit | [[Control Unit]] | Enable escritura Lo |

### Salidas (Hi/Lo)

| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `HI_OUT` | 32 bits | MUX Writeback | Contenido de Hi (MFHI) |
| `LO_OUT` | 32 bits | MUX Writeback | Contenido de Lo (MFLO) |

## Especificación de Registros

### Registros de Propósito General (R0-R31)

| Registro | Nombre | Uso | Notas |
|----------|--------|-----|-------|
| R0 | $zero | Constante 0 | Hardwired, siempre retorna 0, escrituras ignoradas |
| R1-R30 | General | Propósito general | Programador decide uso |
| R31 | $sp | Stack Pointer | Modificado por PUSH/POP/JR |

### Convenciones de Uso (Sugeridas)

Aunque S-MIPS no impone convenciones, típicamente:

| Registro | Uso Típico |
|----------|------------|
| R0 | Siempre 0 |
| R1-R4 | Argumentos de función / valores de retorno |
| R5-R15 | Temporales |
| R16-R23 | Saved registers (preservar en llamadas) |
| R24-R25 | Temporales |
| R26-R27 | Kernel use |
| R28 | Global pointer |
| R29 | Stack pointer |
| R30 | Frame pointer |
| R31 | Stack pointer (S-MIPS) |

**Nota**: S-MIPS usa R31 como SP, no sigue convención MIPS estándar estrictamente.

### Registros Especiales (Hi/Lo)

| Registro | Uso | Instrucciones |
|----------|-----|---------------|
| Hi | Upper 32 bits de MULT/DIV | Resultado de MULT, Remainder de DIV |
| Lo | Lower 32 bits de MULT/DIV | Resultado de MULT, Quotient de DIV |

**Escritura**: Solo por MULT/MULU/DIV/DIVU
**Lectura**: Solo por MFHI/MFLO

## Operaciones

### Lectura de Registros

```verilog
// Dual-port read (simultáneo)
READ_DATA_1 = (READ_REG_1 == 0) ? 32'h00000000 : registers[READ_REG_1]
READ_DATA_2 = (READ_REG_2 == 0) ? 32'h00000000 : registers[READ_REG_2]

// R0 siempre retorna 0, independiente de contenido
// Lectura combinacional (no requiere reloj)
```

**Ejemplo**:
```assembly
ADD R3, R1, R2

READ_REG_1 = 1  (R1)
READ_REG_2 = 2  (R2)

READ_DATA_1 = contenido de R1
READ_DATA_2 = contenido de R2
→ Ambos van a ALU para sumar
```

### Escritura de Registros

```verilog
// Escritura en flanco positivo de CLK
always @(posedge CLK) begin
    if (REG_WRITE && WRITE_REG != 0) begin
        registers[WRITE_REG] <= WRITE_DATA
    end
end

// R0 NUNCA se escribe (WRITE_REG != 0)
// Escritura solo si REG_WRITE = 1
```

**Ejemplo**:
```assembly
ADDI R5, R0, 100  # R5 = 100

Durante WRITEBACK:
    WRITE_REG = 5 (Rt)
    WRITE_DATA = 100 (Immediate)
    REG_WRITE = 1

En próximo flanco positivo:
    R5 <= 100
```

### Protección de R0

```verilog
// Opción 1: No escribir físicamente
if (WRITE_REG != 0) begin
    registers[WRITE_REG] <= WRITE_DATA
end

// Opción 2: Escribir pero forzar lectura a 0
READ_DATA_1 = (READ_REG_1 == 0) ? 32'h0 : registers[READ_REG_1]
```

**Recomendación**: Opción 1 (no escribir) es más eficiente.

### Operaciones Hi/Lo

#### MULT/MULU (Escritura)
```verilog
always @(posedge CLK) begin
    if (HI_WRITE) begin
        Hi <= HI_IN   // Upper 32 bits
    end
    if (LO_WRITE) begin
        Lo <= LO_IN   // Lower 32 bits
    end
end
```

**Ejemplo**:
```assembly
ADDI R1, R0, 1000
ADDI R2, R0, 2000
MULT R1, R2         # Hi:Lo = 2,000,000

ALU calcula: 0x00000000_001E8480
HI_IN = 0x00000000
LO_IN = 0x001E8480
HI_WRITE = 1
LO_WRITE = 1

→ Hi = 0x00000000
→ Lo = 0x001E8480
```

#### MFHI/MFLO (Lectura)
```verilog
// Combinacional
HI_OUT = Hi
LO_OUT = Lo
```

**Ejemplo**:
```assembly
MFHI R3    # R3 = Hi
MFLO R4    # R4 = Lo

MUX Writeback selecciona HI_OUT o LO_OUT
WRITE_DATA = HI_OUT (para MFHI) o LO_OUT (para MFLO)
WRITE_REG = 3 (para MFHI) o 4 (para MFLO)
```

## Pseudocódigo Verilog

```verilog
module register_file(
    input wire [4:0] READ_REG_1,
    input wire [4:0] READ_REG_2,
    input wire [4:0] WRITE_REG,
    input wire [31:0] WRITE_DATA,
    input wire REG_WRITE,
    input wire CLK,
    input wire RESET,

    output wire [31:0] READ_DATA_1,
    output wire [31:0] READ_DATA_2,

    // Hi/Lo
    input wire [31:0] HI_IN,
    input wire [31:0] LO_IN,
    input wire HI_WRITE,
    input wire LO_WRITE,

    output wire [31:0] HI_OUT,
    output wire [31:0] LO_OUT
);

// 32 registros de propósito general (R0-R31)
reg [31:0] registers[31:1];  // R0 no existe físicamente

// Registros especiales
reg [31:0] Hi;
reg [31:0] Lo;

// Lectura combinacional (dual-port)
assign READ_DATA_1 = (READ_REG_1 == 5'b00000) ? 32'h00000000 : registers[READ_REG_1];
assign READ_DATA_2 = (READ_REG_2 == 5'b00000) ? 32'h00000000 : registers[READ_REG_2];

assign HI_OUT = Hi;
assign LO_OUT = Lo;

// Escritura secuencial (single-port)
always @(posedge CLK) begin
    if (RESET) begin
        // Reset todos los registros (opcional)
        for (int i = 1; i < 32; i++)
            registers[i] <= 32'h00000000;
        Hi <= 32'h00000000;
        Lo <= 32'h00000000;
    end else begin
        // Escritura de registros generales
        if (REG_WRITE && WRITE_REG != 5'b00000) begin
            registers[WRITE_REG] <= WRITE_DATA;
        end

        // Escritura de Hi/Lo
        if (HI_WRITE) begin
            Hi <= HI_IN;
        end
        if (LO_WRITE) begin
            Lo <= LO_IN;
        end
    end
end

endmodule
```

## Integración con Data Path

### Lectura (Fase EXECUTE)

```
Instruction Decoder extrae Rs, Rt de instrucción
    ↓
READ_REG_1 = Rs (5 bits)
READ_REG_2 = Rt (5 bits)
    ↓
Register File lee combinacionalmente
    ↓
READ_DATA_1 → ALU operando A
READ_DATA_2 → MUX ALU_B → ALU operando B (o Memory para SW)
```

### Escritura (Fase WRITEBACK)

```
MUX Writeback selecciona fuente:
    - ALU_RESULT (ADD/SUB/AND/OR/etc.)
    - MEMORY_DATA (LW)
    - HI_OUT (MFHI)
    - LO_OUT (MFLO)
    - PC+4 (para link en JAL, si existiera)
    ↓
WRITE_DATA = selección de MUX
    ↓
MUX Rd/Rt selecciona registro destino:
    - Rd (R-type: ADD, SUB, etc.)
    - Rt (I-type: ADDI, LW, etc.)
    ↓
WRITE_REG = Rd o Rt (5 bits)
    ↓
Control Unit activa REG_WRITE = 1
    ↓
En próximo flanco CLK: registers[WRITE_REG] <= WRITE_DATA
```

## Casos de Prueba

### Test 1: Lectura/Escritura Básica
```assembly
ADDI R1, R0, 10    # R1 = 10
ADDI R2, R0, 20    # R2 = 20
ADD R3, R1, R2     # R3 = R1 + R2 = 30
```

**Verificación**:
- R1 = 0x0000000A (10)
- R2 = 0x00000014 (20)
- R3 = 0x0000001E (30)

### Test 2: R0 Hardwired
```assembly
ADDI R0, R0, 100   # Intento escribir R0 (debe fallar)
ADD R1, R0, R0     # R1 = 0 + 0 = 0
```

**Verificación**:
- R0 = 0x00000000 (nunca cambia)
- R1 = 0x00000000

### Test 3: Hi/Lo con MULT
```assembly
ADDI R1, R0, 100
ADDI R2, R0, 200
MULT R1, R2        # Hi:Lo = 20,000
MFHI R3            # R3 = Hi = 0
MFLO R4            # R4 = Lo = 20,000
```

**Verificación**:
- R3 (Hi) = 0x00000000
- R4 (Lo) = 0x00004E20 (20,000)

### Test 4: Hi/Lo con DIV
```assembly
ADDI R1, R0, 17
ADDI R2, R0, 5
DIV R1, R2         # Lo = 3, Hi = 2
MFLO R3            # R3 = quotient = 3
MFHI R4            # R4 = remainder = 2
```

**Verificación**:
- R3 (Lo) = 0x00000003 (3)
- R4 (Hi) = 0x00000002 (2)

### Test 5: Lectura Dual Simultánea
```assembly
ADDI R1, R0, 10
ADDI R2, R0, 20
ADD R3, R1, R2     # Lee R1 y R2 simultáneamente
```

**Verificación**:
- Durante EXECUTE, READ_DATA_1 = 10 y READ_DATA_2 = 20 al mismo tiempo

## Análisis de Correctitud

### ✅ Implementación Correcta

Según análisis del código en s-mips.circ:
1. ✅ 32 registros implementados
2. ✅ R0 retorna siempre 0
3. ✅ Dual-port read funcional
4. ✅ Single-port write funcional
5. ✅ Hi/Lo implementados
6. ✅ Escritura controlada por CLK y REG_WRITE

### Puntos a Validar (Tests Pendientes)

1. ⚠️ **R0 no escribible**: Verificar que escrituras a R0 se ignoran completamente
2. ⚠️ **Hazard RAW**: Verificar si hay forwarding o si se requieren NOPs (Read-After-Write)
3. ⚠️ **R31 como SP**: Verificar modificación correcta en PUSH/POP/JR

## Hazards (Riesgos de Pipeline)

### Read-After-Write (RAW) Hazard

```assembly
ADDI R1, R0, 10    # Ciclo 1: R1 escrito en WRITEBACK
ADD R2, R1, R0     # Ciclo 2: R1 leído en EXECUTE

Si pipeline no tiene forwarding:
    ADD puede leer valor viejo de R1 (antes de ADDI)
```

**Solución**:
- **Forwarding**: Pasar WRITE_DATA directamente a READ_DATA si WRITE_REG == READ_REG
- **Stall**: Detener pipeline hasta que escritura complete
- **NOP**: Insertar instrucciones NOP entre escritura y lectura

**Estado en S-MIPS**: ⚠️ Verificar si implementa forwarding o requiere NOPs

## Performance

### Latencia de Lectura
- **0 ciclos** (combinacional)
- READ_DATA disponible inmediatamente después de cambiar READ_REG

### Latencia de Escritura
- **1 ciclo** (secuencial)
- Escritura efectiva en próximo flanco positivo de CLK

### Throughput
- **2 lecturas/ciclo** (dual-port)
- **1 escritura/ciclo** (single-port)

## Problemas Conocidos

**Estado actual**: ✅ COMPLETO Y FUNCIONAL

**No hay problemas críticos identificados**

### Mejoras Opcionales (No necesarias para aprobar)

1. **Forwarding interno**: Detectar RAW hazard y forward automáticamente
2. **Triple-port read**: Permitir leer 3 registros simultáneamente (no requerido en S-MIPS)
3. **Inicialización de registros**: Cargar valores iniciales en reset (opcional)

## Referencias

- [[Data Path]] - Integración en datapath
- [[ALU]] - Destino de READ_DATA, fuente de Hi/Lo
- [[Instruction Decoder]] - Genera READ_REG_1/2, WRITE_REG
- [[Control Unit]] - Genera REG_WRITE
- Documentación: `s-mips.pdf` - Arquitectura de registros
- Teoría: Patterson-Hennessy Cap. 4 - The Processor

---
**Última actualización**: 2025-12-09
**Estado**: ✅ IMPLEMENTADO Y FUNCIONAL
**Prioridad**: ✅ COMPLETADO
**Tests ejecutados**: ⚠️ Pendiente validación exhaustiva
