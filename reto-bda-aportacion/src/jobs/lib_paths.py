"""
lib_paths.py

Constantes que comparten todos los scripts del pipeline. Las dejo aqui
para no repetir las mismas cadenas en siete ficheros y para que cambiar
el nombre del dispositivo o las credenciales de MinIO sea modificar
una sola linea.
"""

# El dispositivo que pide el enunciado: solo uno.
DEVICE_ID = "sensor_aula_01"

# Endpoints del entorno docker-compose. Los nombres "namenode", "minio"
# se resuelven por DNS dentro de la red del compose, asi que valen igual
# desde jupyter-aula que desde airflow.
HDFS_NAMENODE_HTTP = "http://namenode:9870"   # WebHDFS, lo usa el cliente de Python
HDFS_NAMENODE_RPC  = "hdfs://namenode:9000"   # RPC nativo, lo usa Spark
MINIO_ENDPOINT     = "http://minio:9000"
MINIO_ACCESS_KEY   = "admin"
MINIO_SECRET_KEY   = "adminadmin"
MINIO_BUCKET       = "datalake"

# Rutas de cada capa. Bronze vive en HDFS, Silver/Gold/Quality/Quarantine
# en MinIO. Hay dos versiones de la URL para Silver y Gold: s3a:// la usan
# Spark, s3:// la usan pandas y duckdb.
BRONZE_HDFS_BASE     = f"/datalake/bronze/iot/{DEVICE_ID}"
SILVER_S3A_BASE      = f"s3a://{MINIO_BUCKET}/silver/iot/{DEVICE_ID}"
GOLD_S3A_BASE        = f"s3a://{MINIO_BUCKET}/gold/iot/{DEVICE_ID}"
SILVER_S3_BASE       = f"s3://{MINIO_BUCKET}/silver/iot/{DEVICE_ID}"
GOLD_S3_BASE         = f"s3://{MINIO_BUCKET}/gold/iot/{DEVICE_ID}"
QUALITY_S3_BASE      = f"s3://{MINIO_BUCKET}/quality/iot/{DEVICE_ID}"
QUARANTINE_S3_BASE   = f"s3://{MINIO_BUCKET}/quarantine/iot/{DEVICE_ID}"
QUARANTINE_S3A_BASE  = f"s3a://{MINIO_BUCKET}/quarantine/iot/{DEVICE_ID}"

# Diccionario que pandas y s3fs esperan para hablar con MinIO. Es el mismo
# patron que aparece en el notebook 01_Demo_Lectura_Escritura_HDFS_S3.
PANDAS_S3_STORAGE_OPTIONS = {
    "key": MINIO_ACCESS_KEY,
    "secret": MINIO_SECRET_KEY,
    "client_kwargs": {"endpoint_url": MINIO_ENDPOINT},
}

# Carpeta local donde el generador escribe el JSONL antes de subirlo a HDFS.
# Cambia segun el contenedor: en jupyter-aula es /home/jovyan/work/data/raw/,
# en airflow es /opt/airflow/data/. Lo paso como argumento --raw-dir.
LOCAL_RAW_DIRNAME = "data/raw"
