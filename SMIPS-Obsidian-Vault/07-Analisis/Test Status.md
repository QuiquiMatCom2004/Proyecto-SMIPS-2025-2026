# Test Status (Estado de las Pruebas)

**Tipo**: Reporte de Testing
**Última actualización**: 2025-12-09

## Estado Global de Testing

```
┌─────────────────────────────────────────────────────────┐
│             ESTADO DE TESTING                           │
├─────────────────────────────────────────────────────────┤
│ Tests ejecutados:          0 / 20+ (0%)                 │
│ Tests pasados:             0                            │
│ Tests fallidos:            N/A                          │
│ Componentes validados:     0 / 21 (0%)                  │
│                                                         │
│ Estado:  🔴 SIN VALIDACIÓN                             │
└─────────────────────────────────────────────────────────┘
```

## ⚠️ RAZÓN: Procesador No Funcional

**El procesador NO puede ejecutar tests porque faltan componentes críticos:**

1. 🚨🚨🚨 [[Control Unit]] - Sin esto, no hay fetch-decode-execute cycle
2. 🚨🚨 [[Memory Control]] - Sin esto, no hay acceso a memoria
3. 🔴 [[Random Generator]] - Instrucción RND no funciona

**Resultado**: Imposible cargar o ejecutar programas de prueba

## Tests Disponibles (tests/ directory)

### Operaciones Básicas (10 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 1 | `add.asm` | ADD | ⚠️ No ejecutado |
| 2 | `addi.asm` | ADDI | ⚠️ No ejecutado |
| 3 | `sub.asm` | SUB | ⚠️ No ejecutado |
| 4 | `and.asm` | AND | ⚠️ No ejecutado |
| 5 | `andi.asm` | ANDI | ⚠️ No ejecutado |
| 6 | `or.asm` | OR | ⚠️ No ejecutado |
| 7 | `ori.asm` | ORI | ⚠️ No ejecutado |
| 8 | `xor.asm` | XOR | ⚠️ No ejecutado |
| 9 | `xori.asm` | XORI | ⚠️ No ejecutado |
| 10 | `nor.asm` | NOR | ⚠️ No ejecutado |

### Multiplicación y División (4 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 11 | `mult.asm` | MULT, MFHI, MFLO | ⚠️ No ejecutado |
| 12 | `mulu.asm` | MULU, MFHI, MFLO | ⚠️ No ejecutado |
| 13 | `div.asm` | DIV, MFHI, MFLO | ⚠️ No ejecutado |
| 14 | `divu.asm` | DIVU, MFHI, MFLO | ⚠️ No ejecutado |

### Comparación (2 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 15 | `slt.asm` | SLT | ⚠️ No ejecutado |
| 16 | `slti.asm` | SLTI | ⚠️ No ejecutado |

### Branches (5 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 17 | `beq.asm` | BEQ | ⚠️ No ejecutado |
| 18 | `bne.asm` | BNE | ⚠️ No ejecutado |
| 19 | `blez.asm` | BLEZ | ⚠️ No ejecutado |
| 20 | `bgtz.asm` | BGTZ | ⚠️ No ejecutado |
| 21 | `bltz.asm` | BLTZ | ⚠️ No ejecutado |

### Jumps (1 test)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 22 | `jmp.asm` | J, JR | ⚠️ No ejecutado |

### Memoria (3 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 23 | `mem.asm` | LW, SW | ⚠️ No ejecutado |
| 24 | `sw-lw.asm` | SW, LW (coherencia) | ⚠️ No ejecutado |
| 25 | `sw-push-pop.asm` | SW, PUSH, POP | ⚠️ No ejecutado |

### Stack (3 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 26 | `push.asm` | PUSH | ⚠️ No ejecutado |
| 27 | `pop.asm` | POP | ⚠️ No ejecutado |
| 28 | `push-pop.asm` | PUSH, POP | ⚠️ No ejecutado |

### Especiales (3 tests)

| Test | Archivo | Instrucciones Probadas | Estado |
|------|---------|------------------------|--------|
| 29 | `tty.asm` | TTY | ⚠️ No ejecutado |
| 30 | `rnd.asm` | RND | ⚠️ No ejecutado (falta Random Gen) |
| 31 | `halt.asm` | HALT | ⚠️ No ejecutado |

### Programas Complejos (3 tests)

| Test | Archivo | Líneas | Instrucciones | Estado |
|------|---------|--------|---------------|--------|
| 32 | `liset.asm` | 1765 | Mix completo | ⚠️ No ejecutado |
| 33 | `lemp.asm` | 1222 | Mix completo | ⚠️ No ejecutado |
| 34 | `div-mult-bne.asm` | - | DIV, MULT, BNE | ⚠️ No ejecutado |

## Cómo Ejecutar Tests

### Comando Automático (Recomendado)

```bash
# Desde la raíz del proyecto
./test.py tests s-mips.circ -o ./tests-out

# Esto:
# 1. Encuentra todos los .asm en tests/
# 2. Ensambla cada uno
# 3. Ejecuta en Logisim
# 4. Compara salida con #prints en .asm
# 5. Reporta OK o FAIL
```

### Test Manual Individual

```bash
# 1. Ensamblar programa
python3 assembler.py tests/add.asm -o tests/add

# 2. Abrir s-mips.circ en Logisim
# 3. Cargar Bank en RAM Dispatcher
# 4. Ejecutar simulación
# 5. Verificar salida en terminal
```

## Criterios de Éxito por Test

Cada `.asm` incluye directiva `#prints <expected_output>`:

```assembly
# Ejemplo: add.asm
ADDI R1, R0, 10
ADDI R2, R0, 20
ADD R3, R1, R2
TTY R3

#prints 30
```

**Test pasa si**: Salida en terminal = "30"

## Plan de Testing Recomendado

### Fase 1: Tests Básicos (Después de Control Unit + Memory Control)

**Objetivo**: Validar procesador funcional mínimo

| Test | Propósito |
|------|-----------|
| `addi.asm` | Verificar fetch, decode, ALU, writeback |
| `add.asm` | Verificar lectura dual de registros |
| `beq.asm` | Verificar branch control |
| `mem.asm` | Verificar LW/SW (Memory Control) |

**Esperado**: 4/4 tests pasando

**Si falla**: Depurar componente específico

### Fase 2: Tests Completos (Después de todos los componentes)

**Objetivo**: Validar todas las instrucciones

| Categoría | Tests | Componentes Validados |
|-----------|-------|-----------------------|
| Aritméticas | 10 tests | ALU, Register File |
| Mult/Div | 4 tests | ALU Hi/Lo |
| Branches | 5 tests | Branch Control, ALU flags |
| Memoria | 3 tests | Memory Control, Data Cache |
| Stack | 3 tests | Memory Control, Register File (R31) |
| Especiales | 3 tests | Random Generator, TTY, HALT |

**Esperado**: 28+/31 tests pasando

### Fase 3: Tests de Performance (Con cachés)

**Objetivo**: Validar mejora de performance

| Test | Métrica | Sin Caché | Con I-Cache | Con Ambas |
|------|---------|-----------|-------------|-----------|
| `liset.asm` | Cycles | ~100k | ~30k | ~10k |
| Loop pequeño | Cycles | ~1000 | ~200 | ~100 |
| Hit rate | % | N/A | >80% | >85% |

## Análisis de Cobertura

### Instrucciones NO Cubiertas por Tests (Potencial)

| Instrucción | Razón |
|-------------|-------|
| SLL, SRL, SRA | No hay tests dedicados (verificar si están en programas complejos) |
| BLTZ | Tiene test dedicado |
| KBD | Requiere interacción de usuario (difícil de automatizar) |

**Recomendación**: Crear tests adicionales para SLL/SRL/SRA si no están cubiertos.

## Tests de Caché (Adicionales - Crear manualmente)

### Test 1: Cold Start (I-Cache)
```assembly
# Primera ejecución: todos misses
ADDI R1, R0, 1
ADDI R2, R0, 2
ADDI R3, R0, 3
# ...
```

**Verificar**:
- Primeras instrucciones: misses
- Instrucciones subsecuentes en mismo bloque: hits

### Test 2: Loop Hit Rate (I-Cache)
```assembly
loop:
    ADDI R1, R1, 1
    BEQ R1, R10, end
    J loop
end:
    HALT
```

**Verificar**:
- Primera iteración: misses
- Iteraciones siguientes: todos hits (loop cabe en caché)
- Hit rate > 90%

### Test 3: Conflict Misses (I-Cache)
```assembly
# Instrucciones separadas por tamaño de caché
# Mapean a misma línea → conflict
```

**Verificar**:
- Reemplazos ocurren correctamente
- No corrupción de datos

### Test 4: Data Cache Coherencia
```assembly
SW R1, 0(R2)
LW R3, 0(R2)
# R3 debe = R1
```

**Verificar**:
- Write-through: RAM y caché consistentes
- Read después de write: dato correcto

## Depuración de Fallos

### Si test falla en FETCH
**Posibles causas**:
- Control Unit: Estado START_FETCH incorrecto
- Instruction Cache: Hit/miss logic incorrecta
- Memory Control: RT cycles incorrectos
- RAM: Address translation incorrecta

**Depuración**:
1. Verificar PC tiene dirección correcta
2. Verificar señal FETCH_REQ activa
3. Verificar I-Cache devuelve instrucción correcta
4. Verificar timing (RT cycles esperados)

### Si test falla en EXECUTE
**Posibles causas**:
- Instruction Decoder: Señales de control incorrectas
- ALU: Operación incorrecta
- Register File: Lectura/escritura incorrecta

**Depuración**:
1. Verificar instrucción decodificada correctamente
2. Verificar operandos de ALU correctos
3. Verificar resultado de ALU correcto
4. Verificar flags (ZERO, NEGATIVE)

### Si test falla en MEMORY
**Posibles causas**:
- Memory Control: Address translation incorrecta
- Little-endian conversion: Bit-reverse incorrecto
- Data Cache: Hit/miss logic incorrecta

**Depuración**:
1. Verificar dirección traducida correctamente (byte → block)
2. Verificar word offset correcto
3. Verificar MASK correcto
4. Verificar endianness conversion

### Si test falla en WRITEBACK
**Posibles causas**:
- MUX Writeback: Selección incorrecta
- Control Unit: REG_WRITE no activado

**Depuración**:
1. Verificar fuente de dato correcto (ALU, Memory, Hi/Lo)
2. Verificar registro destino correcto (Rd vs Rt)
3. Verificar REG_WRITE = 1

## Herramientas de Depuración en Logisim

### Probes (Sondas)
- Colocar en señales críticas: PC, Instruction, ALU_RESULT, etc.
- Ver valores en tiempo real

### Tick Frequency
- Cambiar a 1 Hz para stepping manual
- "Tick Once" para avanzar 1 ciclo

### Breakpoints (Condicionales)
- Logisim no tiene breakpoints nativos
- Alternativa: Agregar lógica condicional que detenga reloj

### Logging
- Usar componentes TTY para output de depuración
- Imprimir valores intermedios

## Métricas de Éxito

### Mínimo (Para Aprobar)
- ✅ Tests básicos (4/4) pasando
- ✅ Tests aritméticos (10/10) pasando
- ✅ Tests de memoria (3/3) pasando
- ✅ Tests de branches (5/5) pasando

**Total**: 22/34 tests mínimo

### Objetivo (Para Extraordinario)
- ✅ Todos los tests básicos (28/31) pasando
- ✅ Hit rate I-Cache > 80%
- ✅ Hit rate D-Cache > 80% (si existe)

### Ideal (Para Mundial)
- ✅ Todos los tests (31/31) pasando
- ✅ Programas complejos (liset, lemp) ejecutando correctamente
- ✅ Hit rate > 90% en ambas cachés
- ✅ Performance optimizada

## Próximos Pasos

1. **Implementar Control Unit** (7-10 días)
2. **Implementar Memory Control** (5-6 días)
3. **Ejecutar tests básicos** (2 días)
   - add.asm, addi.asm, beq.asm, mem.asm
4. **Depurar fallos** (2-3 días)
5. **Implementar Instruction Cache** (7-10 días)
6. **Ejecutar tests completos** (3 días)
7. **Depurar fallos** (2-3 días)
8. **Implementar Data Cache** (5-7 días, opcional)
9. **Re-ejecutar tests con cachés** (2 días)
10. **Validación final** (2 días)

**Total tiempo testing**: ~10-15 días (incluido en plan de 40-50 días)

## Referencias

- [[Control Unit]] - Componente crítico para testing
- [[Memory Control]] - Componente crítico para testing
- [[Instruction Cache]] - Mejora performance en tests
- [[Data Cache]] - Mejora performance en tests de memoria
- Documentación: `README.md` en tests/ - Instrucciones de uso
- Script: `test.py` - Automatización de tests

---
**Última actualización**: 2025-12-09
**Estado**: 🔴 SIN TESTS EJECUTADOS (0%)
**Bloqueante**: Control Unit y Memory Control no implementados
**Próximo paso**: Implementar componentes faltantes, luego ejecutar tests básicos
