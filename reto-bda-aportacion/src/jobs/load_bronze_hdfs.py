"""
load_bronze_hdfs.py

Coge el JSONL local que escribio el generador y lo sube a HDFS, dentro de
una carpeta con el nombre year=YYYY/month=MM/day=DD/ (Hive partitioning).

No transformo nada: la regla de Bronze es guardar el dato tal como llega.
Si Silver o Gold petan despues, siempre puedo volver aqui y reprocesar.

Uso WebHDFS (puerto 9870) en vez de la CLI hdfs dfs -put porque el
contenedor de airflow no trae los binarios de Hadoop. La libreria hdfs
de Python hace lo mismo desde codigo, y es el mismo patron que aparece
en el notebook 01_Demo_Lectura_Escritura_HDFS_S3.

Uso:
    python load_bronze_hdfs.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from hdfs import InsecureClient

from lib_paths import BRONZE_HDFS_BASE, DEVICE_ID, HDFS_NAMENODE_HTTP, LOCAL_RAW_DIRNAME


def construir_ruta_hdfs(run_date: datetime) -> str:
    """
    Devuelve la carpeta de HDFS donde toca dejar el JSONL:
        /datalake/bronze/iot/sensor_aula_01/year=2026/month=04/day=30

    El formato columna=valor lo entiende Spark de caja: cuando lea esa
    ruta, infiere las columnas year/month/day automaticamente.
    """
    return (
        f"{BRONZE_HDFS_BASE}"
        f"/year={run_date.year}"
        f"/month={run_date.month:02d}"
        f"/day={run_date.day:02d}"
    )


def subir_a_bronze(local_file: Path, run_date: datetime, client: InsecureClient) -> str:
    """
    Sube un fichero local a HDFS Bronze sin alterarlo.
    Usa makedirs (idempotente) y upload con overwrite=True para que
    re-ejecutar el DAG sobre la misma fecha sea seguro.
    """
    hdfs_dir = construir_ruta_hdfs(run_date)
    client.makedirs(hdfs_dir)

    hdfs_path = f"{hdfs_dir}/{local_file.name}"
    # upload() ya hace streaming, no carga el fichero en memoria
    client.upload(hdfs_path, str(local_file), overwrite=True)
    return hdfs_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=True,
                        help="Fecha logica del run (YYYY-MM-DD)")
    parser.add_argument("--raw-dir", type=str, default=None,
                        help="Carpeta raiz local de los JSONL (por defecto: cwd/data/raw)")
    parser.add_argument("--user", type=str, default="jovyan",
                        help="Usuario HDFS (por defecto jovyan, sin Kerberos en el lab)")
    args = parser.parse_args()

    run_date = datetime.fromisoformat(args.date)
    raw_root = Path(args.raw_dir) if args.raw_dir else (Path.cwd() / LOCAL_RAW_DIRNAME)

    fecha_str = run_date.strftime("%Y-%m-%d")
    carpeta_local = raw_root / DEVICE_ID / fecha_str

    if not carpeta_local.exists():
        raise FileNotFoundError(
            f"No existe {carpeta_local}. "
            f"Ejecuta antes 'generate_iot_data.py --date {args.date}'."
        )

    # Patron del notebook 01_Demo_HDFS_S3:
    #   hdfs_client = InsecureClient('http://namenode:9870', user='jovyan')
    client = InsecureClient(HDFS_NAMENODE_HTTP, user=args.user)

    ficheros = sorted(carpeta_local.glob("*.jsonl"))
    if not ficheros:
        raise FileNotFoundError(f"No hay .jsonl en {carpeta_local}")

    print(f"OK Subiendo {len(ficheros)} fichero(s) a HDFS Bronze ({HDFS_NAMENODE_HTTP})...")
    for local_file in ficheros:
        hdfs_path = subir_a_bronze(local_file, run_date, client)
        print(f"   {local_file.name}  ->  hdfs://{hdfs_path}")

    # Verificacion ligera: listamos lo que hay en la particion para que
    # el log del DAG sirva como evidencia rapida sin abrir HDFS Explorer.
    listing = client.list(construir_ruta_hdfs(run_date), status=False)
    print(f"\nContenido de la particion {fecha_str}:")
    for name in listing:
        print(f"   - {name}")


if __name__ == "__main__":
    main()
