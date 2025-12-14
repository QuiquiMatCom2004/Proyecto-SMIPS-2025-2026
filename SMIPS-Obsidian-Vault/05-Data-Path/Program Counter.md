# Program Counter (PC) - Contador de Programa

**Tipo**: Registro Especial
**Estado**: ✅ #implementado
**Ubicación**: s-mips.circ (líneas 8236-8281)
**Complejidad**: ⭐ Simple
**Prioridad**: ✅ YA EXISTE

## Descripción

El Program Counter (PC) es un registro de 32 bits que almacena la dirección de la próxima instrucción a ejecutar. Es actualizado por [[Branch Control]] en cada ciclo de ejecución.

## Responsabilidades

1. **Almacenar dirección** de la próxima instrucción
2. **Proporcionar dirección** al [[Control Unit]] para fetch
3. **Actualizarse** según cálculo de [[Branch Control]]
4. **Reset** a dirección inicial (típicamente 0x00000000)

## Arquitectura

```
┌────────────────────────────────────────┐
│         PROGRAM COUNTER (PC)           │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  Registro 32 bits con Enable     │ │
│  │                                  │ │
│  │  Current PC [31:0]               │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
│            ▲              │            │
│            │              │            │
│      Next PC          Current PC       │
│   (from Branch Ctl)  (to Mem Ctl)      │
└────────────────────────────────────────┘
```

## Entradas

| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `PC_NEXT` | 32 bits | [[Branch Control]] | Próximo valor del PC |
| `LOAD` | 1 bit | [[Control Unit]] | Habilita carga del nuevo PC |
| `CLK` | 1 bit | Sistema | Reloj del sistema |
| `RESET` | 1 bit | Sistema | Reset sincrónico a 0x00000000 |

## Salidas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `PC_OUT` | 32 bits | Dirección actual (va al [[Control Unit]] para fetch) |

## Comportamiento

### En cada Ciclo de Reloj

```verilog
always @(posedge CLK) begin
    if (RESET) begin
        PC_OUT <= 32'h00000000;  // Reset a dirección 0
    end
    else if (LOAD) begin
        PC_OUT <= PC_NEXT;       // Cargar nuevo PC
    end
    // else: mantener valor actual
end
```

### Momento de Actualización

El PC se actualiza en diferentes momentos según el tipo de instrucción:

**Instrucción Normal (sin branch)**:
```
Ciclo N+2: EXECUTE completa
         → Branch Control calcula PC_NEXT = PC + 4
         → PC carga PC_NEXT
Ciclo N+3: Nuevo PC disponible para fetch
```

**Instrucción Branch Tomado**:
```
Ciclo N+2: EXECUTE completa
         → ALU calcula flags (ZERO, NEG)
         → Branch Control evalúa condición: TRUE
         → Branch Control calcula PC_NEXT = PC + 4 + (offset × 4)
         → PC carga PC_NEXT
Ciclo N+3: Nuevo PC (salto) disponible para fetch
```

**Instrucción Jump**:
```
Ciclo N+2: EXECUTE completa
         → Branch Control extrae address[25:0]
         → Branch Control calcula PC_NEXT = {PC[31:28], address, 2'b00}
         → PC carga PC_NEXT
Ciclo N+3: Nuevo PC (salto) disponible para fetch
```

**Instrucción Jump Register (JR)**:
```
Ciclo N+2: EXECUTE completa
         → Register File proporciona Rs_DATA
         → Branch Control asigna PC_NEXT = Rs_DATA
         → PC carga PC_NEXT
         → Register File actualiza SP = SP + 4
Ciclo N+3: Nuevo PC (return address) disponible para fetch
```

## Valores Iniciales

### Al Reset

```
PC = 0x00000000
```

**Significado**: El programa comienza en la dirección 0 de la memoria.

**Nota**: El assembler coloca la primera instrucción del programa en la dirección 0.

### Alineación

El PC **SIEMPRE** debe ser múltiplo de 4 (alineado a palabra):
- ✅ 0x00000000
- ✅ 0x00000004
- ✅ 0x00000008
- ❌ 0x00000001 (NO VÁLIDO)
- ❌ 0x00000002 (NO VÁLIDO)
- ❌ 0x00000003 (NO VÁLIDO)

**Razón**: Las instrucciones ocupan 32 bits = 4 bytes.

## Timing

### Timing Diagram - Instrucción Normal

```
CLK:     ___───___───___───___───___───___
         0   1   2   3   4   5   6

RESET:   ───___________________________

LOAD:    ___________________───_________

PC_OUT:  [0x00][0x00][0x00][0x00][0x04][0x04]
                               ↑ Cargado

PC_NEXT: [?  ][?  ][?  ][0x04][0x04][?  ]
                         ↑ Branch Ctl calcula
```

### Timing Diagram - Branch Tomado

```
CLK:     ___───___───___───___───___───___
         0   1   2   3   4   5   6

PC_OUT:  [0x04][0x04][0x04][0x04][0x20][0x20]
                               ↑ Salto a 0x20

NEXT_PC: [?  ][?  ][?  ][0x20][0x20][?  ]
                         ↑ PC+4+(offset×4)
                           = 0x04+4+(4×4)
                           = 0x20
```

## Conexión con otros Componentes

### Flujo de Datos

```
┌─────────────────┐
│  Branch Control │
│                 │
│  Calcula:       │
│  • PC + 4       │  NEXT_PC (32 bits)
│  • Branches     │──────────────┐
│  • Jumps        │              │
└─────────────────┘              ▼
                           ┌──────────┐
                           │    PC    │
                           │ (Registro│  PC_OUT (32 bits)
                           │  32-bit) │─────────┐
                           └──────────┘         │
                                                 ▼
                                        ┌──────────────┐
                                        │ Control Unit │
                                        │  (para fetch)│
                                        └──────────────┘
```

### Señales de Control

| Señal | Origen | Destino | Descripción |
|-------|--------|---------|-------------|
| NEXT_PC | [[Branch Control]] | PC | Próxima dirección |
| LOAD | [[Control Unit]] | PC | Habilita carga (usualmente en EXECUTE) |
| PC_OUT | PC | [[Control Unit]] | Dirección para fetch |
| PC_OUT | PC | [[Branch Control]] | Para calcular PC+4, branches |

## Casos Especiales

### 1. HALT

Cuando HALT ejecuta, el PC **NO** se actualiza más:

```
Estado:     EXECUTE → CHECK_INST → HALT_STATE → HALT_STATE → ...
PC:         0x100   → 0x100      → 0x100      → 0x100      → ...
```

**Razón**: Control Unit entra en loop infinito en HALT_STATE, nunca más genera LOAD=1.

### 2. Overflow de PC

¿Qué pasa si PC alcanza 0xFFFFFFFC y ejecuta PC+4?

```
PC actual:  0xFFFFFFFC
PC + 4:     0x00000000 (overflow a 0)
```

**Comportamiento**: Wraparound a 0 (generalmente no deseado en programas reales).

### 3. Jump a Dirección No-Alineada

Si un bug causa jump a dirección no-alineada (ej: 0x00000003):

```
PC = 0x00000003  ❌ NO ALINEADO
```

**Resultado**: Comportamiento indefinido
- Fetch de memoria puede devolver datos incorrectos
- Posible exception (en procesadores reales)
- En S-MIPS: Probablemente instrucción basura

**Prevención**: [[Branch Control]] debe garantizar alineación.

## Implementación en Logisim

### Componente

```
Tipo: Register (32-bit)
Configuración:
├─ Data Bits: 32
├─ Trigger: Rising Edge
├─ Enable Input: Yes
└─ Reset Value: 0x00000000
```

### Conexiones

```
Register "PC"
├─ D (input 32-bit): NEXT_PC (desde Branch Control)
├─ CLK (input 1-bit): CLK (sistema)
├─ EN (input 1-bit): LOAD (desde Control Unit)
├─ RESET (input 1-bit): RESET (sistema)
└─ Q (output 32-bit): PC_OUT
                      ├─ → Control Unit (para fetch)
                      └─ → Branch Control (para calcular next)
```

## Tests de Validación

### Test 1: Incremento Secuencial

```assembly
# Verificar PC incrementa +4 cada instrucción
addi r1, r0, 1    # PC=0x00
addi r2, r0, 2    # PC=0x04
addi r3, r0, 3    # PC=0x08
addi r4, r0, 4    # PC=0x0C
halt              # PC=0x10

# Inspeccionar PC en cada paso (debugger/probes)
# Debe ser: 0, 4, 8, C, 10
```

### Test 2: Branch Modifica PC

```assembly
    addi r1, r0, 5     # PC=0x00
    beq r0, r0, skip   # PC=0x04, salta a skip
    addi r2, r0, 99    # PC=0x08 (SKIP, no ejecuta)
skip:
    addi r3, r0, 10    # PC=0x0C (aquí llega después del salto)
    halt               # PC=0x10

# Verificar: r1=5, r2=0 (no se ejecutó), r3=10
```

### Test 3: Jump Absoluto

```assembly
    j target           # PC=0x00, salta a target
    addi r1, r0, 99    # PC=0x04 (SKIP)

target:
    addi r2, r0, 20    # PC=dirección de target
    halt

# Verificar: r1=0 (no se ejecutó), r2=20
```

## Análisis de Correctitud

### Estado Actual: ✅ IMPLEMENTADO

**Ubicación**: s-mips.circ:8236-8281

**Verificación necesaria**:
- [ ] Reset a 0x00000000 funciona
- [ ] Carga NEXT_PC correctamente cuando LOAD=1
- [ ] Mantiene valor cuando LOAD=0
- [ ] Salida PC_OUT conectada a Control Unit y Branch Control
- [ ] Timing correcto (actualización en rising edge)

### Tests Recomendados

1. **Manual stepping**: Avanzar instrucción por instrucción, verificar PC incrementa +4
2. **Branch testing**: Ejecutar tests/beq.asm, verificar PC salta correctamente
3. **Jump testing**: Ejecutar tests/jmp.asm, verificar saltos absolutos
4. **Reset testing**: Activar RESET, verificar PC vuelve a 0

## Troubleshooting

### Problema: PC no se actualiza

**Causas posibles**:
1. LOAD siempre = 0 (Control Unit no activa)
2. CLK no conectado
3. NEXT_PC no llega desde Branch Control

**Solución**: Verificar conexiones y Control Unit FSM

### Problema: PC incrementa en valores incorrectos

**Causas**:
1. Branch Control calcula mal PC+4
2. NEXT_PC no es múltiplo de 4

**Solución**: Verificar lógica de [[Branch Control]]

### Problema: Branches no funcionan

**Causas**:
1. PC siempre incrementa +4, ignora branches
2. Branch Control no calcula correctamente

**Solución**: Verificar señales de [[Branch Control]] → PC

## Enlaces Relacionados

- [[Branch Control]] - Calcula NEXT_PC
- [[Control Unit]] - Genera LOAD signal
- [[Data Path]] - Componente padre
- [[Memory Control]] - Usa PC_OUT para fetch

---

**Estado**: ✅ Implementado
**Validación**: ⚠️ Pendiente de tests
**Bloquea**: Nada (ya existe)
