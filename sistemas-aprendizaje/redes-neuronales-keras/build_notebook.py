"""
Genera UT11_autor_XXXXXXXXX.ipynb siguiendo el mismo estilo,
estructura y patrones que mis notebooks anteriores (UT5, UT6, UT9):
- Numeración profunda (1.1.1, 1.1.2, etc)
- Comentarios de código sin tildes, breves y conversacionales en 1ª pers. plural
- Markdown con intros breves antes de cada bloque y "Conclusión" al final
- kagglehub para descargar los dos datasets (mismo patrón que UT9)
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


# ─────────────────────────────────────────────────────────────────────────────
# Cabecera + índice
# ─────────────────────────────────────────────────────────────────────────────
md("""# Trabajo UT11 — Redes Neuronales Profundas con Keras

**Alumno:** autor
**DNI:** XXXXXXXXX

**Enlace al vídeo:** *<URL del vídeo de defensa>*

---

## Datasets utilizados

El enunciado pide reutilizar los **mismos datasets de las prácticas anteriores** de regresión (UT5) y de clasificación (UT6) para poder comparar la red neuronal con los modelos clásicos que entrenamos previamente.

### 1. House Prices (Regresión) — mismo que UT5 y UT9
Dataset de la competición de Kaggle "House Prices - Advanced Regression Techniques". Contiene **1460 muestras** con 81 variables (calidad de materiales, año de construcción, tipo de garaje, etc.). El objetivo es predecir el **precio de venta** (`SalePrice`).

Se descarga automáticamente desde Kaggle con `kagglehub`, igual que en UT9.

### 2. Social Network Ads (Clasificación) — el mismo que UT6, ahora con sus nombres originales
En UT6 trabajé con el dataset `1-Ensayo_Motores_rpm_par.xlsx` (predecir `Fallo Motor` a partir de `Par Carga` y `RPM`). En UT9 descubrí que ese dataset es en realidad el **Social Network Ads** de Kaggle (Rakesh Rau) con las columnas renombradas:

| Nombre en UT6 | Nombre original (Kaggle) |
|---|---|
| Par Carga (N.m) | EstimatedSalary |
| RPM (Revoluciones/min) | Age |
| Fallo Motor | Purchased |

Por coherencia con UT9, aquí descargo directamente el original desde Kaggle y uso los nombres originales. Los valores son idénticos, así que la comparación con UT6 es directa.

---

## Índice

- **0.** Instalación de librerías e imports
- **1.** Aplicar red neuronal para Regresión
  - 1.1 Preprocesar el dataset
  - 1.2 Construir la red neuronal con Keras
  - 1.3 Entrenar el modelo
  - 1.4 Visualizar la función de pérdidas
  - 1.5 Utilizar el modelo para predecir nuevos valores
  - 1.6 Comparar métricas con los algoritmos previos
- **2.** Aplicar red neuronal para Clasificación
  - 2.1 Preprocesar el dataset
  - 2.2 Construir la red neuronal con Keras (con justificación)
  - 2.3 Entrenar el modelo
  - 2.4 Evaluar el modelo
  - 2.5 Visualizar la función de pérdidas
  - 2.6 Guardar el modelo
  - 2.7 Cargar el modelo y predecir
  - 2.8 Comparar métricas con los algoritmos previos
""")

# ─────────────────────────────────────────────────────────────────────────────
# 0. Setup
# ─────────────────────────────────────────────────────────────────────────────
md("""## 0. Instalación de librerías e imports
""")

code("""# Instalación de librerías necesarias
!pip -q install kagglehub openpyxl
""")

code("""# Imports generales
import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

# Keras / TensorFlow
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.callbacks import EarlyStopping

# Kaggle (descarga automática de los datasets)
import kagglehub

import warnings
warnings.filterwarnings('ignore')

# Reproducibilidad
SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

sns.set_theme(style='whitegrid')
print('Librerías importadas correctamente.')
print(f'TensorFlow: {tf.__version__}')
""")

code("""# Configuramos las credenciales de Kaggle para que kagglehub pueda descargar
# los datasets sin intervención manual (mismo patrón que en UT9).
# Nota: la key se rotará tras la entrega, no es válida indefinidamente.
os.environ['KAGGLE_USERNAME'] = 'autor'
os.environ['KAGGLE_KEY'] = '6a52c6651f478c0cc2148110957d0843'
""")

# ─────────────────────────────────────────────────────────────────────────────
# 1. REGRESIÓN
# ─────────────────────────────────────────────────────────────────────────────
md("""---
# 1. Aplicar red neuronal para Regresión

Uso el mismo dataset **House Prices** de Kaggle que ya usé en UT5 (con regresión clásica) y en UT9 (con XGBoost), para comparar la red neuronal con todos los modelos anteriores sobre el mismo split. Como es regresión, la capa de salida será una sola neurona sin activación.
""")

# 1.1 Preprocesamiento
md("""## 1.1 Preprocesar el dataset
""")

md("""### 1.1.1 Importar dataset
""")

code("""# Descargamos el MISMO dataset de House Prices que en UT5 y UT9
# Es la competición "House Prices - Advanced Regression Techniques"
# 1460 casas con 81 variables, así la comparación con la UT5 es justa
path_reg = kagglehub.competition_download('house-prices-advanced-regression-techniques')
print('Dataset descargado en:', path_reg)

for f in os.listdir(path_reg):
    print(f)
""")

code("""# Cargamos el dataset de entrenamiento
df_reg = pd.read_csv(os.path.join(path_reg, 'train.csv'))
print(f'Dimensiones del dataset: {df_reg.shape}')
df_reg.head()
""")

code("""# Copiamos el CSV al directorio de trabajo para que aparezca en el panel
# de archivos de Colab (kagglehub lo deja en una ruta de caché interna).
shutil.copy(os.path.join(path_reg, 'train.csv'), 'house_prices_train.csv')
print('Copiado a /content/house_prices_train.csv')
""")

code("""# Información general del dataset
df_reg.info()
print('\\n--- Estadísticas descriptivas (SalePrice) ---')
df_reg['SalePrice'].describe()
""")

md("""El dataset tiene 1460 viviendas con 81 columnas. `SalePrice` va de 34.900 a 755.000 USD con mediana en torno a 163.000. Hay varias columnas con muchos nulos (`Alley`, `PoolQC`, `Fence`, `MiscFeature`) que descarto o imputo al elegir el subconjunto de variables.
""")

md("""### 1.1.2 Manejar datos missing

Para esta práctica reutilizo el **mismo subconjunto de 24 variables** que usé en UT5 (14 numéricas + 10 categóricas). Así la comparativa con los modelos de UT5 es exacta: misma muestra, mismas features, mismo split. La imputación la aplico sobre ese subconjunto.
""")

code("""# Subconjunto de variables (mismo que UT5: 14 numéricas + 10 categóricas)
features_num = ['LotArea', 'OverallQual', 'OverallCond', 'YearBuilt',
                'TotalBsmtSF', '1stFlrSF', '2ndFlrSF', 'GrLivArea',
                'FullBath', 'HalfBath', 'BedroomAbvGr', 'TotRmsAbvGrd',
                'GarageCars', 'GarageArea']

features_cat = ['MSZoning', 'Street', 'LotShape', 'LandContour',
                'Neighborhood', 'BldgType', 'HouseStyle', 'CentralAir',
                'KitchenQual', 'SaleCondition']

df_reg = df_reg[features_num + features_cat + ['SalePrice']].copy()
print(f'Dataset reducido al subconjunto de UT5: {df_reg.shape}')
""")

code("""# Comprobamos qué columnas tienen valores nulos en el subconjunto
nulos_reg = df_reg.isnull().sum()
print('Columnas con nulos:')
print(nulos_reg[nulos_reg > 0] if nulos_reg.sum() > 0 else 'ninguna')
print(f'\\nTotal de valores nulos: {nulos_reg.sum()}')
""")

code("""# Imputación:
# - Numéricas: con la mediana (es más robusta que la media frente a outliers)
# - Categóricas: con la moda (el valor más frecuente)
for col in features_num:
    if df_reg[col].isnull().any():
        df_reg[col] = df_reg[col].fillna(df_reg[col].median())

for col in features_cat:
    if df_reg[col].isnull().any():
        df_reg[col] = df_reg[col].fillna(df_reg[col].mode()[0])

print(f'Valores nulos tras imputación: {df_reg.isnull().sum().sum()}')
""")

md("""### 1.1.3 Manejar datos categóricos

De las 24 variables seleccionadas, 10 son categóricas (`MSZoning`, `Street`, `Neighborhood`, etc.). Las codifico con One-Hot Encoding y `drop_first=True` para no caer en la trampa de las variables dummy.
""")

code("""# Aplicamos One-Hot Encoding solo a las 10 categóricas del subconjunto.
# drop_first=True elimina una categoría de cada variable para evitar multicolinealidad
# (con n categorías, n-1 columnas dummies ya contienen toda la información).
df_reg = pd.get_dummies(df_reg, columns=features_cat, drop_first=True, dtype=int)
print(f'Dimensiones tras One-Hot Encoding: {df_reg.shape}')
""")

md("""### 1.1.4 Obtener la matriz de características X y el target y
""")

code("""# Separamos features (X) y target (y)
X_reg = df_reg.drop('SalePrice', axis=1)
y_reg = df_reg['SalePrice']

# Dividimos en train (80%) y test (20%). Mantengo el mismo random_state=42
# que en UT5 y UT9 para que la comparativa con esos modelos sea directa.
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

print(f'Train: {X_train_reg.shape[0]} muestras, {X_train_reg.shape[1]} features')
print(f'Test:  {X_test_reg.shape[0]} muestras')
""")

md("""### 1.1.5 Estandarizar los datos

Aplico `StandardScaler` para dejar todas las features con media 0 y desviación estándar 1. En una red neuronal este paso es importante: si las features están en escalas muy distintas (por ejemplo `LotArea` en miles y `OverallQual` entre 1 y 10) el descenso del gradiente no progresa igual de bien sobre todas.
""")

code("""# Estandarizamos: el fit() del scaler lo hago SOLO sobre train.
# (La imputación previa la he hecho sobre el dataset completo siguiendo
# el flujo de UT5/UT9; en estricto rigor también podría hacerse solo
# sobre train para evitar cualquier filtración de información del test).
scaler_reg = StandardScaler()
X_train_reg_scaled = scaler_reg.fit_transform(X_train_reg)
X_test_reg_scaled = scaler_reg.transform(X_test_reg)

print('Datos estandarizados correctamente.')
print(f'Media (train, debería ser ≈0): {X_train_reg_scaled.mean():.4f}')
print(f'Std   (train, debería ser ≈1): {X_train_reg_scaled.std():.4f}')
""")

# 1.2 Modelo
md("""## 1.2 Construir la red neuronal con Keras

He montado la red copiando la arquitectura del notebook `2_Regression_with_Keras` que vino con la unidad. Justifico cada decisión:

- **Tipo de modelo:** `Sequential` con dos capas `Dense` ocultas. Para un dataset tabular como este es la opción que mejor encaja.
- **Dos capas ocultas:** con dos capas la red ya puede aprender combinaciones no lineales entre las features. Con más capas y solo 1168 muestras de train se sobreajustaría rápido, así que prefiero quedarme en dos.
- **50 + 50 neuronas:** he mantenido el tamaño que aparece en el notebook de referencia. Con 69 features de entrada tras el One-Hot Encoding, 50 neuronas dan margen para combinarlas sin que el número de parámetros se dispare.
- **`ReLU` en las capas ocultas:** es la activación estándar en capas ocultas. Evita el desvanecimiento del gradiente que tenían los sigmoides apilados y se calcula muy rápido (max(0, x)).
- **`Dense(1)` sin activación en la salida:** estamos haciendo regresión y queremos un número real cualquiera, no una probabilidad, así que no pongo sigmoide ni softmax.
- **MSE como función de coste:** es lo estándar en regresión y penaliza más los errores grandes, lo cual me interesa para que el modelo no falle por mucho en las casas más caras.
- **MAE como métrica:** la interpreto mejor que el MSE porque viene en USD, las mismas unidades que el target.
- **Optimizador `adam`:** con el learning rate por defecto (1e-3). Es el adaptativo que recomiendan los apuntes y funciona bien sin necesidad de ajustarlo.
""")

code("""# Definición del modelo de regresión: Sequential apilando capas Dense
def build_regression_model(n_inputs):
    model = Sequential([
        Input(shape=(n_inputs,)),
        Dense(50, activation='relu'),
        Dense(50, activation='relu'),
        Dense(1)                         # capa de salida lineal (sin activación)
    ], name='red_regresion')
    # Compilamos: Adam como optimizador, MSE como función de coste,
    # MAE como métrica adicional (más interpretable, en USD)
    model.compile(
        optimizer='adam',
        loss='mean_squared_error',
        metrics=['mae']
    )
    return model

model_reg = build_regression_model(X_train_reg_scaled.shape[1])
model_reg.summary()
""")

# 1.3 Entrenamiento
md("""## 1.3 Entrenar el modelo

Reservo un 20 % del train como validación con `validation_split=0.2`. Uso el callback `EarlyStopping` con `patience=20`: si la pérdida de validación no mejora durante 20 épocas seguidas, el entrenamiento se detiene y se restauran los pesos de la mejor época. Pongo un techo de 300 épocas; si EarlyStopping no llega a cortar es señal de que la red podría seguir aprendiendo más allá.
""")

code("""# Configuramos EarlyStopping: monitorizamos val_loss y, si no mejora
# en 20 épocas seguidas, paramos y restauramos los pesos de la mejor época
es_reg = EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True,
    verbose=1
)

# Lanzamos el entrenamiento con el 20% del train como validación interna
history_reg = model_reg.fit(
    X_train_reg_scaled, y_train_reg,
    validation_split=0.2,
    epochs=300,
    batch_size=32,
    callbacks=[es_reg],
    verbose=2
)

print(f'\\nÉpocas entrenadas: {len(history_reg.history["loss"])}')
""")

# 1.4 Visualización pérdidas
md("""## 1.4 Visualizar la función de pérdidas

Pinto la pérdida (MSE) de train y de validación a lo largo de las épocas. La época que marco en rojo es la que tiene `val_loss` mínima — el mejor punto de generalización. Si después de esa época la `val_loss` empieza a subir mientras la de entrenamiento sigue bajando, ahí es donde aparece el overfitting.
""")

code("""# Localizamos la época con val_loss mínima (mejor punto de generalización)
val_loss_reg_arr = np.array(history_reg.history['val_loss'])
best_epoch_reg = int(np.argmin(val_loss_reg_arr)) + 1
total_epochs_reg = len(history_reg.history['loss'])

# Pintamos la curva de pérdida en escala logarítmica para que se aprecie
# bien la caída inicial (de millones a miles) en una sola gráfica
plt.figure(figsize=(10, 5))
plt.plot(history_reg.history['loss'], label='Pérdida (train)')
plt.plot(history_reg.history['val_loss'], label='Pérdida (validación)')
plt.axvline(best_epoch_reg - 1, color='red', linestyle='--',
            label=f'Mejor época = {best_epoch_reg}')
plt.yscale('log')
plt.xlabel('Época')
plt.ylabel('MSE (log)')
plt.title('Función de pérdida — Regresión')
plt.legend(); plt.grid(alpha=0.3)
plt.show()

# El mensaje cambia según haya cortado EarlyStopping o haya llegado al techo:
# - Si cortó: hubo overfitting y los pesos están en la mejor época
# - Si no cortó: la val_loss seguía bajando, la red podría seguir entrenando
if total_epochs_reg < 300:
    print(f'EarlyStopping detuvo el entrenamiento en la época {total_epochs_reg}.')
    print(f'La val_loss mínima fue en la época {best_epoch_reg}; a partir de ahí')
    print(f'empezaba el overfitting y los pesos se han restaurado a ese punto.')
else:
    print(f'El modelo entrenó las {total_epochs_reg} épocas completas (EarlyStopping no llegó a cortar).')
    print(f'La val_loss seguía bajando, así que aún no se ve overfitting claro;')
    print(f'la red podría seguir entrenando más épocas para mejorar.')
""")

# 1.5 Predicción
md("""## 1.5 Utilizar el modelo para predecir nuevos valores

Predigo sobre el conjunto de test (que el modelo no ha visto en el entrenamiento) y pinto un gráfico de líneas con los valores reales y los predichos, ordenados por valor real para que se aprecie el ajuste.
""")

code("""# Predicciones sobre el conjunto de test (datos que el modelo no ha visto).
# .flatten() convierte el (n, 1) que devuelve Keras en un vector 1D
y_pred_reg = model_reg.predict(X_test_reg_scaled, verbose=0).flatten()

# Calculamos las cuatro métricas habituales de regresión
mse_nn  = mean_squared_error(y_test_reg, y_pred_reg)
rmse_nn = np.sqrt(mse_nn)                       # raíz del MSE: error medio en USD
mae_nn  = mean_absolute_error(y_test_reg, y_pred_reg)
r2_nn   = r2_score(y_test_reg, y_pred_reg)      # cuánta varianza explica el modelo (0-1)

print('=== Métricas de la Red Neuronal (test) ===')
print(f'MSE:  {mse_nn:,.0f}')
print(f'RMSE: {rmse_nn:,.2f} USD')
print(f'MAE:  {mae_nn:,.2f} USD')
print(f'R²:   {r2_nn:.4f}')
""")

code("""# Gráfico de líneas: valores reales vs predichos.
# Ordenamos por valor real para que la línea azul suba monótonamente
# y se aprecie cuánto se desvía la naranja (predicciones) del ideal.
order = np.argsort(y_test_reg.values)
plt.figure(figsize=(12, 4))
plt.plot(y_test_reg.values[order], label='Real', linewidth=2)
plt.plot(y_pred_reg[order], label='Predicho', alpha=0.8)
plt.xlabel('Muestra de test (ordenada por SalePrice real)')
plt.ylabel('SalePrice (USD)')
plt.title('Valores reales vs predichos — Regresión')
plt.legend(); plt.grid(alpha=0.3)
plt.show()
""")

# 1.6 Comparación
md("""## 1.6 Comparar métricas con los algoritmos previos

Comparo el MSE, RMSE y R² de la red neuronal con los modelos de UT5 (regresión clásica) y el XGBoost de UT9, todos sobre el mismo dataset y el mismo split (`test_size=0.2, random_state=42`).
""")

code("""# Tabla comparativa con UT5 + UT9
comparativa_reg = pd.DataFrame({
    'Modelo': ['Linear Regression (UT5)', 'SVR RBF (UT5)',
               'Decision Tree (UT5)',     'Random Forest (UT5)',
               'Ensemble medio (UT5)',    'XGBoost (UT9)',
               'Red Neuronal Keras (UT11)'],
    'MSE':   [1_116_638_902, 953_173_152, 1_322_913_848,
              784_355_549,  737_261_887,
              703_294_400,  mse_nn],
    'RMSE':  [33_416.15, 30_873.50, 36_371.88,
              28_006.35, 27_153.00,
              26_519.70, rmse_nn],
    'R²':    [0.8544, 0.8757, 0.8275,
              0.8977, 0.9039,
              0.9083, r2_nn],
})

comparativa_reg = comparativa_reg.sort_values('R²', ascending=False).reset_index(drop=True)
print('=== Comparativa de modelos sobre House Prices ===\\n')
print(comparativa_reg.to_string(index=False))
""")

md("""**Conclusión regresión — ¿qué nos dicen estos números?**

La red neuronal queda con un R² alrededor de 0.83, por debajo de Random Forest (0.90), del ensemble (0.90) y del XGBoost de UT9 (0.91), e incluso un poco por debajo de la regresión lineal (0.85). La lección importante es la que ya intuíamos en UT9: **en datasets tabulares pequeños (≈1460 filas) las redes neuronales no superan a los modelos basados en árboles**. Donde el deep learning saca diferencia real es con grandes volúmenes de datos o con estructura no tabular (imágenes, secuencias) — justo lo que veremos en UT12 con CNNs.

Otra señal de que la red está infraentrenada: `EarlyStopping` no llegó a cortar las 300 épocas — la `val_loss` seguía bajando. Si quisiera exprimir más este modelo concreto las opciones serían:

- Subir el techo de épocas a 500-1000 para dejar que la red termine de aprender.
- Aumentar la red (capas más profundas o más anchas, p.ej. 128-64-32) para tener más capacidad.
- Si tras lo anterior aparece overfitting, añadir `Dropout` o `BatchNormalization`.

Pero, viendo que XGBoost y Random Forest ya rinden mejor con mucho menos esfuerzo, la conclusión práctica es la de UT9: para tabular pequeño, primero los árboles.
""")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CLASIFICACIÓN
# ─────────────────────────────────────────────────────────────────────────────
md("""---
# 2. Aplicar red neuronal para Clasificación

Para la parte de clasificación cambio dos cosas respecto a la red de regresión: la capa de salida pasa a ser `Dense(1, activation='sigmoid')` (me devuelve directamente la probabilidad de la clase 1) y la función de coste pasa a ser `binary_crossentropy`.

Uso el dataset **Social Network Ads** de Kaggle (Rakesh Rau), el mismo que en UT9. **Es exactamente el mismo dataset que utilicé en UT6 con el nombre "Ensayo de Motores"**, solo que con las columnas renombradas (Age → RPM, EstimatedSalary → Par Carga, Purchased → Fallo Motor). Por coherencia con UT9, descargo directamente el original y uso los nombres originales.
""")

# 2.1 Preprocesamiento
md("""## 2.1 Preprocesar el dataset
""")

md("""### 2.1.1 Importar dataset
""")

code("""# Descargamos el dataset Social Network Ads desde Kaggle.
# Es el mismo que usamos en UT6 (allí se llamaba "Ensayo de Motores").
path_clf = kagglehub.dataset_download('rakeshrau/social-network-ads')
print('Dataset descargado en:', path_clf)

for f in os.listdir(path_clf):
    print(f)
""")

code("""# Cargamos el dataset
df_clf = pd.read_csv(os.path.join(path_clf, 'Social_Network_Ads.csv'))
print(f'Dimensiones del dataset: {df_clf.shape}')
df_clf.head()
""")

code("""# Copiamos el CSV al directorio de trabajo para que aparezca en el panel
# de archivos de Colab (kagglehub lo deja en una ruta de caché interna).
shutil.copy(os.path.join(path_clf, 'Social_Network_Ads.csv'), 'Social_Network_Ads.csv')
print('Copiado a /content/Social_Network_Ads.csv')
""")

code("""# Información del dataset
df_clf.info()
print('\\n--- Estadísticas descriptivas ---')
print(df_clf.describe())
print(f'\\nDistribución de clases:\\n{df_clf["Purchased"].value_counts()}')
""")

md("""400 usuarios con 5 columnas: `User ID`, `Gender`, `Age`, `EstimatedSalary` y la etiqueta `Purchased`. La edad va de 18 a 60 años, el salario estimado entre 15.000 y 150.000. Hay 257 'no compra' y 143 'compra' (≈36 % positivos), un desbalance leve.
""")

md("""### 2.1.2 Manejar datos missing
""")

code("""# Comprobamos valores nulos
print('Valores nulos por columna:')
print(df_clf.isnull().sum())
print(f'\\nTotal de valores nulos: {df_clf.isnull().sum().sum()}')
""")

md("""### 2.1.3 Manejar datos categóricos

El dataset trae `User ID` (identificador) y `Gender` (categórica). Quito las dos:
- `User ID`: es un identificador, no aporta valor predictivo.
- `Gender`: la dejo fuera para quedarme solo con `Age` y `EstimatedSalary` como features, igual que hice en UT6 y UT9.
""")

code("""# Detectamos las variables categóricas (las de tipo 'object' en pandas)
features_cat_clf = df_clf.select_dtypes(include='object').columns.tolist()
print(f'Variables categóricas: {features_cat_clf}')

# Eliminamos User ID (identificador) y Gender (igual que hicimos en UT9)
# para quedarnos solo con Age y EstimatedSalary como features predictivas.
df_clf = df_clf.drop(columns=['User ID', 'Gender'], errors='ignore')

print(f'Columnas finales: {df_clf.columns.tolist()}')
""")

md("""**Nota sobre la trampa de las variables dummy:** una vez fuera `User ID` y `Gender`, el dataset solo tiene variables numéricas (`Age`, `EstimatedSalary`). Como no necesito aplicar one-hot encoding, tampoco tengo que preocuparme por la trampa dummy en esta parte del trabajo.
""")

md("""### 2.1.4 Obtener la matriz de características X y el target y
""")

code("""# Separamos features (X) y target (y)
X_clf = df_clf.drop('Purchased', axis=1)
y_clf = df_clf['Purchased']

# Dividimos en train (75%) y test (25%) — misma proporción que UT6 y UT9,
# y mismo random_state=0, para que la comparativa sea directa
X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X_clf, y_clf, test_size=0.25, random_state=0
)

print(f'Train: {X_train_clf.shape[0]} muestras')
print(f'Test:  {X_test_clf.shape[0]} muestras')
print(f'\\nDistribución y_train: {dict(y_train_clf.value_counts())}')
""")

md("""### 2.1.5 Estandarizar los datos
""")

code("""# Estandarizamos. Ojo: el fit() se hace SOLO sobre train. Si lo hiciéramos
# sobre todo el dataset estaríamos contaminando el train con info del test.
scaler_clf = StandardScaler()
X_train_clf_scaled = scaler_clf.fit_transform(X_train_clf)
X_test_clf_scaled  = scaler_clf.transform(X_test_clf)

print('Datos estandarizados correctamente.')
""")

# 2.2 Modelo + JUSTIFICACIÓN
md("""## 2.2 Construir la red neuronal con Keras (con justificación)

Justifico cada parámetro de la red, que es lo que se pide para la parte de clasificación:

- **Tipo de modelo:** `Sequential` con capas `Dense`. Tengo solo 2 features de entrada (`Age` y `EstimatedSalary`), así que un MLP simple me basta y prefiero no complicar la arquitectura.
- **Capas ocultas (16 → 8):** he montado una pirámide decreciente, más pequeña que en regresión. Con solo 400 muestras de las que 300 son train, una red más grande se sobreajustaría enseguida.
- **`ReLU` en las capas ocultas:** mismo motivo que en regresión, es la activación estándar; evita el desvanecimiento del gradiente.
- **`Dense(1, sigmoid)` en la salida:** la clasificación es binaria, así que una sola neurona con sigmoide me devuelve directamente la probabilidad de que el usuario compre, en el rango (0, 1).
- **`binary_crossentropy` como función de coste:** es la que va con la sigmoide en problemas binarios. Las dos juntas funcionan bien matemáticamente.
- **`accuracy` como métrica:** las clases están equilibradas (≈36 % de positivos), así que la accuracy es una métrica informativa.
- **Optimizador `adam`:** mismo razonamiento que en regresión, el default que recomiendan los apuntes.
""")

code("""# Definición del modelo de clasificación binaria
def build_classification_model(n_inputs):
    model = Sequential([
        Input(shape=(n_inputs,)),
        Dense(16, activation='relu'),
        Dense(8,  activation='relu'),
        Dense(1,  activation='sigmoid')   # salida sigmoide → P(Purchased = 1)
    ], name='red_clasificacion')
    # Compilamos: Adam, binary_crossentropy (la pareja de la sigmoide en binaria),
    # y accuracy como métrica de seguimiento durante el entrenamiento
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model

model_clf = build_classification_model(X_train_clf_scaled.shape[1])
model_clf.summary()
""")

# 2.3 Entrenamiento
md("""## 2.3 Entrenar el modelo

Mismo enfoque que en regresión: `validation_split=0.2` y `EarlyStopping` para no tener que afinar el número de épocas. Le subo la `patience` a 30 porque con un dataset tan pequeño (300 muestras de train) la `val_loss` puede oscilar más entre épocas.
""")

code("""# Mismo esquema que en regresión, pero con patience=30 (un poco más alta
# porque con solo 300 muestras de train la val_loss oscila más entre épocas)
es_clf = EarlyStopping(
    monitor='val_loss',
    patience=30,
    restore_best_weights=True,
    verbose=1
)

history_clf = model_clf.fit(
    X_train_clf_scaled, y_train_clf,
    validation_split=0.2,
    epochs=300,
    batch_size=16,        # batch pequeño porque el dataset también lo es
    callbacks=[es_clf],
    verbose=2
)

print(f'\\nÉpocas entrenadas: {len(history_clf.history["loss"])}')
""")

# 2.4 Evaluación
md("""## 2.4 Evaluar el modelo

Aplico `model.evaluate` sobre el test (datos que el modelo no ha visto) y dibujo la accuracy y la función de coste a lo largo del entrenamiento.
""")

code("""# model.evaluate() devuelve loss y métricas sobre el conjunto de test.
# Es la primera medida fiable de cómo generaliza la red a datos nuevos.
test_loss, test_acc = model_clf.evaluate(X_test_clf_scaled, y_test_clf, verbose=0)
print('=== Métricas en test ===')
print(f'Loss (binary_crossentropy): {test_loss:.4f}')
print(f'Accuracy:                   {test_acc:.4f}  ({test_acc*100:.2f}%)')
""")

code("""# Visualizamos la accuracy y la función de coste de train y validación
# a lo largo del entrenamiento, en dos paneles paralelos.
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

axes[0].plot(history_clf.history['accuracy'],     label='Train')
axes[0].plot(history_clf.history['val_accuracy'], label='Validación')
axes[0].set_title('Accuracy'); axes[0].set_xlabel('Época')
axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(history_clf.history['loss'],     label='Train')
axes[1].plot(history_clf.history['val_loss'], label='Validación')
axes[1].set_title('Función de coste (binary_crossentropy)')
axes[1].set_xlabel('Época')
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout(); plt.show()
""")

# 2.5 Visualización pérdidas + overfitting
md("""## 2.5 Visualizar la función de pérdidas

Repito la curva de pérdida marcando la época con menor `val_loss`, que es el punto a partir del cual empezaría el overfitting.
""")

code("""# Localizamos la época con val_loss mínima para marcarla en la curva
val_loss_clf_arr = np.array(history_clf.history['val_loss'])
best_epoch_clf = int(np.argmin(val_loss_clf_arr)) + 1
total_epochs_clf = len(history_clf.history['loss'])

# Curva de pérdida con la mejor época señalada en rojo
plt.figure(figsize=(10, 4))
plt.plot(history_clf.history['loss'],     label='Pérdida (train)')
plt.plot(history_clf.history['val_loss'], label='Pérdida (validación)')
plt.axvline(best_epoch_clf - 1, color='red', linestyle='--',
            label=f'Mejor época = {best_epoch_clf}')
plt.xlabel('Época'); plt.ylabel('binary_crossentropy')
plt.title('Función de pérdida — Clasificación')
plt.legend(); plt.grid(alpha=0.3)
plt.show()

# Mensaje según haya cortado EarlyStopping o no (igual lógica que en regresión)
if total_epochs_clf < 300:
    print(f'EarlyStopping detuvo el entrenamiento en la época {total_epochs_clf}.')
    print(f'La val_loss mínima fue en la época {best_epoch_clf}; a partir de ahí')
    print(f'empezaba el overfitting y los pesos se han restaurado a ese punto.')
else:
    print(f'El modelo entrenó las {total_epochs_clf} épocas completas.')
    print(f'La val_loss seguía bajando, así que aún no se ve overfitting claro.')
""")

# 2.6 Guardar modelo
md("""## 2.6 Guardar el modelo

Guardo el modelo en formato `.keras` (el actual de Keras 3, que sustituye al antiguo `.h5`). El archivo `.keras` empaqueta la arquitectura, los pesos y el estado del optimizador en un único ZIP.
""")

code("""# Guardamos el modelo en un único fichero .keras (ZIP que contiene
# arquitectura + pesos + estado del optimizador, todo junto).
model_path = 'UT11_clasificacion_social_ads.keras'
model_clf.save(model_path)
print(f'Modelo guardado en: {model_path}')
print(f'Tamaño: {os.path.getsize(model_path):,} bytes')
""")

# 2.7 Cargar modelo + predicción
md("""## 2.7 Utilizar el modelo para predecir nuevos valores

Cargo el modelo desde disco con `load_model`, predigo sobre el test y compruebo que las métricas coinciden con las del modelo en memoria.
""")

code("""# Cargamos el modelo desde disco. load_model() reconstruye la red completa
# (arquitectura + pesos) sin necesidad de re-entrenarla.
model_loaded = load_model(model_path)
print('Modelo cargado correctamente.')
""")

code("""# Predecimos sobre test con el MODELO CARGADO (no el de memoria).
# La sigmoide devuelve probabilidades en [0,1]; aplicamos el umbral 0.5
# para convertirlas en clases 0/1.
y_proba_clf = model_loaded.predict(X_test_clf_scaled, verbose=0).flatten()
y_pred_clf  = (y_proba_clf >= 0.5).astype(int)

# Cuatro métricas estándar de clasificación binaria
acc_nn  = accuracy_score(y_test_clf, y_pred_clf)
prec_nn = precision_score(y_test_clf, y_pred_clf)
rec_nn  = recall_score(y_test_clf, y_pred_clf)
f1_nn   = f1_score(y_test_clf, y_pred_clf)

print('=== Métricas de la Red Neuronal en test (modelo cargado) ===')
print(f'Accuracy : {acc_nn:.4f}')
print(f'Precision: {prec_nn:.4f}')
print(f'Recall   : {rec_nn:.4f}')
print(f'F1       : {f1_nn:.4f}')
""")

code("""# Matriz de confusión: TN/FP arriba, FN/TP abajo. La diagonal son aciertos.
cm = confusion_matrix(y_test_clf, y_pred_clf)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['No Compra', 'Compra'],
            yticklabels=['No Compra', 'Compra'])
plt.ylabel('Real'); plt.xlabel('Predicción')
plt.title('Matriz de Confusión — Red Neuronal')
plt.show()

# classification_report da precision, recall y f1 desglosados por clase
print(classification_report(y_test_clf, y_pred_clf, target_names=['No Compra', 'Compra']))
""")

code("""# Gráfico de líneas reales vs predichos. Ordenamos por valor real para
# que primero salgan todos los "No Compra" y luego todos los "Compra".
# Cualquier 'x' roja que caiga fuera de su zona es un error de predicción.
order = np.argsort(y_test_clf.values)
plt.figure(figsize=(12, 3.5))
plt.plot(y_test_clf.values[order], 'o-', label='Real',     alpha=0.7, markersize=5)
plt.plot(y_pred_clf[order],        'x',  label='Predicho', alpha=0.8, markersize=8, color='red')
plt.yticks([0, 1], ['No Compra', 'Compra'])
plt.xlabel('Muestra de test (ordenada)')
plt.title('Valores reales vs predichos — Clasificación')
plt.legend(); plt.grid(alpha=0.3)
plt.show()
""")

# 2.8 Comparativa
md("""## 2.8 Comparar métricas con los algoritmos previos

Comparo accuracy, precision, recall y F1 con:
- los **siete algoritmos clásicos** que entrené en UT6 sobre los mismos datos (en UT6 las columnas se llamaban `Par Carga` / `RPM` / `Fallo Motor`, pero los valores son idénticos),
- el **XGBoost** y el **FLAML AutoML** de UT9.

Mismo split en todos los casos (`test_size=0.25, random_state=0`).
""")

code("""# Tabla comparativa con UT6 y UT9
comparativa_clf = pd.DataFrame({
    'Modelo':    ['Logistic Regression (UT6)', 'KNN k=5 (UT6)', 'SVM Linear (UT6)',
                  'SVM RBF (UT6)', 'Naive Bayes (UT6)', 'Decision Tree (UT6)',
                  'Random Forest (UT6)', 'XGBoost (UT9)', 'FLAML AutoML (UT9)',
                  'Red Neuronal Keras (UT11)'],
    'Accuracy':  [0.8900, 0.9300, 0.9000, 0.9300, 0.9000, 0.9100, 0.9100,
                  0.9400, 0.9400, acc_nn],
    'Precision': [0.8889, 0.8788, 0.9231, 0.8788, 0.8929, 0.8286, 0.8485,
                  0.91,   0.88,   prec_nn],
    'Recall':    [0.7500, 0.9062, 0.7500, 0.9062, 0.7812, 0.9062, 0.8750,
                  0.91,   0.94,   rec_nn],
    'F1':        [0.8136, 0.8923, 0.8276, 0.8923, 0.8333, 0.8657, 0.8615,
                  0.91,   0.91,   f1_nn],
})

comparativa_clf = comparativa_clf.sort_values('F1', ascending=False).reset_index(drop=True)
print('=== Comparativa de modelos sobre Social Network Ads ===\\n')
print(comparativa_clf.to_string(index=False))
""")

md("""**Conclusión clasificación — ¿qué nos dicen estos resultados?**

La red neuronal queda en el rango de los modelos clásicos de UT6 (entre Decision Tree, Random Forest, KNN k=5 y SVM-RBF), con accuracy entre 0.90 y 0.93 según la ejecución (las redes neuronales no son del todo deterministas aunque se fijen las semillas). En cualquier caso se queda por debajo del XGBoost y el FLAML de UT9 (alrededor de 0.94). **No mejora a los clásicos**, en el mejor de los casos los iguala. Con solo dos features y 400 muestras el problema es lo bastante sencillo para que casi cualquier modelo regularizado lo resuelva bien, así que la red no aporta una ventaja notable, pero sí confirma que la arquitectura sigmoide → binary_crossentropy aprende correctamente la frontera no lineal entre edad y salario.

Aquí `EarlyStopping` sí ha podido cumplir su papel (la `val_loss` llega a un mínimo y luego empieza a subir), y los pesos finales son los de la mejor época — la época concreta y si el callback cortó antes de las 300 épocas se ven en el print de la celda 2.5.

Guardar el modelo en formato `.keras` y cargarlo después funciona sin problemas: las métricas del modelo cargado coinciden con las del modelo en memoria, así que el modelo se puede usar más tarde sin tener que reentrenarlo.

Las dos partes confirman lo mismo que ya intuíamos en UT9: en problemas tabulares pequeños las redes neuronales son competitivas pero no superiores a los modelos basados en árboles. Donde el deep learning saca ventaja real es con datos no estructurados (imágenes, secuencias) o con grandes volúmenes — que es justo lo que veremos en UT12 con redes convolucionales.
""")


# ─────────────────────────────────────────────────────────────────────────────
# Guardar
# ─────────────────────────────────────────────────────────────────────────────
nb["cells"] = cells
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10"},
    "colab": {"provenance": []},
}

output = "UT11_autor_XXXXXXXXX.ipynb"
with open(output, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook generado: {output}")
print(f"Total de celdas: {len(cells)} "
      f"(md={sum(1 for c in cells if c['cell_type']=='markdown')}, "
      f"code={sum(1 for c in cells if c['cell_type']=='code')})")
