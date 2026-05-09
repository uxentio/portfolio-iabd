# 📚 CUESTIONARIO RA2 - GUÍA DE ESTUDIO
## Big Data Aplicado

---

## 🔷 MÓDULO 1: Casos de Uso de Big Data

### P1.1: ¿Qué se busca al presentar casos de uso de Big Data?
> ✅ **Conectar conceptos abstractos con escenarios concretos como logs, clickstream o IoT**

### P1.2: ¿Qué problema empuja a pasar de logs locales a logging centralizado?
> ✅ **No saber en qué máquina mirar cuando una incidencia afecta a múltiples servicios**

### P1.3: En arquitectura de logs con agentes, Kafka y ElasticSearch, ¿qué papel juega Kafka?
> ✅ **Actuar como cola distribuida que recibe, amortigua y reparte los eventos de log**

### P1.4: ¿Por qué capturar eventos propios de clickstream en lugar de solo Google Analytics?
> ✅ **Para responder preguntas avanzadas sobre recorridos, experimentos A/B y modelos de recomendación**

### P1.5: ¿Qué característica tienen los datos de sensores IoT?
> ✅ **Cada dispositivo envía poca información, pero el conjunto genera un flujo continuo relevante**

### P1.6: ¿Qué relación hay entre batch y streaming en detección de fraude?
> ✅ **Streaming aporta decisiones rápidas y batch aporta análisis profundos sobre el histórico completo**

### P1.7: ¿Por qué los "small files" son un problema frecuente?
> ✅ **Porque el sistema dedica mucho tiempo a abrir y cerrar miles de archivos minúsculos en lugar de procesar datos**

### P1.8: ¿Qué efecto producen los hotspots y el skew?
> ✅ **Hacen que algunas particiones o tareas se saturen mientras otras quedan casi ociosas**

### P1.9: ¿Cómo ajustan empresas maduras el almacenamiento de logs?
> ✅ **Combinan logs crudos baratos a largo plazo con una ventana corta indexada y métricas agregadas**

### P1.10: ¿Qué enfoque propone el capítulo para elegir tecnologías?
> ✅ **Partir del problema, los datos, los plazos, el presupuesto y la tolerancia al fallo**

---

## 🔷 MÓDULO 2: Computación Distribuida y Resiliencia

### P2.1: ¿Qué problema resuelven los motores distribuidos frente al "script nocturno"?
> ✅ **Trocear el trabajo y ejecutarlo en paralelo sobre datos repartidos en el clúster**

### P2.2: ¿Qué caracteriza al procesamiento batch?
> ✅ **Acumular datos durante un periodo y lanzar jobs que recorren grandes lotes**

### P2.3: ¿Cómo se entiende el procesamiento de streaming?
> ✅ **Como servicios que consumen flujos de eventos continuos y producen resultados casi en tiempo real**

### P2.4: ¿Qué provoca una operación tipo groupByKey o reduceByKey?
> ✅ **Hace que todos los datos con la misma clave se reorganicen hacia la misma tarea**

### P2.5: Ante un fallo donde muere un executor, ¿cómo actúa Spark?
> ✅ **Reejecuta únicamente las tareas falladas en otro executor manteniendo el resto del job en marcha**

### P2.6: ¿Qué permite a un job de Flink reanudarse tras un fallo?
> ✅ **Checkpoints consistentes del estado más offsets de lectura almacenados de las fuentes como Kafka**

### P2.7: ¿Qué busca evitar el uso de backoff en reintentos?
> ✅ **Que los reintentos no saturen aún más un sistema ya debilitado por el primer fallo**

### P2.8: ¿Qué es una operación idempotente?
> ✅ **Una operación cuyo resultado final es el mismo aunque se ejecute varias veces seguidas**

### P2.9: ¿Qué promete la garantía at-least-once?
> ✅ **Que cada mensaje se procesará al menos una vez, pudiendo repetirse en ciertos fallos**

### P2.10: ¿Qué idea resume mejor la resiliencia?
> ✅ **Es una propiedad del conjunto donde diseño, motores, colas, bases y métricas colaboran**

---

## 🔷 MÓDULO 3: Escalabilidad y Elasticidad

### P3.1: ¿Qué distingue escalabilidad de elasticidad?
> ✅ **La escalabilidad describe cómo crece el sistema y la elasticidad cómo se adapta a la carga**

### P3.2: ¿Qué describe mejor el escalado vertical?
> ✅ **Aumentar CPU, RAM y disco de una misma máquina haciéndola más grande**

### P3.3: ¿Qué refleja el escalado horizontal?
> ✅ **Usar varias máquinas similares coordinadas en lugar de un único servidor gigante**

### P3.4: ¿Qué idea capta mejor la elasticidad?
> ✅ **Aumentar y reducir recursos automáticamente según métricas como CPU o tamaño de colas**

### P3.5: ¿Cuál es el papel de las colas en un sistema elástico?
> ✅ **Amortiguar picos permitiendo que productores y consumidores trabajen a ritmos diferentes**

### P3.6: ¿Qué coste adicional introduce la escalabilidad horizontal?
> ✅ **Aumenta la complejidad y la coordinación entre nodos, particiones y reequilibrios**

### P3.7: ¿Qué se entiende por throughput?
> ✅ **La cantidad de trabajo que el sistema realiza por unidad de tiempo**

### P3.8: ¿Cómo se define la latencia?
> ✅ **El tiempo que transcurre desde que una petición entra hasta que se produce la respuesta**

### P3.9: ¿Qué indica una CPU muy baja mientras se quejan de falta de recursos?
> ✅ **Que probablemente la configuración de colas, límites o particiones está impidiendo usar bien la capacidad**

### P3.10: ¿Por qué crear más particiones de Kafka de las necesarias al principio?
> ✅ **Facilitar que el sistema pueda escalar consumidores en el futuro sin rediseñar el topic**

---

## 🔷 MÓDULO 4: Sistemas Distribuidos

### P4.1: ¿Qué describe mejor un sistema distribuido?
> ✅ **Grupo de procesos coordinados que aparentan un único sistema**

### P4.2: ¿En qué situación alguien dice "esto hay que distribuirlo"?
> ✅ **Cuando informes tardan horas y el servidor se satura**

### P4.3: ¿Por qué escalar "hacia arriba" tiene fecha de caducidad?
> ✅ **Porque hay límites físicos y de coste al crecer una sola máquina**

### P4.4: ¿Cómo debe plantearse el diseño frente a fallos?
> ✅ **Aceptar fallos frecuentes y diseñar para seguir operando**

### P4.5: ¿Qué suposición realista debe hacerse sobre la red?
> ✅ **Que algunos mensajes llegarán tarde, duplicados o desordenados**

### P4.6: Según el teorema CAP, ¿qué obliga una partición de red?
> ✅ **Debes elegir entre consistencia fuerte o disponibilidad plena**

### P4.7: ¿Qué ejemplo refleja mejor consistencia eventual?
> ✅ **Ver que el contador de likes tarda pero converge**

### P4.8: ¿Cuál es el objetivo principal de replicar datos?
> ✅ **Aumentar tolerancia a fallos guardando copias en nodos**

### P4.9: ¿Por qué se particionan los datos?
> ✅ **Repartir datos y carga entre nodos con particiones**

### P4.10: ¿Qué describe mejor el skew?
> ✅ **Cuando pocas tareas reciben muchos más datos que el resto**

---

## 📝 CONCEPTOS CLAVE PARA RECORDAR

| Concepto | Definición |
|----------|------------|
| **Throughput** | Trabajo por unidad de tiempo |
| **Latencia** | Tiempo de respuesta de una petición |
| **Escalado vertical** | Máquina más grande (scale up) |
| **Escalado horizontal** | Más máquinas coordinadas (scale out) |
| **Elasticidad** | Adaptarse automáticamente a la carga |
| **Idempotente** | Mismo resultado aunque se repita |
| **At-least-once** | Mensaje procesado al menos 1 vez |
| **Skew** | Carga desigual entre tareas/particiones |
| **Teorema CAP** | Elegir entre consistencia o disponibilidad |
| **Consistencia eventual** | Los datos convergen con el tiempo |
| **Backoff** | Esperar antes de reintentar para no saturar |
| **Checkpoint** | Punto de guardado para recuperación |

---

## 📊 RESPUESTAS RÁPIDAS (Por número)

### Módulo 1
`1:[2] 2:[3] 3:[0] 4:[2] 5:[1] 6:[3] 7:[0] 8:[2] 9:[1] 10:[2]`

### Módulo 2
`1:[1] 2:[2] 3:[0] 4:[2] 5:[0] 6:[1] 7:[3] 8:[2] 9:[1] 10:[1]`

### Módulo 3
`1:[1] 2:[3] 3:[0] 4:[2] 5:[1] 6:[3] 7:[0] 8:[1] 9:[1] 10:[2]`

### Módulo 4
`1:[3] 2:[2] 3:[3] 4:[0] 5:[2] 6:[1] 7:[3] 8:[0] 9:[1] 10:[2]`

---

*Documento generado para estudio - Cuestionario RA2 Big Data Aplicado*
