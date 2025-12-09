# Instruction Register (IR) - Registro de Instrucción

**Tipo**: Registro de Almacenamiento
**Estado**: ✅ #implementado
**Ubicación**: s-mips.circ (líneas 6311-6365)
**Complejidad**: ⭐ Muy Simple
**Prioridad**: ✅ YA EXISTE

## Descripción

El Instruction Register (IR) es un registro de 32 bits que almacena la instrucción actual que está siendo decodificada y ejecutada. Actúa como buffer entre [[Memory Control]] y [[Instruction Decoder]].

## Responsabilidades

1. **Almacenar instrucción** leída desde memoria
2. **Mantener instrucción estable** durante ciclo de ejecución
3. **Proporcionar instrucción** al [[Instruction Decoder]]
4. **Cargarse** solo cuando [[Control Unit]] lo indique (LOAD_I)

## Arquitectura

```
┌──────────────────────────────────────────────┐
│        INSTRUCTION REGISTER (IR)             │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │   Registro 32 bits con Load Enable     │ │
│  │                                        │ │
│  │   Current Instruction [31:0]           │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│            ▲                │                │
│            │                │                │
│    INST_IN (from MC)   INST_OUT              │
│    + LOAD_I signal   (to Decoder)            │
└──────────────────────────────────────────────┘
```

## Entradas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `INST_IN` | 32 bits | Instrucción desde [[Memory Control]] |
| `LOAD_I` | 1 bit | Load enable (desde [[Control Unit]]) |
| `CLK` | 1 bit | Reloj del sistema |
| `RESET` | 1 bit | Reset sincrónico |

## Salidas

| Porto | Ancho | Descripción |
|--------|-------|-------------|
| `INST_OUT` | 32 bits | Instrucción hacia [[Instruction Decoder]] |

## Comportamiento

### Lógica de Carga

```verilog
always @(posedge CLK) begin
    if (RESET) begin
        INST_OUT <= 32'h00000000;  // NOP instruction
    end
    else if (LOAD_I) begin
        INST_OUT <= INST_IN;       // Cargar nueva instrucción
    end
    // else: mantener instrucción actual
end
```

### Momento de Carga

El IR se carga en un momento específico del ciclo de ejecución:

```
Ciclo 1: START_FETCH
       → Control Unit solicita fetch de instrucción

Ciclos 2-N: WAIT_INST_READ
          → Memory Control espera RT cycles
          → RAM proporciona instrucción

Ciclo N+1: LOAD_INST ⭐
         → Control Unit activa LOAD_I = 1
         → IR captura INST_IN
         → Instrucción ahora disponible en INST_OUT

Ciclo N+2: EXECUTE_INST
         → Instruction Decoder lee INST_OUT
         → Data Path ejecuta
```

**Clave**: IR carga **después** de que Memory Control complete el fetch.

## Formato de Instrucción

El IR almacena cualquiera de los 3 formatos de instrucción S-MIPS:

### R-Type
```
[31:26] [25:21] [20:16] [15:11] [10:6 ] [5:0  ]
opcode   rs      rt      rd      shamt   funct
6 bits   5 bits  5 bits  5 bits  5 bits  6 bits
```

### I-Type
```
[31:26] [25:21] [20:16] [15:0        ]
opcode   rs      rt      immediate
6 bits   5 bits  5 bits  16 bits
```

### J-Type
```
[31:26] [25:0                    ]
opcode   address
6 bits   26 bits
```

## Timing Diagram

### Fetch e Instrucción Normal

```
CLK:       ___───___───___───___───___───___───___
           0   1   2   3   4   5   6   7   8

State:     IDLE│STRT│WAIT│WAIT│LOAD│EXEC│CHK │STRT│
                   │    │    │    │ ▲
                   └────RT cycles──┘ │
                                     Load aquí

LOAD_I:    ________________________________________───___

INST_IN:   [????][????][????][????][????][0x2001][0x2001][0x2001]
                                         ↑ Llegó de Memory Control

INST_OUT:  [0x0000][0x0000][0x0000][0x0000][0x0000][0x0000][0x2001]
                                                          ↑ Cargado
```

**Explicación**:
- Ciclos 1-4: Esperando que Memory Control lea instrucción
- Ciclo 5 (LOAD): LOAD_I=1, IR captura 0x20010005 (ejemplo: ADDI R1, R0, 5)
- Ciclo 6 (EXECUTE): Decoder lee INST_OUT = 0x20010005

### Instrucción que Permanece Durante Ejecución

```
Fase de Instrucción 1 (ADD R1, R2, R3):

Ciclo 10: LOAD_INST
        → IR carga instrucción ADD

Ciclo 11: EXECUTE_INST
        → Decoder ve ADD en INST_OUT
        → Register File lee R2, R3
        → ALU calcula R2 + R3
        → Register File escribe R1
        ⚠️ IR mantiene ADD durante todo el ciclo

Ciclo 12: CHECK_INST
        → IR aún mantiene ADD (no cambia hasta próximo LOAD_I)
```

**Importante**: IR **NO cambia** hasta el próximo LOAD_I, garantizando estabilidad.

## Conexión con otros Componentes

### Flujo de Datos

```
 Memory Control            Instruction Register         Instruction Decoder
┌──────────────┐          ┌────────────────────┐      ┌─────────────────┐
│              │ INST_IN  │                    │ INST │                 │
│  Fetch Logic │─────────►│   Register 32-bit  │─────►│ Decode Logic    │
│              │          │   (con load enable)│ OUT  │                 │
└──────────────┘          └────────────────────┘      └─────────────────┘
                                    ▲
                                    │ LOAD_I
                          ┌─────────────────┐
                          │  Control Unit   │
                          │  (LOAD state)   │
                          └─────────────────┘
```

### Señales de Control

| Señal | Origen | Destino | Descripción |
|-------|--------|---------|-------------|
| INST_IN | [[Memory Control]] | IR | Instrucción fetched |
| LOAD_I | [[Control Unit]] | IR | Habilita carga |
| INST_OUT | IR | [[Instruction Decoder]] | Instrucción a decodificar |

## Casos Especiales

### 1. NOP (No Operation)

Instrucción NOP = 0x00000000 (todos los bits en 0):

```
R-Type: opcode=000000, rs=00000, rt=00000, rd=00000, shamt=00000, funct=000000
      = ADD R0, R0, R0 (R0 = R0 + R0 = 0)
      = Efectivamente no hace nada útil
```

**Uso**: Reset inicial, padding, debugging.

### 2. Instrucción Inválida

Si IR contiene un opcode no válido (ej: 0x3E sin definir):

```
INST_OUT = 0x3E??????

Decoder ve opcode 0x3E
→ No hay match en tabla de decodificación
→ Todas las señales de control = 0
→ Posible comportamiento: NOP de facto
```

**Resultado**: Depende de implementación del Decoder
- Opción A: Tratar como NOP
- Opción B: Señal de ERROR (avanzado, no requerido)

### 3. Instrucción Parcialmente Leída

Si Memory Control falla y proporciona datos incompletos:

```
INST_IN = 0x????FFFF (datos basura)
LOAD_I = 1

IR carga basura
→ Decoder intentará decodificar
→ Comportamiento impredecible
```

**Prevención**: Memory Control debe garantizar lectura completa antes de END signal.

## Implementación en Logisim

### Componente

```
Tipo: Register (32-bit)
Configuración:
├─ Data Bits: 32
├─ Trigger: Rising Edge
├─ Enable Input: Yes (LOAD_I)
└─ Reset Value: 0x00000000 (NOP)
```

### Conexiones

```
Register "Instruction Register"
├─ D (input 32-bit): INST_IN
│                    ├─ Source: Memory Control
│                    └─ Via: Tunnel "INST_FROM_MEM"
│
├─ CLK (input 1-bit): System CLK
│
├─ EN (input 1-bit): LOAD_I
│                    ├─ Source: Control Unit
│                    └─ Active during LOAD_INST state
│
├─ RESET (input 1-bit): System RESET
│
└─ Q (output 32-bit): INST_OUT
                      ├─ Destination: Instruction Decoder
                      └─ Via: Splitters para extraer campos
```

## Tests de Validación

### Test 1: Carga Correcta

```assembly
# Verificar que IR carga instrucción fetched
addi r1, r0, 42    # Instrucción: 0x20010002A (ADDI R1, R0, 42)

# En debugger/probes:
# - Ciclo LOAD: IR debe cargar 0x2001002A
# - Ciclo EXECUTE: IR mantiene 0x2001002A
# - Resultado: R1 = 42
```

### Test 2: Estabilidad Durante Ejecución

```assembly
add r2, r1, r1     # Instrucción compleja que toma 1 ciclo

# Verificar en probes:
# - Durante LOAD: IR carga ADD
# - Durante EXECUTE: IR NO cambia
# - Durante CHECK: IR sigue igual
# - Hasta próximo LOAD: IR mantiene ADD
```

### Test 3: Reset

```assembly
# Con procesador ejecutando:
# - Activar RESET
# - IR debe ir a 0x00000000 (NOP)
# - Próxima instrucción debe ser desde PC=0
```

## Análisis de Correctitud

### Estado Actual: ✅ IMPLEMENTADO

**Ubicación**: s-mips.circ:6311-6365

**Verificación necesaria**:
- [ ] Reset a 0x00000000 funciona
- [ ] Carga INST_IN cuando LOAD_I=1
- [ ] Mantiene valor cuando LOAD_I=0
- [ ] INST_OUT conectado correctamente a Decoder
- [ ] Timing: carga en rising edge después de Memory Control END

### Tests Recomendados

1. **Probar con NOP**: Cargar 0x00000000, verificar no causa errores
2. **Probar varias instrucciones**: ADD, ADDI, LW, BEQ, J
3. **Stepping manual**: Avanzar ciclo por ciclo, observar cuándo IR carga
4. **Verificar estabilidad**: Durante EXECUTE, IR no debe cambiar

## Troubleshooting

### Problema: IR siempre contiene 0

**Causas**:
1. LOAD_I nunca se activa (Control Unit no funciona)
2. INST_IN siempre = 0 (Memory Control no proporciona datos)

**Solución**: Verificar Control Unit FSM y Memory Control

### Problema: IR cambia aleatoriamente

**Causas**:
1. LOAD_I activo cuando no debería
2. INST_IN tiene datos inestables

**Solución**: Verificar timing de Control Unit y Memory Control

### Problema: Instrucción incorrecta decodificada

**Causas**:
1. IR carga instrucción incorrecta (bug en Memory Control)
2. Decoder lee campos incorrectos (bug en splitters)

**Solución**:
- Probes en INST_IN vs INST_OUT
- Verificar Memory Control address translation

## Enlaces Relacionados

- [[Control Unit]] - Genera LOAD_I signal
- [[Memory Control]] - Proporciona INST_IN
- [[Instruction Decoder]] - Lee INST_OUT
- [[Data Path]] - Componente padre

---

**Estado**: ✅ Implementado
**Validación**: ⚠️ Pendiente de tests
**Bloquea**: Nada (ya existe)
