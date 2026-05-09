"""
generate_iot_data.py

Simulador del dispositivo IoT del proyecto. Genera lecturas en formato
JSONL y las escribe en disco. Inyecta unos cuantos errores a proposito
para que la capa de validacion tenga algo que detectar.

El esquema y los rangos los saco del propio enunciado del reto. Los
errores tambien los inyecto siguiendo los ejemplos que sugiere el
enunciado (temperaturas imposibles, humedades negativas, duplicados
por "reintento de la cola IoT", etc.).

Uso:
    python generate_iot_data.py --records 1000 --error-rate 0.07 --date 2026-04-30
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Si se ejecuta como script suelto desde Jupyter, ajustar el sys.path no
# es necesario porque ambos ficheros viven en el mismo directorio.
from lib_paths import DEVICE_ID, LOCAL_RAW_DIRNAME


# -----------------------------------------------------------------------------
# Esquema fijo del registro IoT (siguiendo el ejemplo del enunciado E1).
# Cualquier desviacion de este esquema es trabajo de la capa de calidad (E3).
# -----------------------------------------------------------------------------
SCHEMA_FIELDS = (
    "event_id", "device_id", "timestamp",
    "temperature", "humidity", "co2", "battery", "status",
)


def generar_lectura_correcta(idx: int, base_ts: datetime, total_records: int) -> dict:
    """
    Genera una lectura "buena", con valores realistas para un aula:
        - event_id: contador + sufijo hex para evitar choques
        - timestamp: ISO sin Z (mismo formato que el ejemplo del enunciado)
        - temp ~ N(23, 2), hum ~ N(55, 8), CO2 ~ N(620, 80)
        - bateria: descarga lineal de 100 a 15 a lo largo del dia, con un
          poco de ruido. Asi al final del dia se cruza el umbral del 20%
          y aparecen alertas de bateria_baja en la capa Oro.
    """
    ts = base_ts + timedelta(seconds=idx * 30)  # una lectura cada 30s

    # Descarga lineal de la bateria. La curva real de una bateria de litio
    # no es exactamente lineal pero el tramo medio si lo es; me sirve para
    # ver la tendencia en el dashboard.
    progreso = idx / max(total_records - 1, 1)
    battery_base = 100.0 - progreso * 85.0
    battery = max(0, min(100, int(round(battery_base + random.gauss(0, 1.5)))))

    return {
        "event_id":    f"evt_{idx:06d}_{uuid.uuid4().hex[:6]}",
        "device_id":   DEVICE_ID,
        "timestamp":   ts.replace(tzinfo=None).isoformat(timespec="seconds"),
        "temperature": round(random.gauss(23.0, 2.0), 2),
        "humidity":    round(random.gauss(55.0, 8.0), 2),
        "co2":         max(350, int(random.gauss(620, 80))),
        "battery":     battery,
        "status":      "OK",
    }


def inyectar_error(record: dict) -> dict:
    """
    Cambia el registro para que falle alguna regla de calidad. Ocho tipos
    posibles que cubren TODA la lista de pistas del enunciado:
      - temp_outlier      : temperatura fuera de rango (precision)
      - humedad_neg       : humedad negativa (precision)
      - bateria_alta      : bateria > 100% (precision)
      - bateria_negativa  : bateria negativa (precision)
      - co2_null          : CO2 nulo, prueba la deteccion de "campos nulos"
                            que pide el enunciado (completitud)
      - ts_vacio          : timestamp vacio (completitud)
      - ts_malformado     : timestamp con formato distinto al ISO esperado,
                            prueba "fechas mal formadas" del enunciado
                            (completitud)
      - duplicado         : evento duplicado por reintento de cola IoT
                            (consistencia)
    Marca el registro con status='ERR' para que se vea en el log.
    """
    tipo = random.choice([
        "temp_outlier", "humedad_neg",
        "bateria_alta", "bateria_negativa",
        "co2_null",
        "ts_vacio", "ts_malformado",
        "duplicado",
    ])

    if tipo == "temp_outlier":
        # Temperatura imposible (sensor descalibrado).
        record["temperature"] = 150.0
    elif tipo == "humedad_neg":
        # Humedad negativa (no tiene sentido fisico).
        record["humidity"] = -10.0
    elif tipo == "bateria_alta":
        # Bateria por encima del 100% (algun bug de firmware).
        record["battery"] = 130
    elif tipo == "bateria_negativa":
        # Bateria negativa: el enunciado lo cita explicitamente como
        # ejemplo de error a inyectar. Refuerza la deteccion de rangos.
        record["battery"] = -5
    elif tipo == "co2_null":
        # Campo nulo en una metrica numerica. validate_raw lo detecta
        # como missing_co2 (dimension completitud) porque co2 esta en
        # schema.required del YAML. El None se serializa a JSON como
        # 'null' y al volverlo a parsear queda como None.
        record["co2"] = None
    elif tipo == "ts_vacio":
        # Marca temporal vacia (la red perdio el momento de la lectura).
        record["timestamp"] = ""
    elif tipo == "ts_malformado":
        # Timestamp con formato no ISO. validate_raw lo detecta como
        # timestamp_invalid_format al fallar el strptime con el formato
        # del YAML. Distinto fallo de ts_vacio aunque ambos sean
        # completitud.
        record["timestamp"] = "30/04/2026 10:15"
    elif tipo == "duplicado":
        # Marco el registro para que el caller lo clone fuera. Asi simulo
        # un reintento de la cola IoT (el mismo evento llega dos veces).
        record["_marca_duplicar"] = True

    record["status"] = "ERR"
    return record


def generar_dataset(n_records: int, error_rate: float, base_ts: datetime) -> list[dict]:
    """
    Devuelve la lista de registros del dia, con un error_rate aproximado
    de ellos rotos a proposito.
    """
    registros: list[dict] = []
    for i in range(n_records):
        rec = generar_lectura_correcta(i, base_ts, n_records)
        if random.random() < error_rate:
            rec = inyectar_error(rec)
            if rec.pop("_marca_duplicar", False):
                # Para el caso "duplicado" anyado el registro dos veces.
                # Asi el validador debe detectarlo y rechazarlo.
                registros.append(rec)
                rec = dict(rec)
        registros.append(rec)
    return registros


def escribir_jsonl(registros: list[dict], destino: Path) -> None:
    """
    Escribe los registros en un fichero JSONL (una linea = un registro).
    No uso pandas aposta porque en un sensor real los datos llegarian de
    uno en uno y este es el formato natural.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as f:
        for r in registros:
            # Mantenemos solo los campos del esquema (drop _marca_duplicar
            # u otros internos por si se filtran).
            limpio = {k: r.get(k) for k in SCHEMA_FIELDS}
            f.write(json.dumps(limpio, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=1000,
                        help="Numero de registros a generar")
    parser.add_argument("--error-rate", type=float, default=0.07,
                        help="Proporcion de registros con error (0.0 a 1.0)")
    parser.add_argument("--date", type=str, default=None,
                        help="Fecha logica YYYY-MM-DD (por defecto: hoy)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla para reproducibilidad (E1 puntua reproducibilidad)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directorio raiz para data/raw (por defecto: cwd/data/raw)")
    args = parser.parse_args()

    random.seed(args.seed)

    # Fecha logica del run (en Airflow vendra de la macro {{ ds }}).
    if args.date:
        run_date = datetime.fromisoformat(args.date)
    else:
        run_date = datetime.now(timezone.utc).replace(tzinfo=None).date()
        run_date = datetime.combine(run_date, datetime.min.time())

    # Hora de inicio del lote: 09:00 del dia (lectura cada 30s -> 1000 registros = ~8h)
    base_ts = run_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # Ruta de salida: data/raw/sensor_aula_01/YYYY-MM-DD/HHMM.jsonl
    if args.output_dir:
        raw_root = Path(args.output_dir)
    else:
        raw_root = Path.cwd() / LOCAL_RAW_DIRNAME

    fecha_str = run_date.strftime("%Y-%m-%d")
    fichero = raw_root / DEVICE_ID / fecha_str / f"{base_ts.strftime('%H%M')}.jsonl"

    # 1. Generamos
    registros = generar_dataset(args.records, args.error_rate, base_ts)

    # 2. Escribimos
    escribir_jsonl(registros, fichero)

    # 3. Resumen para los logs de Airflow
    n_err = sum(1 for r in registros if r.get("status") == "ERR")
    print(f"OK Generados {len(registros)} registros en {fichero}")
    print(f"   Errores inyectados: {n_err} (~{n_err/len(registros)*100:.1f}%)")
    print(f"   Esquema: {SCHEMA_FIELDS}")


if __name__ == "__main__":
    main()
