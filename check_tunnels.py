#!/usr/bin/env python3
"""
Script para verificar túneles desconectados en el circuito S-MIPS
Uso: python3 check_tunnels.py
"""

import re
from collections import defaultdict

def check_tunnels():
    print("🔍 Verificando túneles en circuito S-MIPS...\n")

    tunnels = defaultdict(lambda: {'in': 0, 'out': 0, 'lines': []})

    with open('s-mips.circ', 'r') as f:
        in_smips = False
        line_num = 0

        for line in f:
            line_num += 1

            # Detectar inicio del circuito S-MIPS
            if 'circuit name="S-MIPS"' in line and 'S-MIPS Board' not in line:
                in_smips = True
                print(f"✅ Encontrado circuito S-MIPS en línea {line_num}\n")
                continue

            # Detectar fin del circuito
            if '</circuit>' in line and in_smips:
                print(f"✅ Fin del circuito S-MIPS en línea {line_num}\n")
                break

            # Buscar túneles dentro del circuito S-MIPS
            if in_smips and 'comp lib="0"' in line and 'name="Tunnel"' in line:
                # Leer siguiente línea para obtener el label
                next_line = next(f, '')
                line_num += 1

                # Extraer label
                label_match = re.search(r'label="([^"]+)"', next_line)
                if label_match:
                    label = label_match.group(1)

                    # Determinar dirección: facing="east" = salida (out), sin facing = entrada (in)
                    if 'facing="east"' in next_line:
                        direction = 'out'
                    else:
                        direction = 'in'

                    tunnels[label][direction] += 1
                    tunnels[label]['lines'].append(line_num)

    # Mostrar resultados
    print("="*70)
    print("REPORTE DE TÚNELES")
    print("="*70)

    complete = []
    incomplete = []

    for label in sorted(tunnels.keys()):
        data = tunnels[label]
        total = data['in'] + data['out']
        status = "✅" if data['in'] > 0 and data['out'] > 0 else "⚠️"

        info = {
            'label': label,
            'in': data['in'],
            'out': data['out'],
            'total': total,
            'lines': data['lines'],
            'status': status
        }

        if data['in'] > 0 and data['out'] > 0:
            complete.append(info)
        else:
            incomplete.append(info)

    # Mostrar túneles completos
    if complete:
        print(f"\n✅ TÚNELES COMPLETOS ({len(complete)}):")
        print("-" * 70)
        for t in complete:
            print(f"  {t['label']:30s}  IN: {t['in']}  OUT: {t['out']}  Total: {t['total']}")

    # Mostrar túneles incompletos (PROBLEMA)
    if incomplete:
        print(f"\n⚠️  TÚNELES INCOMPLETOS ({len(incomplete)}) - REVISAR:")
        print("-" * 70)
        for t in incomplete:
            problem = []
            if t['in'] == 0:
                problem.append("FALTA ENTRADA")
            if t['out'] == 0:
                problem.append("FALTA SALIDA")

            print(f"  ❌ {t['label']:30s}  IN: {t['in']}  OUT: {t['out']}  [{', '.join(problem)}]")
            print(f"     Líneas: {', '.join(map(str, t['lines']))}")
    else:
        print("\n✅ No hay túneles incompletos")

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Total de túneles únicos: {len(tunnels)}")
    print(f"  ✅ Completos (IN + OUT): {len(complete)}")
    print(f"  ⚠️  Incompletos: {len(incomplete)}")

    if incomplete:
        print("\n🚨 ACCIÓN REQUERIDA:")
        print("   Revisa los túneles incompletos y agrega las conexiones faltantes")
        print("   Cada túnel debe tener al menos 1 entrada (sin facing) y 1 salida (facing=east)")
        return False
    else:
        print("\n✅ Todos los túneles están correctamente conectados")
        return True

if __name__ == "__main__":
    try:
        all_ok = check_tunnels()
        exit(0 if all_ok else 1)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo s-mips.circ")
        print("   Ejecuta este script desde la carpeta del proyecto")
        exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        exit(1)
