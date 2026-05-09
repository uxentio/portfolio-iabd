"""
validate_raw_format.py

Filtro rapido entre el generador y la carga a Bronze. Comprueba que cada
linea del JSONL es JSON parseable y tiene las claves minimas (event_id,
device_id, timestamp). Si algo se rompe a este nivel, mejor abortar antes
de subir basura a HDFS.

No valida rangos ni duplicados: de eso se encarga validate_raw.py despues.

Uso:
    python validate_raw_format.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from lib_paths import DEVICE_ID, LOCAL_RAW_DIRNAME

CLAVES_ESTRUCTURALES = ("event_id", "device_id", "timestamp")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=True)
    parser.add_argument("--raw-dir", type=str, default=None)
    args = parser.parse_args()

    run_date = datetime.fromisoformat(args.date)
    raw_root = Path(args.raw_dir) if args.raw_dir else (Path.cwd() / LOCAL_RAW_DIRNAME)
    carpeta = raw_root / DEVICE_ID / run_date.strftime("%Y-%m-%d")

    if not carpeta.exists():
        sys.exit(f"ABORT: no existe {carpeta}. ¿Se ejecuto el generador?")

    ficheros = sorted(carpeta.glob("*.jsonl"))
    if not ficheros:
        sys.exit(f"ABORT: no hay .jsonl en {carpeta}.")

    total_lineas = 0
    primer_registro = None

    for fichero in ficheros:
        with fichero.open(encoding="utf-8") as f:
            for n_linea, linea in enumerate(f, start=1):
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    registro = json.loads(linea)
                except json.JSONDecodeError as e:
                    sys.exit(f"ABORT: {fichero.name}:{n_linea} no es JSON valido ({e})")

                if primer_registro is None:
                    primer_registro = registro
                    faltantes = [k for k in CLAVES_ESTRUCTURALES if k not in registro]
                    if faltantes:
                        sys.exit(
                            f"ABORT: el primer registro de {fichero.name} no tiene "
                            f"las claves estructurales {faltantes}. "
                            f"¿Cambio el esquema del generador?"
                        )

                total_lineas += 1

    print(f"OK Formato inicial valido")
    print(f"   Ficheros revisados: {len(ficheros)}")
    print(f"   Lineas JSON validas: {total_lineas}")
    print(f"   Esquema detectado: {sorted(primer_registro.keys())}")


if __name__ == "__main__":
    main()
