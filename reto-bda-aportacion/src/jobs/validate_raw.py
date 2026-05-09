"""
validate_raw.py

Lee el JSONL de Bronze, aplica las reglas de src/quality/rules_iot.yaml y
escribe dos cosas en MinIO:
  - quarantine/iot/<device>/<fecha>/quarantine.jsonl: los registros que
    fallan, con un campo extra _quality_errors que lista los motivos.
  - quality/iot/<device>/<fecha>/report.json: el resumen del lote
    (totales, conteo por regla, conteo por dimension).

Las dimensiones que uso son las que veiamos en clase: precision,
completitud y consistencia.

Aqui no deduplico todavia, solo detecto los duplicados; la deduplicacion
real la hace Spark mas adelante con dropDuplicates(["event_id"]).

Para 1000 filas pandas + pyyaml es de sobra. Great Expectations seria
matar moscas a cañonazos para este volumen.

Uso:
    python validate_raw.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
import io
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import s3fs
import yaml
from hdfs import InsecureClient

from lib_paths import (
    BRONZE_HDFS_BASE,
    DEVICE_ID,
    HDFS_NAMENODE_HTTP,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    PANDAS_S3_STORAGE_OPTIONS,
    QUALITY_S3_BASE,
    QUARANTINE_S3_BASE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger("validate_raw")


# -----------------------------------------------------------------------------
# Carga de reglas
# -----------------------------------------------------------------------------
def cargar_reglas(yaml_path: Path) -> dict:
    """
    Cargamos las reglas como dict.  Centralizar reglas en YAML evita que la
    logica de validacion se mezcle con los umbrales: cualquier ajuste de
    rango se hace fuera del codigo Python (UT3.4 contratos de datos).
    """
    with yaml_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# -----------------------------------------------------------------------------
# Lectura de Bronze (HDFS) sin trampas: leemos el crudo como string para no
# perder fallos de "completitud" en el parseo automatico de pandas.
# -----------------------------------------------------------------------------
def leer_bronze_jsonl(client: InsecureClient, run_date: datetime) -> list[dict]:
    """
    Lee TODOS los .jsonl de la particion Bronze del dia.
    Devuelve los registros como dicts crudos: NO castea timestamp ni nada,
    porque queremos detectar valores vacios "tal cual llegaron".
    """
    hdfs_dir = (
        f"{BRONZE_HDFS_BASE}"
        f"/year={run_date.year}"
        f"/month={run_date.month:02d}"
        f"/day={run_date.day:02d}"
    )
    log.info(f"Leyendo Bronze desde {HDFS_NAMENODE_HTTP}{hdfs_dir}")

    registros: list[dict] = []
    for nombre in client.list(hdfs_dir, status=False):
        if not nombre.endswith(".jsonl"):
            continue
        ruta_completa = f"{hdfs_dir}/{nombre}"
        with client.read(ruta_completa, encoding="utf-8") as reader:
            for linea in reader:
                linea = linea.strip()
                if not linea:
                    continue
                # json.loads preserva los tipos originales del JSON: las
                # cadenas vacias siguen siendo "" y NO se convierten a None.
                registros.append(json.loads(linea))
    log.info(f"   leidos {len(registros)} registros crudos")
    return registros


# -----------------------------------------------------------------------------
# Reglas individuales: cada una devuelve una lista de "motivos" por registro.
# Asi un mismo registro puede acumular varios errores (mas informativo).
# -----------------------------------------------------------------------------
def _es_vacio(valor) -> bool:
    """None, NaN, o cadena vacia/whitespace -> faltante."""
    if valor is None:
        return True
    if isinstance(valor, float) and pd.isna(valor):
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    return False


def aplicar_reglas(registros: list[dict], reglas: dict) -> tuple[list[dict], list[dict], dict]:
    """
    Recorre los registros aplicando las reglas y devuelve:
      - validos: registros que pasan TODAS las reglas
      - invalidos: registros con al menos un fallo (con _quality_errors)
      - resumen: contador agrupado por dimension y por regla concreta

    Implementacion deliberadamente plana y explicita (sin metaclases ni
    decoradores) para que el profesor lea el flujo de un vistazo.
    """
    required = reglas["schema"]["required"]
    ranges = reglas["ranges"]
    ts_field = reglas["timestamp"]["field"]
    ts_format = reglas["timestamp"]["format"]
    unique_fields = [u["field"] for u in reglas["unique"]]
    expected_device = reglas["expected_device_id"]

    # Para detectar duplicados necesitamos el conteo por valor de cada campo unique
    counts_unique = {f: Counter(r.get(f) for r in registros) for f in unique_fields}

    contador_por_regla: Counter = Counter()

    validos: list[dict] = []
    invalidos: list[dict] = []

    for r in registros:
        errores: list[str] = []

        # 1) Dimension COMPLETITUD: campos requeridos no vacios
        for col in required:
            if col not in r or _es_vacio(r.get(col)):
                errores.append(f"missing_{col}")

        # 2) Dimension PRECISION: rangos fisicos
        for col, rng in ranges.items():
            v = r.get(col)
            if v is None or (isinstance(v, str) and v.strip() == ""):
                continue  # ya capturado por completitud
            try:
                vnum = float(v)
                if not (rng["min"] <= vnum <= rng["max"]):
                    errores.append(f"{col}_out_of_range")
            except (TypeError, ValueError):
                errores.append(f"{col}_not_numeric")

        # 3) Dimension COMPLETITUD: timestamp parseable
        ts = r.get(ts_field)
        if ts and isinstance(ts, str):
            try:
                datetime.strptime(ts, ts_format)
            except ValueError:
                errores.append("timestamp_invalid_format")

        # 4) Dimension CONSISTENCIA: duplicados por campo unique
        for f in unique_fields:
            if counts_unique[f][r.get(f)] > 1:
                errores.append(f"duplicate_{f}")

        # 5) Defensa anti schema-drift: device_id inesperado
        if r.get("device_id") and r.get("device_id") != expected_device:
            errores.append("unexpected_device_id")

        # Acumulamos para el informe
        for e in errores:
            contador_por_regla[e] += 1

        if errores:
            r2 = dict(r)
            r2["_quality_errors"] = errores
            invalidos.append(r2)
        else:
            validos.append(r)

    # Agrupamos por dimension para el informe ejecutivo
    dim_de_regla: dict[str, str] = {}
    for col, rng in ranges.items():
        dim_de_regla[f"{col}_out_of_range"] = rng["dimension"]
        dim_de_regla[f"{col}_not_numeric"] = rng["dimension"]
    for col in required:
        dim_de_regla[f"missing_{col}"] = "completitud"
    dim_de_regla["timestamp_invalid_format"] = reglas["timestamp"]["dimension"]
    for u in reglas["unique"]:
        dim_de_regla[f"duplicate_{u['field']}"] = u["dimension"]
    dim_de_regla["unexpected_device_id"] = "fiabilidad"

    por_dimension: dict[str, int] = defaultdict(int)
    for regla, n in contador_por_regla.items():
        por_dimension[dim_de_regla.get(regla, "otro")] += n

    resumen = {
        "total_records": len(registros),
        "valid_records": len(validos),
        "invalid_records": len(invalidos),
        "by_rule": dict(contador_por_regla),
        "by_dimension": dict(por_dimension),
    }
    return validos, invalidos, resumen


# -----------------------------------------------------------------------------
# Escritura a MinIO: cuarentena (JSONL) + informe (JSON)
# -----------------------------------------------------------------------------
def escribir_cuarentena(invalidos: list[dict], run_date: datetime, fs: s3fs.S3FileSystem) -> str | None:
    if not invalidos:
        log.info("   no hay registros en cuarentena (todo paso las reglas)")
        return None

    fecha_str = run_date.strftime("%Y-%m-%d")
    # bucket/prefix sin el "s3://" para s3fs.open
    ruta = f"{MINIO_BUCKET}/quarantine/iot/{DEVICE_ID}/{fecha_str}/quarantine.jsonl"

    # Escribimos linea a linea para mantener el formato JSONL (UT5).
    with fs.open(ruta, "w", encoding="utf-8") as f:
        for r in invalidos:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    log.info(f"   cuarentena -> s3://{ruta}  ({len(invalidos)} registros)")
    return f"s3://{ruta}"


def escribir_informe(resumen: dict, run_date: datetime, fs: s3fs.S3FileSystem) -> str:
    fecha_str = run_date.strftime("%Y-%m-%d")
    ruta = f"{MINIO_BUCKET}/quality/iot/{DEVICE_ID}/{fecha_str}/report.json"

    # Anyadimos metadatos: cuando se ejecuto y para que dia.
    informe = {
        "device_id": DEVICE_ID,
        "run_date": fecha_str,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **resumen,
    }
    with fs.open(ruta, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)

    log.info(f"   informe   -> s3://{ruta}")
    return f"s3://{ruta}"


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--rules", type=str, default="/opt/airflow/quality/rules_iot.yaml",
                        help="Ruta al YAML de reglas (default: ruta dentro de Airflow)")
    args = parser.parse_args()

    run_date = datetime.fromisoformat(args.date)

    # 1. Cargar reglas. Si la ruta del Airflow no existe (caso Jupyter local),
    #    probamos la ruta relativa al cwd (src/quality/).
    rules_path = Path(args.rules)
    if not rules_path.exists():
        alt = Path.cwd() / "src" / "quality" / "rules_iot.yaml"
        if alt.exists():
            rules_path = alt
        else:
            raise FileNotFoundError(
                f"No encuentro reglas en {args.rules} ni en {alt}"
            )
    reglas = cargar_reglas(rules_path)
    log.info(f"Reglas cargadas desde {rules_path}")

    # 2. Leer Bronze
    hdfs_client = InsecureClient(HDFS_NAMENODE_HTTP, user="jovyan")
    registros = leer_bronze_jsonl(hdfs_client, run_date)

    # 3. Validar
    validos, invalidos, resumen = aplicar_reglas(registros, reglas)

    # 4. Escribir cuarentena + informe a MinIO (estilo notebook 01 del profesor)
    fs = s3fs.S3FileSystem(
        key=MINIO_ACCESS_KEY,
        secret=MINIO_SECRET_KEY,
        client_kwargs={"endpoint_url": MINIO_ENDPOINT},
    )
    escribir_cuarentena(invalidos, run_date, fs)
    escribir_informe(resumen, run_date, fs)

    # 5. Resumen "ejecutivo" en log para Airflow
    print("=" * 60)
    print("INFORME DE CALIDAD")
    print("=" * 60)
    print(f"Total: {resumen['total_records']}  "
          f"Validos: {resumen['valid_records']}  "
          f"Invalidos: {resumen['invalid_records']}")
    print("\nPor dimension:")
    for dim, n in sorted(resumen["by_dimension"].items()):
        print(f"   {dim:15s} {n}")
    print("\nPor regla:")
    for regla, n in sorted(resumen["by_rule"].items()):
        print(f"   {regla:30s} {n}")

    # Politica de fallo: si hay >50% invalidos, hacemos fallar la tarea.
    # Esto refleja la idea UT3.4 de que un pipeline NO debe seguir si los
    # datos estan tan rotos que no merecen procesarse aguas abajo.
    if resumen["invalid_records"] > resumen["total_records"] * 0.5:
        raise RuntimeError(
            "ABORT: mas del 50% de registros invalidos. "
            "Revisar el generador o la configuracion del sensor."
        )


if __name__ == "__main__":
    main()
