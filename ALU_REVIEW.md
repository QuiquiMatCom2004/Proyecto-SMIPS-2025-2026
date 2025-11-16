# Revisión del ALU - S-MIPS Processor

## Operaciones Requeridas

Basándome en los tests disponibles, tu ALU debe implementar:

### Operaciones Aritméticas (7 operaciones)
1. **ADD** - Suma con signo (R-type: opcode=000000, funct=100000)
2. **ADDI** - Suma inmediata con signo (I-type: opcode=001000)
3. **SUB** - Resta con signo (R-type: opcode=000000, funct=100010)
4. **MULT** - Multiplicación con signo (R-type: opcode=000000, funct=011000)
5. **MULU** - Multiplicación sin signo (R-type: opcode=000000, funct=011001)
6. **DIV** - División con signo (R-type: opcode=000000, funct=011010)
7. **DIVU** - División sin signo (R-type: opcode=000000, funct=011011)

### Operaciones Lógicas (7 operaciones)
8. **AND** - AND lógico (R-type: opcode=000000, funct=100100)
9. **ANDI** - AND inmediato (I-type: opcode=001100)
10. **OR** - OR lógico (R-type: opcode=000000, funct=100101)
11. **ORI** - OR inmediato (I-type: opcode=001101)
12. **XOR** - XOR lógico (R-type: opcode=000000, funct=100110)
13. **XORI** - XOR inmediato (I-type: opcode=001110)
14. **NOR** - NOR lógico (R-type: opcode=000000, funct=100111)

### Operaciones de Comparación (4 operaciones)
15. **SLT** - Set if less than (signed) (R-type: opcode=000000, funct=101010)
16. **SLTI** - Set if less than immediate (signed) (I-type: opcode=001010)
17. **SLTU** - Set if less than (unsigned) (R-type: opcode=000000, funct=101011)
18. **SLTIU** - Set if less than immediate (unsigned) (I-type: opcode=001011)

**TOTAL: 18 operaciones ALU**

---

## Análisis de Operaciones Críticas

### 🔴 MULTIPLICACIÓN UNSIGNED (MULU) - CRÍTICO

**Problema potencial:** Logisim solo tiene multiplicador con signo incorporado.

**Caso de prueba crítico:**
```
0xFFFFFFFF × 2 (unsigned)
```

**Resultado esperado (UNSIGNED):**
```
4,294,967,295 × 2 = 8,589,934,590 = 0x1_FFFFFFFE
Hi = 0x00000001
Lo = 0xFFFFFFFE
```

**Resultado INCORRECTO (si usas signed):**
```
-1 × 2 = -2 = 0xFFFFFFFF_FFFFFFFE
Hi = 0xFFFFFFFF  ← ERROR!
Lo = 0xFFFFFFFE
```

**Cómo verificar:**
1. Carga `test_unsigned_critical.asm` en Logisim
2. Pon un probe en Hi después de MULU r1, r2
3. **Si Hi = 0x00000001 → CORRECTO ✓**
4. **Si Hi = 0xFFFFFFFF → INCORRECTO ✗**

**Soluciones:**

**Opción A: Extensión de signo cero (más simple)**
```
Input: A (32-bit), B (32-bit)
1. Zero-extend A → A' (33 bits) = {0, A[31:0]}
2. Zero-extend B → B' (33 bits) = {0, B[31:0]}
3. Multiply A' × B' usando multiplicador signed de 33 bits
4. Resultado = 66 bits, tomar [63:0]
```

**Opción B: Algoritmo long multiplication (más complejo pero sin depender de 33 bits)**
```
Implementar multiplicación binaria manual:
1. Si B es par: resultado = A << 1, B >> 1, repetir
2. Si B es impar: resultado += A, B -= 1, continuar
3. Acumular en 64 bits
```

**Opción C: Corrección del multiplicador signed**
```
Usar la fórmula: unsigned(A,B) = signed(A,B) + corrección
Corrección = (A[31] ? B << 32 : 0) + (B[31] ? A << 32 : 0)
```

**Recomendación:** Opción A si Logisim soporta 33 bits, sino Opción C.

---

### 🔴 DIVISIÓN UNSIGNED (DIVU) - CRÍTICO

**Problema potencial:** La división signed interpreta 0xFFFFFFFF como -1.

**Caso de prueba crítico:**
```
0xFFFFFFFE ÷ 2 (unsigned)
```

**Resultado esperado (UNSIGNED):**
```
4,294,967,294 ÷ 2 = 2,147,483,647 resto 0
Lo (cociente) = 0x7FFFFFFF
Hi (resto) = 0x00000000
```

**Resultado INCORRECTO (si usas signed):**
```
-2 ÷ 2 = -1 resto 0
Lo = 0xFFFFFFFF  ← ERROR!
Hi = 0x00000000
```

**Cómo verificar:**
1. Carga `test_unsigned_critical.asm` en Logisim
2. Pon un probe en Lo después de DIVU r5, r6
3. **Si Lo = 0x7FFFFFFF → CORRECTO ✓**
4. **Si Lo = 0xFFFFFFFF → INCORRECTO ✗**

**Soluciones:**

**Opción A: División binaria larga (restoring division)**
```
1. Q = 0 (cociente), R = 0 (resto)
2. Para i = 31 hasta 0:
   a. R = R << 1
   b. R[0] = A[i]
   c. Si R >= B:
      - R = R - B
      - Q[i] = 1
3. Lo = Q, Hi = R
```

**Opción B: Conversión condicional de signed**
```
if (A >= 0 AND B >= 0):
    usar divider signed directamente
else:
    convertir a positivos, dividir, ajustar resultado
```

**Recomendación:** Opción A (más robusto, siempre funciona).

---

### 🟡 DIVISIÓN SIGNED (DIV) - REQUIERE ATENCIÓN

**Problema:** Manejo de signos en cociente y resto.

**Reglas matemáticas:**
- Signo del cociente: `sign(A) XOR sign(B)`
- Signo del resto: `sign(A)`

**Casos de prueba:**
```
17 ÷ 5 = 3 resto 2
-17 ÷ 5 = -3 resto -2  ← Resto toma signo del dividendo
17 ÷ -5 = -3 resto 2   ← Resto toma signo del dividendo
-17 ÷ -5 = 3 resto -2
```

**Implementación correcta:**
```
1. sign_A = A[31], sign_B = B[31]
2. A_abs = sign_A ? -A : A  (complemento a 2 si negativo)
3. B_abs = sign_B ? -B : B
4. Q_abs, R_abs = unsigned_divide(A_abs, B_abs)
5. Q = (sign_A XOR sign_B) ? -Q_abs : Q_abs
6. R = sign_A ? -R_abs : R_abs
7. Lo = Q, Hi = R
```

**Test incluido:** `tests/div.asm` (6566 ÷ 100 = 65 resto 66, imprime "AB")

---

### 🟡 MULTIPLICACIÓN SIGNED (MULT) - VERIFICAR OVERFLOW

**Caso de prueba importante del test:**
```
20 × 4 = 80 (0x00000050)
Hi = 0x00000000, Lo = 0x00000050

20 × (-4) = -80 (0xFFFFFFB0)
Hi = 0xFFFFFFFF (extensión de signo), Lo = 0xFFFFFFB0

-80 × (-1) = 80
Hi = 0x00000000, Lo = 0x00000050
```

**Verifica que:**
- Hi contiene los bits superiores (extensión de signo para números pequeños)
- Números negativos producen Hi = 0xFFFFFFFF cuando el resultado cabe en 32 bits negativos

**Test incluido:** `tests/mult.asm` (verifica con -4)

---

## Operaciones de Comparación

### SLT vs SLTU - Diferencia crítica

**SLT (Signed):**
```
A = 0xFFFFFFFF (-1 signed)
B = 0x00000001 (1)
SLT A, B → Result = 1 (porque -1 < 1)
```

**SLTU (Unsigned):**
```
A = 0xFFFFFFFF (4,294,967,295 unsigned)
B = 0x00000001 (1)
SLTU A, B → Result = 0 (porque 4,294,967,295 > 1)
```

**Implementación:**
- **SLT:** Restar A - B, mirar bit de signo del resultado (bit 31)
- **SLTU:** Restar A - B sin signo, mirar carry/borrow flag

---

## Flags de Salida del ALU

Tu ALU debe generar:

1. **Result (32 bits):** Resultado de la operación
2. **Hi (32 bits):** Parte alta de multiplicación/división (resto)
3. **Lo (32 bits):** Parte baja de multiplicación/división (cociente)
4. **Zero flag:** Result == 0 (usado en BEQ)
5. **Negative flag:** Result[31] == 1 (usado en BLTZ, BLEZ, BGTZ)

---

## Checklist de Verificación

### Operaciones Básicas
- [ ] ADD: Suma dos registros correctamente
- [ ] ADDI: Suma registro + inmediato (con extensión de signo del inmediato)
- [ ] SUB: Resta correctamente
- [ ] AND, OR, XOR, NOR: Operaciones lógicas bit a bit
- [ ] ANDI, ORI, XORI: Con inmediato (extensión de CERO para lógicas)

### Comparación
- [ ] SLT: Compara con signo (-1 < 1 = true)
- [ ] SLTU: Compara sin signo (0xFFFFFFFF < 1 = false)
- [ ] SLTI: Inmediato con signo
- [ ] SLTIU: Inmediato sin signo

### Multiplicación SIGNED
- [ ] 20 × 4 = 80 (Hi=0, Lo=80)
- [ ] 20 × (-4) = -80 (Hi=0xFFFFFFFF, Lo=0xFFFFFFB0)
- [ ] Números grandes: 65535 × 65535 (overflow a Hi)

### Multiplicación UNSIGNED ⚠️ CRÍTICO
- [ ] 4 × 20 = 80 (Hi=0, Lo=80)
- [ ] 0xFFFFFFFF × 2 = 0x1_FFFFFFFE (Hi=1, Lo=0xFFFFFFFE)
- [ ] 65535 × 65535 = 4,294,836,225 (Hi=0, Lo=0xFFFE0001)

### División SIGNED
- [ ] 6566 ÷ 100 = 65 resto 66
- [ ] -17 ÷ 5 = -3 resto -2
- [ ] 17 ÷ -5 = -3 resto 2

### División UNSIGNED ⚠️ CRÍTICO
- [ ] 6566 ÷ 100 = 65 resto 66
- [ ] 0xFFFFFFFE ÷ 2 = 0x7FFFFFFF resto 0
- [ ] 4,294,967,295 ÷ 10 = 429,496,729 resto 5

---

## Consejos de Implementación

### 1. Estructura Modular del ALU
```
ALU inputs: A (32-bit), B (32-bit), Operation (5-bit)
ALU outputs: Result (32-bit), Hi (32-bit), Lo (32-bit), Zero, Neg

Subcomponentes:
├── Adder/Subtractor (combinational)
├── Logic Unit (AND, OR, XOR, NOR gates)
├── Comparator Signed (uses subtractor + sign bit)
├── Comparator Unsigned (uses subtractor + borrow)
├── Multiplier Signed (Logisim built-in or custom)
├── Multiplier Unsigned (custom circuit - CRÍTICO)
├── Divider Signed (custom circuit con manejo de signos)
├── Divider Unsigned (custom circuit - CRÍTICO)
└── Output Mux (selecciona según Operation code)
```

### 2. Multiplexor de Salida
```
Operation code → Select:
  000 → Adder result
  001 → Subtractor result
  010 → AND result
  011 → OR result
  100 → XOR result
  101 → NOR result
  110 → SLT result
  111 → SLTU result
  ... (asignar códigos para MULT, DIV, etc.)
```

### 3. Gestión de Hi/Lo
Solo MULT, MULU, DIV, DIVU escriben Hi/Lo. El resto de operaciones:
- Hi = 0
- Lo = Result (opcional, o ignorado)

### 4. Testing Incremental

**Fase 1:** Operaciones simples
```bash
python3 test.py tests/add.asm
python3 test.py tests/addi.asm
python3 test.py tests/sub.asm
python3 test.py tests/and.asm
python3 test.py tests/or.asm
python3 test.py tests/xor.asm
python3 test.py tests/nor.asm
```

**Fase 2:** Inmediatos y comparación
```bash
python3 test.py tests/andi.asm
python3 test.py tests/ori.asm
python3 test.py tests/xori.asm
python3 test.py tests/slt.asm
python3 test.py tests/slti.asm
```

**Fase 3:** Multiplicación signed
```bash
python3 test.py tests/mult.asm
```

**Fase 4:** Multiplicación unsigned (verificar con probe)
```bash
python3 test.py tests/mulu.asm
# Además: test_unsigned_critical.asm con probes en Logisim
```

**Fase 5:** División signed
```bash
python3 test.py tests/div.asm
```

**Fase 6:** División unsigned (verificar con probe)
```bash
python3 test.py tests/divu.asm
# Además: test_unsigned_critical.asm con probes en Logisim
```

**Fase 7:** Tests complejos
```bash
python3 test.py tests/div-mult-bne.asm
python3 test.py tests/divu-mulu-bne.asm
```

---

## Errores Comunes

### ❌ Error 1: MULU usa multiplicador signed
**Síntoma:** `mulu` con números grandes (0xFFFFFFFF) da Hi negativo
**Solución:** Implementar multiplicación unsigned separada

### ❌ Error 2: DIVU usa divisor signed
**Síntoma:** `divu` con 0xFFFFFFFE ÷ 2 da cociente = 0xFFFFFFFF
**Solución:** Implementar división unsigned separada

### ❌ Error 3: Resto de DIV con signo incorrecto
**Síntoma:** -17 ÷ 5 da resto = 2 (debería ser -2)
**Solución:** Resto siempre toma signo del dividendo

### ❌ Error 4: Inmediatos lógicos con extensión de signo
**Síntoma:** `andi r1, r2, 0xFFFF` da resultado incorrecto
**Solución:** ANDI, ORI, XORI usan **extensión de cero**, no de signo

### ❌ Error 5: SLT vs SLTU confundidos
**Síntoma:** Comparaciones con números negativos fallan
**Solución:** SLT mira bit de signo, SLTU mira borrow/carry

---

## Recomendaciones Finales

### Prioridad Alta (Debe funcionar perfectamente)
1. ✅ ADD, SUB, ADDI (son la base de todo)
2. ✅ AND, OR, XOR, NOR (simples)
3. ✅ ANDI, ORI, XORI (cuidado con extensión de cero)
4. ✅ SLT, SLTU (críticos para branches condicionales)
5. 🔴 **MULT signed** (muchos tests dependen de esto)
6. 🔴 **DIV signed** (test div.asm)

### Prioridad Media (Necesario para tests avanzados)
7. 🔴 **MULU unsigned** - VERIFICA CON PROBES
8. 🔴 **DIVU unsigned** - VERIFICA CON PROBES
9. ✅ SLTI, SLTIU (menos usados pero necesarios)

### Debugging con Logisim
1. Crea subcircuitos separados para cada operación compleja
2. Testea cada subcircuito independientemente con valores conocidos
3. Usa probes para verificar Hi/Lo en multiplicación/división
4. Para MULU/DIVU, usa `test_unsigned_critical.asm` con probes

### Optimización de Tamaño
- Reutiliza el restador para SUB, SLT, SLTU (solo cambia cómo interpretas el resultado)
- Las operaciones lógicas pueden compartir circuitería
- Si el precio es crítico, considera implementar DIV/DIVU con un solo circuito + lógica de conversión

---

## Próximos Pasos

1. **Abre Logisim y revisa tu ALU actual**
2. **Identifica qué operaciones ya tienes implementadas**
3. **Prueba especialmente MULU y DIVU con test_unsigned_critical.asm**
4. **Si MULU/DIVU fallan, necesitas implementar circuitos unsigned separados**
5. **Usa los tests provistos para verificar cada operación**

¿Necesitas ayuda específica con alguna operación? Puedo ayudarte a diseñar el circuito para MULU o DIVU unsigned.
