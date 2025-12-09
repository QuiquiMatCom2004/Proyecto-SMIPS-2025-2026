# S-MIPS Complete Architecture (Arquitectura Completa)

**Tipo**: Documento de Arquitectura
**Última actualización**: 2025-12-09

## Visión General del Sistema

El procesador S-MIPS (Simplified MIPS) es un procesador RISC de 32 bits diseñado para el curso de Arquitectura de Computadoras de la Universidad de La Habana. Implementa un subconjunto del conjunto de instrucciones MIPS con optimizaciones para simplicidad educativa.

## Jerarquía de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                      S-MIPS BOARD                               │
│                    (NO MODIFICAR)                               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                        CPU                             │    │
│  │                  (TU TRABAJO AQUÍ)                     │    │
│  │                                                        │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │           CONTROL UNIT 🔴                    │     │    │
│  │  │  • FSM de 12 estados                         │     │    │
│  │  │  • Genera señales de control                 │     │    │
│  │  │  • Coordina fetch-decode-execute             │     │    │
│  │  └──────────────────────────────────────────────┘     │    │
│  │                     ↓                                  │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │         MEMORY CONTROL 🔴                    │     │    │
│  │  │  • Interfaz con RAM asíncrona                │     │    │
│  │  │  • Traducción de direcciones                 │     │    │
│  │  │  • Conversión little-endian                  │     │    │
│  │  │  • RT/WT cycle management                    │     │    │
│  │  └──────────────────────────────────────────────┘     │    │
│  │                     ↓                                  │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │           DATA PATH 🟡                       │     │    │
│  │  │                                              │     │    │
│  │  │  ┌────────────────────────────────────┐     │     │    │
│  │  │  │ Instruction Register ✅           │     │     │    │
│  │  │  └────────────────────────────────────┘     │     │    │
│  │  │                ↓                            │     │    │
│  │  │  ┌────────────────────────────────────┐     │     │    │
│  │  │  │ Instruction Decoder ✅            │     │     │    │
│  │  │  │ • 40+ instrucciones               │     │     │    │
│  │  │  │ • Control signals                 │     │     │    │
│  │  │  └────────────────────────────────────┘     │     │    │
│  │  │         ↓         ↓          ↓             │     │    │
│  │  │  ┌──────────┐ ┌──────┐ ┌──────────┐       │     │    │
│  │  │  │Register  │ │ ALU  │ │ Branch   │       │     │    │
│  │  │  │File ✅  │ │  ✅  │ │Control ✅│       │     │    │
│  │  │  │32 regs + │ │40+ops│ │PC calc   │       │     │    │
│  │  │  │Hi/Lo     │ │      │ │          │       │     │    │
│  │  │  └──────────┘ └──────┘ └──────────┘       │     │    │
│  │  │                                            │     │    │
│  │  │  ┌────────────────────────────────────┐    │     │    │
│  │  │  │ Random Generator 🔴               │    │     │    │
│  │  │  │ • LFSR 32-bit                     │    │     │    │
│  │  │  └────────────────────────────────────┘    │     │    │
│  │  │                                            │     │    │
│  │  │  ┌────────────────────────────────────┐    │     │    │
│  │  │  │ MUX Writeback ✅                  │    │     │    │
│  │  │  │ • 8 entradas                      │    │     │    │
│  │  │  └────────────────────────────────────┘    │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              CACHE SYSTEM 🔴                           │ │
│  │                                                        │ │
│  │  ┌──────────────────┐      ┌──────────────────┐      │ │
│  │  │ Instruction      │      │ Data Cache       │      │ │
│  │  │ Cache            │      │ (opcional)       │      │ │
│  │  │ (4+ líneas)      │      │ (4+ líneas)      │      │ │
│  │  │ Direct-Mapped    │      │ Direct-Mapped    │      │ │
│  │  └──────────────────┘      └──────────────────┘      │ │
│  │         ↓                           ↓                 │ │
│  │         └───────────┬───────────────┘                 │ │
│  │                     ↓                                 │ │
│  │         ┌───────────────────────┐                     │ │
│  │         │   Memory Control      │                     │ │
│  │         └───────────────────────┘                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                             ↓                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    RAM (1 MB)                          │ │
│  │              (NO MODIFICAR)                            │ │
│  │  • 65,536 bloques × 16 bytes                          │ │
│  │  • 4 bancos (Bank0, Bank1, Bank2, Bank3)             │ │
│  │  • Asíncrono (RT/WT cycles)                           │ │
│  │  • Big-endian interno                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              RAM Dispatcher                            │ │
│  │              (NO MODIFICAR)                            │ │
│  │  • Testing infrastructure                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Leyenda:
✅ = Implementado y funcional
🟡 = Parcialmente implementado
🔴 = No implementado (faltante)
```

## Especificaciones del Sistema

### CPU
- **Arquitectura**: RISC de 32 bits
- **Conjunto de instrucciones**: Subconjunto MIPS simplificado
- **Registros**: 32 de propósito general + Hi + Lo + PC
- **Pipeline**: No pipelined (ciclo único multi-ciclo)
- **Frecuencia**: Variable (Logisim simulation)

### Memoria
- **Tamaño total**: 1 MB (2^20 bytes)
- **Organización**: 65,536 bloques de 16 bytes
- **Palabras por bloque**: 4 words de 32 bits
- **Bancos**: 4 (Bank0, Bank1, Bank2, Bank3)
- **Alineación**: 4 bytes (instrucciones y datos)
- **Endianness**: Little-endian (CPU) ↔ Big-endian (RAM)
- **Interfaz**: Asíncrona con RT/WT cycles

### Caché (Requerido para aprobar)
- **Mínimo (aprobar)**: Instruction Cache, 4+ líneas, direct-mapped
- **Recomendado (extraordinario)**: + Data Cache, 4+ líneas
- **Avanzado (mundial)**: Set-associative o fully-associative

## Flujo de Ejecución de Instrucciones

```
┌─────────────────────────────────────────────────────────┐
│                  CICLO DE INSTRUCCIÓN                   │
└─────────────────────────────────────────────────────────┘
           │
           ↓
    ┌──────────────┐
    │ 1. FETCH     │  Control Unit solicita instrucción
    │              │  • PC → Instruction Cache
    │              │  • Si hit: 1 ciclo
    │              │  • Si miss: Memory Control → RAM (RT cycles)
    └──────────────┘
           │
           ↓
    ┌──────────────┐
    │ 2. DECODE    │  Instruction Decoder analiza
    │              │  • Extrae opcode, Rs, Rt, Rd, etc.
    │              │  • Genera señales de control
    └──────────────┘
           │
           ↓
    ┌──────────────┐
    │ 3. EXECUTE   │  Data Path ejecuta
    │              │  • Register File → ALU
    │              │  • ALU opera según ALU_OP
    │              │  • Branch Control calcula PC
    └──────────────┘
           │
           ↓
    ┌──────────────┐
    │ 4. MEMORY    │  (Solo LW/SW)
    │              │  • Data Cache (si existe)
    │              │  • Si miss: Memory Control → RAM
    └──────────────┘
           │
           ↓
    ┌──────────────┐
    │ 5. WRITEBACK │  Resultado a registros
    │              │  • MUX Writeback selecciona fuente
    │              │  • Register File escribe
    └──────────────┘
           │
           ↓
    ┌──────────────┐
    │ 6. NEXT PC   │  Actualizar Program Counter
    │              │  • PC = PC+4 (secuencial)
    │              │  • PC = branch target (branch)
    │              │  • PC = jump target (jump)
    └──────────────┘
           │
           └──→ Repetir
```

### Latencias por Tipo de Instrucción

#### Sin Caché (Estado actual - LENTO)
```
Tipo R (ADD, SUB, etc.):
    FETCH (RT cycles) + DECODE (1) + EXECUTE (1) + WRITEBACK (1)
    = RT + 3 cycles

Tipo I aritmético (ADDI, ORI, etc.):
    FETCH (RT) + DECODE (1) + EXECUTE (1) + WRITEBACK (1)
    = RT + 3 cycles

LW (Load Word):
    FETCH (RT) + DECODE (1) + EXECUTE (1) + MEMORY (RT) + WRITEBACK (1)
    = 2×RT + 4 cycles

SW (Store Word):
    FETCH (RT) + DECODE (1) + EXECUTE (1) + MEMORY (WT)
    = RT + WT + 3 cycles

Branch (BEQ, BNE, etc.):
    FETCH (RT) + DECODE (1) + EXECUTE (1) + NEXT_PC (1)
    = RT + 3 cycles

Jump (J):
    FETCH (RT) + DECODE (1) + NEXT_PC (1)
    = RT + 2 cycles
```

#### Con Instruction Cache (Hit rate > 80%)
```
Tipo R: 1 (I-Cache hit) + 1 (DECODE) + 1 (EXECUTE) + 1 (WB) = 4 cycles
LW:     1 + 1 + 1 + RT (D-Cache miss) + 1 = RT + 4 cycles
```

#### Con Ambas Cachés (Hit rate > 80%)
```
Tipo R: 4 cycles (sin acceso a memoria)
LW:     1 + 1 + 1 + 1 (D-Cache hit) + 1 = 5 cycles
SW:     1 + 1 + 1 + 1 (D-Cache hit, write-back) = 4 cycles
```

**Mejora de performance**: ~RT×10 veces más rápido con cachés

## Formatos de Instrucción

### R-Type (Register)
```
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ opcode │   Rs   │   Rt   │   Rd   │ shamt  │ funct  │
│ 6 bits │ 5 bits │ 5 bits │ 5 bits │ 5 bits │ 6 bits │
└────────┴────────┴────────┴────────┴────────┴────────┘

Ejemplos: ADD, SUB, AND, OR, XOR, NOR, SLT, MULT, DIV, SLL, SRL, SRA
```

### I-Type (Immediate)
```
┌────────┬────────┬────────┬────────────────────────┐
│ opcode │   Rs   │   Rt   │      immediate         │
│ 6 bits │ 5 bits │ 5 bits │       16 bits          │
└────────┴────────┴────────┴────────────────────────┘

Ejemplos: ADDI, ANDI, ORI, XORI, SLTI, BEQ, BNE, BLEZ, BGTZ, LW, SW, PUSH, POP
```

### J-Type (Jump)
```
┌────────┬──────────────────────────────────────────┐
│ opcode │              address                     │
│ 6 bits │             26 bits                      │
└────────┴──────────────────────────────────────────┘

Ejemplos: J, JAL (si existe), HALT, TTY, KBD, RND
```

## Conjunto de Instrucciones Completo

### Aritméticas (7 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| ADD Rd, Rs, Rt | R | Rd = Rs + Rt |
| SUB Rd, Rs, Rt | R | Rd = Rs - Rt |
| ADDI Rt, Rs, Imm | I | Rt = Rs + SignExt(Imm) |
| MULT Rs, Rt | R | Hi:Lo = Rs × Rt (signed) |
| MULU Rs, Rt | R | Hi:Lo = Rs × Rt (unsigned) |
| DIV Rs, Rt | R | Lo = Rs / Rt, Hi = Rs % Rt (signed) |
| DIVU Rs, Rt | R | Lo = Rs / Rt, Hi = Rs % Rt (unsigned) |

### Lógicas (7 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| AND Rd, Rs, Rt | R | Rd = Rs & Rt |
| OR Rd, Rs, Rt | R | Rd = Rs \| Rt |
| XOR Rd, Rs, Rt | R | Rd = Rs ^ Rt |
| NOR Rd, Rs, Rt | R | Rd = ~(Rs \| Rt) |
| ANDI Rt, Rs, Imm | I | Rt = Rs & ZeroExt(Imm) |
| ORI Rt, Rs, Imm | I | Rt = Rs \| ZeroExt(Imm) |
| XORI Rt, Rs, Imm | I | Rt = Rs ^ ZeroExt(Imm) |

### Shift (3 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| SLL Rd, Rt, Shamt | R | Rd = Rt << Shamt |
| SRL Rd, Rt, Shamt | R | Rd = Rt >> Shamt (logical) |
| SRA Rd, Rt, Shamt | R | Rd = Rt >> Shamt (arithmetic) |

### Comparación (2 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| SLT Rd, Rs, Rt | R | Rd = (Rs < Rt) ? 1 : 0 (signed) |
| SLTI Rt, Rs, Imm | I | Rt = (Rs < SignExt(Imm)) ? 1 : 0 |

### Branches (5 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| BEQ Rs, Rt, Offset | I | if (Rs == Rt) PC = PC + 4 + SignExt(Offset)<<2 |
| BNE Rs, Rt, Offset | I | if (Rs != Rt) PC = PC + 4 + SignExt(Offset)<<2 |
| BLEZ Rs, Offset | I | if (Rs <= 0) PC = PC + 4 + SignExt(Offset)<<2 |
| BGTZ Rs, Offset | I | if (Rs > 0) PC = PC + 4 + SignExt(Offset)<<2 |
| BLTZ Rs, Offset | I | if (Rs < 0) PC = PC + 4 + SignExt(Offset)<<2 |

### Jumps (2 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| J Address | J | PC = {PC[31:28], Address[25:0], 2'b00} |
| JR Rs | R | PC = Rs, SP = SP + 4 |

### Memoria (2 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| LW Rt, Offset(Rs) | I | Rt = Memory[Rs + SignExt(Offset)] |
| SW Rt, Offset(Rs) | I | Memory[Rs + SignExt(Offset)] = Rt |

### Stack (2 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| PUSH Rs | I | SP = SP - 4, Memory[SP] = Rs |
| POP Rt | I | Rt = Memory[SP], SP = SP + 4 |

### Especiales (6 instrucciones)
| Instrucción | Tipo | Operación |
|-------------|------|-----------|
| MFHI Rd | R | Rd = Hi |
| MFLO Rd | R | Rd = Lo |
| TTY Rs | J | Output Rs[6:0] to terminal |
| KBD Rd | J | Rd = keyboard input (or -1 if none) |
| RND Rd | J | Rd = random number |
| HALT | J | Stop execution |

**Total**: 40+ instrucciones

## Interfaz de Memoria

### Dirección de Memoria (32 bits)

```
┌──────────────────┬──────────┬────────────┬────────┐
│  Block Address   │  Word    │   Byte     │ Align  │
│    16 bits       │ Offset   │  Offset    │        │
│   bits [19:4]    │  [3:2]   │   [1:0]    │  = 00  │
└──────────────────┴──────────┴────────────┴────────┘

Block Address: Selecciona uno de 65,536 bloques
Word Offset:   Selecciona una de 4 palabras dentro del bloque
Byte Offset:   Debe ser 00 (alineación a 4 bytes)
```

### RAM Interface (Asíncrona)

#### Entradas
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| ADDR | 16 bits | Block address (dirección[19:4]) |
| CS | 1 bit | Chip Select (1 = activo) |
| R/W | 1 bit | 0 = Read, 1 = Write |
| I0-I3 | 4×32 bits | Datos a escribir (4 words) |
| MASK | 4 bits | Selección de bancos (bit i = habilitar banco i) |

#### Salidas
| Puerto | Ancho | Descripción |
|--------|-------|-------------|
| O0-O3 | 4×32 bits | Datos leídos (4 words del bloque) |
| RT | N bits | Read Time (ciclos de lectura) |
| WT | N bits | Write Time (ciclos de escritura) |

### Conversión Little-Endian

```
CPU (Little-Endian):     Byte 0 es LSB, Byte 3 es MSB
    0x12345678 → [0x78, 0x56, 0x34, 0x12]

RAM (Big-Endian):        Byte 0 es MSB, Byte 3 es LSB
    0x12345678 → [0x12, 0x34, 0x56, 0x78]

Memory Control debe:
    WRITE: Bit-reverse antes de escribir a RAM
    READ:  Bit-reverse después de leer de RAM

Bit-reverse: swap bit 0 ↔ bit 31, bit 1 ↔ bit 30, ..., bit 15 ↔ bit 16
```

## Estado de Implementación del Proyecto

### Componentes Implementados (11/21) - 52%

| Componente | Estado | Ubicación |
|------------|--------|-----------|
| [[ALU]] | ✅ Completo | Data Path → ALU |
| [[Register File]] | ✅ Completo | Data Path → Register File |
| [[Instruction Decoder]] | ✅ Completo | Data Path → Instruction Decoder |
| [[Branch Control]] | ✅ Completo | Data Path → Branch Control |
| Program Counter | ✅ Completo | Data Path → PC |
| Instruction Register | ✅ Completo | Data Path → IR |
| MUX Writeback | ✅ Completo | Data Path → MUX |
| MUX ALU_B | ✅ Completo | Data Path → MUX |
| MUX Rd/Rt | ✅ Completo | Data Path → MUX |
| Sign Extender | ✅ Completo | Data Path → Extender |
| Zero Extender | ✅ Completo | Data Path → Extender |

### Componentes Faltantes (10/21) - 48%

| Componente | Prioridad | Tiempo Estimado |
|------------|-----------|-----------------|
| [[Control Unit]] | 🚨🚨🚨 CRÍTICO | 7-10 días |
| [[Memory Control]] | 🚨🚨 BLOQUEANTE | 5-6 días |
| [[Instruction Cache]] | 🔴 ALTA | 7-10 días |
| [[Data Cache]] | 🟡 MEDIA | 5-7 días |
| [[Random Generator]] | 🟢 BAJA | 2-3 horas |

**Total trabajo pendiente**: 40-50 días
**Deadline**: 31 enero 2025 (52 días restantes)
**Margen**: AJUSTADO

## Criterios de Calificación

### Requisitos Mínimos (3 puntos - SUSPENSO)
- ❌ Control Unit funcional
- ❌ Memory Control funcional
- ❌ Data Path completo
- ❌ Procesador ejecuta instrucciones básicas

### Para Aprobar (5 puntos - Primera Convocatoria)
- ✅ Todo lo anterior
- ❌ Instruction Cache (4+ líneas, direct-mapped)
- ❌ Tests básicos pasando

### Para Extraordinario (5 puntos - Segunda Convocatoria)
- ✅ Todo lo anterior
- ❌ Data Cache (4+ líneas)
- ❌ Tests completos pasando
- ❌ Performance mejorada

### Para Mundial (5 puntos - Tercera Convocatoria)
- ✅ Todo lo anterior
- ❌ Set-Associative o Fully-Associative cache
- ❌ LRU replacement policy
- ❌ Performance optimizada
- ❌ Costo ≤ 100 unidades

## Referencias

- [[Dashboard]] - Estado global del proyecto
- [[Control Unit]] - FSM principal
- [[Memory Control]] - Interfaz con RAM
- [[Cache System Overview]] - Sistema de cachés
- [[Data Path]] - Flujo de datos
- Documentación: `s-mips.pdf` - Especificación completa
- Documentación: `WORKFLOW_PROYECTO.md` - Plan de trabajo

---
**Creado**: 2025-12-09
**Propósito**: Visión arquitectónica completa del procesador S-MIPS
**Estado**: DOCUMENTACIÓN COMPLETA - Implementación 52%
