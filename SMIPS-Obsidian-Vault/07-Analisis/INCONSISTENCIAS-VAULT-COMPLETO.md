# Inconsistencias del Vault - Análisis Completo

**Fecha**: 2025-12-13
**Revisión**: Completa de todas las conexiones entre componentes

---

## 🔍 METODOLOGÍA

Para cada conexión entre componentes A → B:
1. Verificar que componente A documente la salida hacia B
2. Verificar que componente B documente la entrada desde A
3. Verificar que anchos de bits coincidan
4. Verificar que nombres de señales sean consistentes

---

## ❌ INCONSISTENCIAS ENCONTRADAS

### 1. Branch Control → Register File: SP_INCREMENT

**Problema**: Branch Control dice que envía `SP_INCREMENT`, pero Register File NO lo documenta.

**Branch Control.md línea 100**:
```markdown
| `SP_INCREMENT` | 1 bit | [[Register File]] | Señal para SP += 4 (JR) |
```

**Register File.md**:
- ❌ NO documenta entrada `SP_INCREMENT`
- ✅ PERO sí documenta el mecanismo correcto (usar puertos normales)

**Solución**: ELIMINAR `SP_INCREMENT` de Branch Control porque es INCORRECTO según CORRECCIONES-CRITICAS-VAULT.md. SP se modifica usando:
- `WRITE_REG = 31`
- `WRITE_DATA = ALU_RESULT`
- `REG_WRITE = 1`

---

### 2. Data Path: Entradas mal documentadas

**Problema**: Data Path documenta entradas genéricas sin especificar fuente real.

**Data Path.md líneas 108-120 (tabla de entradas)**:
```markdown
| `LOAD_INST` | 1 bit | Control Unit | Cargar instrucción en IR |
| `REG_WRITE` | 1 bit | Control Unit | Enable escritura en Register File |
```

**Pero debería especificar**:
- `LOAD_I` (no `LOAD_INST`)
- Fuente explícita: "Control Unit"

**Inconsistencia adicional**: Data Path lista señales que en realidad van a sus subcomponentes:
- `REG_WRITE` va a Register File (subcomponente), no directamente a Data Path
- `ALU_SRC` va a MUX ALU_B (subcomponente)

**Solución**: Data Path debe documentar:
1. Entradas que ENTRAN al Data Path desde Control Unit/Memory Control
2. Conexiones INTERNAS entre subcomponentes en sección separada

---

### 3. Control Unit: Señales de entrada/salida incompletas

**Problema**: Control Unit no documenta TODAS las señales que genera.

**Control Unit.md líneas 148-163**:
```markdown
### Hacia [[Data Path]]
| [[LOAD_I]] | 1 bit | Carga instrucción en [[Instruction Register]] |
| [[EXECUTE]] | 1 bit | Habilita ejecución en [[Data Path]] |
```

**Falta documentar**:
- ❌ `EN` (Data Path Enable)
- ❌ `CLK_DP` (Clock del Data Path)
- ❌ Todas las señales de control que realmente genera el Instruction Decoder, no el Control Unit

**Confusión**: El Vault confunde qué señales genera Control Unit vs cuáles genera Instruction Decoder.

**REALIDAD**:
- **Control Unit genera**: `LOAD_I`, `EXECUTE`, `START_MC`, `R/W`, `PUSH_LOAD`, `CLR`
- **Instruction Decoder genera**: `REG_WRITE`, `ALU_OP`, `ALU_SRC`, `REG_DST`, `MEM_READ`, `MEM_WRITE`, etc.

**Solución**: Separar claramente señales de Control Unit vs Instruction Decoder.

---

### 4. Memory Control ↔ Data Path: Señales mal nombradas

**Problema**: Inconsistencia en nombres de señales.

**Memory Control debería recibir**:
- `ADDRESS` (dirección efectiva calculada por ALU)
- `WRITE_DATA` (dato a escribir desde Register File)

**Pero Data Path no documenta estas salidas explícitamente en su tabla principal**.

**Data Path.md líneas 597-664** tiene la tabla completa de conexiones agregada recientemente, PERO:
- Está en sección separada
- No está en la tabla principal de "Salidas a Memory Control" (líneas 138-144)

**Solución**: Unificar las tablas de I/O principales con la tabla de conexiones completas.

---

### 5. Instruction Register → Instruction Decoder: Nombre inconsistente

**Instruction Register.md línea 52**:
```markdown
| `INST_OUT` | 32 bits | [[Instruction Decoder]] | Instrucción hacia Decoder |
```

**Pero Instruction Decoder.md línea 81**:
```markdown
| `INSTRUCTION` | 32 bits | [[Instruction Register]] | Instrucción a decodificar |
```

**Problema**:
- Instruction Register llama a la salida `INST_OUT`
- Instruction Decoder llama a la entrada `INSTRUCTION`

**Solución**: Unificar nombres. Usar `INSTRUCTION` (más claro).

---

### 6. Program Counter ↔ Branch Control: Nombre inconsistente

**Program Counter.md línea 43**:
```markdown
| `NEXT_PC` | 32 bits | Próximo valor del PC (desde [[Branch Control]]) |
```

**Branch Control.md línea 99**:
```markdown
| `PC_NEXT` | 32 bits | [[Program Counter]] | Siguiente valor de PC |
```

**Problema**:
- Program Counter espera `NEXT_PC`
- Branch Control genera `PC_NEXT`

**Solución**: Unificar nombres. Usar `PC_NEXT` (consistente con convención del Vault).

---

### 7. ALU → Register File: Hi/Lo - Señales incompletas en Register File

**ALU.md líneas 44-46**:
```markdown
| `HI` | 32 bits | [[Register File]] | Parte alta (mult/div) |
| `LO` | 32 bits | [[Register File]] | Parte baja (mult/div) |
```

**Register File.md** (revisado recientemente) SÍ documenta:
```markdown
| `HI_IN` | 32 bits | [[ALU]] | Valor para Hi (MULT/DIV) |
| `LO_IN` | 32 bits | [[ALU]] | Valor para Lo (MULT/DIV) |
```

**Inconsistencia**:
- ALU llama a las salidas `HI` y `LO`
- Register File llama a las entradas `HI_IN` y `LO_IN`

**Solución**: Clarificar que son la misma señal con nombres diferentes en cada extremo.

---

### 8. Instruction Decoder: Señales que NO genera directamente

**Problema**: Instruction Decoder documenta señales de control que en realidad requieren combinación con Control Unit.

**Instruction Decoder.md líneas 101-106**:
```markdown
| `REG_WRITE` | 1 bit | [[Register File]] | Enable escritura registro |
| `MEM_READ` | 1 bit | [[Memory Control]] | Leer memoria |
| `MEM_WRITE` | 1 bit | [[Memory Control]] | Escribir memoria |
```

**REALIDAD**: Estas señales dependen de:
1. Instruction Decoder → genera señal base según opcode/funct
2. Control Unit → activa/desactiva según estado (no escribir durante FETCH, por ejemplo)

**Ejemplo**: `REG_WRITE` debe ser `REG_WRITE = (decoder_says_write) AND (state == EXECUTE) AND (!HALT)`

**Solución**: Documentar que Instruction Decoder genera "señales de control RAW" que Control Unit puede modificar según estado.

---

### 9. Data Path: No documenta Memory Control como entrada

**Data Path.md líneas 122-127**:
```markdown
### Entradas desde Memory Control
| `INSTRUCTION_IN` | 32 bits | Instrucción leída de memoria |
| `MEMORY_DATA` | 32 bits | Dato leído de memoria (LW) |
```

**Problema**: Estas señales van a subcomponentes específicos, no a "Data Path" como entidad:
- `INSTRUCTION_IN` → Instruction Register
- `MEMORY_DATA` → MUX Writeback → Register File

**Data Path** es un contenedor de componentes, no un componente que recibe señales directamente.

**Solución**: Documentar claramente:
- "Entradas al Data Path" (señales que cruzan la frontera)
- "Conexiones internas" (entre subcomponentes dentro del Data Path)

---

### 10. Branch Control: No documenta entrada PC_CURRENT

**Branch Control.md línea 84**:
```markdown
| `PC` | 32 bits | [[Program Counter]] | Program Counter actual |
```

**Pero debería ser**:
```markdown
| `PC_CURRENT` | 32 bits | [[Program Counter]] | Program Counter actual |
```

Para distinguirlo de `PC_NEXT` (salida).

**Solución**: Renombrar a `PC_CURRENT` o `PC_IN` para claridad.

---

## 📊 RESUMEN DE INCONSISTENCIAS POR TIPO

### Tipo 1: Señales inexistentes (5 casos)
1. ❌ `SP_INCREMENT` (Branch Control → Register File) - NO DEBE EXISTIR
2. ❌ `EN` desde Control Unit a Data Path - NO DOCUMENTADO
3. ❌ `CLK_DP` desde Control Unit a Data Path - NO DOCUMENTADO
4. ❌ Varias señales de Instruction Decoder listadas en Control Unit

### Tipo 2: Nombres inconsistentes (5 casos)
1. `INST_OUT` vs `INSTRUCTION` (IR → Decoder)
2. `NEXT_PC` vs `PC_NEXT` (Branch Control → PC)
3. `HI`/`LO` vs `HI_IN`/`LO_IN` (ALU → Register File)
4. `PC` vs `PC_CURRENT` (PC → Branch Control)
5. `LOAD_INST` vs `LOAD_I` (Control Unit → Data Path)

### Tipo 3: Estructura documental confusa (4 casos)
1. Data Path documenta señales que van a subcomponentes
2. Control Unit vs Instruction Decoder - quién genera qué
3. Señales "raw" vs señales "finales" con lógica de Control Unit
4. Fronteras de componentes no claras (Data Path como contenedor)

---

## ✅ PLAN DE CORRECCIÓN

### Fase 1: Eliminar señales incorrectas
- [ ] Eliminar `SP_INCREMENT` de Branch Control
- [ ] Documentar mecanismo correcto de SP en Branch Control (remitir a Register File)

### Fase 2: Unificar nombres de señales
- [ ] `INST_OUT` → `INSTRUCTION` (Instruction Register)
- [ ] `NEXT_PC` → `PC_NEXT` (Program Counter)
- [ ] Documentar claramente aliases `HI`/`HI_IN`, `LO`/`LO_IN`
- [ ] `PC` → `PC_CURRENT` (entrada de Branch Control)
- [ ] `LOAD_INST` → `LOAD_I` (todos los archivos)

### Fase 3: Clarificar arquitectura
- [ ] Data Path: Separar "Entradas al contenedor" vs "Conexiones internas"
- [ ] Control Unit: Listar solo señales que REALMENTE genera
- [ ] Instruction Decoder: Marcar señales como "raw control signals"
- [ ] Todos los componentes: Tabla de I/O consistente con tabla de conexiones

### Fase 4: Crear matriz de verificación
- [ ] Tabla bidireccional: Para cada señal A→B, verificar que B→A esté documentado
- [ ] Script de validación automática

---

## 🎯 PRIORIDADES

**Prioridad 1 - CRÍTICO** (afecta implementación):
1. Eliminar `SP_INCREMENT` (señal incorrecta)
2. Clarificar Control Unit vs Instruction Decoder (quién genera qué)

**Prioridad 2 - IMPORTANTE** (confusión al leer):
3. Unificar nombres de señales
4. Separar Data Path como contenedor vs componente

**Prioridad 3 - MEJORA** (completitud):
5. Documentar todas las señales faltantes
6. Crear tabla de verificación bidireccional

---

## 📝 SIGUIENTE PASO

Corregir cada archivo del Vault según este análisis, empezando por:
1. Branch Control (eliminar SP_INCREMENT)
2. Register File (ya está correcto después de actualización reciente)
3. Control Unit (clarificar señales que genera)
4. Instruction Decoder (marcar como "raw signals")
5. Data Path (reestructurar I/O)
