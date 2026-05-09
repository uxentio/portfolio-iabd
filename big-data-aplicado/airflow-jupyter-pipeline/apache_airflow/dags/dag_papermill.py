from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Argumentos por defecto
dag_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    "dag_papermill",
    description="DAG que ejecuta un notebook con Papermill",
    default_args=dag_args,
    schedule=None,  # Solo ejecucion manual
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["papermill", "jupyter"],
)

def ejecutar_notebook(**kwargs):
    """
    Usa Papermill para ejecutar un notebook parametrizable.
    Los parametros se pasan desde la configuracion del DAG.
    """
    import papermill as pm

    conf = kwargs['dag_run'].conf or {}
    nombre = conf.get("nombre", "Mundo")
    repeticiones = conf.get("repeticiones", 3)

    pm.execute_notebook(
        input_path="/opt/airflow/notebooks/notebook_parametrizable.ipynb",
        output_path="/opt/airflow/notebooks/notebook_output.ipynb",
        parameters={
            "nombre": nombre,
            "repeticiones": repeticiones
        }
    )

tarea_notebook = PythonOperator(
    task_id="ejecutar_notebook",
    python_callable=ejecutar_notebook,
    dag=dag,
)
