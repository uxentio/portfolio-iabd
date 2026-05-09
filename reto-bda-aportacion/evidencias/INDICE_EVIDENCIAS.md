# Indice de Evidencias - Reto 02 RA5

Capturas del pipeline IoT Medallon ejecutado por autor.
Ordenadas por timestamp (filename).

## Cronologia del proyecto

### 30/04/2026 - Pipeline funcionando (HDFS, MinIO)

Capturas del entorno tras la ejecucion exitosa del DAG:

| Timestamp | Probable contenido | Cubre criterio |
|---|---|---|
| 17:12-17:13 | Lista DAGs Airflow, MinIO datalake con quality | E6, E3 |
| 17:15-17:16 | MinIO Gold (sensor_aula_01 carpetas) | E5 |
| 17:22-17:30 | Graph view DAG verde + log Spark + HDFS Bronze | E6, E2 |
| 17:31-17:35 | MinIO Silver Parquet, Cuarentena, Gold subcarpetas | E4, E3, E5 |
| 17:42 | Vista final HDFS/MinIO | E2-E5 |

### 01/05/2026 - Superset y Dashboard

| Timestamp | Probable contenido | Cubre criterio |
|---|---|---|
| 10:23-10:34 | Configuracion conexion DuckDB-MinIO en Superset | E7 |
| 10:36-10:54 | Datasets virtuales (gold_hourly, gold_daily, gold_anomalies) | E7 |
| 10:58-11:05 | Creacion Chart 1 (Line evolucion temp/hum/CO2) | E7 (0,2pt) |
| 11:10-11:14 | Mejora Chart 1 a doble eje Y (Mixed Chart) | E7 calidad |
| 11:18-11:24 | Charts 2, 3, 4 (Bar anomalias, Big Number, Tabla) + Dashboard | E7 (0,6pt) |

## Mapeo recomendado a la memoria PDF

Para insertar en el PDF, agrupa las capturas en estas secciones:

### Capa Bronze (HDFS)
- `2026-04-30 1727...` - HDFS Browser mostrando `/datalake/bronze/iot/sensor_aula_01/year=2026/month=04/day=30/0900.jsonl` (183 KB)

### Validacion / Calidad
- `2026-04-30 17...` - MinIO mostrando carpetas `quality/` y `quarantine/`
- `2026-04-30 17...` - Contenido de quarantine.jsonl (17.8 KiB)
- Adjuntar tambien el `report.json` literal (459 B):
```json
{
  "device_id": "sensor_aula_01",
  "run_date": "2026-04-30",
  "total_records": 1016,
  "valid_records": 936,
  "invalid_records": 80,
  "by_rule": {
    "humidity_out_of_range": 13,
    "battery_out_of_range": 14,
    "temperature_out_of_range": 10,
    "duplicate_event_id": 32,
    "missing_timestamp": 11
  },
  "by_dimension": {
    "precision": 37,
    "consistencia": 32,
    "completitud": 11
  }
}
```

### Capa Silver (MinIO Parquet)
- `2026-04-30 17...` - MinIO `silver/iot/sensor_aula_01/year=2026/month=4/day=30/part-00000-...snappy.parquet` (32 KiB)

### Capa Gold (3 datasets en MinIO)
- `2026-04-30 17...` - MinIO `gold/iot/sensor_aula_01/` con 3 subcarpetas: anomalies, daily_summary, hourly_metrics
- `2026-04-30 17...` - hourly_metrics: _SUCCESS + 1 parquet (3.4 KiB)
- `2026-04-30 17...` - daily_summary: _SUCCESS + 1 parquet (2.1 KiB)
- `2026-04-30 17...` - anomalies: _SUCCESS + 3 parquets (3.3, 3.5, 4.4 KiB)

### Orquestacion Airflow
- `2026-04-30 17...` - Lista DAGs con `iot_medallion_pipeline` y runs success/failed
- `2026-04-30 17...` - Graph view del DAG con las 6 tareas verdes
- `2026-04-30 17...` - Log de la tarea `4_bronze_to_silver` mostrando salida REAL de Spark

### Dashboard Superset
- `2026-05-01 10...` - Configuracion DuckDB con engine_params JSON
- `2026-05-01 10...` - Lista de datasets virtuales en Superset
- `2026-05-01 11...` - Chart 1: Line chart con doble eje Y (temp/hum + CO2)
- `2026-05-01 11...` - Chart 2: Bar chart anomalias por tipo
- `2026-05-01 11...` - Chart 3: Big Number "952 lecturas validas hoy"
- `2026-05-01 11...` - Chart 4: Tabla detalle anomalias (43 filas)
- `2026-05-01 11...` - Dashboard "IoT Aula - Medallon" completo

## Como usar este indice

1. Abre cada captura en orden cronologico
2. Renombra (opcional) con nombres descriptivos del estilo `e2_hdfs_bronze.png`
3. Insertalas en la memoria PDF en su seccion correspondiente
4. Anota debajo de cada imagen una breve descripcion (1 linea)
