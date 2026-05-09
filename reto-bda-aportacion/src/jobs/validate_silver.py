"""
validate_silver.py

Despues de que Spark haya escrito Silver, lo leo de vuelta y compruebo
que cumple lo que se supone que tiene que cumplir:
  - Existe y se puede leer.
  - Tiene mas de cero filas.
  - Los tipos son los que toca (timestamp es datetime, temperature es float).
  - No hay nulos en event_id, timestamp ni device_id.
  - event_id es unico (la deduplicacion funciono).

Si algo falla la tarea aborta y el DAG no continua. Sirve de red de
seguridad por si bronze_to_silver "termina bien" pero deja una salida
corrupta o vacia.

Uso:
    python validate_silver.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

import pandas as pd

from lib_paths import (
    PANDAS_S3_STORAGE_OPTIONS,
    SILVER_S3_BASE,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=False)
    parser.add_argument("--min-rows", type=int, default=1,
                        help="Numero minimo de filas para considerar Silver valido")
    args = parser.parse_args()

    print(f"Leyendo Silver desde {SILVER_S3_BASE}")
    try:
        df = pd.read_parquet(SILVER_S3_BASE, storage_options=PANDAS_S3_STORAGE_OPTIONS)
    except Exception as e:
        sys.exit(f"ABORT: no se puede leer Silver Parquet: {e}")

    n_filas = len(df)
    if n_filas < args.min_rows:
        sys.exit(f"ABORT: Silver solo tiene {n_filas} filas (minimo esperado {args.min_rows}).")

    columnas_obligatorias = {
        "event_id", "device_id", "timestamp",
        "temperature", "humidity", "co2", "battery", "status",
        "year", "month", "day", "hour",
    }
    faltan = columnas_obligatorias - set(df.columns)
    if faltan:
        sys.exit(f"ABORT: faltan columnas en Silver: {faltan}")

    # Comprobacion de tipos basicos
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        sys.exit(f"ABORT: timestamp no es datetime64 sino {df['timestamp'].dtype}")

    if not pd.api.types.is_float_dtype(df["temperature"]):
        sys.exit(f"ABORT: temperature deberia ser float, es {df['temperature'].dtype}")

    # Nulos en columnas criticas
    for col in ("event_id", "device_id", "timestamp"):
        n_nulos = df[col].isna().sum()
        if n_nulos > 0:
            sys.exit(f"ABORT: {col} tiene {n_nulos} nulos en Silver (deberian ser 0)")

    # Idempotencia: event_id unico
    n_unicos = df["event_id"].nunique()
    if n_unicos != n_filas:
        sys.exit(f"ABORT: event_id duplicados en Silver ({n_filas - n_unicos} duplicados)")

    print(f"OK Silver pasa todas las validaciones")
    print(f"   Filas: {n_filas}")
    print(f"   Columnas: {sorted(df.columns)}")
    print(f"   Rango temperatura: [{df['temperature'].min():.2f}, {df['temperature'].max():.2f}]")
    print(f"   Rango humedad:     [{df['humidity'].min():.2f}, {df['humidity'].max():.2f}]")
    print(f"   Rango CO2:         [{df['co2'].min()}, {df['co2'].max()}]")
    print(f"   Rango bateria:     [{df['battery'].min()}, {df['battery'].max()}]")


if __name__ == "__main__":
    main()
