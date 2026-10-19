# Portfolio · Especialización en Inteligencia Artificial y Big Data

Recopilación de las prácticas, retos y proyectos que realicé durante el
**Curso de Especialización en Inteligencia Artificial y Big Data** (Formación
Profesional de Grado Superior — el "máster de FP" en IA y Big Data).

El repositorio está organizado por los **módulos profesionales** del título, de
modo que cada carpeta corresponde a una asignatura del curso. Dentro de cada
módulo hay un `README.md` propio con el detalle de cada trabajo.

> Autor: [@uxentio](https://github.com/uxentio) · Curso 2024–2025

---

## Estructura del repositorio

| Carpeta | Módulo profesional |
|---|---|
| [`modelos-ia/`](modelos-ia/) | 5061 — Modelos de Inteligencia Artificial |
| [`sistemas-aprendizaje/`](sistemas-aprendizaje/) | 5062 — Sistemas de Aprendizaje Automático |
| [`programacion-ia/`](programacion-ia/) | 5063 — Programación de Inteligencia Artificial |
| [`sistemas-big-data/`](sistemas-big-data/) | 5064 — Sistemas de Big Data |
| [`big-data-aplicado/`](big-data-aplicado/) | 5065 — Big Data Aplicado |
| [`reto-bda-aportacion/`](reto-bda-aportacion/) | Aportación propia al reto de Big Data |

---

## 5061 · Modelos de IA

Lógica difusa, sistemas expertos, RAG y servicios cognoscitivos en la nube.

| Proyecto | Descripción |
|---|---|
| [`fuzzy-anfis-package/`](modelos-ia/fuzzy-anfis-package) | Proyecto final: paquete ANFIS / lógica difusa |
| [`fuzzy-confort-riego/`](modelos-ia/fuzzy-confort-riego) | Sistemas difusos para confort térmico y riego automático |
| [`rag-anything-llm/`](modelos-ia/rag-anything-llm) | RAG con AnythingLLM sobre documentación técnica |
| [`azure-form-recognizer-ocr/`](modelos-ia/azure-form-recognizer-ocr) | OCR de facturas con Azure Form Recognizer |
| `frenador-tren-{mamdani,tsk}.py` | Sistema de frenado de tren: comparación Mamdani vs. TSK |

## 5062 · Sistemas de Aprendizaje Automático

Flujo completo de ML clásico: datos, modelos supervisados y no supervisados,
reducción de dimensionalidad, redes neuronales y explicabilidad.

| Proyecto | Descripción |
|---|---|
| [`clasificacion-supervisada/`](sistemas-aprendizaje/clasificacion-supervisada) | Clasificación con scikit-learn |
| [`clustering-no-supervisado/`](sistemas-aprendizaje/clustering-no-supervisado) | K-Means, clustering jerárquico y por afinidad |
| [`pca-reduccion-dimensionalidad/`](sistemas-aprendizaje/pca-reduccion-dimensionalidad) | PCA y LDA sobre el dataset Wine |
| [`automl-explainable-ml/`](sistemas-aprendizaje/automl-explainable-ml) | AutoML y explicabilidad (SHAP, Explainer Dashboard) |
| [`redes-neuronales-keras/`](sistemas-aprendizaje/redes-neuronales-keras) | Redes neuronales con Keras (clasificación, regresión, MLP) |
| [`algoritmos-geneticos/`](sistemas-aprendizaje/algoritmos-geneticos) | Optimización con algoritmos genéticos |

## 5063 · Programación de IA

Agentes, automatización (RPA), integración con LLMs e IoT.

| Proyecto | Descripción |
|---|---|
| [`agentes-ia-rpa-rag/`](programacion-ia/agentes-ia-rpa-rag) | Cosmic Briefing (n8n + Telegram + Groq), estación IoT y RPA + RAG con Playwright |
| [`iot-mqtt-nodered-maui/`](programacion-ia/iot-mqtt-nodered-maui) | Integración IoT: MQTT + Node-RED + .NET MAUI + LLM |
| [`ejercicios-csharp-poo/`](programacion-ia/ejercicios-csharp-poo) | Ejercicios de programación orientada a objetos en C# |
| [`tarea-llm-integration/`](programacion-ia/tarea-llm-integration) | Memoria de integración con LLMs |

## 5064 · Sistemas de Big Data

Fundamentos del ecosistema distribuido y comparativas de rendimiento.

| Proyecto | Descripción |
|---|---|
| [`pandas-vs-polars/`](sistemas-big-data/pandas-vs-polars) | Comparativa Pandas vs. Polars (joins, agrupaciones, pivotes) |
| [`hadoop-hdfs-spark/`](sistemas-big-data/hadoop-hdfs-spark) | Fundamentos de Hadoop, HDFS y Apache Spark |
| [`sistema-experto-clima/`](sistemas-big-data/sistema-experto-clima) | Sistema experto de control climático de edificios |
| `viz-*.pdf` | Tareas de visualización avanzada (Pokémon, Avocado, Diamonds, Videogames…) |

## 5065 · Big Data Aplicado

Orquestación, monitorización y calidad del dato en entornos reales.

| Proyecto | Descripción |
|---|---|
| [`airflow-jupyter-pipeline/`](big-data-aplicado/airflow-jupyter-pipeline) | Entorno con Apache Airflow + Jupyter (DAGs con Papermill) |
| [`grafana-prometheus-monitoring/`](big-data-aplicado/grafana-prometheus-monitoring) | Monitorización con Grafana + Prometheus |
| [`calidad-integridad-datos/`](big-data-aplicado/calidad-integridad-datos) | Calidad e integridad de datos en entornos distribuidos |

## Reto de Big Data — aportación propia

En [`reto-bda-aportacion/`](reto-bda-aportacion/) incluyo mi contribución
(overrides de Docker, evidencias y código en `src/`) sobre el entorno docente de
Big Data. El entorno base es material del profesorado y no se redistribuye aquí.

---

## Proyectos en repositorios aparte

- **MovieApp** — gestión de películas en .NET (API + WPF + MAUI + consola). Repositorio privado.
- [books-pipeline](https://github.com/uxentio/books-pipeline) — pipeline ETL de libros (Goodreads + Google Books).
- [BDA_Proyecto_UT1_RA1](https://github.com/uxentio/BDA_Proyecto_UT1_RA1) — análisis de ejecución presupuestaria.

## Tecnologías

**Lenguajes:** Python, C#/.NET, SQL · **ML/IA:** scikit-learn, Keras/TensorFlow,
LangChain, pandas, Polars · **Big Data:** Hadoop, Spark, Airflow, Cassandra ·
**Infra/observabilidad:** Docker, Azure, Grafana, Prometheus · **IoT/automatización:**
MQTT, Node-RED, n8n.

## Reproducibilidad

- Los datasets pesados, entornos virtuales (`venv/`, `node_modules/`, `bin/`, `obj/`)
  y los `.zip` quedan fuera del control de versiones (ver `.gitignore`). Para ejecutar
  un proyecto, instala sus dependencias desde el `requirements.txt` o `package.json`
  correspondiente.
- Las claves de API (NASA, Groq, etc.) se han sustituido por marcadores de posición;
  usa las tuyas para ejecutar los proyectos que las requieran.

## Contacto

[@uxentio](https://github.com/uxentio)
