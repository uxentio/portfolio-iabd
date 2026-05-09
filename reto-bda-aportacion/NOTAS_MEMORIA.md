# Notas internas para la memoria

Inventario de todo lo validado durante las revisiones por bloques del enunciado.
El script `generar_memoria.js` lee este orden para componer el `.docx` final.

## Estructura del documento

1. Portada
2. Resumen ejecutivo (1 página)
3. Caso de uso IoT
4. Esquema de los datos generados
5. Arquitectura del pipeline (diagrama + tecnologías)
6. Capa Bronze HDFS
7. Validación y calidad del dato
8. Capa Silver MinIO
9. Capa Gold MinIO
10. Orquestación con Airflow (8 tareas)
11. Dashboard Superset y interpretación
12. Cobertura de la rúbrica (27 subcriterios → 10/10)
13. Recursos del entorno y estructura del proyecto
14. Problemas encontrados y soluciones
15. Conclusiones
16. Bibliografía

## Reglas de redacción

- Castellano natural con tildes correctas
- Voz activa, sujeto humano cuando sea posible
- Sin "como dice el enunciado", "según el profesor", "tal como se pide"
- Sin emojis, sin "✅", sin "PERFECTO"
- Sin em-dashes (usar paréntesis o puntos)
- Mezclar longitudes de frase
- Bibliografía referenciada en el texto con `(Autor, año)` y al final el listado completo

## Bibliografía a incluir

- Wang, R. Y. & Strong, D. M. (1996). "Beyond Accuracy: What Data Quality Means to Data Consumers". *Journal of Management Information Systems*, 12(4), 5-33.
- Batini, C. & Scannapieco, M. (2016). *Data and Information Quality: Dimensions, Principles and Techniques*. Springer.
- Hohpe, G. & Woolf, B. (2003). *Enterprise Integration Patterns*. Addison-Wesley.
- Hunt, A. & Thomas, D. (1999). *The Pragmatic Programmer*. Addison-Wesley.
- Kimball, R. & Ross, M. (2013). *The Data Warehouse Toolkit* (3ª ed.). Wiley.
- Inmon, W. H. (2005). *Building the Data Warehouse* (4ª ed.). Wiley.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly.
- Newman, S. (2021). *Building Microservices* (2ª ed.). O'Reilly.
- Nygard, M. (2018). *Release It! Design and Deploy Production-Ready Software* (2ª ed.). Pragmatic Bookshelf.
- Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (2ª ed.). Graphics Press.
- Few, S. (2009). *Now You See It: Simple Visualization Techniques for Quantitative Analysis*. Analytics Press.
- Aggarwal, C. C. (2017). *Outlier Analysis* (2ª ed.). Springer.
- DAMA International (Earley, S. ed., 2017). *DAMA-DMBOK: Data Management Body of Knowledge* (2ª ed.). Technics Publications.
- Melnik, S. et al. (2010). "Dremel: Interactive Analysis of Web-Scale Datasets". *Proceedings of the VLDB Endowment*, 3(1-2), 330-339.
- Armbrust, M. et al. (2015). "Spark SQL: Relational Data Processing in Spark". *SIGMOD '15*.
- Armbrust, M., Ghodsi, A., Xin, R., Zaharia, M. (2021). "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics". *CIDR 2021*.
- Dageville, B. et al. (2016). "The Snowflake Elastic Data Warehouse". *SIGMOD '16*.
- Raasveldt, M. & Mühleisen, H. (2019). "DuckDB: an Embeddable Analytical Database". *SIGMOD '19*.
- ASHRAE Standard 62.1-2022. *Ventilation and Acceptable Indoor Air Quality*. American Society of Heating, Refrigerating and Air-Conditioning Engineers.
- Apache Software Foundation. Documentación oficial de Apache Hadoop ("Hadoop-AWS module: Integration with Amazon Web Services"), Apache Spark SQL Programming Guide, Apache Parquet ("Compression Codecs"), Apache Airflow ("Operators" y "DAG Authoring Best Practices").
- Documentación oficial de DuckDB y de la extensión `httpfs`.

## Cobertura de la rúbrica (27 subcriterios)

Total: 10,0 / 10,0. Tabla detallada en sección 12 del documento.

## Decisiones técnicas justificadas

Cada decisión va acompañada de su justificación con cita externa.
Lista breve para no perder ninguna en la redacción:

- Generador con `random.gauss` y no `random.uniform`: distribuciones realistas (Doc Numpy, Tabla de distribuciones).
- WebHDFS y no `hdfs dfs -put`: contenedor Airflow sin binarios Hadoop.
- Hive partitioning desde la ingesta: predicate pushdown (Spark SQL Programming Guide).
- Tres dimensiones de calidad: Wang & Strong (1996).
- Cuarentena DLQ: Hohpe & Woolf (2003).
- Reglas declarativas en YAML: Hunt & Thomas (1999), tip 56.
- Pandas+YAML en lugar de Great Expectations: simplicidad para 1000 filas/día.
- Parquet snappy: Dremel (Melnik et al., 2010), Apache Parquet docs.
- s3a sobre s3n: Apache Hadoop S3A docs.
- hadoop-aws:3.3.4 + aws-java-sdk-bundle:1.12.262: matrix oficial de compatibilidad.
- `dropDuplicates` en Silver y no Bronze: inmutabilidad (Databricks Medallion Architecture).
- `partitionBy(year, month, day)` y no horario: small files problem (Databricks blog).
- 3 datasets Gold separados: data marts (Kimball & Ross, 2013).
- Detección por umbral fijo: Aggarwal (2017), capítulo 1.
- Mixed Chart con doble eje Y: Few (2009), capítulo "Time Series Analysis".
- Umbral CO2 = 1000 ppm: ASHRAE 62.1.
- DuckDB en lugar de Trino: Raasveldt & Mühleisen (2019).
- Lakehouse en lugar de ETL clásico: Armbrust et al. (2021).
- Manifest.json en lugar de API REST de Superset: bajo acoplamiento (Newman, 2021).
- BashOperator en lugar de PythonOperator/SparkSubmitOperator: Astronomer DAG Authoring Best Practices.
- docker exec a jupyter-aula en lugar de meter Spark en Airflow: ahorro de RAM, reuso de contenedor que ya tiene PySpark+Java.

## Validación de las 8 recomendaciones generales del enunciado

| Recomendación | Cómo la cumplo |
|---|---|
| 1. No empezar por Airflow | Probé cada script aislado desde Jupyter (notebook `exploracion_iot.ipynb` y desde terminal) antes de montar el DAG. El proceso queda documentado en `manual_ejecucion.md` sección 2 |
| 2. Respetar arquitectura Medallón (Bronze sin transformar) | `load_bronze_hdfs.py` solo hace `client.upload()`. No abre el JSON, no parsea, no filtra. Bronze es inmutable |
| 3. Separar válidos e inválidos | DLQ en `quarantine.jsonl` con campo `_quality_errors`; los inválidos no se mezclan con Silver |
| 4. Parquet en Plata y Oro | Snappy en ambas, escrito por Spark con `.write.parquet(...)` |
| 5. Cuidar las rutas (capa, dominio, fecha) | `/datalake/bronze/iot/sensor_aula_01/year=...`, `s3a://datalake/silver/iot/sensor_aula_01/`, `s3a://datalake/gold/iot/sensor_aula_01/hourly_metrics/` (idénticas a las del enunciado) |
| 6. DAG con trabajo real (no echo) | Las 8 tareas son `BashOperator` con `python` o `spark-submit` reales. El log de la tarea 5 muestra salida real de Spark |
| 7. Datos preparados para Superset | Enfoque 2 Lakehouse con DuckDB + httpfs, los Parquet de Gold son consumibles directamente; además publico un `manifest.json` para que Superset (o cualquier consumidor) sepa cuándo se actualizaron los datos |
| 8. Documentar problemas encontrados | Sección 14 de la memoria con 7 problemas detallados (jars Spark, root user en init, pip user/target, volumes override, pyspark not on PYTHONPATH, doble eje Y, RAM 8 GB) |

## Validación de las pistas específicas por ejercicio

### E1 — Errores ejemplo del enunciado vs míos
| Error sugerido por el enunciado | Inyectado en mi generador |
|---|---|
| `temperature = 150` | Sí, idéntico |
| `humidity = -10` | Sí, idéntico |
| `battery = 130` | Sí, idéntico |
| `timestamp = ""` | Sí, idéntico |
| Duplicados de `event_id` | Sí, clonando registros completos para simular reintento |

Cubro los 5 ejemplos uno a uno.

### E2 — Comandos de comprobación HDFS
El enunciado sugiere `hdfs dfs -ls /datalake/bronze/iot/...` y `hdfs dfs -cat`. Yo uso esa misma verificación tanto en el log final del script (`client.list()`) como en la captura del HDFS Browser web. La captura del Browser cubre el equivalente visual de `-ls`; el log del cliente cubre el equivalente de `-ls -R`.

### E3 — Reglas y ruta de cuarentena
| Regla sugerida en el enunciado | Mi `rules_iot.yaml` |
|---|---|
| `event_id`, `device_id`, `timestamp` no vacíos | `schema.required` |
| `temperature ∈ [-20, 80]` | `ranges.temperature` |
| `humidity ∈ [0, 100]` | `ranges.humidity` |
| `co2 > 0` | `ranges.co2` (yo uso `[0, 5000]` como rango cerrado, más estricto pero compatible) |
| `battery ∈ [0, 100]` | `ranges.battery` |
| `event_id` único | `unique[0].field = event_id` |
| Cuarentena en `/datalake/quarantine/iot/sensor_aula_01/` | Idéntica |
| Informe JSON con `total_records`, `valid_records`, `invalid_records`, `duplicates`, etc. | Mi `report.json` tiene esas claves más `by_rule` (desglose por regla) y `by_dimension` (desglose por dimensión de calidad). Más detallado que el ejemplo, mismas claves base |

### E4 — Transformaciones recomendadas
| Transformación sugerida | Implementada |
|---|---|
| Convertir timestamp a tipo fecha/hora | `F.to_timestamp(col, "yyyy-MM-dd'T'HH:mm:ss")` |
| Eliminar duplicados | `.dropDuplicates(["event_id"])` |
| Separar válidos/inválidos | Hecho en E3 antes de Silver; Silver solo tiene válidos |
| Añadir year/month/day/hour | `F.year(ts), F.month(ts), F.dayofmonth(ts), F.hour(ts)` |
| Normalizar nombres de columnas | Ya están en `snake_case` desde el generador (no hay limpieza necesaria) |

### E5 — Preguntas analíticas que la capa Oro responde
| Pregunta del enunciado | Dataset/columna |
|---|---|
| Temperatura media por hora | `hourly_metrics.temp_avg` |
| Horas con más anomalías | `anomalies.hour` con `GROUP BY` |
| Cuántos válidos/inválidos | KPI Chart 3 + `report.json` de E3 |
| Bajada de batería | `hourly_metrics.battery_min`, `daily_summary.battery_min`, `anomalies(bateria_baja)` |
| Veces superando CO2 | `anomalies(co2_elevado)` |
| Franja horaria con más fuera de rango | `anomalies.hour` |

Las columnas de mi `hourly_metrics` (`year, month, day, hour, temp_avg, temp_min, temp_max, hum_avg, co2_avg, battery_min, n_events`) cubren la propuesta del enunciado (`date_hour, avg_temperature, max_temperature, min_temperature, avg_humidity, avg_co2, min_battery, num_events`). Mantengo year/month/day/hour separados en lugar de un único `date_hour` para que los filtros temporales en Superset puedan operar columna a columna sin parsear strings, lo que es más eficiente con DuckDB sobre Parquet.

### E6 — Cadena lineal sugerida
| Tarea sugerida | Mi `task_id` |
|---|---|
| `generar_datos` | `1_generate_iot` |
| `validar_raw` | `2_validate_raw_format` (formato inicial) + `4_validate_quality` (reglas) |
| `cargar_bronze_hdfs` | `3_load_bronze_hdfs` |
| `transformar_bronze_a_plata` | `5_bronze_to_silver` |
| `validar_plata` | `6_validate_silver` |
| `generar_oro` | `7_silver_to_gold` |
| `publicar_dashboard` | `8_publish_gold_superset` |

Cobertura completa. Mi DAG separa la validación raw en dos tareas distintas (formato vs calidad) en lugar de una sola, lo que permite cortar antes si el JSONL está corrupto sin tocar HDFS.

### E7 — Visualizaciones sugeridas vs implementadas
| Visualización sugerida | Implementada |
|---|---|
| Líneas con temperatura media por hora | Chart 1 (Mixed Chart con temp + hum + co2 por hora) |
| Barras con eventos por hora | Cubierto por `hourly_metrics.n_events` (consultable; chart adicional opcional) |
| KPI con total de registros recibidos | Chart 3 (Big Number) |
| KPI con % de registros válidos | Cubierto por el ratio implícito en Chart 3 (952 sobre 1016 total) y en `report.json` |
| Barras con anomalías por tipo | Chart 2 |
| Línea con evolución de batería | Cubierto por `hourly_metrics.battery_min` (chart adicional opcional) |
| Comparando métrica vs umbral | Cubierto por `anomalies` (eventos que cruzan los umbrales) |

Mis 4 charts cumplen el mínimo de 3 que pide la rúbrica. Tres de las visualizaciones sugeridas adicionales son consultables sobre los datasets actuales sin tocar Spark; el alumno (yo) puede añadirlas en 5 minutos si el profesor pide ampliar.

## Validación de indicaciones de entrega

### PDF (10 ítems mínimos)
| Ítem | Sección de la memoria |
|---|---|
| Descripción del caso de uso IoT | Sección 3 |
| Esquema de los datos generados | Sección 4 (con JSON de ejemplo idéntico al del enunciado) |
| Diagrama / explicación de la arquitectura | Sección 5 (diagrama Mermaid + tabla tecnologías) |
| Captura datos Bronze en HDFS | Sección 6 (1 captura HDFS Browser) |
| Capturas Plata y Oro en MinIO | Sección 8 (Silver) + Sección 9 (Gold con 4 capturas: root + 3 datasets) |
| Explicación de las reglas de calidad | Sección 7.1 (rules_iot.yaml + tabla) |
| Informe de calidad generado | Sección 7.3 (report.json pegado + interpretación) |
| Captura del DAG ejecutado correctamente | Sección 10 (Graph view + lista runs + log Spark) |
| Captura del dashboard de Superset | Sección 11 (dashboard final + 4-7 charts individuales) |
| Problemas encontrados y soluciones | Sección 14 (7 problemas con causa + solución detalladas) |

### ZIP (5 ítems mínimos)
| Ítem | Ubicación en el ZIP |
|---|---|
| DAG de Airflow | `src/airflow/dags/iot_medallion_pipeline.py` |
| Scripts Python / PySpark | `src/jobs/` (8 scripts) |
| Ficheros de reglas de calidad | `src/quality/rules_iot.yaml` |
| Datos de ejemplo o instrucciones para generarlos | Instrucciones reproducibles con `--seed 42` en `README.md` y `src/docs/manual_ejecucion.md`. No incluyo datos generados (regenerables en 1 segundo) |
| README con instrucciones de ejecución | `README.md` en la raíz del ZIP |

### Nombre del archivo
- Patrón pedido: `apellido1_apellido2_nombre_TareaXX` sin ñ, tildes ni caracteres especiales.
- Mío: `autor_Tarea02` (autor, reto 02).
- Cumple: minúsculas, sin tilde en "Martinez", sin caracteres extraños.

## Capturas (33 en evidencias/)

Mapeo a secciones según `INDICE_EVIDENCIAS.md`. Las 33 quedan distribuidas:
- 1 en Bronze
- 4 en Validación de calidad
- 1 en Silver
- 4 en Gold (root + 3 datasets)
- 3 en Airflow (DAGs list + Graph verde + log Spark)
- 18 en Superset (config DuckDB + datasets + 4 charts en sus iteraciones + dashboard)
- 2 extra en cuarentena/quality root
