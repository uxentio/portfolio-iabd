FROM apache/airflow:2.8.3

# Instalamos papermill para poder ejecutar notebooks desde los DAGs
RUN pip install --no-cache-dir papermill ipykernel
