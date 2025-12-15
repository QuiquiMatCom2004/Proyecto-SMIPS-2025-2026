# Análisis Crítico de Pines y Responsabilidades

**Fecha**: 2025-12-14
**Propósito**: Identificar inconsistencias en conteo de pines y responsabilidades arquitectónicas

---

## 🔴 PROBLEMAS CRÍTICOS ENCONTRADOS

### 1. INCONSISTENCIA MASIVA: Control Unit ↔ Data Path

#### Control Unit → Data Path (según Control Unit.md)

**Control Unit dice que ENVÍA:**
1. `LOAD_I` (1 bit)
2. `EXECUTE` (1 bit)
3. `EN` (1 bit)
4. `PUSH_LOAD` (1 bit)
5. `RESET` (1 bit)

**Total: 5 salidas**

#### Control Unit → Data Path (según Data Path.md)

**Data Path dice que RECIBE desde Control Unit:**
1. `LOAD_INST` (1 bit) - mismo que LOAD_I
2. `EN` (1 bit)
3. `REG_WRITE` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
4. `MEM_TO_REG` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
5. `ALU_SRC` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
6. `REG_DST` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
7. `BRANCH` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
8. `JUMP` (1 bit) ❌ **NO ESTÁ EN CONTROL UNIT**
9. `CLK` (1 bit) - es global, no de Control Unit
10. `RESET` (1 bit)

**Total: 10 entradas (6 NO coinciden)**

#### Pines en Control Unit que NO están en Data Path:
- `EXECUTE` ❌ **Data Path NO lo recibe**
- `PUSH_LOAD` ❌ **Data Path NO lo recibe**

#### Pines en Data Path que NO están en Control Unit:
- `REG_WRITE` ❌ **Control Unit NO lo envía**
- `MEM_TO_REG` ❌ **Control Unit NO lo envía**
- `ALU_SRC` ❌ **Control Unit NO lo envía**
- `REG_DST` ❌ **Control Unit NO lo envía**
- `BRANCH` ❌ **Control Unit NO lo envía**
- `JUMP` ❌ **Control Unit NO lo envía**

---

### 2. Data Path → Control Unit

#### Data Path → Control Unit (según Data Path.md)

**Data Path dice que ENVÍA:**
1. `HALT` (1 bit)
2. `MC_NEEDED` (1 bit)
3. `IS_WRITE` (1 bit)
4. `PUSH` (1 bit)
5. `POP` (1 bit)
6. `OPCODE` (6 bits)
7. `FUNCT` (6 bits)
8. `ZERO` (1 bit)
9. `NEGATIVE` (1 bit)

**Total: 9 salidas (19 bits)**

#### Data Path → Control Unit (según Control Unit.md)

**Control Unit dice que RECIBE:**
1. `HALT` (1 bit) ✅
2. `MC_NEEDED` (1 bit) ✅
3. `IS_WRITE` (1 bit) ✅
4. `PUSH` (1 bit) ✅
5. `POP` (1 bit) ✅

**Total: 5 entradas**

#### Pines en Data Path que NO están en Control Unit:
- `OPCODE` (6 bits) ❌ **Control Unit NO lo recibe**
- `FUNCT` (6 bits) ❌ **Control Unit NO lo recibe**
- `ZERO` (1 bit) ❌ **Control Unit NO lo recibe**
- `NEGATIVE` (1 bit) ❌ **Control Unit NO lo recibe**

**Nota**: Estos pines probablemente son INTERNOS de Data Path, no salidas hacia Control Unit.

---

### 3. Control Unit ↔ Memory Control

#### Control Unit → Memory Control (según Control Unit.md)

**Control Unit dice que ENVÍA:**
1. `START_MC` (1 bit)
2. `R/W` (1 bit)

**Total: 2 salidas**

#### Control Unit → Memory Control (según Memory Control.md)

**Memory Control dice que RECIBE:**
1. `START_MC` (1 bit) ✅
2. `R/W` (1 bit) ✅
3. `CLK` (1 bit) - es global
4. `RESET` (1 bit) - es global

**Total: 4 entradas (2 son globales)**

✅ **CONSISTENTE** (ignorando señales globales)

---

#### Memory Control → Control Unit (según Memory Control.md)

**Memory Control dice que ENVÍA:**
1. `MC_END` (1 bit)

**Total: 1 salida**

#### Memory Control → Control Unit (según Control Unit.md)

**Control Unit dice que RECIBE:**
1. `MC_END` (1 bit) ✅

**Total: 1 entrada**

✅ **CONSISTENTE**

---

### 4. Data Path ↔ Memory Control

#### Data Path → Memory Control (según Data Path.md)

**Data Path dice que ENVÍA:**
1. `ADDRESS` (32 bits)
2. `WRITE_DATA` (32 bits)
3. `PC_OUT` (32 bits)

**Total: 3 salidas (96 bits)**

#### Data Path → Memory Control (según Memory Control.md - Opción A)

**Memory Control dice que RECIBE:**
1. `PC` (32 bits) - ¿es PC_OUT?
2. `MEM_ADDRESS` (32 bits) - ¿es ADDRESS?
3. `DATA_WRITE` (32 bits) - ¿es WRITE_DATA?

**Total: 3 entradas (96 bits)**

⚠️ **PARCIALMENTE CONSISTENTE** (nomenclatura diferente)

---

#### Memory Control → Data Path (según Memory Control.md)

**Memory Control dice que ENVÍA:**
1. `DATA_READ` (32 bits)
2. `BLOCK_OUT` (128 bits) - solo para cachés

**Total: 2 salidas (160 bits)**

#### Memory Control → Data Path (según Data Path.md)

**Data Path dice que RECIBE:**
1. `INSTRUCTION_IN` (32 bits)
2. `MEMORY_DATA` (32 bits)

**Total: 2 entradas (64 bits)**

❌ **INCONSISTENTE en nombres y propósito**:
- `INSTRUCTION_IN` ¿es `DATA_READ` cuando se hace fetch?
- `MEMORY_DATA` ¿es `DATA_READ` cuando se hace LW?
- `BLOCK_OUT` no aparece en Data Path (es para cachés)

---

## 🏗️ PROBLEMA ARQUITECTÓNICO FUNDAMENTAL

### ¿Quién genera las señales de control?

Hay una **confusión arquitectónica crítica** sobre quién genera qué señales.

#### En MIPS Tradicional:

```
┌─────────────────────────────────────────────────┐
│              CONTROL UNIT (FSM)                 │
│  • Estados: FETCH, DECODE, EXECUTE, MEM, WB    │
│  • Genera: LOAD_I, EXECUTE, START_MC           │
│  • NO genera: REG_WRITE, ALU_OP, etc.          │
└─────────────────────────────────────────────────┘
              ↓                      ↑
        LOAD_I, EXECUTE        HALT, MC_NEEDED
              ↓                      ↑
┌─────────────────────────────────────────────────┐
│              DATA PATH                          │
│  ┌───────────────────────────────────────────┐  │
│  │      INSTRUCTION DECODER                  │  │
│  │  • Analiza opcode, funct                 │  │
│  │  • Genera: REG_WRITE, MEM_TO_REG,        │  │
│  │    ALU_SRC, REG_DST, BRANCH, JUMP,       │  │
│  │    ALU_OP, MC_NEEDED, IS_WRITE           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Register File, ALU, Branch Control, etc.      │
└─────────────────────────────────────────────────┘
```

#### Según la documentación actual:

**Control Unit.md dice:**
- Control Unit es solo FSM de estados
- NO menciona que genere REG_WRITE, ALU_OP, etc.
- Solo genera: LOAD_I, EXECUTE, EN, PUSH_LOAD, RESET

**Data Path.md dice:**
- Data Path RECIBE: REG_WRITE, MEM_TO_REG, ALU_SRC, REG_DST, BRANCH, JUMP
- Pero Control Unit NO las envía ❌

**Instruction Decoder** (dentro de Data Path):
- Genera: ALU_OP, señales de control
- Debería generar TODAS las señales de control de bajo nivel

---

## 🔍 ANÁLISIS DE RESPONSABILIDADES

### Señales que DEBE generar Instruction Decoder (dentro de Data Path):

Estas señales son **INTERNAS** de Data Path, generadas por Instruction Decoder:

1. ✅ `ALU_OP` (4-6 bits) - Operación de ALU
2. ✅ `REG_WRITE` (1 bit) - Escribir en Register File
3. ✅ `MEM_TO_REG` (1 bit) - Seleccionar memoria para writeback
4. ✅ `ALU_SRC` (1 bit) - Usar immediate
5. ✅ `REG_DST` (1 bit) - Destino Rd o Rt
6. ✅ `BRANCH` (1 bit) - Es instrucción branch
7. ✅ `JUMP` (1 bit) - Es instrucción jump
8. ✅ `MC_NEEDED` (1 bit) - Necesita memoria (LW/SW/PUSH/POP)
9. ✅ `IS_WRITE` (1 bit) - Tipo de operación memoria
10. ✅ `HALT` (1 bit) - Instrucción HALT
11. ✅ `PUSH` (1 bit) - Instrucción PUSH
12. ✅ `POP` (1 bit) - Instrucción POP
13. ✅ `WB_SEL` (3 bits) - Selector de writeback

### Señales que DEBE generar Control Unit (FSM):

Estas señales son de **CONTROL DE ALTO NIVEL**:

1. ✅ `LOAD_I` / `LOAD_INST` (1 bit) - Cargar instrucción en IR
2. ✅ `EXECUTE` (1 bit) - Habilitar ejecución (si se usa)
3. ✅ `EN` (1 bit) - Enable de Data Path
4. ✅ `START_MC` (1 bit) - Iniciar Memory Control
5. ✅ `R/W` (1 bit) - Tipo de operación memoria (coordinado con IS_WRITE de Data Path)
6. ❓ `PUSH_LOAD` (1 bit) - ¿Realmente necesario?

### Señales GLOBALES (no generadas por ningún componente específico):

1. `CLK` - Reloj del sistema
2. `RESET` - Reset sincrónico

---

## 🚨 PINES PROBLEMÁTICOS ESPECÍFICOS

### 1. `EXECUTE` - ¿Necesario?

**Control Unit.md** dice que genera `EXECUTE`.
**Data Path.md** NO lo recibe.

**Pregunta**: ¿Data Path necesita una señal EXECUTE explícita, o simplemente ejecuta cuando hay instrucción válida y EN=1?

**Recomendación**:
- Si Data Path ejecuta automáticamente cuando `EN=1` y hay instrucción cargada → **ELIMINAR `EXECUTE`**
- Si necesita señal explícita → **AGREGAR `EXECUTE` a entradas de Data Path**

---

### 2. `PUSH_LOAD` - ¿Necesario?

**Control Unit.md** dice que genera `PUSH_LOAD` para 2º ciclo de PUSH.
**Data Path.md** NO lo recibe.

**Pregunta**: ¿Cómo Data Path sabe que está en el 2º ciclo de PUSH?

**Análisis**:
- PUSH requiere 2 ciclos:
  1. Escribir Rs en memoria[SP-4]
  2. (Potencialmente) actualizar SP

**Recomendación**:
- Si Control Unit necesita señalizar 2º ciclo → **AGREGAR `PUSH_LOAD` a entradas de Data Path**
- Si Data Path maneja PUSH internamente en 1 ciclo → **ELIMINAR `PUSH_LOAD` de Control Unit**

---

### 3. `OPCODE`, `FUNCT`, `ZERO`, `NEGATIVE` - ¿Salidas de Data Path?

**Data Path.md** dice que ENVÍA `OPCODE`, `FUNCT`, `ZERO`, `NEGATIVE` a Control Unit.
**Control Unit.md** NO los recibe.

**Análisis**:
- `OPCODE` y `FUNCT` son campos de la instrucción
- `ZERO` y `NEGATIVE` son flags de ALU

**Pregunta**: ¿Control Unit necesita estos valores para decisiones de FSM?

**Arquitecturas posibles**:

**Opción A (MIPS tradicional - microcodificado)**:
- Control Unit recibe OPCODE y genera señales de control
- Instruction Decoder NO existe como componente separado
- ❌ NO parece ser este caso

**Opción B (MIPS hardwired control)**:
- Instruction Decoder (dentro de Data Path) analiza OPCODE/FUNCT
- Genera todas las señales de control internamente
- Control Unit solo coordina timing (FETCH, EXECUTE, MEM, WB)
- ✅ Parece ser este caso

**Recomendación**:
- Si Control Unit NO necesita OPCODE/FUNCT/ZERO/NEGATIVE → **SON INTERNOS de Data Path**
- Solo exportar: HALT, MC_NEEDED, IS_WRITE, PUSH, POP

---

### 4. `REG_WRITE`, `MEM_TO_REG`, `ALU_SRC`, `REG_DST`, `BRANCH`, `JUMP` - ¿De dónde vienen?

**Data Path.md** dice que RECIBE estas señales de Control Unit.
**Control Unit.md** NO las envía.

**Análisis**:
- Estas son señales de control de bajo nivel
- Dependen del opcode/funct de la instrucción
- En MIPS hardwired, las genera Instruction Decoder

**Problema**: Hay una **inconsistencia fundamental**.

**Dos posibles soluciones**:

**Solución 1: Instruction Decoder genera señales (RECOMENDADO)**
- Instruction Decoder (dentro de Data Path) genera todas estas señales
- Son **INTERNAS** de Data Path
- Control Unit NO las envía
- **ELIMINAR** estas entradas de "Entradas desde Control Unit" en Data Path.md

**Solución 2: Control Unit genera señales (microcodificado)**
- Control Unit recibe OPCODE/FUNCT de Data Path
- Control Unit tiene ROM/lógica para generar señales de control
- Control Unit envía REG_WRITE, ALU_OP, etc. a Data Path
- **AGREGAR** estas salidas en Control Unit.md

**Recomendación**: **Solución 1** (Instruction Decoder interno)

---

## 📊 TABLA DE CORRECCIONES NECESARIAS

### Control Unit.md

| Acción | Pin | Justificación |
|--------|-----|---------------|
| ❓ REVISAR | `EXECUTE` | ¿Data Path lo necesita? Si no → ELIMINAR |
| ❓ REVISAR | `PUSH_LOAD` | ¿Data Path lo necesita? Si no → ELIMINAR |
| ❌ NO AGREGAR | `REG_WRITE`, `MEM_TO_REG`, `ALU_SRC`, `REG_DST`, `BRANCH`, `JUMP` | Son INTERNOS de Data Path |

### Data Path.md

| Acción | Pin | Justificación |
|--------|-----|---------------|
| ❌ ELIMINAR de entradas | `REG_WRITE` | Generado por Instruction Decoder (interno) |
| ❌ ELIMINAR de entradas | `MEM_TO_REG` | Generado por Instruction Decoder (interno) |
| ❌ ELIMINAR de entradas | `ALU_SRC` | Generado por Instruction Decoder (interno) |
| ❌ ELIMINAR de entradas | `REG_DST` | Generado por Instruction Decoder (interno) |
| ❌ ELIMINAR de entradas | `BRANCH` | Generado por Instruction Decoder (interno) |
| ❌ ELIMINAR de entradas | `JUMP` | Generado por Instruction Decoder (interno) |
| ❓ AGREGAR entrada (si necesario) | `EXECUTE` | Si Control Unit lo genera |
| ❓ AGREGAR entrada (si necesario) | `PUSH_LOAD` | Si Control Unit lo genera |
| ❌ ELIMINAR de salidas | `OPCODE` | Interno, no sale a Control Unit |
| ❌ ELIMINAR de salidas | `FUNCT` | Interno, no sale a Control Unit |
| ❌ ELIMINAR de salidas | `ZERO` | Interno (o solo para Branch Control interno) |
| ❌ ELIMINAR de salidas | `NEGATIVE` | Interno (o solo para Branch Control interno) |

### Memory Control.md

| Acción | Pin | Justificación |
|--------|-----|---------------|
| ✅ ACLARAR nomenclatura | `PC` vs `PC_OUT` | Mismo pin, nombres diferentes |
| ✅ ACLARAR nomenclatura | `MEM_ADDRESS` vs `ADDRESS` | Mismo pin, nombres diferentes |
| ✅ ACLARAR nomenclatura | `DATA_WRITE` vs `WRITE_DATA` | Mismo pin, nombres diferentes |
| ✅ ACLARAR nomenclatura | `DATA_READ` vs `INSTRUCTION_IN`/`MEMORY_DATA` | DATA_READ se usa para ambos según contexto |

---

## 🎯 ARQUITECTURA RECOMENDADA

### Señales Control Unit ↔ Data Path

```
Control Unit ────→ Data Path
  • LOAD_I (cargar instrucción)
  • EN (enable general)
  • [EXECUTE] (si necesario)
  • [PUSH_LOAD] (si necesario para 2º ciclo PUSH)
  • RESET (global)
  • CLK (global)

Data Path ────→ Control Unit
  • HALT (instrucción HALT detectada)
  • MC_NEEDED (necesita acceso a memoria)
  • IS_WRITE (tipo de acceso: 0=read, 1=write)
  • PUSH (instrucción PUSH, para FSM)
  • POP (instrucción POP, para FSM)
```

### Señales INTERNAS de Data Path (Instruction Decoder)

```
Instruction Decoder (dentro de Data Path):
  • REG_WRITE → Register File
  • MEM_TO_REG → MUX Writeback
  • ALU_SRC → MUX ALU_B
  • REG_DST → MUX Rd/Rt
  • BRANCH → Branch Control
  • JUMP → Branch Control
  • ALU_OP → ALU
  • WB_SEL → MUX Writeback
  • [Todas las demás señales de control interno]
```

---

## ✅ PRÓXIMOS PASOS

1. **Decisión arquitectónica**: ¿Instruction Decoder genera señales de control internamente? (RECOMENDADO: SÍ)

2. **Si SÍ (Solución 1 - RECOMENDADO)**:
   - ELIMINAR de Data Path.md entradas: REG_WRITE, MEM_TO_REG, ALU_SRC, REG_DST, BRANCH, JUMP
   - ELIMINAR de Data Path.md salidas: OPCODE, FUNCT, ZERO, NEGATIVE (son internos)
   - ACLARAR en Instruction Decoder.md que genera TODAS las señales de control
   - REVISAR si EXECUTE y PUSH_LOAD son necesarios

3. **Si NO (Solución 2 - microcodificado)**:
   - AGREGAR a Control Unit.md salidas: REG_WRITE, MEM_TO_REG, ALU_SRC, REG_DST, BRANCH, JUMP, ALU_OP
   - AGREGAR a Control Unit.md entradas: OPCODE, FUNCT
   - MODIFICAR Control Unit para incluir ROM/lógica de control

4. **Revisar nomenclatura**:
   - Unificar: LOAD_I = LOAD_INST
   - Unificar: PC_OUT = PC
   - Unificar: ADDRESS = MEM_ADDRESS
   - Unificar: WRITE_DATA = DATA_WRITE
   - Aclarar: DATA_READ se usa como INSTRUCTION_IN (fetch) o MEMORY_DATA (LW)

---

**Estado**: ⚠️ REQUIERE DECISIÓN ARQUITECTÓNICA URGENTE
**Prioridad**: 🔴 CRÍTICA - Afecta toda la implementación
**Recomendación**: Adoptar **Solución 1** (Instruction Decoder genera señales internamente)
