# Guía de Integración Práctica - S-MIPS

**Objetivo**: Conectar todos los componentes del procesador S-MIPS paso a paso
**Audiencia**: Implementador con componentes individuales ya creados
**Prerrequisito**: Haber implementado componentes según especificaciones

---

## 🎯 Orden de Integración Recomendado

**NO intentes conectar todo a la vez**. Sigue este orden para debugging incremental:

### Fase 1: Data Path Interno (2-3 días)
### Fase 2: Control Unit + Memory Control (3-4 días)
### Fase 3: Integración CPU Completo (2-3 días)
### Fase 4: Cache System (opcional, 5-7 días)

---

## Fase 1: Integrar Data Path Interno

### Objetivo
Conectar todos los componentes **dentro** del Data Path para que puedan ejecutar instrucciones (asumiendo que la instrucción ya está cargada en IR).

### Componentes a Conectar
1. [[Instruction Register]]
2. [[Instruction Decoder]]
3. [[Register File]]
4. [[ALU]]
5. [[Branch Control]]
6. [[Program Counter]]
7. [[Random Generator]] (si existe)

### Paso 1.1: Instruction Decoder → Register File

```
Conexiones:
├─ Instruction Register (IR) [31:0]
│  └─→ Instruction Decoder input INST[31:0]
│
├─ Decoder extrae campos:
│  ├─ RS[4:0] → Register File READ_ADDR_1
│  ├─ RT[4:0] → Register File READ_ADDR_2
│  ├─ RD[4:0] → (a MUX)
│  ├─ IMM[15:0] → Sign Extender → IMM_EXT[31:0]
│  └─ Signals: WR_EN, USE_IMM, etc.
│
└─ Register File outputs:
   ├─ RS_DATA[31:0] → ALU operand A
   └─ RT_DATA[31:0] → (a MUX para ALU operand B)
```

**Test**:
```assembly
addi r1, r0, 42  # Cargar manualmente en IR
# Verificar con probes:
# - Decoder extrae RS=0, RT=1, IMM=42
# - Register File lee R0 (=0)
# - Sign Extender produce 0x0000002A
```

### Paso 1.2: ALU Connections

```
Conexiones:
├─ ALU Operand A:
│  └─ RS_DATA (direct from Register File)
│
├─ ALU Operand B:
│  └─ MUX (2:1, 32-bit):
│     ├─ Input 0: RT_DATA (para R-type)
│     ├─ Input 1: IMM_EXT (para I-type)
│     └─ Select: USE_IMM (from Decoder)
│
├─ ALU Operation:
│  └─ ALU_OP[4:0] (from Decoder)
│
└─ ALU Outputs:
   ├─ RESULT[31:0] → (a MUX Writeback)
   ├─ ZERO flag → Branch Control
   ├─ NEG flag → Branch Control
   ├─ HI[31:0] → Register File HI_IN
   └─ LO[31:0] → Register File LO_IN
```

**Test**:
```assembly
add r3, r1, r2  # R1=5, R2=10
# Cargar en IR, activar EXECUTE
# Verificar: ALU_RESULT = 15
```

### Paso 1.3: Branch Control

```
Conexiones:
├─ Branch Control Inputs:
│  ├─ PC_CURRENT[31:0] (from PC register)
│  ├─ OFFSET[15:0] (from Decoder, sign-extended)
│  ├─ JUMP_ADDR[25:0] (from Decoder)
│  ├─ RS_DATA[31:0] (for JR)
│  ├─ ZERO flag (from ALU)
│  ├─ NEG flag (from ALU)
│  └─ BRANCH_TYPE[2:0] (from Decoder)
│
└─ Branch Control Output:
   └─ PC_NEXT[31:0] → PC register
```

**Test**:
```assembly
beq r1, r1, label  # R1==R1, debe saltar
# Verificar: PC_NEXT = PC + 4 + (offset × 4)
```

### Paso 1.4: Writeback Path

```
MUX Writeback (8:1, 32-bit):
├─ Input 0: ALU_RESULT
├─ Input 1: MEM_DATA (from Memory Control, fase 2)
├─ Input 2: PC + 4 (for JAL)
├─ Input 3: HI_DATA (for MFHI)
├─ Input 4: LO_DATA (for MFLO)
├─ Input 5: KBD_DATA (for KBD)
├─ Input 6: RANDOM_VALUE (from Random Generator)
├─ Input 7: (unused/zero)
├─ Select: WR_SEL[2:0] (from Decoder)
└─ Output: WR_DATA[31:0] → Register File DATA_IN
```

### Paso 1.5: Register Destination Selector

```
MUX Register Destination (2:1, 5-bit):
├─ Input 0: RT[4:0] (para I-type: ADDI, LW)
├─ Input 1: RD[4:0] (para R-type: ADD, SUB)
├─ Select: USE_RT (from Decoder)
└─ Output: WR_ADDR[4:0] → Register File WRITE_ADDR
```

### Verificación Fase 1

**Checklist**:
- [ ] IR carga instrucción correctamente
- [ ] Decoder extrae todos los campos
- [ ] Register File lee registros correctos
- [ ] ALU calcula operaciones correctas
- [ ] Branch Control calcula PC_NEXT correctos
- [ ] Writeback escribe en registro correcto
- [ ] Tests manuales de ADD, ADDI, BEQ pasan

**Tests Recomendados** (sin memoria aún):
```assembly
# Test 1: Arithmetic
addi r1, r0, 10
addi r2, r0, 20
add r3, r1, r2
# r3 debe ser 30

# Test 2: Branch
addi r1, r0, 5
beq r1, r1, skip
addi r2, r0, 99  # No ejecutar
skip:
addi r2, r0, 10  # Ejecutar
# r2 debe ser 10
```

---

## Fase 2: Integrar Control Unit y Memory Control

### Objetivo
Añadir coordinación temporal y acceso a memoria.

### Paso 2.1: Control Unit FSM

```
Crear subcircuito "Control Unit" con:
├─ State Register (3-4 bits)
├─ Next State Logic
└─ Output Logic

Estados:
├─ IDLE
├─ START_FETCH
├─ WAIT_INST_READ
├─ LOAD_INST
├─ EXECUTE_INST
├─ CHECK_INST
├─ START_MEM_WRITE (si necesario)
├─ WAIT_WRITE
├─ START_MEM_READ (si necesario)
├─ WAIT_READ
├─ CHECK_STACK (para PUSH/POP)
└─ HALT_STATE
```

### Paso 2.2: Control Unit → Data Path

```
Señales de Control Unit a Data Path:
├─ LOAD_I → Instruction Register enable
├─ EXECUTE → Habilita ejecución (WR_EN cuando apropiado)
└─ PUSH_LOAD → Para segundo ciclo de PUSH

Señales de Data Path a Control Unit:
├─ HALT → Para detener
├─ MC_NEEDED → Necesita acceso a memoria
├─ IS_WRITE → Tipo de acceso (0=read, 1=write)
├─ PUSH → Instrucción PUSH
└─ POP → Instrucción POP
```

### Paso 2.3: Memory Control Structure

```
Crear subcircuito "Memory Control" con:
├─ [[Memory State Machine]]
├─ [[Address Translator]]
├─ [[Little-Endian Converter]] (×5 instancias)
├─ [[Word Selector]]
└─ [[MASK Generator]]
```

### Paso 2.4: Control Unit ↔ Memory Control

```
Conexiones:
├─ Control Unit → Memory Control:
│  ├─ START_MC → Inicia operación
│  └─ R/W → Tipo de operación
│
└─ Memory Control → Control Unit:
   └─ MC_END → Operación completada
```

### Paso 2.5: Memory Control ↔ RAM

```
Conexiones:
├─ Memory Control → RAM:
│  ├─ ADDR[15:0] → Block address
│  ├─ CS → Chip select
│  ├─ R/W_RAM → Read/Write
│  ├─ I0-I3[31:0] → Write data
│  └─ MASK[3:0] → Write mask
│
└─ RAM → Memory Control:
   ├─ O0-O3[31:0] → Read data
   ├─ RT[3:0] → Read time
   └─ WT[3:0] → Write time
```

### Paso 2.6: Data Path ↔ Memory Control

```
Para Fetch (instrucciones):
├─ PC_OUT → Memory Control ADDRESS
└─ Memory Control INST_OUT → IR INST_IN

Para Load/Store (datos):
├─ ALU_RESULT (dirección) → Memory Control ADDRESS
├─ RT_DATA (dato) → Memory Control DATA_WRITE
└─ Memory Control DATA_READ → MUX Writeback
```

### Verificación Fase 2

**Checklist**:
- [ ] Control Unit cicla correctamente
- [ ] Fetch de instrucciones funciona
- [ ] LW lee datos correctos de RAM
- [ ] SW escribe datos correctos a RAM
- [ ] Timing correcto (espera RT/WT cycles)

**Tests Recomendados**:
```assembly
# Test 3: Memory
addi r1, r0, 100
sw r1, 0(r0)
lw r2, 0(r0)
beq r1, r2, pass
halt
pass:
addi r10, r0, 99
halt
```

---

## Fase 3: Integración Completa del CPU

### Paso 3.1: Conectar Todo en "S-MIPS CPU"

```
Circuito "S-MIPS CPU" (componente principal):
├─ Control Unit (subcircuito)
├─ Memory Control (subcircuito)
└─ Data Path (subcircuito)

Conexiones externas del CPU:
├─ A RAM:
│  ├─ ADDR, CS, R/W, I0-I3, MASK (outputs)
│  └─ O0-O3, RT, WT (inputs)
│
├─ Reloj y Reset:
│  ├─ CLK (input)
│  └─ RESET (input)
│
└─ I/O:
   ├─ TTY_DATA[6:0], TTY_EN (outputs)
   └─ KBD_DATA[6:0], KBD_AVAIL, KBD_EN (inputs)
```

### Paso 3.2: S-MIPS Board (Top Level)

```
Circuito "S-MIPS Board":
├─ S-MIPS CPU (tu implementación)
├─ RAM Module (proporcionado)
├─ RAM Dispatcher (proporcionado, para tests)
├─ TTY Terminal (proporcionado)
└─ KBD Input (proporcionado)

⚠️ NO MODIFICAR RAM, RAM Dispatcher, ni Board
```

### Verificación Fase 3

**Checklist Completo**:
- [ ] CPU arranca desde PC=0
- [ ] Ejecuta instrucciones secuencialmente
- [ ] Branches y jumps funcionan
- [ ] LW/SW funcionan
- [ ] PUSH/POP funcionan
- [ ] TTY imprime caracteres
- [ ] HALT detiene procesador
- [ ] RND genera valores (si implementado)

**Tests Completos**:
```bash
# Ejecutar test suite
./test.py tests s-mips.circ -o tests-out

# Tests críticos:
tests/add.asm
tests/addi.asm
tests/beq.asm
tests/sw-lw.asm
tests/push-pop.asm
tests/tty.asm
tests/halt.asm
```

---

## Fase 4: Añadir Cache System (Opcional)

**Solo después de que CPU básico funcione al 100%**

### Paso 4.1: Instruction Cache

```
Insertar entre Control Unit y Memory Control:

ANTES:
Control Unit → Memory Control → RAM

DESPUÉS:
Control Unit → I-Cache → Memory Control → RAM
                  ↓ hit
              1 cycle
```

### Paso 4.2: Data Cache

```
Insertar entre Data Path y Memory Control:

ANTES:
Data Path (LW/SW) → Memory Control → RAM

DESPUÉS:
Data Path → D-Cache → Memory Control → RAM
               ↓ hit
           1 cycle
```

### Paso 4.3: Modificar Control Unit

```
Nuevo flujo para Instruction Fetch:
├─ START_FETCH → I-Cache
├─ I-Cache hit? → LOAD_INST (1 ciclo)
├─ I-Cache miss? → Memory Control → wait RT → LOAD_INST
└─ Cache automáticamente fill on miss
```

**Ver**: [[Direct-Mapped Cache Implementation]] para detalles

---

## 🐛 Debugging Tips por Fase

### Fase 1 Issues

**Problema**: Registros no se actualizan
- Verificar WR_EN activo cuando debe
- Verificar CLK conectado a Register File
- Verificar WR_ADDR correcto

**Problema**: ALU resultado incorrecto
- Probes en operandos A y B
- Verificar ALU_OP desde Decoder
- Test ALU aislado con valores conocidos

**Problema**: Branch no salta
- Verificar flags ZERO/NEG
- Verificar BRANCH_TYPE desde Decoder
- Verificar cálculo de offset (× 4)

### Fase 2 Issues

**Problema**: CPU no avanza
- Verificar Control Unit FSM con probes
- Verificar MC_END llega a Control Unit
- Verificar CLK conectado a todos los componentes

**Problema**: Fetch infinito
- Verificar Memory Control genera MC_END
- Verificar RT value leído de RAM
- Verificar Address Translator

**Problema**: LW/SW datos incorrectos
- Verificar Little-Endian Converter
- Verificar Word Selector
- Verificar MASK Generator

### Fase 3 Issues

**Problema**: Tests fallan aleatoriamente
- Verificar timing de todas las señales
- Buscar race conditions
- Verificar RESET inicializa todo

**Problema**: Algunos tests pasan, otros fallan
- Identificar patrón (¿solo branches? ¿solo memoria?)
- Debug componente específico aislado
- Verificar casos edge (ej: R0 siempre = 0)

---

## ⚡ Optimización de Integración

### Uso de Tunnels

**CRÍTICO**: Usa tunnels extensivamente para evitar wire spaghetti

```
Ejemplo:
├─ PC_OUT → Tunnel "PC"
├─ Branch Control lee Tunnel "PC"
├─ Memory Control lee Tunnel "PC"
└─ Data Path muestra Tunnel "PC" (para debugging)
```

### Subcircuitos Claros

```
Jerarquía recomendada:
S-MIPS Board
└─ S-MIPS CPU
   ├─ Control Unit
   ├─ Memory Control
   │  ├─ Memory FSM
   │  ├─ Address Translator
   │  ├─ Little-Endian Converter
   │  ├─ Word Selector
   │  └─ MASK Generator
   └─ Data Path
      ├─ Instruction Register
      ├─ Instruction Decoder
      ├─ Register File
      ├─ ALU
      ├─ Branch Control
      ├─ Program Counter
      └─ Random Generator
```

### Probes Estratégicos

```
Probes esenciales:
├─ PC (siempre visible)
├─ IR (instrucción actual)
├─ Control Unit state
├─ ALU result
├─ Register File: R0, R1, R2, R10 (resultados)
└─ Flags: HALT, MC_END, CACHE_HIT
```

---

## 📊 Checklist de Integración Completa

### Data Path (Fase 1)
- [ ] Instruction Decoder extrae campos
- [ ] Register File lee/escribe
- [ ] ALU calcula correctamente
- [ ] Branch Control calcula PC_NEXT
- [ ] Writeback path funcional
- [ ] Tests manuales (sin memoria) pasan

### Control + Memory (Fase 2)
- [ ] Control Unit FSM completo
- [ ] Memory Control fetch funcional
- [ ] LW/SW funcionan
- [ ] Timing correcto (RT/WT)
- [ ] Little-endian correcto
- [ ] Tests con memoria pasan

### CPU Completo (Fase 3)
- [ ] Integración en S-MIPS Board
- [ ] Todos los componentes conectados
- [ ] Test suite completo (15+ tests)
- [ ] Sin warnings de Logisim
- [ ] Cost ≤ 100 unidades

### Cache (Fase 4 - Opcional)
- [ ] I-Cache implementado (4+ líneas)
- [ ] D-Cache implementado (4+ líneas)
- [ ] Hit/miss logic funcional
- [ ] Performance mejora medible
- [ ] Tests siguen pasando

---

## 🎯 Timeline Estimado

| Fase | Días | Acumulado |
|------|------|-----------|
| Fase 1: Data Path | 2-3 | 3 días |
| Fase 2: Control+Memory | 3-4 | 7 días |
| Fase 3: Integración | 2-3 | 10 días |
| Fase 4: Cache (opt) | 5-7 | 17 días |

**Total para CPU básico funcional**: ~10 días
**Total para CPU con cache (aprobar)**: ~17 días

---

## Enlaces Relacionados

- [[Control Unit]] - FSM principal
- [[Memory Control]] - Interfaz RAM
- [[Data Path]] - Ejecución
- [[Direct-Mapped Cache Implementation]] - Sistema cache
- [[Dashboard]] - Estado del proyecto

---

**Última actualización**: 2025-12-09
**Propósito**: Guía paso a paso para integrar S-MIPS
**Nivel**: Implementación práctica
