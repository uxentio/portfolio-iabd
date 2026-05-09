"""
silver_to_gold.py

Lee Silver y produce tres datasets agregados que va a consumir Superset:

  hourly_metrics  - una fila por hora con avg/min/max y conteo de eventos.
                    Es el dataset principal de la grafica horaria.
  daily_summary   - una fila por dia. Para los KPIs del dashboard.
  anomalies       - eventos sospechosos (CO2 alto, temperatura fuera de
                    confort, bateria baja, etc.) etiquetados con su tipo.

El patron groupBy().agg(F.avg(...).alias(...)) es el mismo que vimos en
clase en el notebook 03b_Spark_ETL_Basico, en la seccion de "Capa Oro".

Gold no esta particionado. A esta escala (24 filas/dia en hourly, 1 en
daily) particionar es contraproducente, porque genera un monton de
ficheros pequenos. Si en el futuro hay varios meses de historico,
añadir partitionBy("year","month") es trivial.

Uso (dentro de jupyter-aula):
    spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \\
                 silver_to_gold.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

import s3fs
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

sys.path.insert(0, "/home/jovyan/work/src/jobs")
from lib_paths import (  # noqa: E402
    DEVICE_ID,
    GOLD_S3A_BASE,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    SILVER_S3A_BASE,
)


# Umbrales "de confort" para anomalias (no son fisicos, son contextuales).
# Vienen del enunciado: "anomalias por tipo: temperatura alta, humedad baja,
# CO2 elevado, bateria baja".
TEMP_CONFORT_MIN, TEMP_CONFORT_MAX = 18.0, 28.0
HUMEDAD_CONFORT_MIN, HUMEDAD_CONFORT_MAX = 30.0, 70.0
CO2_UMBRAL_ALERTA = 1000   # ppm. Estandar comun de ventilacion en aulas
BATTERY_UMBRAL_BAJA = 20   # %


def construir_spark() -> SparkSession:
    """Misma config s3a que bronze_to_silver -- consistencia entre scripts."""
    return (
        SparkSession.builder
        .appName("silver_to_gold_iot")
        .master("local[*]")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.262",
        )
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .getOrCreate()
    )


def construir_hourly(silver):
    """
    Patron del notebook 03b del profesor: groupBy + agg + alias.
    Convertimos las lecturas individuales del sensor en agregados horarios (KPI).
    """
    return (
        silver
        .groupBy("year", "month", "day", "hour")
        .agg(
            F.round(F.avg("temperature"), 2).alias("temp_avg"),
            F.min("temperature").alias("temp_min"),
            F.max("temperature").alias("temp_max"),
            F.round(F.avg("humidity"), 2).alias("hum_avg"),
            F.round(F.avg("co2"), 0).alias("co2_avg"),
            F.min("battery").alias("battery_min"),
            F.count("*").alias("n_events"),
        )
        .orderBy("year", "month", "day", "hour")
    )


def construir_daily(silver):
    """
    Resumen diario: una fila por dia con los KPIs principales para los Big
    Numbers del dashboard ("temperatura media de hoy", "lecturas totales hoy",
    "bateria minima del dia").
    """
    return (
        silver
        .groupBy("year", "month", "day")
        .agg(
            F.round(F.avg("temperature"), 2).alias("temp_avg"),
            F.round(F.avg("humidity"), 2).alias("hum_avg"),
            F.round(F.avg("co2"), 0).alias("co2_avg"),
            F.min("battery").alias("battery_min"),
            F.count("*").alias("n_events"),
        )
        .orderBy("year", "month", "day")
    )


def listar_cuarentenas_disponibles(fs, base_pseudo: str) -> list[str]:
    """
    Devuelve la lista de paths s3a:// de cada quarantine.jsonl que exista
    bajo el prefijo dado. base_pseudo va sin esquema, por ejemplo
    'datalake/quarantine/iot/sensor_aula_01'.
    """
    if not fs.exists(base_pseudo):
        return []
    encontrados = fs.glob(f"{base_pseudo}/*/quarantine.jsonl")
    return [f"s3a://{p}" for p in encontrados]


def leer_invalidos_agregados(spark, fs):
    """
    Lee los quarantine.jsonl de TODAS las fechas y devuelve dos DataFrames:

      - invalidos_hora: agregado por (year, month, day, hour) con la columna
        n_invalid_events. Solo contiene registros cuyo timestamp interno
        parsea: los que tienen el campo timestamp roto (vacio o mal
        formado) no se pueden asignar a una hora concreta y quedan fuera
        de este agregado horario.

      - invalidos_dia: agregado por (year, month, day) con n_invalid_events.
        Aqui la fecha NO viene del timestamp interno sino del nombre del
        directorio de cuarentena, que el pipeline siempre escribe bien.
        Asi cuenta TODOS los invalidos del dia, incluyendo los que tenian
        el timestamp roto.

    Si no hay cuarentena en MinIO (caso "todo paso las reglas"), devuelve
    None, None y el caller anyade columnas con ceros.
    """
    base = f"{MINIO_BUCKET}/quarantine/iot/{DEVICE_ID}"
    paths = listar_cuarentenas_disponibles(fs, base)
    if not paths:
        return None, None

    invalidos = spark.read.json(paths)

    # input_file_name() permite extraer la fecha del path. La columna _path
    # se descarta despues, no aparece en el resultado.
    invalidos = invalidos.withColumn("_path", F.input_file_name())
    invalidos = invalidos.withColumn(
        "_fecha_path",
        F.regexp_extract("_path", r"(\d{4}-\d{2}-\d{2})", 1),
    ).filter(F.col("_fecha_path") != "")

    invalidos = invalidos.withColumn("_fecha", F.to_date("_fecha_path", "yyyy-MM-dd"))
    invalidos = (
        invalidos
        .withColumn("year",  F.year("_fecha"))
        .withColumn("month", F.month("_fecha"))
        .withColumn("day",   F.dayofmonth("_fecha"))
    )

    # Hora: del timestamp interno si parsea, NULL si esta vacio o mal formado.
    invalidos = invalidos.withColumn(
        "ts_parsed",
        F.to_timestamp(F.col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss"),
    )

    invalidos_hora = (
        invalidos
        .filter(F.col("ts_parsed").isNotNull())
        .withColumn("hour", F.hour("ts_parsed"))
        .groupBy("year", "month", "day", "hour")
        .agg(F.count("*").alias("n_invalid_events"))
    )
    invalidos_dia = (
        invalidos
        .groupBy("year", "month", "day")
        .agg(F.count("*").alias("n_invalid_events"))
    )
    return invalidos_hora, invalidos_dia


def enriquecer_con_calidad(hourly, daily, invalidos_hora, invalidos_dia):
    """
    Anyade n_valid_events, n_invalid_events, n_events y pct_valid a los
    agregados horarios y diarios. La columna que antes se llamaba
    n_events (count de Silver) pasa a llamarse n_valid_events porque
    Silver ya solo contiene los validos. Los nombres encajan con los
    ejemplos que el enunciado lista en el Ejercicio 5.
    """
    # ---- Hourly ----
    hourly = hourly.withColumnRenamed("n_events", "n_valid_events")
    if invalidos_hora is not None:
        hourly = (
            hourly
            .join(invalidos_hora, on=["year", "month", "day", "hour"], how="left")
            .fillna({"n_invalid_events": 0})
        )
    else:
        hourly = hourly.withColumn("n_invalid_events", F.lit(0))
    hourly = hourly.withColumn(
        "n_events",
        F.col("n_valid_events") + F.col("n_invalid_events"),
    )
    hourly = hourly.withColumn(
        "pct_valid",
        F.round(F.col("n_valid_events") / F.col("n_events") * 100, 1),
    )

    # ---- Daily ----
    daily = daily.withColumnRenamed("n_events", "n_valid_events")
    if invalidos_dia is not None:
        daily = (
            daily
            .join(invalidos_dia, on=["year", "month", "day"], how="left")
            .fillna({"n_invalid_events": 0})
        )
    else:
        daily = daily.withColumn("n_invalid_events", F.lit(0))
    daily = daily.withColumn(
        "n_events",
        F.col("n_valid_events") + F.col("n_invalid_events"),
    )
    daily = daily.withColumn(
        "pct_valid",
        F.round(F.col("n_valid_events") / F.col("n_events") * 100, 1),
    )

    return hourly, daily


def construir_anomalies(silver):
    """
    Dataset largo (un evento sospechoso por fila) con un campo 'anomaly_type'
    para que Superset pueda hacer "GROUP BY anomaly_type" y generar la
    grafica de "anomalias por tipo" pedida en el enunciado.

    Importante: usamos UNION en lugar de un OR gigante porque queremos que
    un mismo evento que dispara dos alertas (p.ej. CO2 alto Y temperatura
    alta) aparezca dos veces, una por tipo. Eso es lo correcto para una
    grafica de barras agrupada.
    """
    base_cols = ["event_id", "timestamp", "temperature",
                 "humidity", "co2", "battery", "year", "month", "day", "hour"]

    temp_alta = (silver.filter(F.col("temperature") > TEMP_CONFORT_MAX)
                  .select(*base_cols, F.lit("temperatura_alta").alias("anomaly_type")))
    temp_baja = (silver.filter(F.col("temperature") < TEMP_CONFORT_MIN)
                  .select(*base_cols, F.lit("temperatura_baja").alias("anomaly_type")))
    hum_alta  = (silver.filter(F.col("humidity") > HUMEDAD_CONFORT_MAX)
                  .select(*base_cols, F.lit("humedad_alta").alias("anomaly_type")))
    hum_baja  = (silver.filter(F.col("humidity") < HUMEDAD_CONFORT_MIN)
                  .select(*base_cols, F.lit("humedad_baja").alias("anomaly_type")))
    co2_alto  = (silver.filter(F.col("co2") > CO2_UMBRAL_ALERTA)
                  .select(*base_cols, F.lit("co2_elevado").alias("anomaly_type")))
    bat_baja  = (silver.filter(F.col("battery") < BATTERY_UMBRAL_BAJA)
                  .select(*base_cols, F.lit("bateria_baja").alias("anomaly_type")))

    return temp_alta.unionByName(temp_baja) \
                    .unionByName(hum_alta) \
                    .unionByName(hum_baja) \
                    .unionByName(co2_alto) \
                    .unionByName(bat_baja)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=False,
                        help="YYYY-MM-DD (informativo; agregamos TODO el Silver)")
    args = parser.parse_args()

    spark = construir_spark()
    print(f"OK Spark inicializado (version {spark.version})")

    # Cliente s3fs para sondear la cuarentena (pyarrow/spark.read.json
    # peta si la ruta no existe; preferimos comprobar antes con s3fs).
    fs = s3fs.S3FileSystem(
        key=MINIO_ACCESS_KEY,
        secret=MINIO_SECRET_KEY,
        client_kwargs={"endpoint_url": MINIO_ENDPOINT},
    )

    # Leemos TODO Silver, no solo el dia, para que Gold refleje siempre
    # el historico completo. Si el dataset crece mucho, se podria filtrar
    # aqui por fecha y hacer escritura particionada incremental, pero a
    # esta escala (kilo-eventos por dia) el overwrite global es trivial.
    print(f"OK Leyendo Silver: {SILVER_S3A_BASE}")
    silver = spark.read.parquet(SILVER_S3A_BASE)
    n = silver.count()
    print(f"   {n} registros en Silver")
    silver.cache()  # 3 lecturas (hourly/daily/anomalies) -> compensa cachear

    # Cuarentena: la usamos para anyadir n_invalid_events a hourly y daily,
    # y de paso responder al ejemplo del enunciado E5 (num_valid_events,
    # num_invalid_events). Si no hay cuarentena, las columnas quedan a 0.
    print("OK Sondeando cuarentena para enriquecer agregados de calidad")
    invalidos_hora, invalidos_dia = leer_invalidos_agregados(spark, fs)
    if invalidos_dia is not None:
        total_inv = invalidos_dia.agg(F.sum("n_invalid_events").alias("s")).collect()[0]["s"]
        print(f"   cuarentena leida: {total_inv} registros invalidos en total")
    else:
        print("   no hay cuarentena en MinIO (todo paso las reglas)")

    # 1. Construimos los tres bases. Anomalies primero porque necesitamos
    #    su conteo agregado para las columnas n_alerts de hourly y daily.
    hourly_base = construir_hourly(silver)
    daily_base  = construir_daily(silver)
    anomalies   = construir_anomalies(silver)

    # 2. Enriquecemos hourly y daily con n_valid_events / n_invalid_events
    #    (sacados de la cuarentena) y con n_alerts (contando anomalies).
    hourly, daily = enriquecer_con_calidad(
        hourly_base, daily_base, invalidos_hora, invalidos_dia,
    )
    alertas_hora = (
        anomalies.groupBy("year", "month", "day", "hour")
                 .agg(F.count("*").alias("n_alerts"))
    )
    alertas_dia = (
        anomalies.groupBy("year", "month", "day")
                 .agg(F.count("*").alias("n_alerts"))
    )
    hourly = (
        hourly.join(alertas_hora, on=["year", "month", "day", "hour"], how="left")
              .fillna({"n_alerts": 0})
    )
    daily = (
        daily.join(alertas_dia, on=["year", "month", "day"], how="left")
             .fillna({"n_alerts": 0})
    )

    # 3. Escritura: los tres datasets en MinIO en formato Parquet snappy.
    ruta_hourly = f"{GOLD_S3A_BASE}/hourly_metrics"
    print(f"OK Escribiendo hourly_metrics ({hourly.count()} filas) en {ruta_hourly}")
    hourly.write.mode("overwrite").parquet(ruta_hourly)

    ruta_daily = f"{GOLD_S3A_BASE}/daily_summary"
    print(f"OK Escribiendo daily_summary ({daily.count()} filas) en {ruta_daily}")
    daily.write.mode("overwrite").parquet(ruta_daily)

    ruta_anom = f"{GOLD_S3A_BASE}/anomalies"
    print(f"OK Escribiendo anomalies ({anomalies.count()} filas) en {ruta_anom}")
    anomalies.write.mode("overwrite").parquet(ruta_anom)

    # Verificacion ligera
    print("\nOK Resumen agregaciones generadas:")
    print(f"   hourly_metrics  -> {hourly.count()} filas (1 por hora)")
    print(f"   daily_summary   -> {daily.count()} filas (1 por dia)")
    print(f"   anomalies       -> {anomalies.count()} eventos sospechosos")

    spark.stop()
    print("OK silver_to_gold finalizado")


if __name__ == "__main__":
    main()
