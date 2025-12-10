# Random Generator (Generador de Números Aleatorios)

**Tipo**: Componente Auxiliar
**Estado**:✅  #implementado 
**Ubicación**: **NO EXISTE**
**Complejidad**: ⭐ Muy Simple
**Prioridad**: 🟡 MEDIA
**Tiempo estimado**: 2-3 horas

## Descripción

El Random Generator es un Linear Feedback Shift Register (LFSR) de 32 bits que genera números pseudoaleatorios para la instrucción RND. Usa un polinomio primitivo para garantizar un período máximo (2^32 - 1).

## Responsabilidades

1. **Generar valores pseudoaleatorios** en cada ciclo de reloj
2. **Proporcionar salida de 32 bits** al [[Data Path]]
3. **Mantener estado interno** que evoluciona con cada RND

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│           RANDOM GENERATOR (LFSR 32-bit)            │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │                                               │ │
│  │   [31][30][29][28]...[3][2][1][0]           │ │
│  │     │                  │   │   │             │ │
│  │     └──XOR────XOR──────┴───┴───┘             │ │
│  │             │                                 │ │
│  │             └──────────────────►[Feedback]    │ │
│  │                                               │ │
│  │   Polynomial: x^32 + x^22 + x^2 + x^1 + 1    │ │
│  │   Taps: bit[31], bit[21], bit[1], bit[0]     │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│                        │                            │
│                        ▼                            │
│              [32-bit Random Output]                 │
└─────────────────────────────────────────────────────┘
```

## Entradas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `CLK` | 1 bit | Reloj del sistema |
| `RESET` | 1 bit | Reset sincrónico (seed inicial) |
| `ENABLE` | 1 bit | Habilita actualización (cuando RND ejecuta) |

## Salidas

| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| `RANDOM_VALUE` | 32 bits | Valor pseudoaleatorio actual |

## Implementación en Logisim

### Componentes Necesarios

1. **32 Flip-Flops** (o 1 registro de 32 bits)
2. **3 XOR gates** (para taps)
3. **1 Multiplexer** (para feedback)

### Configuración del LFSR

**Polinomio Primitivo**: x^32 + x^22 + x^2 + x^1 + 1

**Taps** (posiciones donde se toma XOR):
- Bit 31 (MSB)
- Bit 21
- Bit 1
- Bit 0 (LSB)

### Lógica de Feedback

```verilog
// Calcular bit de feedback
feedback_bit = state[31] ^ state[21] ^ state[1] ^ state[0];

// Shift a la derecha e insertar feedback en MSB
next_state = {feedback_bit, state[31:1]};
```

### Pseudocódigo Logisim

```
Componentes:
├─ Register "LFSR_STATE" (32 bits)
│  └─ Initial value: 0xACE1 (seed arbitrario no-cero)
│
├─ Splitter (extraer bits individuales)
│  ├─ Output: bit[31]
│  ├─ Output: bit[21]
│  ├─ Output: bit[1]
│  └─ Output: bit[0]
│
├─ XOR Gate 1
│  ├─ Input A: bit[31]
│  └─ Input B: bit[21]
│
├─ XOR Gate 2
│  ├─ Input A: result of XOR1
│  └─ Input B: bit[1]
│
├─ XOR Gate 3 (feedback bit)
│  ├─ Input A: result of XOR2
│  └─ Input B: bit[0]
│
├─ Shifter (shift right by 1)
│  ├─ Input: current state
│  └─ Output: shifted value
│
├─ Combiner
│  ├─ Input MSB: feedback bit
│  └─ Input [30:0]: shifted value [31:1]
│
└─ Multiplexer (actualización condicional)
   ├─ Input 0: current state (ENABLE=0)
   ├─ Input 1: new state (ENABLE=1)
   └─ Select: ENABLE

Output: Current LFSR_STATE → RANDOM_VALUE
```

## Valores de Ejemplo

### Secuencia Inicial (seed = 0xACE1)

| Ciclo | Estado (hex) | Estado (bin) | Feedback |
|-------|--------------|--------------|----------|
| 0 | 0x0000ACE1 | 0...1010110011100001 | - |
| 1 | 0x00005670 | 0...0101011001110000 | 0 |
| 2 | 0x00002B38 | 0...0010101100111000 | 0 |
| 3 | 0x0000159C | 0...0001010110011100 | 0 |
| 4 | 0x00000ACE | 0...0000101011001110 | 0 |
| 5 | 0x00000567 | 0...0000010101100111 | 0 |
| 6 | 0x800002B3 | 1...0000001010110011 | 1 |
| ... | ... | ... | ... |

**Nota**: El período del LFSR es 2^32 - 1 = 4,294,967,295 ciclos antes de repetirse.

## Consideraciones Importantes

### 1. Seed Inicial

**NUNCA usar 0x00000000 como seed** - el LFSR se quedaría en 0 forever.

**Opciones de seed**:
- Fijo: 0xACE1 (usado en ejemplo)
- Basado en tiempo: No disponible en Logisim
- Hardcoded: Cualquier valor no-cero

### 2. Calidad de Aleatoriedad

LFSR produce secuencia **pseudoaleatoria**, NO verdaderamente aleatoria:
- ✅ Suficiente para pruebas y demos
- ✅ Período muy largo (4 mil millones de valores)
- ❌ NO usar para criptografía
- ❌ Secuencia predecible si se conoce el estado

### 3. Actualización

El LFSR puede:
- **Opción A**: Actualizarse cada CLK (genera nuevo valor continuamente)
- **Opción B**: Actualizarse solo cuando ENABLE=1 (cuando RND ejecuta)

**Recomendación**: Opción B (solo cuando RND ejecuta)

## Conexión con Data Path

### Integración

```
Random Generator → [[MUX Writeback]] (entrada WR_RANDOM)
                → Seleccionado cuando WR_SEL=RANDOM

Instruction Decoder → Detecta RND Rd
                    → Activa ENABLE en Random Generator
                    → Activa WR_SEL=RANDOM
                    → Activa WR_EN=1
                    → Especifica WR_ADDR=Rd
```

### Señales

- **ENABLE**: Generado por [[Instruction Decoder]] cuando opcode=RND
- **RANDOM_VALUE**: Conectado a puerto RANDOM del [[MUX Writeback]]

## Instrucción RND

### Formato

```
Tipo J: [opcode(6)][address(26)]
RND Rd: opcode = 0x3F (especial), Rd codificado en address[4:0]
```

### Comportamiento

```
RND R5:
  1. Decoder detecta opcode RND
  2. ENABLE=1 → Random Generator actualiza
  3. RANDOM_VALUE → MUX Writeback
  4. WR_EN=1, WR_ADDR=R5
  5. Register File escribe RANDOM_VALUE en R5
```

## Tests de Validación

### Test 1: Valor No-Cero

```assembly
# Test que RND no retorna 0 siempre
rnd r1
addi r2, r0, 0
beq r1, r2, fail    # Si r1 == 0, sospechoso
j success

fail:
  addi r10, r0, 1   # FAIL
  halt

success:
  addi r10, r0, 2   # PASS
  halt
```

### Test 2: Valores Diferentes

```assembly
# Test que RND genera valores distintos
rnd r1
rnd r2
beq r1, r2, fail    # Si r1 == r2, mal funcionamiento
j success

fail:
  addi r10, r0, 1   # FAIL (puede fallar 1/4B veces)
  halt

success:
  addi r10, r0, 2   # PASS
  halt
```

### Test 3: Distribución (Informal)

```assembly
# Generar 10 valores y verificar que no todos son iguales
rnd r1
rnd r2
rnd r3
rnd r4
rnd r5
rnd r6
rnd r7
rnd r8
rnd r9
rnd r10

# Verificación manual de que hay variedad
# (test informal, requiere observación)
halt
```

## Troubleshooting

### Problema: Siempre retorna 0

**Causa**: Seed inicial = 0
**Solución**: Cambiar initial value del registro a cualquier valor no-cero (ej: 0xACE1)

### Problema: Secuencia se repite rápidamente

**Causa**: Polinomio incorrecto o taps mal conectados
**Solución**: Verificar taps en bits 31, 21, 1, 0

### Problema: Siempre retorna el mismo valor

**Causa**: ENABLE no funciona, registro no se actualiza
**Solución**: Verificar que [[Instruction Decoder]] activa ENABLE cuando RND ejecuta

## Archivo en s-mips.circ

**Ubicación esperada**: Subcircuito "Random Generator" dentro de [[Data Path]]

**Conexiones**:
```
Data Path
├─ Random Generator (subcircuito)
│  ├─ IN: CLK (del sistema)
│  ├─ IN: ENABLE (de Instruction Decoder)
│  └─ OUT: RANDOM_VALUE (32 bits)
│
└─ MUX Writeback
   ├─ Input RANDOM: RANDOM_VALUE
   └─ Select: WR_SEL
```

## Estimación de Implementación

**Complejidad**: ⭐ Muy Simple
**Tiempo**: 2-3 horas
**Prioridad**: 🟡 Media (solo afecta 1 instrucción)

### Desglose

1. Crear subcircuito "Random Generator" (30 min)
2. Implementar LFSR con taps (45 min)
3. Conectar a Data Path (30 min)
4. Modificar Instruction Decoder para RND (30 min)
5. Validar con tests (45 min)

**Total**: 2-3 horas

## Enlaces Relacionados

- [[Data Path]] - Componente padre
- [[Instruction Decoder]] - Genera ENABLE signal
- [[MUX Writeback]] - Selecciona RANDOM_VALUE
- [[Register File]] - Destino final del valor aleatorio
- [[Test Status]] - tests/rnd.asm para validación

---

**Prioridad**: Baja-Media (puede implementarse después de Control Unit y Memory Control)
**Impacto**: Solo afecta instrucción RND
**Bloquea**: 1 test (tests/rnd.asm)
