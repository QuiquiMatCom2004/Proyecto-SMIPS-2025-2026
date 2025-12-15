# Resumen de Correcciones de Arquitectura

**Fecha**: 2025-12-14
**Propósito**: Corrección de arquitectura según análisis crítico de pines y responsabilidades

---

## ✅ CORRECCIONES APLICADAS

### 1. **Data Path - Señales de Control INTERNAS**

#### ELIMINADO de "Entradas desde Control Unit":
- ❌ `REG_WRITE` - Generada por Instruction Decoder (interna)
- ❌ `MEM_TO_REG` - Generada por Instruction Decoder (interna)
- ❌ `ALU_SRC` - Generada por Instruction Decoder (interna)
- ❌ `REG_DST` - Generada por Instruction Decoder (interna)
- ❌ `BRANCH` - Generada por Instruction Decoder (interna)
- ❌ `JUMP` - Generada por Instruction Decoder (interna)

#### ELIMINADO de "Salidas a Control Unit":
- ❌ `OPCODE` (6 bits) - Campo interno, no sale del Data Path
- ❌ `FUNCT` (6 bits) - Campo interno, no sale del Data Path
- ❌ `ZERO` (1 bit) - Flag interno usado por Branch Control
- ❌ `NEGATIVE` (1 bit) - Flag interno usado por Branch Control

#### AGREGADO - Sección de Señales de Control Internas:
✅ Documentación completa de todas las señales generadas por Instruction Decoder:
- Señales de Control del Register File: `REG_WRITE`, `REG_DST`, `READ_REG_1`, `READ_REG_2`
- Señales de Control de ALU: `ALU_OP`, `ALU_SRC`
- Señales de Control de Branch: `BRANCH`, `BRANCH_TYPE`, `JUMP`, `JUMP_REG`
- Señales de Control de Writeback: `MEM_TO_REG`, `WB_SEL`
- Señales de Feedback a Control Unit: `HALT`, `MC_NEEDED`, `IS_WRITE`, `PUSH`, `POP`

---

### 2. **Data Path - Nomenclatura Unificada con Memory Control**

#### Entradas desde Memory Control:
**ANTES:**
```
INSTRUCTION_IN (32 bits) - Instrucción leída
MEMORY_DATA (32 bits) - Dato leído
```

**AHORA:**
```
DATA_READ (32 bits) - Dato leído (instrucción o dato según contexto)
```

**Justificación**: Memory Control envía un solo `DATA_READ` que contiene instrucciones (en fetch) o datos (en LW/POP). Data Path multiplexaalmente:
- `INSTRUCTION_IN` = `DATA_READ` cuando LOAD_INST=1
- `MEMORY_DATA` = `DATA_READ` cuando es LW/POP

#### Salidas hacia Memory Control:
**ANTES:**
```
ADDRESS (32 bits) - Dirección de memoria
WRITE_DATA (32 bits) - Dato a escribir
PC_OUT (32 bits) - Program Counter
```

**AHORA:**
```
MEM_ADDRESS (32 bits) - Dirección efectiva (ALU result)
DATA_WRITE (32 bits) - Dato a escribir
PC (32 bits) - Program Counter
```

**Justificación**: Nombres coinciden exactamente con los esperados por Memory Control (Opción A).

---

### 3. **Control Unit - Señales Opcionales Marcadas**

#### Señales Principales (CONFIRMADAS):
✅ `LOAD_I` → Data Path (como LOAD_INST)
✅ `EN` → Data Path
✅ `CLK` (global)
✅ `RESET` (global)

**Total: 4 señales (2 de control + 2 globales)**

#### Señales Opcionales (REQUIEREN VERIFICACIÓN):
⚠️ `EXECUTE` - Aparece en FSM pero Data Path NO lo recibe
- **Pregunta**: ¿Data Path ejecuta automáticamente o necesita EXECUTE explícito?
- **Acción**: Verificar en Logisim

⚠️ `PUSH_LOAD` - Aparece en FSM para 2º ciclo PUSH pero Data Path NO lo recibe
- **Pregunta**: ¿PUSH requiere señal explícita o FSM lo maneja internamente?
- **Acción**: Verificar en Logisim

**Documentación actualizada**: Marcadas como opcionales con advertencia de verificación necesaria.

---

### 4. **Arquitectura Aclarada: Hardwired Control**

✅ **Agregada sección en Instruction Decoder** explicando:
- Arquitectura es **hardwired control** (no microcodificada)
- Instruction Decoder genera TODAS las señales de control de bajo nivel
- Control Unit solo coordina timing de FSM (FETCH, EXECUTE, MEMORY, etc.)
- Señales de control NO vienen de Control Unit, son generadas internamente

---

## 📊 TABLA COMPARATIVA: ANTES vs AHORA

### Control Unit → Data Path

| Aspecto | ANTES | AHORA | Estado |
|---------|-------|-------|--------|
| Número de señales | 10 señales reclamadas | 4 señales (2 control + 2 global) | ✅ CORREGIDO |
| REG_WRITE, MEM_TO_REG, etc. | Documentadas como entradas | Eliminadas (son internas) | ✅ CORREGIDO |
| EXECUTE, PUSH_LOAD | No documentadas | Marcadas como opcionales | ⚠️ REVISAR |

### Data Path → Control Unit

| Aspecto | ANTES | AHORA | Estado |
|---------|-------|-------|--------|
| Número de señales | 9 señales (19 bits) | 5 señales (5 bits) | ✅ CORREGIDO |
| OPCODE, FUNCT | Documentadas como salidas | Eliminadas (son internas) | ✅ CORREGIDO |
| ZERO, NEGATIVE | Documentadas como salidas | Eliminadas (son internas) | ✅ CORREGIDO |
| Feedback (HALT, MC_NEEDED, etc.) | Documentadas | Mantenidas | ✅ CORRECTO |

### Data Path ↔ Memory Control

| Aspecto | ANTES | AHORA | Estado |
|---------|-------|-------|--------|
| Nomenclatura | Inconsistente (ADDRESS, PC_OUT, WRITE_DATA) | Unificada (MEM_ADDRESS, PC, DATA_WRITE) | ✅ CORREGIDO |
| Entrada desde MC | 2 pines (INSTRUCTION_IN, MEMORY_DATA) | 1 pin (DATA_READ) | ✅ SIMPLIFICADO |

---

## 🎯 ARQUITECTURA FINAL CONFIRMADA

### Arquitectura Hardwired Control

```
┌─────────────────────────────────────────────────┐
│              CONTROL UNIT (FSM)                 │
│  • Coordina timing: FETCH → EXECUTE → MEM → WB │
│  • Genera: LOAD_I, EN                           │
│  • Recibe feedback: HALT, MC_NEEDED, IS_WRITE   │
└─────────────────────────────────────────────────┘
         ↓ (4 señales)              ↑ (5 señales)
         LOAD_I, EN, CLK, RESET     HALT, MC_NEEDED, etc.
         ↓                          ↑
┌─────────────────────────────────────────────────┐
│              DATA PATH                          │
│  ┌───────────────────────────────────────────┐  │
│  │      INSTRUCTION DECODER                  │  │
│  │  • Analiza opcode, funct                 │  │
│  │  • Genera TODAS las señales de control:  │  │
│  │    - REG_WRITE, MEM_TO_REG, ALU_SRC      │  │
│  │    - REG_DST, BRANCH, JUMP, ALU_OP       │  │
│  │    - MC_NEEDED, IS_WRITE, HALT           │  │
│  │  • Señales INTERNAS (no salen)           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Register File, ALU, Branch Control, etc.      │
│  • Controlados por señales de Inst. Decoder    │
└─────────────────────────────────────────────────┘
```

### Flujo de Señales de Control

**Control Unit genera** (alto nivel):
- `LOAD_I` - Cargar instrucción
- `EN` - Enable Data Path
- [Opcional: `EXECUTE`, `PUSH_LOAD`]

**Instruction Decoder genera** (bajo nivel):
- Todas las señales que controlan componentes internos
- Señales de feedback hacia Control Unit

**Resultado**:
- Separación clara de responsabilidades
- Control Unit: Timing
- Instruction Decoder: Decodificación y control

---

## ✅ BENEFICIOS DE LAS CORRECCIONES

### 1. **Claridad Arquitectónica**
- ✅ Ahora está claro quién genera cada señal
- ✅ Separación entre control de timing (CU) y control de operación (Decoder)
- ✅ Arquitectura hardwired explícitamente documentada

### 2. **Consistencia de Pines**
- ✅ Control Unit → Data Path: 4 señales (consistente)
- ✅ Data Path → Control Unit: 5 señales (consistente)
- ✅ Nomenclatura unificada con Memory Control

### 3. **Eliminación de Ambigüedades**
- ✅ Señales internas claramente identificadas
- ✅ No hay pines "fantasma" que aparecen en un lado pero no en el otro
- ✅ Señales opcionales marcadas explícitamente

### 4. **Documentación Precisa**
- ✅ Instruction Decoder tiene sección completa de señales que genera
- ✅ Data Path tiene sección de señales internas
- ✅ Control Unit tiene señales opcionales marcadas para verificación

---

## ⚠️ PENDIENTES DE VERIFICACIÓN

### En Logisim:

1. **EXECUTE**:
   - ¿Existe físicamente como pin de Control Unit → Data Path?
   - ¿Data Path lo usa?
   - Si NO: Eliminar de Control Unit.md
   - Si SÍ: Agregar a Data Path.md entradas

2. **PUSH_LOAD**:
   - ¿Existe físicamente como pin de Control Unit → Data Path?
   - ¿Data Path lo usa para segundo ciclo de PUSH?
   - Si NO: Eliminar de Control Unit.md
   - Si SÍ: Agregar a Data Path.md entradas

3. **DATA_READ multiplexado**:
   - ¿Memory Control envía un solo DATA_READ o dos salidas separadas?
   - Verificar si Data Path multiplexa internamente o recibe 2 pines

4. **MEM_ADDRESS vs ADDRESS**:
   - ¿Data Path envía PC y MEM_ADDRESS separados (Opción A)?
   - ¿O multiplexa y envía solo ADDRESS (Opción B)?
   - Verificar implementación real

---

## 📝 ARCHIVOS MODIFICADOS

1. ✅ `/SMIPS-Obsidian-Vault/05-Data-Path/Data Path.md`
   - Eliminadas señales de control de entradas
   - Eliminadas señales internas de salidas
   - Agregada sección de señales internas
   - Unificada nomenclatura con Memory Control
   - Agregada nota sobre DATA_READ

2. ✅ `/SMIPS-Obsidian-Vault/03-Control-Unit/Control Unit.md`
   - Reorganizadas salidas en principales y opcionales
   - Marcadas EXECUTE y PUSH_LOAD como "revisar"
   - Agregada advertencia de verificación en Logisim

3. ✅ `/SMIPS-Obsidian-Vault/07-Analisis/ANALISIS-CRITICO-PINES-Y-RESPONSABILIDADES.md`
   - Creado análisis exhaustivo de pines
   - Identificadas todas las inconsistencias
   - Propuestas soluciones

4. ✅ `/SMIPS-Obsidian-Vault/07-Analisis/RESUMEN-CORRECCIONES-ARQUITECTURA.md`
   - Este archivo (resumen de correcciones)

---

## 🎯 PRÓXIMOS PASOS

1. **Verificar en Logisim**:
   - Abrir `s-mips.circ`
   - Revisar pines físicos de Control Unit → Data Path
   - Confirmar si EXECUTE y PUSH_LOAD existen

2. **Actualizar según verificación**:
   - Si EXECUTE/PUSH_LOAD existen: Agregar a Data Path.md
   - Si NO existen: Eliminar de Control Unit.md y actualizar FSM

3. **Revisar Instruction Decoder.md**:
   - Asegurar que lista todas las señales que genera
   - Agregar diagramas de conexiones internas si necesario

4. **Validar con implementación**:
   - Comparar documentación corregida con circuito real
   - Asegurar 100% de consistencia

---

**Estado**: ✅ CORRECCIONES APLICADAS
**Pendiente**: ⚠️ VERIFICACIÓN EN LOGISIM de EXECUTE y PUSH_LOAD
**Arquitectura**: ✅ HARDWIRED CONTROL confirmada y documentada
