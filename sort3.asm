# Programa: Ordenar 3 elementos en memoria (bubble sort)
# Array inicial en direcciones:
#   0x1000: 30 (arr[0])
#   0x1004: 10 (arr[1])
#   0x1008: 20 (arr[2])
# Resultado esperado: 10, 20, 30

#prints 10,20,30

.text
main:
    # Inicializar dirección base del array en R10
    ADDI R10, R0, 0x1000    # R10 = dirección base (0x1000)

    # Cargar los 3 valores del array en registros
    LW R1, 0(R10)           # R1 = arr[0] = 30
    LW R2, 4(R10)           # R2 = arr[1] = 10
    LW R3, 8(R10)           # R3 = arr[2] = 20

    # Primera comparación: arr[0] vs arr[1]
    # Si R1 <= R2, no swap, saltar a comp2
    SLT R4, R2, R1          # R4 = 1 si R2 < R1 (10 < 30), else 0
    BEQ R4, R0, comp2       # Si R4 == 0, saltar a comp2 (no swap)

    # Swap R1 y R2
swap1:
    ADD R5, R1, R0          # R5 = R1 (temp)
    ADD R1, R2, R0          # R1 = R2
    ADD R2, R5, R0          # R2 = R5 (antiguo R1)

    # Segunda comparación: arr[1] vs arr[2]
comp2:
    SLT R4, R3, R2          # R4 = 1 si R3 < R2 (20 < 30), else 0
    BEQ R4, R0, comp3       # Si R4 == 0, saltar a comp3 (no swap)

    # Swap R2 y R3
swap2:
    ADD R5, R2, R0          # R5 = R2 (temp)
    ADD R2, R3, R0          # R2 = R3
    ADD R3, R5, R0          # R3 = R5 (antiguo R2)

    # Tercera comparación: arr[0] vs arr[1] (por si hubo cambio)
comp3:
    SLT R4, R2, R1          # R4 = 1 si R2 < R1, else 0
    BEQ R4, R0, done        # Si R4 == 0, terminamos

    # Swap R1 y R2 (última vez)
swap3:
    ADD R5, R1, R0          # R5 = R1 (temp)
    ADD R1, R2, R0          # R1 = R2
    ADD R2, R5, R0          # R2 = R5 (antiguo R1)

done:
    # Guardar valores ordenados de vuelta en memoria
    SW R1, 0(R10)           # arr[0] = R1 (menor valor)
    SW R2, 4(R10)           # arr[1] = R2 (valor medio)
    SW R3, 8(R10)           # arr[2] = R3 (mayor valor)

    # Imprimir resultados usando TTY
    TTY R1                  # Imprimir arr[0]
    TTY R2                  # Imprimir arr[1]
    TTY R3                  # Imprimir arr[2]

    # Terminar
    HALT

.data
# Valores iniciales (simulados en memoria 0x1000)
# Estos se cargarían manualmente en RAM antes de ejecutar
# 0x1000: .word 30
# 0x1004: .word 10
# 0x1008: .word 20
