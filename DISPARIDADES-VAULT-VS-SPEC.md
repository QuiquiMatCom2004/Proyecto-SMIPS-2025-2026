# Disparidades entre Vault y Especificación Real

**Fecha**: 2025-12-13
**Análisis**: Vault vs S-MIPS_PROCESSOR_GUIDE.md y especificación del proyecto
**Objetivo**: Identificar qué falta en el Vault para que sea funcionalmente completo

---

## 🎯 Pregunta Crítica

**"¿Podría alguien implementar un procesador S-MIPS funcional SOLO con el Vault?"**

**Respuesta**: ❌ **NO - Faltan detalles críticos de implementación**

---

## 🚨 DISPARIDAD CRÍTICA #1: Modificación del Stack Pointer (R31/SP)

### Lo que dice el Vault

**Register File.md** (línea 98):
```
| R31 | $sp | Stack Pointer | Modificado por PUSH/POP/JR |
```

**Branch Control.md** (líneas 68-74):
```
### 4. Jump Register (JR Rs)
PC_NEXT = Rs
SP = SP + 4
```

**Branch Control.md** (línea 100):
```
| `SP_INCREMENT` | 1 bit | [[Register File]] | Señal para SP += 4 (JR) |
```

### Problema

❌ **NINGÚN archivo especifica CÓMO se implementa la modificación de SP**

El Vault dice:
- "SP es modificado por PUSH/POP/JR" ✓ (correcto)
- "SP = SP + 4" ✓ (correcto)
- "Señal SP_INCREMENT" ✓ (correcto conceptualmente)

Pero NO dice:
- ❌ **Cómo se genera la señal SP_INCREMENT**
- ❌ **Dónde se conecta SP_INCREMENT**
- ❌ **Qué hace Register File cuando recibe SP_INCREMENT**
- ❌ **Cómo se lee el valor actual de SP**
- ❌ **Cómo se calcula el nuevo valor de SP**

### Lo que dice la Especificación Real

**S-MIPS_PROCESSOR_GUIDE.md** (líneas 1456-1459):
```
Cycle 7: Execute
         - Register File reads R1
         - ALU computes SP - 4
         - Register File writes to SP
```

**Mecanismo REAL**:
1. ✅ Register File lee R31 (SP) usando puerto de lectura normal
2. ✅ ALU calcula `SP - 4` (para PUSH) o `SP + 4` (para POP/JR)
3. ✅ Resultado se escribe de vuelta a R31 usando puerto de escritura normal
4. ✅ Se usa `WRITE_REG = 31` y `REG_WRITE = 1`

**NO hay señal especial `SP_INCREMENT`** - SP se modifica como cualquier registro normal.

### Disparidad Detallada

| Aspecto | Vault | Realidad | Gap |
|---------|-------|----------|-----|
| **Lectura de SP** | No especificada | READ_REG_1 o READ_REG_2 = 31 | ❌ Falta |
| **Cálculo nuevo SP** | "SP = SP + 4" abstracto | ALU calcula SP ± 4 | ❌ Falta |
| **Escritura a SP** | "Señal SP_INCREMENT" | WRITE_REG=31, REG_WRITE=1 | ❌ Incorrecto |
| **Puerto especial** | Implica puerto especial | Usa puertos normales | ❌ Confuso |

---

## 🚨 DISPARIDAD CRÍTICA #2: Instrucciones PUSH/POP

### Lo que dice el Vault

**Instruction Decoder.md** (líneas 217-218):
```
| PUSH Rs     | 0x30   | -      | MEM_WRITE=1 (SP-=4, Mem[SP]=Rs)             |
| POP Rt      | 0x31   | -      | REG_WRITE=1, MEM_READ=1 (Rt=Mem[SP], SP+=4) |
```

**Vault dice en comentarios**:
- PUSH: "SP-=4, Mem[SP]=Rs"
- POP: "Rt=Mem[SP], SP+=4"

### Problema

❌ **NO especifica CÓMO se implementa cada paso**

Para PUSH Rs:
- ❌ No dice cuándo/cómo se decrementa SP
- ❌ No dice qué registro lee para obtener SP actual
- ❌ No dice cómo se calcula la dirección de memoria
- ❌ No dice en qué orden ocurren las operaciones

### Lo que dice la Especificación Real

**S-MIPS_PROCESSOR_GUIDE.md** (líneas 1454-1466):
```
Cycle 1-5: Fetch PUSH instruction
Cycle 6: LOAD_I
Cycle 7: Execute
         - Register File reads R1 (Rs)
         - Register File reads R31 (SP)
         - ALU computes SP - 4
         - Register File writes to SP (nuevo SP)
Cycle 8: Control Unit detects memory write
Cycle 9: START write operation (usa nuevo SP como dirección)
Cycles 10-11: Wait WT cycles
Cycle 12: Memory write complete
```

**Orden REAL para PUSH Rs**:
1. ✅ Leer Rs (dato a guardar)
2. ✅ Leer R31 (SP actual)
3. ✅ ALU calcula `SP_nuevo = SP - 4`
4. ✅ Escribir SP_nuevo a R31
5. ✅ Iniciar escritura de memoria: `Mem[SP_nuevo] = Rs`

### Disparidad Detallada

| Paso | Vault | Realidad | Gap |
|------|-------|----------|-----|
| **1. Leer SP** | No especificado | READ_REG_2 = 31 | ❌ Falta |
| **2. Leer Rs** | Implícito | READ_REG_1 = Rs | ⚠️ Parcial |
| **3. Calcular SP-4** | "SP-=4" | ALU: operando_A=SP, operando_B=4, OP=SUB | ❌ Falta |
| **4. Escribir SP** | No especificado | WRITE_REG=31, WRITE_DATA=ALU_RESULT | ❌ Falta |
| **5. Dirección memoria** | No especificado | ADDRESS = SP_nuevo (de R31) | ❌ Falta |
| **6. Dato memoria** | "Mem[SP]=Rs" | DATA = Rs (del paso 2) | ⚠️ Parcial |

---

## 🚨 DISPARIDAD CRÍTICA #3: Señales de Control entre Componentes

### Lo que dice el Vault

**Data Path.md** NO tiene una sección completa de "Conexiones entre Componentes"

Cada componente especifica entradas/salidas individualmente, pero NO hay un diagrama o tabla que muestre TODAS las conexiones del sistema.

### Lo que falta

❌ **Tabla completa de señales del Data Path**

Ejemplo de lo que DEBERÍA existir:

```
=== SEÑALES DEL DATA PATH ===

De Instruction Decoder → Register File:
  - READ_REG_1 [5 bits]
  - READ_REG_2 [5 bits]
  - WRITE_REG [5 bits] (via MUX Rd/Rt)

De Register File → ALU:
  - READ_DATA_1 [32 bits] → ALU operando A
  - READ_DATA_2 [32 bits] → MUX ALU_B

De ALU → Register File:
  - RESULT [32 bits] → MUX Writeback
  - HI [32 bits] → entrada HI_IN
  - LO [32 bits] → entrada LO_IN

De Control Unit → Register File:
  - REG_WRITE [1 bit]
  - HI_WRITE [1 bit]
  - LO_WRITE [1 bit]

... etc ...
```

### Disparidad

| Aspecto | Vault | Necesidad Real | Gap |
|---------|-------|----------------|-----|
| **Diagrama de conexiones** | ❌ No existe | Crítico para implementación | ❌ Falta |
| **Tabla de señales** | ❌ No existe | Crítico para debugging | ❌ Falta |
| **Anchos de bus** | ⚠️ Parcial | Todos especificados | ⚠️ Incompleto |
| **Dirección de señales** | ⚠️ Implícito | Explícito con flechas | ⚠️ Confuso |

---

## 🚨 DISPARIDAD CRÍTICA #4: Instrucción JR

### Lo que dice el Vault

**Branch Control.md** (líneas 68-74):
```
### 4. Jump Register (JR Rs)
PC_NEXT = Rs
SP = SP + 4

Salta a dirección contenida en Rs
Incrementa Stack Pointer en 4 (retorno de función)
```

### Problema

❌ **NO especifica que Rs Y R31 se leen SIMULTÁNEAMENTE**

Para JR, el procesador necesita:
1. ✅ Leer Rs (para obtener nueva dirección de PC)
2. ✅ Leer R31 (SP) (para calcular SP+4)
3. ✅ Escribir nuevo PC = Rs
4. ✅ Escribir nuevo SP = SP+4

Pero el Vault NO dice:
- ❌ Qué puertos de lectura se usan (Rs en puerto 1, SP en puerto 2)
- ❌ Cómo el ALU calcula SP+4 al mismo tiempo que Branch Control usa Rs
- ❌ Que se necesita escribir a R31 en el mismo ciclo

### Lo que dice la Especificación Real

**S-MIPS_PROCESSOR_GUIDE.md** (línea 710):
```
JR: SP = SP + 4 (return from function)
```

**Mecanismo REAL**:
```
JR Rs:
  READ_REG_1 = Rs         → READ_DATA_1 va a Branch Control
  READ_REG_2 = 31 (SP)    → READ_DATA_2 va a ALU operando B

  Branch Control:
    PC_NEXT = READ_DATA_1 (Rs)

  ALU:
    RESULT = READ_DATA_2 + 4  (SP + 4)

  Register File:
    WRITE_REG = 31
    WRITE_DATA = ALU_RESULT
    REG_WRITE = 1
```

### Disparidad Detallada

| Aspecto | Vault | Realidad | Gap |
|---------|-------|----------|-----|
| **Dual read** | No especificado | Rs y SP leídos simultáneamente | ❌ Falta |
| **PC update** | "PC_NEXT = Rs" ✓ | Correcto | ✓ OK |
| **SP update** | "SP = SP + 4" | Vía ALU y escritura a R31 | ❌ Falta mecanismo |
| **Escritura register** | No especificado | WRITE_REG=31, REG_WRITE=1 | ❌ Falta |

---

## 🚨 DISPARIDAD CRÍTICA #5: Señales del Control Unit

### Lo que dice el Vault

**Control Unit.md** especifica señales de salida:
```
- LOAD_I
- EXECUTE
- START_MC
- R/W
- PUSH_LOAD
```

### Problema

❌ **Faltan señales críticas documentadas**

Señales que SÍ necesita Control Unit (basado en spec real):
1. ✅ `LOAD_I` - Cargar instrucción
2. ✅ `EXECUTE` - Ejecutar
3. ✅ `START_MC` - Iniciar Memory Control
4. ✅ `R/W` - Read/Write para memoria
5. ✅ `PUSH_LOAD` - Para doble ciclo de PUSH/POP
6. ❌ **`REG_WRITE`** - Enable escritura en Register File (FALTA)
7. ❌ **`HI_WRITE`, `LO_WRITE`** - Enable Hi/Lo (FALTA)
8. ❌ **`PC_WRITE`** - Enable escritura de PC (FALTA o implícito)

### Disparidad

El Vault dice que Control Unit genera señales de control, pero NO lista TODAS las señales que realmente necesita.

---

## 🚨 DISPARIDAD CRÍTICA #6: Interfaz Memory Control ↔ Data Path

### Lo que dice el Vault

**Memory Control.md** especifica entradas/salidas, pero:

❌ **NO especifica cómo se conecta la dirección de memoria**

Para PUSH/POP/LW/SW, Memory Control necesita:
- Dirección de memoria: ¿De dónde viene?
- Dato a escribir: ¿De dónde viene?
- Dato leído: ¿A dónde va?

### Lo que dice la Especificación Real

**Dirección de memoria**:
- Para LW/SW con offset: `ADDRESS = Rs + SignExt(offset)` (calculado por ALU)
- Para PUSH/POP: `ADDRESS = SP_nuevo` (R31 después de ±4)

**El Vault NO especifica**:
- ❌ Que el ALU calcula la dirección efectiva
- ❌ Que el resultado del ALU se usa como dirección
- ❌ Cómo Memory Control recibe esta dirección

---

## 📊 Tabla Resumen de Disparidades

| # | Disparidad | Impacto | Severidad |
|---|------------|---------|-----------|
| 1 | Modificación de SP (R31) | Sin esto, PUSH/POP/JR no funcionan | 🔴 CRÍTICO |
| 2 | Detalle de PUSH/POP | Implementación incorrecta | 🔴 CRÍTICO |
| 3 | Tabla completa de señales | Confusión al conectar | 🟡 ALTO |
| 4 | JR con SP increment | JR no modifica SP correctamente | 🔴 CRÍTICO |
| 5 | Señales de Control Unit | Faltan señales necesarias | 🟡 ALTO |
| 6 | Interfaz Memory Control | Conexiones incorrectas | 🟡 ALTO |
| 7 | Orden de operaciones PUSH/POP | Timing incorrecto | 🟡 ALTO |
| 8 | Doble ciclo de PUSH/POP | Control Unit mal implementado | 🟡 ALTO |

---

## 🎯 ¿Sería Funcional el Vault?

**Respuesta**: ❌ **NO, sin consultar especificación externa**

### Lo que SÍ se puede implementar solo con el Vault

✅ Estructura básica de componentes
✅ ALU operaciones
✅ Register File estructura
✅ Instrucciones simples (ADD, SUB, AND, OR)
✅ Branches simples (BEQ, BNE)
✅ Jump absoluto (J)

### Lo que NO se puede implementar solo con el Vault

❌ PUSH/POP (falta mecanismo de SP)
❌ JR con SP increment (falta doble lectura + escritura)
❌ LW/SW con offset (falta cálculo de dirección efectiva)
❌ MULT/DIV con Hi/Lo (señales de control incompletas)
❌ Conexiones correctas entre componentes
❌ Timing correcto de señales de control

---

## 🔧 Lo que Necesitas Implementar (Basado en Spec Real)

### Para PUSH Rs

**Configuración de señales**:
```
Control Signals:
  REG_WRITE = 1           (para escribir nuevo SP)
  MEM_WRITE = 1           (para escribir a memoria)

Instruction Decoder:
  READ_REG_1 = Rs         (dato a guardar)
  READ_REG_2 = 31 (SP)    (SP actual)
  WRITE_REG = 31          (destino: SP)
  ALU_OP = SUB            (para SP - 4)

Datapath Flow:
  1. READ_DATA_1 = Register[Rs]     (dato)
  2. READ_DATA_2 = Register[31]     (SP)
  3. ALU: RESULT = SP - 4           (nuevo SP)
  4. Register[31] = RESULT          (actualizar SP)
  5. Memory[RESULT] = READ_DATA_1   (guardar dato en nueva posición)
```

### Para POP Rt

**Configuración de señales**:
```
Control Signals:
  REG_WRITE = 1           (para escribir dato leído + nuevo SP)
  MEM_READ = 1            (para leer de memoria)

Instruction Decoder:
  READ_REG_1 = (no usado)
  READ_REG_2 = 31 (SP)    (SP actual)
  WRITE_REG = Rt          (en primer ciclo: destino dato)
               31         (en segundo ciclo: destino SP)
  ALU_OP = ADD            (para SP + 4)

Datapath Flow (2 ciclos):
  Ciclo 1 - Leer memoria:
    1. READ_DATA_2 = Register[31]   (SP)
    2. Memory[SP] → MEMORY_DATA     (leer dato)
    3. Register[Rt] = MEMORY_DATA   (guardar dato leído)

  Ciclo 2 - Actualizar SP:
    1. READ_DATA_2 = Register[31]   (SP)
    2. ALU: RESULT = SP + 4         (nuevo SP)
    3. Register[31] = RESULT        (actualizar SP)
```

### Para JR Rs

**Configuración de señales**:
```
Control Signals:
  REG_WRITE = 1           (para escribir nuevo SP)
  JUMP_REG = 1            (para Branch Control)

Instruction Decoder:
  READ_REG_1 = Rs         (nueva dirección PC)
  READ_REG_2 = 31 (SP)    (SP actual)
  WRITE_REG = 31          (destino: SP)
  ALU_OP = ADD            (para SP + 4)

Datapath Flow:
  1. READ_DATA_1 = Register[Rs]     (nueva PC)
  2. READ_DATA_2 = Register[31]     (SP)
  3. Branch Control: PC_NEXT = READ_DATA_1
  4. ALU: RESULT = SP + 4           (nuevo SP)
  5. Register[31] = RESULT          (actualizar SP)
```

---

## 🎯 Conclusión

El Vault tiene **~60-70% de la información necesaria** para implementar el procesador.

**Falta el 30-40%** que son los detalles de implementación específicos, especialmente:
- Cómo se modifican registros especiales (SP, Hi, Lo)
- Conexiones exactas entre componentes
- Orden de operaciones en instrucciones complejas
- Señales de control completas

**Necesitarías consultar**:
- S-MIPS_PROCESSOR_GUIDE.md
- Especificación oficial (s-mips.pdf)
- Tests de assembly para inferir comportamiento

---

## 📝 Recomendaciones para Corregir el Vault

### Alta Prioridad

1. ✅ Añadir sección "Modificación de SP (R31)" con mecanismo completo
2. ✅ Actualizar PUSH/POP con orden de operaciones paso a paso
3. ✅ Actualizar JR con doble lectura (Rs + SP)
4. ✅ Crear diagrama completo de conexiones del Data Path
5. ✅ Completar lista de señales del Control Unit

### Media Prioridad

6. Añadir ejemplos de valores en cada paso (trace de ejecución)
7. Diagramas de timing para instrucciones complejas
8. Tabla de todas las señales del sistema con origen/destino

### Baja Prioridad

9. Diagramas de Verilog/HDL pseudocódigo más detallado
10. Tests unitarios por componente

---

**Tu problema actual**: Probablemente tienes implementaciones parciales basadas en el Vault, pero te faltan las conexiones correctas porque el Vault no las especifica completamente.

**Solución**: Usa la especificación real (S-MIPS_PROCESSOR_GUIDE.md) para los detalles de implementación que faltan en el Vault.
