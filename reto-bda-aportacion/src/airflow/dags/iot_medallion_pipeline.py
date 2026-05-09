"""
iot_medallion_pipeline.py

DAG que encadena las 8 fases del pipeline en serie. Cada tarea es un
BashOperator que llama a un script de la carpeta src/jobs.

Las dos tareas Spark (bronze_to_silver y silver_to_gold) no se ejecutan
dentro del contenedor de airflow, sino que se delegan al contenedor
jupyter-aula con docker exec spark-submit. Es asi porque la imagen
oficial de airflow no trae Java ni PySpark, mientras que jupyter-aula si.

Para que airflow pueda llamar a docker exec, el override extiende su
imagen instalando docker.io y monta /var/run/docker.sock. La idea es la
misma que el profesor aplica al compartir PostgreSQL entre Airflow y
Superset: reusar lo que ya hay en lugar de duplicar.

Disparar el DAG manualmente:
    docker exec airflow-scheduler airflow dags trigger iot_medallion_pipeline
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago


# ---------------------------------------------------------------------------
# Argumentos por defecto aplicados a TODAS las tareas.
# Patron del profesor (notebook 08_Orquestacion_y_Monitorizacion_UT4):
#   - retries=1 + retry_delay corto para uso educativo
#   - email_on_failure=False (sin SMTP en el lab)
# ---------------------------------------------------------------------------
default_args = {
    "owner": "autor",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


# Comandos reutilizables: hacemos las llamadas "docker exec" a jupyter-aula
# para los jobs PySpark.  El contenedor de jupyter-aula es siempre el mismo
# nombre (definido en docker-compose.yml del profesor), asi que esto es estable.
JUPYTER_CONTAINER = "jupyter-aula"
JOBS_PATH_AIRFLOW = "/opt/airflow/jobs"            # montaje del override
JOBS_PATH_JUPYTER = "/home/jovyan/work/src/jobs"   # ruta dentro de jupyter

# Jars necesarios para que Spark pueda escribir/leer en MinIO con el conector
# S3A. Las versiones 3.3.4 + 1.12.262 son las testadas con Spark 3.5/Hadoop 3.4
# que viene en la imagen jupyter/pyspark-notebook. Otras combinaciones suelen
# tirar NoSuchMethodError en runtime.
# La primera ejecucion descarga ~150 MB de Maven Central (Ivy lo cachea en
# ~/.ivy2 dentro del contenedor jupyter, asi que ejecuciones posteriores
# son rapidas).
SPARK_PACKAGES = (
    "org.apache.hadoop:hadoop-aws:3.3.4,"
    "com.amazonaws:aws-java-sdk-bundle:1.12.262"
)


with DAG(
    dag_id="iot_medallion_pipeline",
    default_args=default_args,
    description=(
        "Reto 02 RA5: Pipeline medallon Bronze HDFS -> Silver MinIO -> "
        "Gold MinIO -> Superset, sobre datos de un sensor IoT de aula."
    ),
    schedule_interval=None,           # Se ejecuta manualmente desde la UI
    catchup=False,
    tags=["educativo", "ut5", "iot", "medallion", "ra5"],
) as dag:

    # -----------------------------------------------------------------------
    # 1. Generador IoT
    # Genera 1000 lecturas con ~7% errores controlados.
    # Se ejecuta DENTRO del propio contenedor airflow porque es Python puro.
    # -----------------------------------------------------------------------
    generate_iot = BashOperator(
        task_id="1_generate_iot",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/generate_iot_data.py "
            f"--records 1000 --error-rate 0.07 "
            f"--date {{{{ ds }}}} "
            f"--output-dir /opt/airflow/data/raw"
        ),
    )

    # -----------------------------------------------------------------------
    # 2. Validar formato inicial del JSONL (pre-Bronze)
    # Antes de tocar HDFS, verifica que el fichero existe, es JSON valido
    # y tiene las claves estructurales (event_id, device_id, timestamp).
    # Esto evita contaminar Bronze con basura estructural.
    # -----------------------------------------------------------------------
    validate_raw_format = BashOperator(
        task_id="2_validate_raw_format",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/validate_raw_format.py "
            f"--date {{{{ ds }}}} "
            f"--raw-dir /opt/airflow/data/raw"
        ),
    )

    # -----------------------------------------------------------------------
    # 3. Carga Bronze a HDFS
    # WebHDFS via libreria 'hdfs' instalada en la imagen extendida de airflow.
    # -----------------------------------------------------------------------
    load_bronze = BashOperator(
        task_id="3_load_bronze_hdfs",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/load_bronze_hdfs.py "
            f"--date {{{{ ds }}}} "
            f"--raw-dir /opt/airflow/data/raw"
        ),
    )

    # -----------------------------------------------------------------------
    # 4. Validaciones de calidad (UT3 completo)
    # Lee Bronze, aplica reglas de rules_iot.yaml, escribe cuarentena +
    # informe JSON en MinIO. Si >50% invalidos, falla la tarea.
    # -----------------------------------------------------------------------
    validate_quality = BashOperator(
        task_id="4_validate_quality",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/validate_raw.py "
            f"--date {{{{ ds }}}} "
            f"--rules /opt/airflow/quality/rules_iot.yaml"
        ),
    )

    # -----------------------------------------------------------------------
    # 5. Bronze -> Silver con PySpark
    # Delegamos al contenedor jupyter-aula (que tiene Spark+Java).
    # `docker exec` funciona porque el override monta /var/run/docker.sock.
    # -----------------------------------------------------------------------
    # IMPORTANTE: usamos `spark-submit` en lugar de `python` porque la imagen
    # jupyter/pyspark-notebook no expone el modulo pyspark via import directo
    # (el modulo vive en /usr/local/spark/python/, fuera del PYTHONPATH por
    # defecto). spark-submit configura PYTHONPATH, classpath Java y la JVM
    # automaticamente.
    bronze_to_silver = BashOperator(
        task_id="5_bronze_to_silver",
        bash_command=(
            f"docker exec {JUPYTER_CONTAINER} "
            f"spark-submit --packages {SPARK_PACKAGES} "
            f"{JOBS_PATH_JUPYTER}/bronze_to_silver.py "
            f"--date {{{{ ds }}}}"
        ),
        # Spark suele tardar mas la primera vez por la descarga de jars
        retries=2,
        retry_delay=timedelta(minutes=3),
    )

    # -----------------------------------------------------------------------
    # 6. Validar la capa Plata (post-Silver)
    # Re-lee el Parquet escrito en MinIO y comprueba garantias: > 0 filas,
    # tipos correctos, sin nulos en columnas criticas, event_id unico.
    # -----------------------------------------------------------------------
    validate_silver = BashOperator(
        task_id="6_validate_silver",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/validate_silver.py "
            f"--date {{{{ ds }}}}"
        ),
    )

    # -----------------------------------------------------------------------
    # 7. Silver -> Gold con PySpark
    # Mismo patron spark-submit via docker exec. Genera los 3 datasets Gold.
    # -----------------------------------------------------------------------
    silver_to_gold = BashOperator(
        task_id="7_silver_to_gold",
        bash_command=(
            f"docker exec {JUPYTER_CONTAINER} "
            f"spark-submit --packages {SPARK_PACKAGES} "
            f"{JOBS_PATH_JUPYTER}/silver_to_gold.py "
            f"--date {{{{ ds }}}}"
        ),
        retries=2,
        retry_delay=timedelta(minutes=3),
    )

    # -----------------------------------------------------------------------
    # 8. Preparar datos para Superset
    # Smoke test sobre los 3 datasets Gold (que se leen igual que lo hara
    # DuckDB+httpfs en Superset) y publica un manifest.json en MinIO con
    # metadatos del run. Si algun dataset esta vacio o ilegible, aborta.
    # -----------------------------------------------------------------------
    publish_gold_superset = BashOperator(
        task_id="8_publish_gold_superset",
        bash_command=(
            f"python {JOBS_PATH_AIRFLOW}/publish_gold_superset.py "
            f"--date {{{{ ds }}}}"
        ),
    )

    # -----------------------------------------------------------------------
    # Dependencias (lineales, una detras de otra)
    # -----------------------------------------------------------------------
    (
        generate_iot
        >> validate_raw_format
        >> load_bronze
        >> validate_quality
        >> bronze_to_silver
        >> validate_silver
        >> silver_to_gold
        >> publish_gold_superset
    )
