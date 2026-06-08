# Portfolio IABD

Trabajos del ciclo de **Inteligencia Artificial y Big Data**: prácticas, retos y proyectos finales.

### Lenguajes y entornos

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![C#](https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=csharp&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-512BD4?style=for-the-badge&logo=dotnet&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### Machine Learning / IA

![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-CD792C?style=for-the-badge&logo=polars&logoColor=white)

### Big Data / Orquestación

![Apache Hadoop](https://img.shields.io/badge/Hadoop-66CCFF?style=for-the-badge&logo=apachehadoop&logoColor=black)
![Apache Spark](https://img.shields.io/badge/Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![Cassandra](https://img.shields.io/badge/Cassandra-1287B1?style=for-the-badge&logo=apachecassandra&logoColor=white)

### Cloud / Observabilidad / Automatización

![Microsoft Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=mqtt&logoColor=white)
![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=for-the-badge&logo=node-red&logoColor=white)

## Proyectos por módulo

### 🧠 [`modelos-ia/`](modelos-ia/) — Modelos de IA

| Proyecto | Tema |
|---|---|
| [`fuzzy-anfis-package/`](modelos-ia/fuzzy-anfis-package) | Paquete final ANFIS / lógica difusa |
| [`fuzzy-confort-riego/`](modelos-ia/fuzzy-confort-riego) | Sistemas difusos: confort térmico y riego automático |
| [`rag-anything-llm/`](modelos-ia/rag-anything-llm) | RAG con AnythingLLM sobre documentación técnica |
| [`azure-form-recognizer-ocr/`](modelos-ia/azure-form-recognizer-ocr) | OCR de facturas con Azure Form Recognizer |
| `frenador-tren-{mamdani,tsk}.py` | Sistema de frenado de tren — Mamdani vs TSK |

### 📈 [`sistemas-aprendizaje/`](sistemas-aprendizaje/) — Sistemas de Aprendizaje

| Proyecto | Tema |
|---|---|
| [`clasificacion-supervisada/`](sistemas-aprendizaje/clasificacion-supervisada) | Clasificación con scikit-learn |
| [`clustering-no-supervisado/`](sistemas-aprendizaje/clustering-no-supervisado) | K-Means, clustering jerárquico, afinidad |
| [`pca-reduccion-dimensionalidad/`](sistemas-aprendizaje/pca-reduccion-dimensionalidad) | PCA y LDA con dataset Wine |
| [`automl-explainable-ml/`](sistemas-aprendizaje/automl-explainable-ml) | AutoML + explicabilidad (SHAP, Explainer Dashboard) |
| [`redes-neuronales-keras/`](sistemas-aprendizaje/redes-neuronales-keras) | Deep learning con Keras (clasificación, regresión, MLP) |
| [`algoritmos-geneticos/`](sistemas-aprendizaje/algoritmos-geneticos) | Algoritmos genéticos |

### 🤖 [`programacion-ia/`](programacion-ia/) — Programación para IA

| Proyecto | Tema |
|---|---|
| [`agentes-ia-rpa-rag/`](programacion-ia/agentes-ia-rpa-rag) | Cosmic Briefing (n8n + Telegram + Groq), Estación IoT, RPA + RAG con Playwright |
| [`iot-mqtt-nodered-maui/`](programacion-ia/iot-mqtt-nodered-maui) | Integración IoT: MQTT + Node-RED + .NET MAUI + LLM |
| [`ejercicios-csharp-poo/`](programacion-ia/ejercicios-csharp-poo) | Ejercicios de POO en C# |
| [`tarea-llm-integration/`](programacion-ia/tarea-llm-integration) | Memoria de integración con LLMs |
| [`language-tutor-system/`](programacion-ia/language-tutor-system) | Tutor de idiomas adaptativo: prompt de sistema + esquema de progreso (ingeniería de prompts) |

### 🗄️ [`big-data-aplicado/`](big-data-aplicado/) — Big Data Aplicado

| Proyecto | Tema |
|---|---|
| [`airflow-jupyter-pipeline/`](big-data-aplicado/airflow-jupyter-pipeline) | Mini-entorno con Apache Airflow + Jupyter (Papermill DAGs) |
| [`grafana-prometheus-monitoring/`](big-data-aplicado/grafana-prometheus-monitoring) | Dashboard de monitorización con Grafana + Prometheus |
| [`calidad-integridad-datos/`](big-data-aplicado/calidad-integridad-datos) | Calidad y fiabilidad de datos en entornos distribuidos |

### 📊 [`sistemas-big-data/`](sistemas-big-data/) — Sistemas Big Data

| Proyecto | Tema |
|---|---|
| [`pandas-vs-polars/`](sistemas-big-data/pandas-vs-polars) | Comparativa Pandas vs Polars (joins, agrupaciones, pivotes) |
| [`hadoop-hdfs-spark/`](sistemas-big-data/hadoop-hdfs-spark) | Conceptos fundamentales de Hadoop, HDFS y Apache Spark |
| [`sistema-experto-clima/`](sistemas-big-data/sistema-experto-clima) | Sistema experto de control climático de edificios |
| `viz-*.pdf` | Tareas de visualización avanzada (Pokémon, Avocado, Diamonds, Videogames…) |

### 🐳 [`reto-bda-aportacion/`](reto-bda-aportacion/) — Reto BDA (mi aportación)

Aportación propia (overrides Docker, evidencias y código `src/`) sobre el entorno docente de Big Data. **El entorno base es del profesor y no se redistribuye aquí.**

## Proyectos en repos independientes

- **MovieApp** — Sistema de gestión de películas en .NET (API + WPF + MAUI + consola). Repo privado.
- [books-pipeline](https://github.com/uxentio/books-pipeline) — Pipeline ETL de libros (Goodreads + Google Books).
- [BDA_Proyecto_UT1_RA1](https://github.com/uxentio/BDA_Proyecto_UT1_RA1) — Análisis de ejecución presupuestaria.

## Notas

- Datasets pesados, entornos virtuales (`venv/`, `node_modules/`, `bin/obj/`) y archivos `.zip` están excluidos vía `.gitignore`. Para reproducir, instalar dependencias del `requirements.txt` o `package.json` correspondiente.
- Las API keys (NASA, Groq, etc.) están reemplazadas por placeholders. Aporta las tuyas para ejecutar.

## Contacto

[@uxentio](https://github.com/uxentio)
