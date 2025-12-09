# Cache System Overview (Sistema de Caché Completo)

**Tipo**: Sistema de Memoria Jerárquica
**Estado**: 🔴 #faltante **CRÍTICO PARA APROBAR**
**Ubicación**: **NO EXISTE**
**Complejidad**: ⭐⭐⭐⭐ Muy Compleja
**Prioridad**: 🔴 ALTA (para nota > 3)

## ⚠️ REQUISITO OBLIGATORIO PARA APROBAR

**SIN CACHÉ = MÁXIMO 3 PUNTOS = SUSPENSO**

Según especificaciones del proyecto:
- **Sin caché**: Máximo 3 puntos
- **Con 1 caché (instruction, direct-mapped, 4+ líneas)**: 5 puntos (Primera Convocatoria)
- **Con 2 cachés (instruction + data, 4+ líneas c/u)**: 5 puntos (Segunda Convocatoria)
- **Con 2 cachés + mapeo avanzado (set-associative/fully-associative)**: 5 puntos (Tercera Convocatoria)

## Arquitectura del Sistema de Caché

### Configuración Mínima (Para Aprobar)

```
┌────────────────────────────────────────────────────┐
│                    CPU                             │
│                     ↓                              │
│         ┌───────────────────────┐                  │
│         │  INSTRUCTION CACHE    │                  │
│         │  • 4+ líneas          │                  │
│         │  • Direct-Mapped      │                  │
│         │  • Tag + Valid        │                  │
│         └───────────────────────┘                  │
│                     ↓                              │
│         ┌───────────────────────┐                  │
│         │   Memory Control      │                  │
│         └───────────────────────┘                  │
│                     ↓                              │
│                   RAM                              │
└────────────────────────────────────────────────────┘

Nota: 5 puntos (Primera Convocatoria)
```

### Configuración Recomendada (Para Extraordinario)

```
┌────────────────────────────────────────────────────┐
│                    CPU                             │
│              ↓            ↓                        │
│    ┌───────────────┐  ┌──────────────┐            │
│    │ INSTRUCTION   │  │  DATA        │            │
│    │ CACHE         │  │  CACHE       │            │
│    │ • 4+ líneas   │  │  • 4+ líneas │            │
│    │ • Direct      │  │  • Direct    │            │
│    └───────────────┘  └──────────────┘            │
│              ↓            ↓                        │
│         ┌───────────────────────┐                  │
│         │   Memory Control      │                  │
│         └───────────────────────┘                  │
│                     ↓                              │
│                   RAM                              │
└────────────────────────────────────────────────────┘

Nota: 5 puntos (Segunda Convocatoria)
```

### Configuración Avanzada (Para Mundial)

```
┌────────────────────────────────────────────────────┐
│                    CPU                             │
│              ↓            ↓                        │
│    ┌───────────────┐  ┌──────────────┐            │
│    │ INSTRUCTION   │  │  DATA        │            │
│    │ CACHE         │  │  CACHE       │            │
│    │ • 8+ líneas   │  │  • 8+ líneas │            │
│    │ • 2-way Set   │  │  • 2-way Set │            │
│    │   Associative │  │   Associative│            │
│    │ • LRU         │  │  • LRU       │            │
│    └───────────────┘  └──────────────┘            │
│              ↓            ↓                        │
│         ┌───────────────────────┐                  │
│         │   Memory Control      │                  │
│         └───────────────────────┘                  │
│                     ↓                              │
│                   RAM                              │
└────────────────────────────────────────────────────┘

Nota: 5 puntos (Tercera Convocatoria)
```

## Componentes del Sistema

### 1. [[Instruction Cache]] - OBLIGATORIO
**Estado**: 🔴 NO EXISTE
**Requisito**: Mínimo 4 líneas
**Función**: Cachear instrucciones para reducir latencia de fetch
**Conexión**: Entre [[Control Unit]] y [[Memory Control]]

### 2. [[Data Cache]] - PARA EXTRAORDINARIO
**Estado**: 🔴 NO EXISTE
**Requisito**: Mínimo 4 líneas, separada de instruction cache
**Función**: Cachear datos para LW/SW
**Conexión**: Entre [[Data Path]] y [[Memory Control]]

### 3. Tipos de Mapeo

#### [[Direct-Mapped Cache]] - MÍNIMO
- Cada bloque de memoria → 1 posición única en caché
- Simple de implementar
- Conflictos frecuentes

#### [[Set-Associative Cache]] - AVANZADO
- Cada bloque → múltiples posiciones posibles (2-way, 4-way)
- Menos conflictos que direct-mapped
- Requiere política de reemplazo (LRU, FIFO, Random)

#### [[Fully-Associative Cache]] - MÁS AVANZADO
- Cada bloque → cualquier posición en caché
- Mínimos conflictos
- Más complejo (comparadores para cada línea)

## Estructura de una Línea de Caché

```
┌──────┬────────┬──────────────────────────────────┐
│ Valid│  Tag   │           Data Block             │
│ 1 bit│ N bits │      4 words × 32 bits           │
│      │        │         = 128 bits               │
└──────┴────────┴──────────────────────────────────┘

Valid: 0 = línea vacía, 1 = línea contiene dato válido
Tag:   Identificador del bloque almacenado
Data:  Bloque completo (16 bytes = 4 palabras)
```

### Opcionalmente (para Write-Back)
```
┌──────┬─────┬────────┬──────────────────────────┐
│ Valid│Dirty│  Tag   │       Data Block         │
│ 1 bit│1 bit│ N bits │      128 bits            │
└──────┴─────┴────────┴──────────────────────────┘

Dirty: 1 = bloque modificado, debe escribirse a RAM antes de reemplazo
```

## Operación de la Caché

### Lectura (Load/Fetch)

```
1. CPU solicita dato en dirección X
2. Cache extrae: Tag, Index, Offset
3. Cache verifica línea[Index]:
   a) Valid=1 AND Tag match? → CACHE HIT
      • Devolver palabra del bloque (usando offset)
      • Latencia: 1 ciclo
   b) Valid=0 OR Tag mismatch? → CACHE MISS
      • Solicitar bloque completo a Memory Control
      • Esperar RT cycles
      • Cargar bloque en línea[Index]
      • Actualizar Tag y Valid=1
      • Devolver palabra solicitada
      • Latencia: 1 + RT cycles
```

### Escritura (Store)

**Política Write-Through (más simple)**:
```
1. CPU escribe dato en dirección X
2. Cache verifica hit/miss:
   a) CACHE HIT:
      • Actualizar palabra en bloque
      • Escribir también a RAM (via Memory Control)
      • Latencia: 1 + WT cycles
   b) CACHE MISS:
      • Write-through NO allocate: escribir solo a RAM
      • Latencia: WT cycles
```

**Política Write-Back (más eficiente, requiere Dirty bit)**:
```
1. CPU escribe dato en dirección X
2. Cache verifica hit/miss:
   a) CACHE HIT:
      • Actualizar palabra en bloque
      • Marcar Dirty=1
      • NO escribir a RAM aún
      • Latencia: 1 ciclo
   b) CACHE MISS:
      • Cargar bloque de RAM (si hay espacio)
      • Actualizar palabra
      • Marcar Dirty=1
      • Si reemplazo: escribir bloque viejo a RAM si Dirty=1
      • Latencia: variable
```

**Recomendación**: Implementar Write-Through primero (más simple).

## Desglose de Dirección

### Ejemplo: Caché Direct-Mapped con 4 Líneas

```
Dirección de 32 bits:
┌─────────────────────────┬──────────┬────────────┬────────┐
│        Tag              │  Index   │Word Offset │  Byte  │
│      26 bits            │  2 bits  │   2 bits   │ 2 bits │
│     bits [31:6]         │  [5:4]   │   [3:2]    │ [1:0]  │
└─────────────────────────┴──────────┴────────────┴────────┘

Tag:         Identifica bloque único
Index:       Selecciona línea en caché (0-3 para 4 líneas)
Word Offset: Selecciona palabra dentro del bloque (0-3)
Byte Offset: Debe ser 00 (alineación)
```

### Ejemplo: Caché 2-Way Set-Associative con 8 Líneas (4 Sets)

```
┌─────────────────────────┬──────────┬────────────┬────────┐
│        Tag              │  Set     │Word Offset │  Byte  │
│      26 bits            │  2 bits  │   2 bits   │ 2 bits │
│     bits [31:6]         │  [5:4]   │   [3:2]    │ [1:0]  │
└─────────────────────────┴──────────┴────────────┴────────┘

Set:    Selecciona set (0-3)
Dentro de cada set: 2 vías (ways) → comparar Tag con ambas
```

## Integración con el Sistema

### Sin Caché (Estado Actual - SUSPENSO)
```
Control Unit → Memory Control → RAM (fetch)
Data Path → Memory Control → RAM (LW/SW)
```
**Latencia por instrucción**: RT + WT cycles (lento)

### Con Instruction Cache (Para Aprobar)
```
Control Unit → Instruction Cache → Memory Control → RAM
                     ↓ (on hit)
               Instrucción (1 cycle)

Data Path → Memory Control → RAM (LW/SW sin caché)
```
**Latencia fetch (hit)**: 1 cycle (rápido)
**Latencia fetch (miss)**: 1 + RT cycles

### Con Ambas Cachés (Para Extraordinario)
```
Control Unit → Instruction Cache → Memory Control → RAM
                     ↓ (on hit)
               Instrucción (1 cycle)

Data Path → Data Cache → Memory Control → RAM
               ↓ (on hit)
           Dato (1 cycle)
```
**Latencia fetch (hit)**: 1 cycle
**Latencia LW (hit)**: 1 cycle
**Mejora de performance**: Significativa en loops

## Interfaz de Instruction Cache

### Entradas
| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `PC` | 32 bits | [[Control Unit]] | Dirección de instrucción |
| `FETCH_REQ` | 1 bit | [[Control Unit]] | Solicitud de fetch |
| `CLK` | 1 bit | Sistema | Reloj |
| `RESET` | 1 bit | Sistema | Reset (invalidar todas las líneas) |

### Salidas
| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `INSTRUCTION` | 32 bits | [[Instruction Register]] | Instrucción leída |
| `I_CACHE_READY` | 1 bit | [[Control Unit]] | Dato disponible (hit o miss resuelto) |

### Conexión con Memory Control (on miss)
| Señal | Dirección |
|-------|-----------|
| `MC_START` | Cache → MC |
| `MC_ADDRESS` | Cache → MC |
| `MC_BLOCK_DATA` | MC → Cache |
| `MC_END` | MC → Cache |

## Interfaz de Data Cache

### Entradas
| Puerto | Ancho | Fuente | Descripción |
|--------|-------|--------|-------------|
| `ADDRESS` | 32 bits | [[Data Path]] | Dirección de dato |
| `DATA_WRITE` | 32 bits | [[Data Path]] | Dato a escribir (SW) |
| `READ_REQ` | 1 bit | [[Data Path]] | Solicitud de lectura (LW) |
| `WRITE_REQ` | 1 bit | [[Data Path]] | Solicitud de escritura (SW) |
| `CLK` | 1 bit | Sistema | Reloj |
| `RESET` | 1 bit | Sistema | Reset |

### Salidas
| Puerto | Ancho | Destino | Descripción |
|--------|-------|---------|-------------|
| `DATA_READ` | 32 bits | [[Data Path]] | Dato leído (LW) |
| `D_CACHE_READY` | 1 bit | [[Control Unit]] | Operación completada |

## Políticas de Reemplazo (para Set-Associative/Fully-Associative)

### LRU (Least Recently Used) - RECOMENDADO
- Reemplazar la línea menos recientemente usada
- Requiere bits de edad por línea
- Mejor rendimiento en acceso a datos

### FIFO (First In, First Out)
- Reemplazar la línea más antigua
- Requiere contador de edad
- Más simple que LRU

### Random
- Reemplazar línea aleatoria
- Más simple de implementar
- Rendimiento aceptable

## Estimación de Trabajo

### Instruction Cache (Direct-Mapped, 4 líneas)
**Tiempo**: 7-10 días
**Desglose**:
1. Diseñar estructura de línea (1 día)
2. Implementar lógica de hit/miss (2 días)
3. Implementar carga de bloque (1 día)
4. Integrar con Control Unit y Memory Control (2 días)
5. Testing y depuración (2-3 días)

### Data Cache (Direct-Mapped, 4 líneas)
**Tiempo**: 5-7 días adicionales (si ya tienes instruction cache)
**Desglose**:
1. Adaptar diseño de instruction cache (2 días)
2. Implementar write-through (2 días)
3. Integrar con Data Path (1 día)
4. Testing (2 días)

### Set-Associative (2-way)
**Tiempo**: 7-10 días adicionales
**Desglose**:
1. Modificar estructura (comparadores múltiples) (3 días)
2. Implementar política de reemplazo (3 días)
3. Testing (3-4 días)

## Plan de Implementación Recomendado

### Fase 1: Aprobar (Semanas 3-4)
1. Implementar [[Instruction Cache]] direct-mapped, 4 líneas
2. Integrar con [[Control Unit]] y [[Memory Control]]
3. Validar con tests básicos
4. **Resultado**: 5 puntos (Primera Convocatoria)

### Fase 2: Extraordinario (Semanas 5-6)
1. Implementar [[Data Cache]] direct-mapped, 4 líneas
2. Integrar con [[Data Path]]
3. Validar con tests de memoria
4. **Resultado**: 5 puntos (Segunda Convocatoria)

### Fase 3: Mundial (Semanas 7+)
1. Upgrade ambas cachés a 2-way set-associative
2. Implementar LRU
3. Optimizar performance
4. **Resultado**: 5 puntos (Tercera Convocatoria)

## Verificación

### Tests para Instruction Cache
1. **Cold start**: Primeras instrucciones (todos misses)
2. **Loop pequeño**: Instrucciones en caché (todos hits)
3. **Conflict**: Instrucciones que mapean a misma línea
4. **Programa grande**: Mix de hits y misses

### Tests para Data Cache
1. **LW repetido**: Misma dirección (hit después del primer miss)
2. **SW + LW**: Verificar coherencia
3. **Array access**: Acceso secuencial
4. **Matrix access**: Patrón no secuencial

### Métricas
- **Hit Rate**: hits / (hits + misses)
  - Objetivo: >80% para programas típicos
- **Average Latency**: (hits × 1 + misses × (1+RT)) / total_accesses
  - Comparar con/sin caché

## Problemas Conocidos

**Estado actual**: 🔴 NO IMPLEMENTADO

**Impacto sin caché**:
- ❌ Nota máxima: 3 puntos (SUSPENSO)
- ❌ Performance extremadamente lenta
- ❌ Cada instrucción espera RT cycles

**Prioridad**: 🔴 ALTA (tercera después de Control Unit y Memory Control)

## Referencias

- Documentación: `WORKFLOW_PROYECTO.md` Fase 5
- Documentación: `S-MIPS_PROCESSOR_GUIDE_fixed.md` sobre caché
- Especificación: `s-mips.pdf` requisitos de caché
- Teoría: Patterson-Hennessy Cap. 5 - Memory Hierarchy

## Componentes Relacionados

- [[Instruction Cache]] - Especificación detallada
- [[Data Cache]] - Especificación detallada
- [[Direct-Mapped Cache]] - Implementación simple
- [[Set-Associative Cache]] - Implementación avanzada
- [[Memory Control]] - Interfaz con RAM
- [[Control Unit]] - Coordinación

---
**Última actualización**: 2025-12-09
**Estado**: 🔴 NO IMPLEMENTADO - BLOQUEA APROBADO
**Prioridad**: 🔴 ALTA (después de Control Unit y Memory Control)
**Nota sin esto**: Máximo 3 puntos (SUSPENSO GARANTIZADO)
