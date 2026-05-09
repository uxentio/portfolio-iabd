# =============================================================================
# airflow.Dockerfile -- Reto 02 RA5 (autor)
#
# Extiende la imagen oficial de Airflow del entorno del profesor con:
#   1. Cliente Docker (docker.io)  -> permite que el contenedor airflow lance
#      `docker exec jupyter-aula python ...` para los pasos PySpark del DAG.
#      Reusamos PySpark+Java ya instalados en jupyter-aula en lugar de
#      engordar la imagen Airflow con Java (decision pedagogica analoga
#      a la del profesor de reusar PostgreSQL para Superset y Airflow).
#   2. Librerias Python para los jobs no-Spark del DAG:
#        - hdfs    (cliente WebHDFS, patron del notebook 01_Demo_HDFS_S3)
#        - pyarrow (manipulacion eficiente de datos columnares)
#        - boto3 + s3fs  (lectura/escritura MinIO al estilo "pandas + storage_options")
#        - pyyaml  (carga las reglas declarativas de calidad rules_iot.yaml)
#
# Detalle de implementacion (NOTA TECNICA):
# La imagen oficial de Airflow BLOQUEA `pip install` ejecutado como root por
# politica de seguridad. Pero nosotros necesitamos que el contenedor arranque
# como root para poder usar el socket Docker (/var/run/docker.sock).
# Solucion: instalamos las libs como user 'airflow' (que es lo que la imagen
# permite) pero en una carpeta global compartida (/opt/extra-libs), y exponemos
# esa ruta via PYTHONPATH para que el interprete las encuentre independientemente
# de si esta corriendo como root o como airflow.
# =============================================================================

FROM apache/airflow:2.8.3

USER root

# Cliente Docker (NO el daemon - el daemon vive en el host de Docker Desktop).
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

# Carpeta compartida para libs Python.
# - chown a airflow:0 -> el user airflow puede escribir
# - permisos 755 -> root y otros pueden leer/ejecutar
RUN mkdir -p /opt/extra-libs && chown airflow:0 /opt/extra-libs

USER airflow

# pip install --target instala los paquetes en la ruta indicada en lugar
# de en site-packages. Asi obtenemos un site-packages "portable" en
# /opt/extra-libs que aniadimos al PYTHONPATH global.
# PIP_USER=no es necesario porque la imagen de Airflow define PIP_USER=true
# por defecto (para forzar instalaciones a /home/airflow/.local), pero eso
# es incompatible con --target.
RUN PIP_USER=no pip install --no-cache-dir --target /opt/extra-libs \
    hdfs \
    pyarrow \
    boto3 \
    s3fs \
    pyyaml

# PYTHONPATH global: anyadido a CUALQUIER interprete python invocado en este
# contenedor (root o airflow), asi tanto los BashOperator del DAG como los
# tests manuales encuentran las libs.
ENV PYTHONPATH=/opt/extra-libs:${PYTHONPATH:-}
