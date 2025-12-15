# Corrección FSM Control Unit para Direct-Mapped Cache

**Fecha**: 2025-12-14
**Propósito**: Corregir FSM para reflejar correctamente el comportamiento de cachés direct-mapped
**Archivo actualizado**: `/SMIPS-Obsidian-Vault/03-Control-Unit/Control Unit.md`

---

## 🔍 PROBLEMA IDENTIFICADO

El usuario señaló un error crítico en el diseño del FSM:

> "ICacheReady es básicamente si la cache hizo hit o no entonces eso no está reflejado en la máquina de estado en el caso de si no hace hit que hacemos. Ten en cuenta que las caches son DirectMapping me parece que eso significa que en un solo ciclo de reloj tienen la respuesta."

**El problema**:
- Las cachés **direct-mapped** responden en **1 ciclo** si hay HIT o MISS (comparación de tag)
- El FSM original NO distinguía entre HIT y MISS en estados separados
- El FSM original asumía que `CACHE_READY` se evaluaba indefinidamente, sin distinguir:
  - **HIT**: Dato listo inmediatamente (1 ciclo)
  - **MISS**: Caché debe ir a RAM (1 + RT ciclos adicionales)

---

## ✅ SOLUCIÓN APLICADA

### Cambio Conceptual

**ANTES** (incorreto):
```
WAIT_INST_CACHE:
  - Espera a que I_CACHE_READY=1
  - Duración: "1 ciclo si hit, 1+RT si miss" (ambiguo)
```

**AHORA** (correcto):
```
WAIT_INST_CACHE (1 ciclo):
  - Compara tag
  - Si I_CACHE_HIT=1 → dato listo → LOAD_INST (HIT)
  - Si I_CACHE_HIT=0 → ir a RAM → WAIT_INST_MISS (MISS)

WAIT_INST_MISS (RT ciclos):
  - Espera mientras caché trae bloque de RAM
  - Cuando I_CACHE_READY=1 → LOAD_INST
```

### Nuevos Estados Agregados

Se pasó de **2 estados de caché** a **4 estados de caché**:

1. **WAIT_INST_CACHE** (0010) - Compara tag I-Cache, **siempre 1 ciclo**
2. **WAIT_INST_MISS** (0011) - Espera fetch de RAM, **RT ciclos**
3. **WAIT_DATA_CACHE** (1010) - Compara tag D-Cache, **siempre 1 ciclo**
4. **WAIT_DATA_MISS** (1011) - Espera operación con RAM, **RT/WT ciclos**

### Señales Actualizadas

**Entradas desde Cache System**:

| Señal | Función ANTES | Función AHORA |
|-------|---------------|---------------|
| `I_CACHE_HIT` | Opcional (estadísticas) | **Requerida**: indica hit/miss en 1 ciclo |
| `I_CACHE_READY` | "Dato listo" (ambiguo) | **Específica**: dato listo después de miss (solo relevante si hubo MISS) |
| `D_CACHE_HIT` | Opcional (estadísticas) | **Requerida**: indica hit/miss en 1 ciclo |
| `D_CACHE_READY` | "Dato listo" (ambiguo) | **Específica**: operación completa después de miss |

**Aclaración de semántica**:
- `CACHE_HIT` se evalúa **después de 1 ciclo** (comparación de tag en direct-mapped)
- `CACHE_READY` solo es relevante en caso de MISS, indica que la operación con RAM terminó

---

## 📊 CAMBIOS EN EL FSM

### 1. Diagrama de Estados (Mermaid)

**Agregadas transiciones**:
```mermaid
WAIT_INST_CACHE --> LOAD_INST : I_CACHE_HIT = 1 (1 ciclo)
WAIT_INST_CACHE --> WAIT_INST_MISS : I_CACHE_HIT = 0

WAIT_INST_MISS --> WAIT_INST_MISS : I_CACHE_READY = 0
WAIT_INST_MISS --> LOAD_INST : I_CACHE_READY = 1

WAIT_DATA_CACHE --> CHECK_STACK : D_CACHE_HIT = 1 (1 ciclo)
WAIT_DATA_CACHE --> WAIT_DATA_MISS : D_CACHE_HIT = 0

WAIT_DATA_MISS --> WAIT_DATA_MISS : D_CACHE_READY = 0
WAIT_DATA_MISS --> CHECK_STACK : D_CACHE_READY = 1
```

### 2. Tabla de Transiciones

**Agregadas 8 nuevas filas**:

| Estado Actual       | Condición       | Próximo Estado  | Comentario |
| ------------------- | --------------- | --------------- | ---------- |
| WAIT_INST_CACHE 🔵  | I_CACHE_HIT=1   | LOAD_INST       | Dato listo en 1 ciclo |
| WAIT_INST_CACHE 🔵  | I_CACHE_HIT=0   | WAIT_INST_MISS  | Cache va a RAM |
| WAIT_INST_MISS 🔵   | I_CACHE_READY=0 | WAIT_INST_MISS  | Esperando RAM |
| WAIT_INST_MISS 🔵   | I_CACHE_READY=1 | LOAD_INST       | Dato de RAM listo |
| WAIT_DATA_CACHE 🔵  | D_CACHE_HIT=1   | CHECK_STACK     | Operación en 1 ciclo |
| WAIT_DATA_CACHE 🔵  | D_CACHE_HIT=0   | WAIT_DATA_MISS  | Cache va a RAM |
| WAIT_DATA_MISS 🔵   | D_CACHE_READY=0 | WAIT_DATA_MISS  | Esperando RAM |
| WAIT_DATA_MISS 🔵   | D_CACHE_READY=1 | CHECK_STACK     | Operación completa |

**Total de transiciones**: 19 (antes) → **33 (ahora)**

### 3. Codificaciones de Estado

**Recodificadas para incluir 4 estados de caché**:

```
IDLE             = 0000
START_FETCH      = 0001
WAIT_INST_CACHE  = 0010 🔵 (nuevo: compara tag, 1 ciclo)
WAIT_INST_MISS   = 0011 🔵 (nuevo: espera RAM, RT ciclos)
WAIT_INST_READ   = 0100 (bypass)
LOAD_INST        = 0101
EXECUTE_INST     = 0110
CHECK_INST       = 0111
START_MEM_WRITE  = 1000
START_MEM_READ   = 1001
WAIT_DATA_CACHE  = 1010 🔵 (nuevo: compara tag, 1 ciclo)
WAIT_DATA_MISS   = 1011 🔵 (nuevo: espera RAM, RT/WT ciclos)
WAIT_WRITE       = 1100 (bypass)
WAIT_READ        = 1101 (bypass)
CHECK_STACK      = 1110
HALT_STATE       = 1111
```

**Total**: 16 estados (antes 14), usando 4 bits completos.

### 4. Pseudocódigo Actualizado

**ANTES**:
```verilog
WAIT_INST_CACHE:
    if (I_CACHE_READY)
        state <= LOAD_INST;
```

**AHORA**:
```verilog
WAIT_INST_CACHE:
    // Después de 1 ciclo, caché ya comparó tag
    if (I_CACHE_HIT == 1'b1)
        state <= LOAD_INST;         // HIT: dato listo inmediato
    else
        state <= WAIT_INST_MISS;    // MISS: ir a buscar a RAM

WAIT_INST_MISS:
    // Esperando que caché traiga bloque de RAM
    if (I_CACHE_READY)
        state <= LOAD_INST;         // Dato de RAM ya disponible
```

**Lo mismo para Data Cache** (WAIT_DATA_CACHE → WAIT_DATA_MISS).

---

## ⏱️ TIMING CORREGIDO

### Instrucción Normal (solo I-Cache)

#### Cache HIT (95% del tiempo):
```
Ciclo 1: START_FETCH → WAIT_INST_CACHE (I_CACHE_REQ=1)
Ciclo 2: WAIT_INST_CACHE compara tag → I_CACHE_HIT=1 → LOAD_INST
Ciclo 3: LOAD_INST
Ciclo 4: EXECUTE_INST
Ciclo 5: CHECK_INST → START_FETCH

Total: 5 ciclos (vs 6 sin cache, si RT=3)
Mejora: 16% más rápido
```

#### Cache MISS (5% del tiempo):
```
Ciclo 1: START_FETCH → WAIT_INST_CACHE (I_CACHE_REQ=1)
Ciclo 2: WAIT_INST_CACHE compara tag → I_CACHE_HIT=0 → WAIT_INST_MISS
Ciclos 3-(RT+2): WAIT_INST_MISS (caché trae de RAM)
Ciclo RT+2: I_CACHE_READY=1 → LOAD_INST
Ciclo RT+3: LOAD_INST
Ciclo RT+4: EXECUTE_INST
Ciclo RT+5: CHECK_INST → START_FETCH

Total: RT+5 ciclos (vs RT+3 sin cache)
Penalidad: 2 ciclos extra (1 para tag, 1 overhead FSM)
```

### Instrucción LW (ambas cachés)

#### Double HIT (mejor caso):
```
Total: 5 ciclos
  - Fetch: 2 ciclos (I-Cache hit en ciclo 2)
  - Execute: 2 ciclos
  - Memory: 1 ciclo (D-Cache hit en ciclo 5)

vs 11 ciclos sin cache (si RT=3)
Mejora: 54% más rápido
```

#### I-HIT + D-MISS:
```
Total: RT+5 ciclos
  - Fetch: 2 ciclos (I-Cache hit)
  - Execute: 2 ciclos
  - Memory: RT+1 ciclos (D-Cache miss, espera en WAIT_DATA_MISS)

vs 2*RT+5 = 11 ciclos sin cache (si RT=3)
Mejora: RT ciclos (50% si RT=3)
```

#### Double MISS (peor caso):
```
Total: 2*RT+7 ciclos
  - Fetch: RT+2 ciclos (I-Cache miss)
  - Execute: 2 ciclos
  - Memory: RT+3 ciclos (D-Cache miss)

vs 2*RT+5 ciclos sin cache
Penalidad: 2 ciclos extra
```

**Conclusión importante**: Con double miss, el sistema es **ligeramente más lento** que sin cachés (2 ciclos de overhead). Por eso el bypass es crítico para degradación graceful.

---

## 🎯 BENEFICIOS DE LA CORRECCIÓN

### 1. **Refleja correctamente direct-mapped cache**
- ✅ Tag comparison siempre toma **exactamente 1 ciclo**
- ✅ Estados `WAIT_*_CACHE` duran **siempre 1 ciclo** (predecible)
- ✅ Estados `WAIT_*_MISS` duran **RT/WT ciclos** (acceso a RAM)

### 2. **Lógica de control más clara**
- ✅ FSM distingue explícitamente entre HIT (rápido) y MISS (lento)
- ✅ No hay ambigüedad en duración de estados
- ✅ Señales tienen semántica bien definida

### 3. **Timing predecible**
- ✅ HIT: siempre 2 ciclos para fetch (START_FETCH + WAIT_INST_CACHE)
- ✅ MISS: siempre RT+2 ciclos para fetch (+ WAIT_INST_MISS)
- ✅ Fácil calcular peor caso y mejor caso

### 4. **Implementación más simple en Logisim**
- ✅ Estados de caché tienen propósito único y claro
- ✅ Transiciones basadas en señales de 1 bit simples (HIT/READY)
- ✅ No hay lógica combinacional compleja en transiciones

---

## 📈 ESTADÍSTICAS

### Cambios en documentación:

| Aspecto | ANTES | AHORA | Cambio |
|---------|-------|-------|--------|
| Estados totales | 14 | 16 | +2 estados |
| Estados de caché | 2 | 4 | +2 estados |
| Transiciones | 27 | 33 | +6 transiciones |
| Señales de entrada (cache) | 2 opcionales, 2 requeridas | 4 requeridas | Mejor definidas |
| Líneas de pseudocódigo | ~80 | ~100 | +25% más detalle |

### Complejidad del FSM:

- **Bits de estado**: 4 bits (sin cambio, 16 estados posibles)
- **Comparadores adicionales**: +2 (para I_CACHE_HIT y D_CACHE_HIT)
- **Multiplexores adicionales**: +2 (transiciones HIT/MISS)

---

## 🔄 COMPARACIÓN: ANTES vs AHORA

### Flujo de Instruction Fetch

**ANTES** (incorrecto/ambiguo):
```
START_FETCH → WAIT_INST_CACHE → [espera indefinida] → LOAD_INST
```
- ❌ No claro cuánto dura WAIT_INST_CACHE
- ❌ CACHE_READY significa tanto "hit" como "miss completado"

**AHORA** (correcto):
```
START_FETCH → WAIT_INST_CACHE (1 ciclo) → {
    HIT → LOAD_INST (inmediato)
    MISS → WAIT_INST_MISS (RT ciclos) → LOAD_INST
}
```
- ✅ WAIT_INST_CACHE siempre 1 ciclo
- ✅ CACHE_HIT indica hit/miss
- ✅ CACHE_READY indica solo "miss completado"

### Señales de Caché

**ANTES**:
```
I_CACHE_READY: "Caché tiene dato listo (hit o miss completado)"
I_CACHE_HIT: "Opcional, para estadísticas"
```
- ❌ Ambiguo: ¿READY=1 en qué ciclo? ¿Ciclo 1 si hit, ciclo RT si miss?
- ❌ HIT marcado como opcional, pero es crítico para FSM

**AHORA**:
```
I_CACHE_HIT: "1=hit, 0=miss. Direct-mapped → responde en 1 ciclo" [REQUERIDO]
I_CACHE_READY: "Dato listo después de miss (solo relevante si HIT=0)" [REQUERIDO]
```
- ✅ HIT es la señal primaria (1 ciclo después de REQ)
- ✅ READY es la señal secundaria (solo para MISS)
- ✅ Timing completamente especificado

---

## ⚠️ IMPLICACIONES PARA IMPLEMENTACIÓN

### En Logisim (Control Unit):

1. **Agregar 2 nuevos estados**: WAIT_INST_MISS (0011), WAIT_DATA_MISS (1011)
2. **Actualizar lógica de transiciones**:
   - Desde WAIT_INST_CACHE: comparar `I_CACHE_HIT` (no `I_CACHE_READY`)
   - Desde WAIT_DATA_CACHE: comparar `D_CACHE_HIT` (no `D_CACHE_READY`)
3. **Cambiar pines de entrada**:
   - `I_CACHE_HIT` y `D_CACHE_HIT` ahora son **REQUERIDOS** (no opcionales)
   - `I_CACHE_READY` y `D_CACHE_READY` se usan en estados `WAIT_*_MISS`

### En Logisim (Cache):

La caché debe generar señales correctamente:

```verilog
// Ciclo 1 después de CACHE_REQ:
always @(posedge CLK) begin
    if (CACHE_REQ) begin
        tag_match = (tag == stored_tag) && valid;
        CACHE_HIT = tag_match;  // Disponible en ciclo 1

        if (tag_match) begin
            // HIT: dato ya está disponible
            CACHE_READY = 1;  // Opcional ponerlo a 1
        end
        else begin
            // MISS: iniciar fetch de RAM
            CACHE_READY = 0;
            start_ram_fetch = 1;
        end
    end

    // En ciclos posteriores, si hubo MISS:
    if (ram_fetch_complete) begin
        CACHE_READY = 1;  // Señalar que dato de RAM está listo
    end
end
```

---

## ✅ VALIDACIÓN

### Casos de prueba necesarios:

1. **HIT en I-Cache**: Verificar que `WAIT_INST_CACHE → LOAD_INST` en 2 ciclos totales
2. **MISS en I-Cache**: Verificar que `WAIT_INST_CACHE → WAIT_INST_MISS → LOAD_INST` en RT+2 ciclos
3. **HIT en D-Cache**: Verificar operación LW completa en 1 ciclo de memoria
4. **MISS en D-Cache**: Verificar operación LW completa en RT+1 ciclos de memoria
5. **Double MISS**: Verificar que penalidad es exactamente 2 ciclos vs bypass

---

## 📝 ARCHIVOS MODIFICADOS

1. ✅ **Control Unit.md** - Actualizado completamente:
   - Nuevas señales de entrada (I_CACHE_HIT, D_CACHE_HIT requeridas)
   - 4 estados de caché (WAIT_*_CACHE + WAIT_*_MISS)
   - Tabla de transiciones expandida (33 filas)
   - Pseudocódigo con lógica HIT/MISS explícita
   - Timing corregido para HIT y MISS separadamente
   - Codificaciones de estado actualizadas (16 estados)

2. ✅ **CORRECCION-FSM-DIRECT-MAPPED-CACHE.md** - Este documento (resumen de corrección)

---

## 🚀 PRÓXIMOS PASOS

1. **Implementar en Logisim**:
   - Actualizar FSM de Control Unit con 16 estados
   - Agregar lógica de transiciones para HIT/MISS
   - Conectar señales I_CACHE_HIT y D_CACHE_HIT como entradas requeridas

2. **Actualizar Cache.md** (si existe):
   - Especificar que cachés deben generar CACHE_HIT en 1 ciclo
   - Especificar timing de CACHE_READY (solo después de MISS)

3. **Testing**:
   - Test 1: I-Cache HIT (verificar 5 ciclos para ADD)
   - Test 2: I-Cache MISS (verificar RT+5 ciclos para ADD)
   - Test 3: D-Cache HIT en LW (verificar 1 ciclo de memoria)
   - Test 4: D-Cache MISS en LW (verificar RT+1 ciclos de memoria)

---

**Estado**: ✅ CORRECCIÓN APLICADA A DOCUMENTACIÓN
**Pendiente**: Implementación en Logisim
**Impacto**: Crítico - FSM anterior era incorrecto para direct-mapped cache
**Riesgo**: Bajo - Corrección alinea FSM con realidad de hardware direct-mapped

---

**Gracias al usuario por identificar este error crítico. El FSM ahora refleja correctamente el comportamiento de cachés direct-mapped con tag comparison en 1 ciclo y distingue claramente entre HIT (rápido) y MISS (lento).**
