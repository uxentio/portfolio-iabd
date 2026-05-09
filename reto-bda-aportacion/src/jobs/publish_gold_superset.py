"""
publish_gold_superset.py

Tarea final del DAG. Hace dos cosas:

1) Lee los tres Parquet de Gold con pandas+s3fs (la misma libreria que
   DuckDB usa por debajo) y comprueba que tienen filas. Si alguno esta
   vacio o ilegible, aborta.

2) Escribe un manifest.json en s3://datalake/published/iot/<device>/<fecha>/
   con metadatos del run (n filas por dataset, columnas, fecha). Sirve
   como "contrato" para que cualquier consumidor (Superset u otro) sepa
   si los datos son frescos.

No llamo a la API REST de Superset desde el DAG porque eso requeriria
credenciales y acoplaria el pipeline a la herramienta de visualizacion.
Mejor un fichero plano en MinIO que cualquiera puede leer.

Uso:
    python publish_gold_superset.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import pandas as pd
import s3fs

from lib_paths import (
    DEVICE_ID,
    GOLD_S3_BASE,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    PANDAS_S3_STORAGE_OPTIONS,
)

DATASETS_GOLD = ("hourly_metrics", "daily_summary", "anomalies")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=True)
    args = parser.parse_args()

    run_date = datetime.fromisoformat(args.date)
    fecha_str = run_date.strftime("%Y-%m-%d")

    manifiesto = {
        "device_id": DEVICE_ID,
        "run_date": fecha_str,
        "published_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "datasets": {},
    }

    print("Smoke test de datasets Gold (lectura desde MinIO)...")
    for ds in DATASETS_GOLD:
        ruta = f"{GOLD_S3_BASE}/{ds}"
        try:
            df = pd.read_parquet(ruta, storage_options=PANDAS_S3_STORAGE_OPTIONS)
        except Exception as e:
            sys.exit(f"ABORT: no se puede leer {ruta}: {e}")

        n_filas = len(df)
        if n_filas == 0:
            sys.exit(f"ABORT: {ds} esta vacio")

        manifiesto["datasets"][ds] = {
            "path": ruta,
            "rows": n_filas,
            "columns": list(df.columns),
        }
        print(f"   OK {ds:18s} {n_filas:4d} filas")

    # Publicar manifiesto en MinIO
    fs = s3fs.S3FileSystem(
        key=MINIO_ACCESS_KEY,
        secret=MINIO_SECRET_KEY,
        client_kwargs={"endpoint_url": MINIO_ENDPOINT},
    )
    ruta_manifiesto = f"{MINIO_BUCKET}/published/iot/{DEVICE_ID}/{fecha_str}/manifest.json"
    with fs.open(ruta_manifiesto, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=2)
    print(f"\nOK Manifiesto publicado en s3://{ruta_manifiesto}")

    # Recordatorio operativo en el log para que el alumno no se pierda
    print(
        "\nSiguiente paso: cambiar al perfil 'bi' y abrir Superset.\n"
        "  docker compose ... down --remove-orphans\n"
        "  docker compose ... --profile core --profile bi up -d\n"
        "  -> http://localhost:8089"
    )


if __name__ == "__main__":
    main()
