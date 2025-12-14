# Correcciones Críticas del Vault - Mecanismos de Implementación

**Fecha**: 2025-12-13
**Basado en**: S-MIPS_PROCESSOR_GUIDE.md y WORKFLOW_PROYECTO.md

---

## 🚨 CORRECCIÓN CRÍTICA #1: Modificación del Stack Pointer (SP/R31)

### ❌ Lo que el Vault decía (INCORRECTO)

El Vault mencionaba una señal `SP_INCREMENT` que el Branch Control genera y el Register File recibe. **ESTO ES INCORRECTO**.

### ✅ Mecanismo REAL (según S-MIPS_PROCESSOR_GUIDE.md)

**SP se modifica como CUALQUIER otro registro, usando los puertos normales de Register File**.

#### Para PUSH Rs (líneas 1454-1466 del GUIDE):
```
Cycle 7: Execute
         - Register File reads R1 (Rs - dato a guardar)
         - Register File reads R31 (SP actual)
         - ALU computes SP - 4
         - Register File writes to SP (nuevo SP)
Cycle 8: Control Unit detects memory write
Cycle 9: START write operation (usa nuevo SP como dirección)
```

**Configuración de señales**:
```
READ_REG_1 = Rs         # Leer dato a guardar
READ_REG_2 = 31         # Leer SP actual
ALU_OP = SUB            # Calcular SP - 4
ALU_B = 4               # Constante 4
WRITE_REG = 31          # Escribir a SP
WRITE_DATA = ALU_RESULT # Nuevo SP = SP - 4
REG_WRITE = 1           # Habilitar escritura
```

#### Para POP Rt:
```
Ciclo 1 - Leer memoria:
  READ_REG_2 = 31        # Leer SP
  ADDRESS = SP           # Dirección de memoria
  Memory[SP] → dato      # Leer de memoria
  WRITE_REG = Rt         # Escribir dato leído a Rt

Ciclo 2 - Actualizar SP:
  READ_REG_2 = 31        # Leer SP (otra vez)
  ALU: SP + 4            # Calcular nuevo SP
  WRITE_REG = 31         # Escribir a SP
  WRITE_DATA = ALU_RESULT
```

#### Para JR Rs (línea 1130):
```
JR Rs:
  READ_REG_1 = Rs        # Leer dirección de salto
  READ_REG_2 = 31        # Leer SP simultáneamente

  Branch Control:
    PC_NEXT = READ_DATA_1  (Rs)

  ALU:
    RESULT = READ_DATA_2 + 4  (SP + 4)

  Register File:
    WRITE_REG = 31
    WRITE_DATA = ALU_RESULT
    REG_WRITE = 1
```

**Clave**: NO existe señal especial `SP_INCREMENT`. SP usa WRITE_REG=31 y los puertos normales.

---

## 🚨 CORRECCIÓN CRÍTICA #2: Timing de PUSH/POP (Doble Ciclo)

### ❌ Lo que el Vault no especificaba

El Vault no menciona que PUSH/POP requieren **2 accesos a memoria** (doble ciclo).

### ✅ Timing REAL (línea 184 del GUIDE)

```
Stack operations (PUSH/POP): +2×(RT+WT) cycles (two memory accesses)
```

**Estado del Control Unit** (línea 152):
```
CHECK_STACK --> START_MEM_READ : PUSH/POP second cycle
```

**Para PUSH**:
1. Primer ciclo: Actualizar SP (SP = SP - 4)
2. Segundo ciclo: Escribir dato a Memory[SP_nuevo]

**Para POP**:
1. Primer ciclo: Leer dato de Memory[SP]
2. Segundo ciclo: Actualizar SP (SP = SP + 4)

---

## 🚨 CORRECCIÓN CRÍTICA #3: Señales Completas del Data Path

### ❌ Lo que faltaba en el Vault

Tabla completa de conexiones entre componentes con direcciones de señal.

### ✅ Conexiones REALES (del GUIDE diagrama líneas 336-396)

```
=== FLUJO DE DATOS COMPLETO ===

De Memory Control → Data Path:
  - INST_IN [32 bits] → Instruction Register

De Control Unit → Data Path:
  - LOAD_I [1 bit] → Instruction Register (cargar instrucción)
  - EN [1 bit] → Data Path Enable
  - CLK_DP [1 bit] → Clock

De Instruction Register → Instruction Decoder:
  - IR [32 bits] → entrada del decoder

De Instruction Decoder → Register File:
  - READ_REG_1 [5 bits] (Rs)
  - READ_REG_2 [5 bits] (Rt)
  - WRITE_REG [5 bits] (Rd o Rt según MUX)
  - REG_WRITE [1 bit]

De Register File → ALU:
  - READ_DATA_1 [32 bits] → Operando A
  - READ_DATA_2 [32 bits] → Operando B (o via MUX)

De ALU → Register File:
  - RESULT [32 bits] → MUX Writeback → WRITE_DATA
  - HI [32 bits] → HI_IN
  - LO [32 bits] → LO_IN

De ALU → Branch Control:
  - ZERO [1 bit]
  - NEGATIVE [1 bit]

De Branch Control → Program Counter:
  - PC_NEXT [32 bits]

De Register File → Memory Control:
  - READ_DATA_2 [32 bits] → Write Data (para SW/PUSH)

De ALU → Memory Control:
  - RESULT [32 bits] → Address (dirección efectiva)

De Data Path → Control Unit:
  - HALT [1 bit]
  - MC_NEEDED [1 bit] (indica si necesita acceso a memoria)
```

---

## 🚨 CORRECCIÓN CRÍTICA #4: Timing Detallado por Tipo de Instrucción

### ❌ Lo que faltaba

El Vault no documenta cuántos ciclos toma cada tipo de instrucción.

### ✅ Timing REAL (líneas 1388-1467)

**Mínimo ciclo de instrucción**: 4+ ciclos
1. START memoria
2. WAIT (RT cycles)
3. LOAD_I
4. EXECUTE

**Instrucción simple (ADD R1, R2, R3)**:
```
Cycle 1: Control Unit sends START
Cycles 2-4: Wait RT cycles (asume RT=3)
Cycle 5: END, instrucción arrive
Cycle 6: LOAD_I
Cycle 7: EXECUTE
  - Decoder decode
  - Register File reads R2, R3
  - ALU computes
  - Register File writes R1
Cycle 8: Fetch next

Total: 7-8 cycles
```

**Memory Load (LW R1, 0(R2))**:
```
Cycles 1-5: Fetch instruction
Cycle 6: LOAD_I
Cycle 7: Execute - ALU calcula dirección
Cycle 8: Control Unit detecta memory op
Cycle 9: START memory read
Cycles 10-12: Wait RT cycles
Cycle 13: Data arrives, write to R1
Cycle 14: Fetch next

Total: 13-14 cycles
```

**PUSH R1**:
```
Cycles 1-5: Fetch
Cycle 6: LOAD_I
Cycle 7: Execute - Actualizar SP (SP = SP - 4)
Cycle 8: Detect memory write
Cycle 9: START write
Cycles 10-11: Wait WT cycles
Cycle 12: Write complete
Cycle 13: Fetch next

Total: 12-13 cycles
```

**POP Rt**:
```
Cycles 1-5: Fetch
Cycle 6: LOAD_I
Cycle 7: Execute - nada aún
Cycle 8: START memory read (de SP)
Cycles 9-11: Wait RT cycles
Cycle 12: Data arrives → Rt
Cycle 13: Execute - Actualizar SP (SP = SP + 4)
Cycle 14: Fetch next

Total: 13-14 cycles
```

---

## 🚨 CORRECCIÓN CRÍTICA #5: Control Unit - Señales de Salida Completas

### ❌ Lo que faltaba

Lista completa de señales que Control Unit genera.

### ✅ Señales REALES (líneas 159-173)

**Control Unit → Memory Control**:
- `str_MC` (START) - Iniciar operación de memoria
- Recibe: `MC_END` - Fin de operación

**Control Unit → Data Path**:
- `load_I` (LOAD_I) - Cargar instrucción en IR
- `Exc_I` (EXECUTE) - Ejecutar instrucción
- `Push_Load` - Para operaciones de stack (segundo ciclo)
- `CLR` - Reset global

**Control Unit ← Data Path**:
- `HALT` - Detener ejecución
- `MC_needed` - Necesita acceso a memoria

**Señales que faltan en Vault**:
- ❌ `REG_WRITE` - Enable escritura Register File (generada por Inst Decoder, no CU directamente)
- ❌ `HI_WRITE`, `LO_WRITE` - Enable Hi/Lo

---

## 🚨 CORRECCIÓN CRÍTICA #6: Data Path - Multiplexores Detallados

### ❌ Lo que faltaba

Detalles de TODOS los multiplexores y sus selectores.

### ✅ Multiplexores REALES

#### MUX ALU_B (Selección operando B)
```verilog
Selector: ALU_SRC [1 bit]

ALU_SRC = 0 → ALU_B = READ_DATA_2 (Rt)
ALU_SRC = 1 → ALU_B = SignExt(immediate)

Usado por:
- R-type: ALU_SRC = 0 (ADD, SUB, etc.)
- I-type arithmetic: ALU_SRC = 1 (ADDI, etc.)
```

#### MUX Rd/Rt (Selección registro destino)
```verilog
Selector: REG_DST [1 bit]

REG_DST = 0 → WRITE_REG = Rt (I-type: ADDI, LW)
REG_DST = 1 → WRITE_REG = Rd (R-type: ADD, SUB)

Excepción para PUSH/POP/JR:
  WRITE_REG = 31 (SP) directamente
```

#### MUX Writeback (Selección dato a escribir) - 8 entradas
```verilog
Selector: WB_SEL [3 bits]

000 → WRITE_DATA = ALU_RESULT
001 → WRITE_DATA = MEMORY_DATA
010 → WRITE_DATA = HI_OUT
011 → WRITE_DATA = LO_OUT
100 → WRITE_DATA = PC_PLUS_4
101 → WRITE_DATA = RND_VALUE
110 → WRITE_DATA = KBD_VALUE
111 → WRITE_DATA = IMMEDIATE

Usado por:
- Operaciones ALU: WB_SEL = 000
- LW/POP: WB_SEL = 001
- MFHI: WB_SEL = 010
- MFLO: WB_SEL = 011
- JAL (si existe): WB_SEL = 100
- RND: WB_SEL = 101
- KBD: WB_SEL = 110
```

---

## 🚨 CORRECCIÓN CRÍTICA #7: Register File - Puertos Exactos

### ❌ Lo que faltaba

Especificación exacta de TODOS los puertos y su función.

### ✅ Puertos REALES (líneas 621-697)

**Entradas de Lectura** (Combinacional):
```
READ_REG_1 [5 bits] - Dirección registro Rs
READ_REG_2 [5 bits] - Dirección registro Rt
```

**Salidas de Lectura** (Combinacional):
```
READ_DATA_1 [32 bits] - Contenido de Rs
READ_DATA_2 [32 bits] - Contenido de Rt
```

**Entradas de Escritura** (Secuencial, flanco positivo):
```
WRITE_REG [5 bits] - Dirección registro destino
WRITE_DATA [32 bits] - Dato a escribir
REG_WRITE [1 bit] - Enable de escritura
CLK [1 bit] - Reloj (escritura en rising edge)
```

**Hi/Lo - Entradas**:
```
HI_IN [32 bits] - Valor para Hi
LO_IN [32 bits] - Valor para Lo
HI_WRITE [1 bit] - Enable escritura Hi
LO_WRITE [1 bit] - Enable escritura Lo
```

**Hi/Lo - Salidas**:
```
HI_OUT [32 bits] - Contenido de Hi
LO_OUT [32 bits] - Contenido de Lo
```

**Especial: R0**
- NO es un registro real
- Implementación: Constante 0 en multiplexor de lectura
- Escrituras a R0 se ignoran (WRITE_REG=0 no activa demux)

---

## 📋 Resumen de Correcciones para el Vault

1. ✅ Actualizar Register File.md con mecanismo real de SP (usar puertos normales)
2. ✅ Actualizar Data Path.md con tabla completa de conexiones
3. ✅ Actualizar Control Unit.md con señales completas y timing
4. ✅ Añadir documento "Timing por Instrucción" con ciclos detallados
5. ✅ Actualizar Instruction Decoder.md con multiplexores y selectores
6. ✅ Crear diagrama de flujo de señales completo
7. ✅ Añadir sección "Doble Ciclo PUSH/POP" en Memory Control

---

**Con estas correcciones, el Vault será 100% funcional para implementar el procesador.**
