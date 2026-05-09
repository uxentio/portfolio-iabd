# Guion del vídeo de defensa — UT11

**Duración objetivo:** 9:00 · **techo:** 10:00
**Cómo grabar:** pantalla compartida con el notebook a la izquierda y un poco de espacio para hablar. Voz en primera persona, tono normal de alumno presentando el trabajo.
**Antes de grabar:** abre el `.ipynb` en Colab con todas las celdas ejecutadas. Cuando la guía diga `[N]:` me refiero al número que Colab pone en el cajetín de la celda de código (ese contador que aparece a la izquierda de cada bloque).

---

## Reparto del tiempo

| Bloque | Min | Acumulado |
|---|---|---|
| 0. Intro | 0:30 | 0:30 |
| 1. Regresión | 4:00 | 4:30 |
| 2. Clasificación | 4:00 | 8:30 |
| 3. Cierre | 0:30 | 9:00 |

---

## 0. Intro (0:30) — cabecera del notebook

> **Mostrar:** la celda de cabecera con tu nombre, DNI y el enlace al vídeo.

«Hola, soy autor, DNI XXXXXXXXX. Os presento el trabajo de la UT11, redes neuronales profundas con Keras.

El trabajo tiene dos partes: una red de regresión sobre el dataset *House Prices* que ya usé en UT5 y UT9, y una red de clasificación binaria sobre *Social Network Ads*, que es el mismo dataset que en UT6 estaba renombrado como "Ensayo de Motores" — eso lo descubrí cuando preparaba UT9. Los dos datasets se descargan automáticamente de Kaggle al ejecutar el notebook.»

---

## 1. REGRESIÓN (4:00)

### 1.1 Preprocesamiento — celdas `[4]` a `[13]` (1:30)

> **Mostrar:** ir bajando por el bloque "1.1 Preprocesar el dataset", celda a celda.

«Para regresión uso *House Prices*. Son 1460 viviendas con 81 columnas, y lo que predigo es `SalePrice`.

En la celda `[4]` lo descargo con `kagglehub`, igual que hice en UT9. La `[5]` carga el CSV, la `[6]` lo copia a `/content/` para que aparezca en el panel de archivos de Colab. La `[7]` muestra el `info()` y el `describe()` del target — `SalePrice` va de unos 35.000 a 755.000 USD.

En la `[8]` reduzco al **mismo subconjunto de 24 variables que usé en UT5**: 14 numéricas y 10 categóricas. Así la comparativa con los modelos de UT5 es directa, sobre las mismas features y el mismo split.

La `[9]` comprueba que no hay nulos en el subset, la `[10]` aplica imputación por mediana y moda (no encuentra nada que rellenar porque las columnas problemáticas como `Alley` o `PoolQC` no están en el subset). La `[11]` aplica One-Hot Encoding con `drop_first=True` para evitar la trampa dummy — el dataset pasa de 25 a 70 columnas.

Las celdas `[12]` y `[13]` separan X e y, hacen un split 80/20 con `random_state=42` (el mismo que UT5 y UT9), y estandarizan con `StandardScaler` ajustando solo con el train.»

### 1.2 Modelo — celda `[14]` (0:30)

> **Mostrar:** la celda `[14]` con la función `build_regression_model` y el `model.summary()`.

«La arquitectura es la del notebook `2_Regression_with_Keras` que vino con la unidad: dos capas densas de 50 neuronas con `ReLU` y una salida `Dense(1)` sin activación. En regresión necesito un número real cualquiera, no una probabilidad, por eso la salida es lineal.

Compilo con `Adam`, `MSE` como función de coste y `MAE` como métrica adicional, que es más interpretable porque viene en USD. La red tiene 6.101 parámetros entrenables.»

### 1.3 Entrenamiento — celda `[15]` (0:30)

> **Mostrar:** la celda `[15]`, hacer scroll por las épocas y comentar.

«Entreno con `validation_split=0.2`, batch 32 y un techo de 300 épocas. El callback `EarlyStopping` con `patience=20` debería cortar si la `val_loss` deja de mejorar. En esta ejecución el modelo entrenó las 300 completas — no llegó a cortar.»

### 1.4 Pérdidas y overfitting — celda `[16]` (0:30)

> **Mostrar:** el gráfico de pérdida en escala log con la línea roja de la mejor época, y el print de debajo.

«La gráfica está en escala logarítmica para que se aprecie bien la caída inicial. La línea roja marca la mejor época, que en este caso coincide con la última: la `val_loss` seguía bajando suavemente cuando el entrenamiento terminó. El print confirma que la red podría seguir aprendiendo si subiera el techo a 500 o 1000 épocas, lo que indica que está infraentrenada.»

### 1.5 Predicción — celdas `[17]` y `[18]` (0:30)

> **Mostrar:** el output con las métricas y luego el gráfico de líneas real vs predicho.

«En la `[17]` predigo sobre el test, que el modelo no ha visto durante el entrenamiento. Salen estos números: **R² = 0.8274**, RMSE de unos 36.000 USD y MAE de unos 24.000 USD.

La `[18]` dibuja un gráfico de líneas con los valores reales en azul y los predichos en naranja, ordenados por precio real. El ajuste es razonable en el rango central. En las casas más caras la naranja se separa más, ahí el modelo tiene menos muestras para aprender.»

### 1.6 Comparación con UT5 y UT9 — celda `[19]` (0:30)

> **Mostrar:** la tabla comparativa y el bloque de conclusión que viene justo después.

«La tabla compara con los cinco modelos clásicos de UT5 y el XGBoost de UT9. La red queda en R² 0.8274, prácticamente empatada con el Decision Tree de UT5 (0.8275), y por debajo de todos los demás. La conclusión es la misma que ya saqué en UT9: en datasets tabulares pequeños las redes neuronales no superan a los modelos basados en árboles. El deep learning destaca con grandes volúmenes de datos o con datos no estructurados, que es lo que toca en UT12.»

---

## 2. CLASIFICACIÓN (4:00)

### 2.1 Preprocesamiento — celdas `[20]` a `[27]` (0:50)

> **Mostrar:** el bloque del head del dataset y los pasos de preprocesado.

«Para clasificación uso *Social Network Ads*: 400 usuarios, edad y salario estimado, y la etiqueta `Purchased`. Es el mismo dataset que en UT6 estaba con las columnas renombradas; aquí uso los nombres originales por coherencia con UT9.

La `[20]` lo descarga con `kagglehub`, la `[21]` lo carga, la `[22]` lo copia a `/content/`. La `[23]` muestra que el dataset tiene 5 columnas y la distribución 257 'no compra' / 143 'compra' — un desbalance leve.

La `[24]` confirma que no hay nulos. La `[25]` elimina `User ID` y `Gender` para quedarme con `Age` y `EstimatedSalary`, igual que hice en UT6 y UT9. Las `[26]` y `[27]` hacen el split 75/25 con `random_state=0` y estandarizan.»

### 2.2 Modelo y justificación — celda `[28]` (0:50)

> **Mostrar:** el `model.summary()` y la lista de bullets de justificación encima.

«Aquí la rúbrica pide justificar los parámetros, así que voy uno por uno:

Modelo `Sequential` con capas densas — encaja con datos tabulares. Dos capas ocultas de 16 y 8 neuronas, una pirámide decreciente más pequeña que en regresión, porque con solo 400 muestras una red más grande sobreajustaría enseguida. `ReLU` en las ocultas, como antes.

La salida es `Dense(1, sigmoid)`: clasificación binaria, una neurona con sigmoide me devuelve la probabilidad de compra entre 0 y 1. Función de coste `binary_crossentropy`, que es la que va con sigmoide en problemas binarios. Métrica `accuracy`. Optimizador `Adam` con el learning rate por defecto.»

### 2.3 Entrenamiento — celda `[29]` (0:20)

> **Mostrar:** rápidamente las épocas para que se vea que entrena.

«Mismo esquema que en regresión, pero con `patience=30` (más alta porque con tan pocas muestras la `val_loss` puede oscilar más) y batch_size 16. Como pasó en regresión, EarlyStopping tampoco cortó esta vez.»

### 2.4 Evaluación — celdas `[30]` y `[31]` (0:30)

> **Mostrar:** primero el output numérico de evaluate, luego el gráfico de accuracy y loss.

«La `[30]` aplica `model.evaluate` sobre el test y devuelve loss 0.2385 y **accuracy 0.93**.

La `[31]` dibuja la accuracy y la función de coste de train y validación a lo largo del entrenamiento, los dos elementos que pide la rúbrica para "evaluar el modelo".»

### 2.5 Pérdidas — celda `[32]` (0:20)

> **Mostrar:** la curva de pérdida y el print con la mejor época.

«Vuelvo a pintar la curva de pérdida marcando la mejor época en rojo. Otra vez 300 épocas completas sin que `EarlyStopping` cortase, pero las dos curvas están planas y casi tocándose, así que la red ha convergido bien.»

### 2.6 y 2.7 Guardar y cargar — celdas `[33]` a `[37]` (0:40)

> **Mostrar:** el `model.save`, el `load_model`, las métricas del modelo cargado, la matriz de confusión y el gráfico de líneas.

«La `[33]` guarda el modelo en formato `.keras`, que es un ZIP con la arquitectura, los pesos y el optimizador, todo en 27 KB.

En la `[34]` lo cargo con `load_model`. La `[35]` predice sobre el test con ese modelo cargado y devuelve **accuracy 0.93, precision 0.88, recall 0.91 y F1 0.89** — las mismas métricas que el modelo en memoria, lo que confirma que el ciclo guardado-carga funciona.

La `[36]` muestra la matriz de confusión: 64 'no compra' bien clasificadas, 4 falsos positivos, 3 falsos negativos y 29 'compra' bien clasificadas. La `[37]` lo grafica con líneas, ordenado por valor real, para que se aprecien los pocos errores.»

### 2.8 Comparación con UT6 y UT9 — celda `[38]` (0:30)

> **Mostrar:** la tabla comparativa final y la conclusión.

«La tabla compara accuracy, precision, recall y F1 con los siete clásicos de UT6 y los dos modelos de UT9. La red queda con accuracy 0.93 y F1 0.89, prácticamente empatada con KNN-k5 y SVM-RBF, y por debajo de XGBoost y FLAML de UT9 que llegan al 0.94. Igual que en regresión: la red no mejora a los clásicos, los iguala.»

---

## 3. Cierre (0:30)

> **Mostrar:** la conclusión final del notebook.

«Las dos partes confirman lo mismo: en problemas tabulares pequeños las redes neuronales no superan a los modelos basados en árboles. El deep learning destaca cuando hay datos no estructurados o grandes volúmenes, que es justo lo que toca en UT12 con redes convolucionales. Gracias.»

---

## Antes de grabar

- Notebook ejecutado de principio a fin con todos los outputs visibles.
- En la cabecera el placeholder `<URL del vídeo de defensa>` lo dejas como está hasta que tengas el enlace, y luego lo sustituyes.
- Resolución de pantalla mínima 1920×1080 para que se lea el código.
- Prueba el micro grabando 10 segundos y escuchándote.
- Si te equivocas, sigue: cortas en post o regrabas el bloque entero.

## Subida del vídeo

1. YouTube como **No listado** (público con enlace, no aparece en búsquedas).
2. Pega el enlace en la celda de cabecera del Colab donde dice `*<URL del vídeo de defensa>*`.
3. Guarda el notebook (`Ctrl+S`).
4. Sube `UT11_autor_XXXXXXXXX.ipynb` a la plataforma. Los datasets se descargan automáticamente al ejecutarlo, no hace falta adjuntarlos.
