# Reto BDA — Aportación propia

Mi aportación sobre el entorno docente de Big Data del profesor (`entorno_bda_v1`). **Solo se incluye lo que es mío**: el entorno base completo (NameNode, DataNodes, YARN, JupyterLab, MinIO, Airflow, Superset, Prometheus, Grafana) es del profesor y no se redistribuye aquí.

## Estructura

| Carpeta / archivo | Descripción |
|---|---|
| [`entorno_overrides/`](entorno_overrides) | `docker-compose.override.yml` que extiende el entorno del profesor sin tocar el original |
| [`evidencias/`](evidencias) | Capturas y artefactos del pipeline IoT Medallon ejecutado |
| [`src/`](src) | Código propio: `quality/rules_iot.yaml`, `docs/arquitectura.md`, `docs/manual_ejecucion.md`, `docs/diccionario_datos.md` |
| `autor_Tarea02.{docx,pdf}` | Memoria de la tarea |
| `NOTAS_MEMORIA.md` | Notas y referencias de la memoria |

## Cómo reproducir

Pre-requisito: tener el entorno del profesor (`entorno_bda_v1`) descargado y funcional. Después aplicar el override de [`entorno_overrides/`](entorno_overrides) sin modificar el `docker-compose.yml` original.
