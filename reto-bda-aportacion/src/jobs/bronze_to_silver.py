"""
bronze_to_silver.py

Lee el JSONL de Bronze desde HDFS, lo limpia con Spark y escribe Parquet
en MinIO particionado por year/month/day.

Sigue el mismo patron que vimos en clase (notebook 03b_Spark_ETL_Basico):
SparkSession en local[*], spark.read.json desde HDFS, write.parquet al
sitio de destino. La unica diferencia es que el destino es MinIO en
lugar de HDFS, asi que hay que aniadir la configuracion s3a.

Limpieza que aplico antes de escribir:
- Caster timestamp a TimestampType y descartar las filas que no parsean.
- Filtrar valores fuera de rango fisico (temperatura, humedad, CO2, bateria).
- Quitar duplicados por event_id.
- Aniadir las columnas year/month/day/hour para el particionado.

Spark se ejecuta dentro del contenedor jupyter-aula porque es donde estan
PySpark y Java instalados; airflow lo invoca con docker exec spark-submit.

Uso (dentro de jupyter-aula):
    spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \\
                 bronze_to_silver.py --date 2026-04-30
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

# Estos imports asumen que estamos dentro del contenedor jupyter-aula
# que viene con PySpark 3.5.0 preinstalado (jupyter/pyspark-notebook).
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Aseguramos que /home/jovyan/work/src/jobs esta en el path para localizar lib_paths
sys.path.insert(0, "/home/jovyan/work/src/jobs")
from lib_paths import (  # noqa: E402
    BRONZE_HDFS_BASE,
    HDFS_NAMENODE_RPC,
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    SILVER_S3A_BASE,
)


# -----------------------------------------------------------------------------
# Esquema explicito.  Si el JSON tiene un campo extra, Spark lo ignora;
# si tiene un campo del tipo equivocado, lo deja como NULL.  Esto es la
# defensa en codigo del "contrato de datos" del que hablaba UT3.4.
# -----------------------------------------------------------------------------
SCHEMA_BRONZE = StructType([
    StructField("event_id",    StringType(), False),
    StructField("device_id",   StringType(), False),
    StructField("timestamp",   StringType(), True),   # parseamos a TimestampType despues
    StructField("temperature", DoubleType(),  True),
    StructField("humidity",    DoubleType(),  True),
    StructField("co2",         IntegerType(), True),
    StructField("battery",     IntegerType(), True),
    StructField("status",      StringType(),  True),
])


def construir_spark() -> SparkSession:
    """
    Crea la SparkSession con la config necesaria para hablar S3A con MinIO.
    El conector S3A vive en hadoop-aws + aws-java-sdk-bundle; por eso los
    declaramos en spark.jars.packages y Spark los descarga al primer arranque
    (~150MB la primera vez, despues cacheado en ~/.ivy2/cache).

    Las versiones 3.3.4 / 1.12.262 son compatibles con Spark 3.5 + Hadoop 3.4
    (las versiones del jupyter.Dockerfile del profesor); otras combinaciones
    suelen tirar NoSuchMethodError al escribir.
    """
    return (
        SparkSession.builder
        .appName("bronze_to_silver_iot")
        .master("local[*]")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.262",
        )
        # Conexion S3A -> MinIO (path-style obligatorio para MinIO)
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        # Compresion snappy: estandar de facto en Parquet, balance velocidad/tamaño
        .config("spark.sql.parquet.compression.codec", "snappy")
        # Reduce el ruido de logs al imprescindible (queremos ver QUE pasa, no debug Java)
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )


def leer_bronze(spark: SparkSession, run_date: datetime):
    """
    Lectura del JSONL crudo del dia con esquema explicito.
    Patron exacto del notebook 03b_Spark_ETL_Basico (UT4): spark.read + ruta hdfs://.
    """
    ruta = (
        f"{HDFS_NAMENODE_RPC}{BRONZE_HDFS_BASE}"
        f"/year={run_date.year}/month={run_date.month:02d}/day={run_date.day:02d}/*.jsonl"
    )
    print(f"OK Leyendo Bronze: {ruta}")
    return spark.read.schema(SCHEMA_BRONZE).json(ruta)


def limpiar(df):
    """
    Reglas de limpieza alineadas con rules_iot.yaml.  Las repetimos aqui
    en lugar de leer el YAML para mantener el script Spark autocontenido
    (es lo que hace el profesor en 03b: la "limpieza" vive en el ETL).

    Nota didactica: el orden importa.
        1) Convertimos timestamp a TimestampType -> filas con timestamp
           vacio o mal formado quedan con ts=null y caen en el filter.
        2) Filtramos rangos fisicos -> dimension PRECISION.
        3) dropDuplicates(event_id) -> dimension CONSISTENCIA, idempotencia
           (UT3.4 ejemplo 1).
        4) Anyadimos columnas year/month/day/hour para el particionado y
           para que Gold pueda agrupar sin volver a parsear strings.
    """
    return (
        df
        # 1. Parseo de timestamp con formato estricto (defensa anti-drift)
        .withColumn("ts", F.to_timestamp("timestamp", "yyyy-MM-dd'T'HH:mm:ss"))
        .filter(F.col("ts").isNotNull())
        # 2. Rangos fisicos (UT3.1.c precision)
        .filter(F.col("temperature").between(-20, 80))
        .filter(F.col("humidity").between(0, 100))
        .filter(F.col("co2").between(0, 5000))
        .filter(F.col("battery").between(0, 100))
        # 3. Dedupe por id unico (UT3.4 idempotencia ante reintentos)
        .dropDuplicates(["event_id"])
        # 4. Columnas de particion + simplificacion del esquema
        .withColumn("year",  F.year("ts"))
        .withColumn("month", F.month("ts"))
        .withColumn("day",   F.dayofmonth("ts"))
        .withColumn("hour",  F.hour("ts"))
        .drop("timestamp")
        .withColumnRenamed("ts", "timestamp")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run_date = datetime.fromisoformat(args.date)

    spark = construir_spark()
    print(f"OK Spark inicializado (version {spark.version}, master local[*])")

    df_bronze = leer_bronze(spark, run_date)
    n_in = df_bronze.count()
    print(f"   {n_in} registros leidos de Bronze")

    df_silver = limpiar(df_bronze)
    n_out = df_silver.count()
    print(f"   {n_out} registros tras limpieza ({n_in - n_out} descartados)")

    # Escritura Parquet particionada en MinIO via S3A (UT5 + extension RA5).
    # Particionamos por year/month/day SOLO; hour va como columna normal
    # porque tener 24 carpetitas por dia complica la lectura desde Superset
    # sin aportar beneficio real a esta escala.
    print(f"OK Escribiendo Silver en {SILVER_S3A_BASE}")
    (
        df_silver.write
        .mode("overwrite")
        .partitionBy("year", "month", "day")
        .parquet(SILVER_S3A_BASE)
    )

    # Comprobacion rapida: re-leer el primer parquet para confirmar tipos
    print("OK Verificacion (re-lectura de Silver):")
    df_silver.printSchema()
    df_silver.show(5, truncate=False)

    spark.stop()
    print("OK bronze_to_silver finalizado")


if __name__ == "__main__":
    main()
