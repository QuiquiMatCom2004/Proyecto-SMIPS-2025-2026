# Diagnóstico: Alta Impedancia en S-MIPS

**Síntomas reportados**:
- Todos los cables con alta impedancia (Z)
- Oscilación evidente según dashboard
- FSM ya corregida pero persiste el problema

---

## 🔍 Análisis Realizado

### 1. Verificación de Estructura
✅ **Componentes principales existen**:
- Control Unit en (880,700)
- Memory Control en (900,860)
- DATA PATH en (890,390)

✅ **Hay 70 cables (wires)** conectando componentes

### 2. Verificación de Clock
✅ **Pin de Clock existe** en (400,340)
✅ **Clock conectado a túnel** "CLK" en (420,340)

---

## 🚨 CAUSAS PROBABLES DE ALTA IMPEDANCIA

### Causa #1: Clock NO está pulsando
**Síntoma**: Si el clock del S-MIPS Board no está conectado o no pulsa, todos los componentes secuenciales quedan "congelados" y producen alta impedancia.

**Verificación**:
```
1. Abrir s-mips.circ en Logisim
2. Ir al circuito "S-MIPS Board" (circuito principal)
3. Verificar que hay un componente Clock
4. Verificar que el Clock está CONECTADO al pin Clock del CPU (S-MIPS)
5. Iniciar simulación (Ctrl+K o Simulate > Ticks Enabled)
6. Verificar que el Clock está pulsando (debe cambiar 0→1→0→1)
```

**Solución si falta Clock**:
```
1. En S-MIPS Board, agregar Clock (Wiring > Clock)
2. Conectar Clock al pin "Clock" del componente S-MIPS (CPU)
3. Configurar frecuencia (ej: 1 Hz para debug, 4.1 kHz para operación normal)
```

---

### Causa #2: Reset atascado en activo (CLR=1)
**Síntoma**: Si la señal CLR (clear/reset) está permanentemente en 1, todos los componentes están en reset continuo y no procesan datos.

**Verificación**:
```
1. En S-MIPS Board, buscar señal Reset
2. Verificar que Reset está en 0 (inactivo) durante operación normal
3. Reset debe ser 1 solo al inicio, luego 0
```

**Solución**:
```
1. Conectar Reset a un Button o Pin de entrada
2. Asegurar que está en 0 durante ejecución
3. Pulsar Reset solo para reiniciar, no mantenerlo presionado
```

---

### Causa #3: Componentes sin Enable
**Síntoma**: Si los componentes no reciben señales de enable (EN), no se activan y producen alta impedancia.

**Componentes que requieren Enable**:
- **DATA PATH**: Necesita `EN=1` para ejecutar
- **Memory Control**: Necesita `START_MC=1` para operar
- **Control Unit**: Genera los enables, pero necesita estar en estado activo

**Verificación**:
```
1. Verificar que DATA PATH recibe EN=1 cuando debe ejecutar
2. Verificar que Memory Control recibe START_MC cuando debe leer/escribir
3. Verificar que Control Unit NO está en estado HALT o IDLE permanente
```

---

### Causa #4: Loop Combinacional (Oscilación)
**Síntoma**: Si hay un loop combinacional, Logisim detecta oscilación y puede detener la simulación o marcar señales como indefinidas.

**Ubicación probable**: Control Unit ↔ Memory Control

**Verificación**:
```
1. En Logisim, ir a Simulate > Logging
2. Buscar mensajes de "oscillation detected" o "combinational loop"
3. Identificar qué señales están oscilando
```

**Solución**:
```
En Control Unit:
- Asegurar que mc_end está registrada (flip-flop) antes de entrar a lógica de transición
- Verificar que Start_MC se genera en estado secuencial, no combinacional

En FSM (subcircuito de Control Unit):
- Verificar que TODAS las transiciones de estado están sincronizadas con CLK
- Asegurar que no hay paths combinacionales de salida → entrada
```

---

### Causa #5: Túneles Desconectados
**Síntoma**: Si un túnel tiene solo entrada o solo salida (sin pareja), las señales quedan flotantes.

**Verificación**:
```bash
# En terminal, ejecutar:
python3 << 'EOF'
import re
tunnels = {}
with open('s-mips.circ', 'r') as f:
    in_smips = False
    for line in f:
        if 'circuit name="S-MIPS"' in line:
            in_smips = True
        elif '</circuit>' in line and in_smips:
            break
        elif in_smips and 'Tunnel' in line:
            match = re.search(r'label="([^"]+)"', line)
            if match:
                label = match.group(1)
                facing = 'out' if 'facing="east"' in line else 'in'
                tunnels[label] = tunnels.get(label, []) + [facing]

for label, dirs in sorted(tunnels.items()):
    if len(dirs) < 2 or ('in' not in dirs) or ('out' not in dirs):
        print(f"⚠️  {label}: {dirs} (INCOMPLETO)")
EOF
```

**Solución**:
- Para cada túnel incompleto, agregar pareja (entrada + salida)
- Asegurar que nombres coinciden EXACTAMENTE (case-sensitive)

---

### Causa #6: Pines de S-MIPS no conectados en Board
**Síntoma**: Si el componente S-MIPS está instanciado en S-MIPS Board pero sus pines no están conectados, no recibe ni envía señales.

**Pines críticos del S-MIPS (CPU)**:
```
ENTRADAS (deben estar conectadas):
- Clock: Reloj del sistema
- Addr: Dirección de RAM (desde RAM)
- RT, WT: Timing de RAM
- O0, O1, O2, O3: Datos de RAM
- KBD EN, KBD CLR, KBD DATA, KBD AVAIL: Teclado
- RESET: Reset del sistema

SALIDAS (deben estar conectadas):
- CS: Chip Select para RAM
- R/W: Read/Write para RAM
- I0, I1, I2, I3: Datos a RAM
- Mask: Máscara de bancos
- TTY EN, TTY DATA: Terminal
- STOP: Señal de HALT
```

**Verificación**:
```
1. Ir a circuito "S-MIPS Board"
2. Seleccionar componente S-MIPS (CPU)
3. Verificar que TODOS los pines tienen cables conectados (no "floating")
4. En particular verificar:
   - Clock conectado a Clock component
   - Reset conectado a Button/Pin
   - RAM conectada (Addr, I0-I3, O0-O3, CS, R/W, Mask, RT, WT)
```

---

## 🔧 PROCEDIMIENTO DE DIAGNÓSTICO PASO A PASO

### Paso 1: Verificar Clock
```
1. Abrir s-mips.circ en Logisim
2. Ir a "S-MIPS Board"
3. Buscar componente Clock
4. SI NO HAY CLOCK:
   a. Agregar Clock (Wiring > Clock)
   b. Configurar a 1 Hz
   c. Conectar a pin Clock del S-MIPS (CPU)
5. Iniciar simulación (Ctrl+K)
6. Verificar que Clock pulsa (cambia 0→1→0→1)
```

**Si el clock NO pulsa → SOLUCIÓN ENCONTRADA**: Agregar/conectar Clock

### Paso 2: Verificar Reset
```
1. Buscar señal Reset en S-MIPS Board
2. Verificar valor actual:
   - Debe ser 0 durante operación
   - Solo 1 al inicio para reset
3. SI Reset=1 permanente:
   a. Conectar Reset a Button (Wiring > Button)
   b. Dejar sin presionar (valor=0) durante ejecución
   c. Presionar solo para reiniciar
```

**Si Reset está en 1 → SOLUCIÓN ENCONTRADA**: Poner Reset en 0

### Paso 3: Verificar Pines del CPU
```
1. Seleccionar componente S-MIPS (CPU) en Board
2. Verificar TODOS los pines:
   - ¿Tienen cables conectados?
   - ¿Los cables van a componentes válidos?
3. Pines CRÍTICOS que DEBEN estar conectados:
   - Clock ✅
   - Reset ✅
   - RAM (CS, R/W, Addr, I0-I3, O0-O3) ✅
```

**Si algún pin crítico NO está conectado → SOLUCIÓN ENCONTRADA**: Conectar pin

### Paso 4: Verificar Estado de Control Unit
```
1. Entrar al circuito S-MIPS (doble clic en CPU)
2. Entrar a Control Unit (doble clic)
3. Entrar a FSM (doble clic)
4. Iniciar simulación
5. Observar registro de estado:
   - ¿Cambia de valor?
   - ¿Se queda en IDLE (0000)?
   - ¿Se queda en HALT (1111)?
6. SI se queda estancado en un estado:
   a. Verificar que mc_end llega correctamente
   b. Verificar que transiciones de estado funcionan
```

**Si FSM no cambia de estado → Problema en lógica de FSM**

### Paso 5: Verificar Oscilación
```
1. En Logisim, activar logging: Simulate > Logging
2. Iniciar simulación
3. Buscar mensajes:
   - "Oscillation detected"
   - "Combinational loop"
4. SI hay oscilación:
   - Anotar qué señales oscilan
   - Buscar loop: señal A → componente B → señal C → componente A
   - Insertar registro (flip-flop) para romper loop
```

**Si hay oscilación → Insertar flip-flop en el loop**

---

## 📋 CHECKLIST RÁPIDO

Antes de continuar debugging, verificar:

⬜ Clock del Board está agregado y pulsando (1 Hz o más)
⬜ Clock conectado al pin Clock del CPU (S-MIPS)
⬜ Reset en valor 0 durante ejecución (no presionado)
⬜ Componente S-MIPS (CPU) tiene TODOS los pines conectados
⬜ RAM conectada correctamente (8 pines entrada, 6 pines salida)
⬜ No hay mensajes de oscilación en Simulate > Logging
⬜ Simulación está activa (Ctrl+K, Ticks Enabled)

---

## 🎯 SOLUCIÓN MÁS PROBABLE

**Basándome en el síntoma "todos los cables con alta impedancia"**, la causa #1 es la MÁS PROBABLE:

### ❌ PROBLEMA: Clock no está conectado o no está pulsando

**Síntomas**:
- TODOS los componentes secuenciales (registros, flip-flops) mantienen sus valores
- Salidas de componentes combinacionales que dependen de registros quedan en Z (alta impedancia)
- No hay actividad en el circuito

**Solución**:
```
1. Ir a "S-MIPS Board" (circuito principal)
2. Agregar Clock si no existe (Wiring > Clock)
3. Configurar Clock a 1 Hz para debug
4. Conectar Clock al pin "Clock" del componente S-MIPS (el cuadrado grande del CPU)
5. Presionar Ctrl+K para iniciar simulación
6. Presionar Ctrl+T varias veces para avanzar ticks manualmente
7. Observar que las señales empiezan a cambiar
```

---

## 📞 PRÓXIMOS PASOS

1. **Verificar Clock**: Ir a S-MIPS Board y verificar que Clock existe y está conectado
2. **Iniciar simulación**: Presionar Ctrl+K (Simulate > Ticks Enabled)
3. **Observar actividad**: Verificar que señales cambian
4. **Si persiste**: Verificar Reset=0 y pines conectados
5. **Reportar hallazgos**: Indicar qué paso falló para diagnóstico específico

---

**RECORDATORIO**: Alta impedancia (Z) en TODOS los cables sugiere que los componentes secuenciales no están recibiendo clock o están en reset continuo. Esto NO es un problema de conexiones internas del circuito, sino de señales de control del nivel superior (Board).
