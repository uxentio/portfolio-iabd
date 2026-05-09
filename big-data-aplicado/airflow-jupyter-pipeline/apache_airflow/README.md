# Reto 01: Mini entorno de trabajo con Jupyter Notebook y Apache Airflow

Entorno Docker que despliega **Jupyter Notebook** y **Apache Airflow** para trabajar con DAGs, la API REST y Papermill. Diseñado para ser **fácil de desplegar** y **autocontenido** (sin morir en el intento).

Basado en la estructura del entorno del profesor (hadoop-lab_v6) y en el vídeo de Albert Coronado facilitado en clase.

---

## 🏗️ Arquitectura del Entorno

El sistema levanta **5 servicios** Docker que trabajan en conjunto:

1.  **PostgreSQL**: Base de datos para los metadatos de Airflow (DAGs, ejecuciones, logs, usuarios).
2.  **Airflow Init**: Servicio de inicialización. Crea las tablas y el usuario admin. Se ejecuta solo una vez y se para.
3.  **Airflow Webserver**: Interfaz web de Airflow para gestionar DAGs y ver logs.
4.  **Airflow Scheduler**: Planificador que ejecuta los DAGs automáticamente.
5.  **Jupyter Notebook**: Tu **zona de trabajo**. Desde aquí interactuarás con Airflow usando la API REST y la CLI.

> **💡 Nota:** Se usa **LocalExecutor** con PostgreSQL en vez del SequentialExecutor por defecto. Esto permite ejecutar tareas en paralelo y es más estable. Configuración recomendada por la documentación oficial de Airflow.

### 📦 Gestión de Dependencias

Todo el entorno se construye con dos Dockerfiles personalizados:

- **`airflow.Dockerfile`**: Extiende la imagen oficial de Airflow 2.8.3 añadiendo `papermill` e `ipykernel` (necesarios para ejecutar notebooks desde DAGs).
- **`jupyter.Dockerfile`**: Extiende la imagen base de Jupyter añadiendo `requests`, `papermill`, `apache-airflow` (para la CLI), `graphviz`, `tzdata`, `ipywidgets` y herramientas LaTeX para exportar a PDF.

> **💡 Tip:** Si necesitas añadir una nueva librería de Python, simplemente añádela al `RUN pip install` del Dockerfile correspondiente y reconstruye con `docker compose build`.

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos
- **Docker Desktop** instalado y en ejecución.
- Al menos **2 GB de RAM** asignados a Docker.

### 2. Arrancar el Entorno
Abre una terminal (PowerShell o CMD) en la carpeta del proyecto y ejecuta:

```bash
docker compose up --build -d
```

> **⏳ IMPORTANTE:** La primera vez tardará varios minutos porque tiene que descargar las imágenes base (Airflow ~1GB, Jupyter ~1GB) e instalar las dependencias. Las siguientes veces será mucho más rápido porque Docker cachea las capas.

### 3. Verificar Estado
Para ver si los servicios están listos:

```bash
docker ps
```

Deberías ver **4 contenedores** con estado `Up`:

| Contenedor | Imagen | Puerto |
| :--- | :--- | :--- |
| `reto01-postgres` | postgres:13 | 5432 (interno) |
| `reto01-airflow-webserver` | airflow:2.8.3 (custom) | 8080 |
| `reto01-airflow-scheduler` | airflow:2.8.3 (custom) | - |
| `reto01-jupyter` | jupyter/base-notebook (custom) | 8888 |

> **Nota:** `reto01-airflow-init` aparecerá como `Exited (0)`. Es normal: solo se ejecuta una vez para inicializar la BD.

---

## 🔗 Puntos de Acceso

| Servicio | URL | Credenciales |
| :--- | :--- | :--- |
| **Airflow** | [http://localhost:8080](http://localhost:8080) | Usuario: `admin` / Contraseña: `admin` |
| **Jupyter** | [http://localhost:8888](http://localhost:8888) | Sin token ni contraseña |

---

## 📂 Estructura del Proyecto

```
RETO 01/
├── docker-compose.yml              # Orquesta los 5 servicios
├── airflow.Dockerfile              # Imagen Airflow + papermill
├── jupyter.Dockerfile              # Imagen Jupyter + airflow CLI + dependencias
├── dags/
│   ├── test.py                     # DAG test1 (del vídeo de Albert Coronado)
│   └── dag_papermill.py            # DAG que ejecuta notebooks con Papermill
├── notebooks/
│   ├── Reto01_Jupyter_Airflow.ipynb        # Notebook principal (3 ejercicios)
│   └── notebook_parametrizable.ipynb       # Notebook parametrizable (ejercicio 3)
├── logs/                           # Logs de Airflow (se genera automáticamente)
├── plugins/                        # Plugins de Airflow (vacío)
└── README.md                       # Este fichero
```

---

## 📓 Cómo Usar el Notebook

1. Abre Jupyter en [http://localhost:8888](http://localhost:8888)
2. Ve a la carpeta `notebooks/`
3. Abre `Reto01_Jupyter_Airflow.ipynb`
4. Ejecuta las celdas en orden con `Shift+Enter`

El notebook cubre los **3 ejercicios** del reto:
- **Secciones 1-2:** Conexión a la API REST de Airflow
- **Secciones 3-7:** Lanzamiento de DAGs, consulta de estado, error controlado
- **Secciones 8-9:** CLI de Airflow desde Jupyter
- **Secciones 10-12:** Integración con Papermill

> **💡 Tip:** Si al ejecutar alguna celda sale un warning en amarillo, no pasa nada. Los warnings de Pendulum están filtrados en la primera celda de código. Si sale alguno nuevo, reinicia el kernel (Kernel > Restart).

---

## ⚙️ Gestión del Entorno

### Parar el entorno (manteniendo datos)
```bash
docker compose down
```

### Volver a arrancarlo
```bash
docker compose up -d
```

### Borrar TODO y empezar de cero (Factory Reset)
⚠️ **Cuidado:** Esto borrará los datos de PostgreSQL (ejecuciones, logs de Airflow).
```bash
docker compose down -v
```

### Reconstruir imágenes (si has cambiado un Dockerfile)
```bash
docker compose build
docker compose up -d
```

---

## 💻 Acceso Directo a los Contenedores

Si necesitas entrar en algún contenedor para depurar:

| Contenedor | Comando |
| :--- | :--- |
| **Jupyter** | `docker exec -it reto01-jupyter bash` |
| **Airflow Webserver** | `docker exec -it reto01-airflow-webserver bash` |
| **Airflow Scheduler** | `docker exec -it reto01-airflow-scheduler bash` |
| **PostgreSQL** | `docker exec -it reto01-postgres psql -U airflow` |

> **Tip:** Para salir del contenedor, escribe `exit`.

---

## ❓ Solución de Problemas (Troubleshooting)

**1. "No puedo entrar a Jupyter (conexión rechazada)"**
- **Causa:** El contenedor aún está arrancando o instalando dependencias.
- **Solución:** Espera un par de minutos. Puedes ver los logs con:
  ```bash
  docker compose logs -f jupyter
  ```
  Cuando veas `Jupyter Server ... is running`, ya está listo.

**2. "Airflow no muestra los DAGs"**
- **Causa:** El scheduler tarda unos segundos en detectar los DAGs nuevos.
- **Solución:** Espera 30 segundos y recarga la página. Si sigue sin aparecer, revisa que los ficheros `.py` estén en la carpeta `dags/`.

**3. "El DAG de Papermill falla con FileNotFoundError"**
- **Causa:** El scheduler no tiene acceso a la carpeta de notebooks.
- **Solución:** Verifica que en el `docker-compose.yml` el scheduler tenga el volumen `./notebooks:/opt/airflow/notebooks`.

**4. "Sale un warning de Pendulum/DeprecationWarning"**
- **Causa:** Incompatibilidad entre Airflow 2.8.3 y la versión de Pendulum.
- **Solución:** Ya está filtrado en la primera celda del notebook con `warnings.filterwarnings`. No afecta al funcionamiento.
