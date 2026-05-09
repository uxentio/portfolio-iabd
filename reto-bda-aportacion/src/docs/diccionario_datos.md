# Diccionario de Datos - Reto 02 RA5

**Sensor unico:** `sensor_aula_01` (sensor ambiental simulado para aula).
**Frecuencia:** una lectura cada 30 segundos (~1000 registros por dia).

## Capa BRONZE - JSONL crudo en HDFS

**Ruta:** `hdfs://namenode:9000/datalake/bronze/iot/sensor_aula_01/year=YYYY/month=MM/day=DD/HHMM.jsonl`

**Formato:** Una linea = un JSON valido.

| Campo | Tipo (JSON) | Descripcion | Notas / Errores posibles |
|---|---|---|---|
| `event_id` | string | Identificador unico del evento (`evt_NNNNNN_HEXHEXH`) | Pueden aparecer DUPLICADOS por reintentos de la "cola simulada" (UT3.4) |
| `device_id` | string | Identificador del dispositivo. Constante: `sensor_aula_01` | Defendido contra "schema drift" (UT3.4 ej.3) |
| `timestamp` | string | Marca temporal ISO `"YYYY-MM-DDTHH:MM:SS"` (UTC sin sufijo Z) | Puede llegar VACIO `""` o MAL FORMADO `"30/04/2026 10:15"` (completitud) |
| `temperature` | number | Temperatura en grados Celsius | Puede aparecer FUERA DE RANGO: `150.0` (sensor descalibrado, UT3.1.c) |
| `humidity` | number | Humedad relativa % | Puede aparecer NEGATIVA: `-10.0` (precision rota) |
| `co2` | integer | CO2 en partes por millon (ppm) | Esperado 350-2000; alertas a partir de 1000. Puede llegar NULO (completitud) |
| `battery` | integer | Bateria del dispositivo % | Puede aparecer >100 (`130`, firmware bug) o NEGATIVA (`-5`, precision rota) |
| `status` | string | `"OK"` para registros validos, `"ERR"` para los inyectados con error | Solo informativo; la validacion real la hace `validate_raw.py` |

**Tasa de errores esperada:** ~7% (configurable via `--error-rate` en el generador). Los errores se reparten uniformemente entre 8 tipos: `temp_outlier`, `humedad_neg`, `bateria_alta`, `bateria_negativa`, `co2_null`, `ts_vacio`, `ts_malformado`, `duplicado`. Cubren las tres dimensiones de calidad (precision, completitud, consistencia).

---

## Capa de CALIDAD - Cuarentena y Informe en MinIO

### Cuarentena

**Ruta:** `s3://datalake/quarantine/iot/sensor_aula_01/YYYY-MM-DD/quarantine.jsonl`

Mismo esquema que Bronze + un campo extra:

| Campo | Tipo | Descripcion |
|---|---|---|
| `_quality_errors` | array de strings | Lista de motivos por los que el registro fue rechazado. Ejemplo: `["temperature_out_of_range", "duplicate_event_id"]` |

### Informe

**Ruta:** `s3://datalake/quality/iot/sensor_aula_01/YYYY-MM-DD/report.json`

```json
{
  "device_id": "sensor_aula_01",
  "run_date": "2026-04-27",
  "generated_at_utc": "2026-04-27T18:00:00+00:00",
  "total_records": 1000,
  "valid_records": 932,
  "invalid_records": 68,
  "by_rule": {
    "temperature_out_of_range": 14,
    "humidity_out_of_range": 13,
    "battery_out_of_range": 11,
    "missing_timestamp": 12,
    "duplicate_event_id": 18
  },
  "by_dimension": {
    "precision": 38,
    "completitud": 12,
    "consistencia": 18
  }
}
```

Las claves `by_dimension` mapean a las **tres dimensiones de calidad** definidas
por el profesor en UT3.1 (ver `1. Calidad y fiabilidad de los datos.md`).

---

## Capa SILVER - Parquet limpio en MinIO

**Ruta:** `s3a://datalake/silver/iot/sensor_aula_01/year=YYYY/month=MM/day=DD/`
(`s3a://` desde Spark, `s3://` desde pandas/duckdb)

**Formato:** Parquet snappy, particionado Hive por `year/month/day`.

| Campo | Tipo (Spark) | Descripcion |
|---|---|---|
| `event_id` | StringType | Identificador unico (deduplicado: aqui ya no hay duplicados) |
| `device_id` | StringType | `"sensor_aula_01"` |
| `timestamp` | TimestampType | Parseado de la cadena ISO de Bronze |
| `temperature` | DoubleType | En rango fisico [-20, 80] |
| `humidity` | DoubleType | En rango fisico [0, 100] |
| `co2` | IntegerType | En rango fisico [0, 5000] |
| `battery` | IntegerType | En rango fisico [0, 100] |
| `status` | StringType | Conservamos el campo aunque ya no haya `"ERR"` |
| `year` | IntegerType | Columna de particion (derivada de `timestamp`) |
| `month` | IntegerType | Columna de particion |
| `day` | IntegerType | Columna de particion |
| `hour` | IntegerType | Columna NO particion (para agregaciones rapidas en Gold) |

**Garantias de Silver:**
- 0 registros con timestamp invalido
- 0 registros fuera de rango
- 0 duplicados de `event_id` (idempotencia, UT3.4)
- Tipos correctos (no strings sin parsear)

---

## Capa GOLD - 3 datasets agregados en MinIO

### `hourly_metrics/`

**Ruta:** `s3a://datalake/gold/iot/sensor_aula_01/hourly_metrics/`
**Granularidad:** una fila por hora (24 filas por dia).

| Campo | Tipo | Descripcion |
|---|---|---|
| `year` | int | |
| `month` | int | |
| `day` | int | |
| `hour` | int | 0-23 |
| `temp_avg` | double | Temperatura media de la hora (2 decimales) |
| `temp_min` | double | Minima de la hora |
| `temp_max` | double | Maxima de la hora |
| `hum_avg` | double | Humedad media (2 decimales) |
| `co2_avg` | double | CO2 medio (entero redondeado) |
| `battery_min` | int | Bateria minima en la hora |
| `n_valid_events` | long | Numero de lecturas validas en la hora (las que llegaron a Silver) |
| `n_invalid_events` | long | Numero de lecturas que fueron a cuarentena en esa hora (las que tienen timestamp parseable; el resto se cuenta a nivel diario) |
| `n_events` | long | Total: `n_valid_events + n_invalid_events` |
| `pct_valid` | double | Porcentaje de validez de la hora (`n_valid_events / n_events * 100`) |
| `n_alerts` | long | Numero de anomalias detectadas en esa hora (un evento puede dispararse por varios tipos, cuenta total) |

### `daily_summary/`

**Ruta:** `s3a://datalake/gold/iot/sensor_aula_01/daily_summary/`
**Granularidad:** una fila por dia.

| Campo | Tipo | Descripcion |
|---|---|---|
| `year`, `month`, `day` | int | Particion logica |
| `temp_avg` | double | Temperatura media del dia |
| `hum_avg` | double | Humedad media |
| `co2_avg` | double | CO2 medio |
| `battery_min` | int | Bateria mas baja del dia (KPI de salud del sensor) |
| `n_valid_events` | long | Lecturas validas del dia |
| `n_invalid_events` | long | Lecturas que fueron a cuarentena ese dia (la fecha sale del path de cuarentena, no del timestamp interno, asi que cuenta TODOS los invalidos del dia) |
| `n_events` | long | Total recibido en el dia |
| `pct_valid` | double | Porcentaje diario de registros que pasaron la validacion |
| `n_alerts` | long | Anomalias detectadas en el dia |

### `anomalies/`

**Ruta:** `s3a://datalake/gold/iot/sensor_aula_01/anomalies/`
**Granularidad:** una fila por evento sospechoso. Un mismo evento aparece
una vez por cada tipo de anomalia que dispara (ej.: si tiene CO2 alto Y
temperatura alta, aparecera dos veces, una por tipo).

| Campo | Tipo | Descripcion |
|---|---|---|
| `event_id` | string | Trazabilidad al evento original |
| `timestamp` | timestamp | |
| `temperature`, `humidity`, `co2`, `battery` | numericos | Lecturas |
| `year`, `month`, `day`, `hour` | int | |
| `anomaly_type` | string | Uno de: `temperatura_alta`, `temperatura_baja`, `humedad_alta`, `humedad_baja`, `co2_elevado`, `bateria_baja` |

**Umbrales de anomalia** (no son fisicos; son contextuales para un aula):

| Tipo | Condicion |
|---|---|
| `temperatura_alta` | `temperature > 28.0` |
| `temperatura_baja` | `temperature < 18.0` |
| `humedad_alta` | `humidity > 70.0` |
| `humedad_baja` | `humidity < 30.0` |
| `co2_elevado` | `co2 > 1000` (umbral comun de ventilacion) |
| `bateria_baja` | `battery < 20` |
