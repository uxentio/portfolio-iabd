# GUION VIDEO - UT9 AutoML (max 10 minutos)

Abre el notebook YA EJECUTADO en Colab y ve scrolleando segun hablas.
Las celdas de codigo se identifican con In [X] que es el numero visible.
Las celdas markdown no tienen numero, se identifican por su titulo.

---

## INTRO (0:00 - 1:00)

**→ VE AL TITULO** — "Trabajo Final UT9 - Auto Machine Learning" (cabecera del notebook)

"Buenas, soy autor. Trabajo final de la UT9 sobre AutoML.

Uso los mismos datasets de las practicas anteriores: el House Prices de
Kaggle, el mismo de la UT5 con 1460 casas y 81 variables, y el Social
Network Ads para clasificacion, el mismo de la UT6. Este ultimo nos lo
dieron como Ensayo de Motores pero al buscarlo en Kaggle resulta que es
el Social Network Ads con las columnas renombradas.

Sobre AutoML uso FLAML en vez de auto-sklearn o PyCaret porque ninguno
funciona con Python 3.12 que es lo que trae Colab."

**→ VE A In [1]** — El pip install

"Aqui instalamos las librerias que necesitamos: xgboost, shap para la
interpretabilidad, kagglehub para descargar los datasets directamente
desde Kaggle, y flaml para el AutoML."

**→ VE A In [2]** — Los imports

"Los imports de siempre: pandas, numpy, matplotlib, seaborn, sklearn
para las metricas y el preprocesado, y xgboost."

---

## 1. XGBOOST REGRESION (1:00 - 3:15)

**→ SCROLLEA** por los titulos markdown "1.1 XGBoost para Regresión" y "1.1.1 Importar dataset"

(scrollea rapido, no hace falta pararse)

**→ VE A In [3]** — Sale: Descarga del dataset con kagglehub

"El dataset se descarga automaticamente desde Kaggle con mis credenciales.
Es la competicion House Prices Advanced Regression Techniques, exactamente
el mismo que usamos en la UT5."

**→ VE A In [4]** — Sale: Dimensiones del dataset: (1460, 81)

"Aqui vemos el dataset, 1460 casas con 81 variables. Tiene cosas como
la calidad general de la casa, la superficie habitable, el numero de
plazas de garaje, el año de construccion..."

**→ VE A In [5]** — Sale: df_reg.info() y estadisticas descriptivas

"Con info vemos los tipos de datos y con describe las estadisticas basicas.
Hay variables numericas y categoricas mezcladas."

**→ VE A In [6]** — Sale: los valores nulos por columna

"Tiene bastantes nulos, los rellenamos con mediana y moda."

**→ VE A In [7]** — Sale: Valores nulos tras imputación: 0

"Despues de imputar ya no queda ningun nulo."

**→ VE A In [8] y In [9]** — Sale: Variables categóricas (43) y el encoding

"Hay 43 variables categoricas. Las 4 binarias las paso a 0 y 1, y las
39 restantes con One-Hot Encoding con drop_first para evitar la trampa
de las variables dummy."

**→ VE A In [10]** — Sale: Train: 1168, Test: 292

"Separamos 80-20 en train y test."

**→ VE A In [11]** — Sale: Datos estandarizados

"Estandarizamos. Importante: el fit solo se hace sobre train para no
contaminar el test, eso es el data leakage."

**→ VE A In [12]** — Sale: Comparativa de hiperparámetros con los 3 resultados

"He probado 3 configuraciones con validacion cruzada. La conservadora
con 100 arboles y profundidad 3 da un R² de 0.85. La equilibrada con 200
arboles y profundidad 6 da un 0.83. Y la agresiva con 500 arboles y
profundidad 8 da un 0.82. Gana la conservadora, lo cual tiene sentido
porque con demasiada profundidad el modelo sobreajusta, se aprende los
datos de entrenamiento de memoria y luego falla con datos nuevos."

**→ VE A In [13] y In [14]** — Sale: R²=0.9083, RMSE=26519, y el grafico de puntos

"Con la mejor configuracion, el R² sale 0.91. En la UT5 el mejor modelo
era el ensemble con 0.90. O sea que XGBoost lo iguala e incluso lo supera
ligeramente, lo cual es logico porque XGBoost es precisamente un algoritmo
que combina arboles corrigiendo errores, que es la idea del gradient
boosting.

En el grafico vemos que los puntos estan bastante pegados a la linea roja.
En las casas mas caras se desvian mas, y esto es normal porque las casas
caras suelen tener algo especial que el modelo no puede capturar solo con
las variables del dataset."

---

## 2. XGBOOST CLASIFICACION (3:00 - 5:00)

**→ VE A In [15]** — Sale: Descarga del Social Network Ads desde Kaggle

"Igual que antes, se descarga automatico desde Kaggle."

**→ VE A In [16] y In [17]** — Sale: (400, 5) y la distribucion de clases

"400 usuarios, 5 columnas. Hay mas gente que no compra que la que si,
un desbalanceo moderado, por eso luego no nos fiamos solo de la exactitud."

**→ VE A In [18]** — Sale: 0 valores nulos

"No tiene valores nulos, asi que no hay que imputar nada."

**→ VE A In [19]** — Sale: Eliminamos User ID y Gender

"Quitamos User ID porque es un identificador sin valor predictivo, y
Gender para quedarnos con las mismas variables que usamos en la UT6."

**→ VE A In [20]** — Sale: Train: 300 muestras, Test: 100 muestras

"Dividimos 75-25, igual que en la UT6, para que la comparacion sea justa."

**→ VE A In [21]** — Sale: Datos estandarizados

"Estandarizamos, el fit solo en train para evitar data leakage."

**→ VE A In [22]** — Sale: las 3 configs, gana Conservador con 0.8833

"Otra vez 3 configuraciones. Aqui tambien gana la conservadora con un
0.88, muy parecida a las otras. Con un dataset tan simple, con solo 2
variables, no hace falta mucha profundidad."

**→ VE A In [23]** — Sale: la matriz de confusion azul

"En la matriz de confusion vemos los aciertos en la diagonal y los
fallos fuera. Los falsos negativos son clientes que si compraron pero
el modelo dijo que no. En marketing esos serian clientes a los que no
les habriamos mostrado publicidad."

**→ VE A In [25]** — Sale: la curva ROC

"La curva ROC se aleja bastante de la diagonal, el modelo ha aprendido
bien a distinguir compradores de no compradores."

**→ VE A In [26]** — Sale: la tabla y el grafico de barras

"Comparativa con la UT6: XGBoost saca un 0.94, mejor que KNN y SVM RBF
que daban 0.93. La mejora es pequena porque el dataset es muy simple,
pero ahi esta."

---

## 3. AUTOML CON FLAML (5:00 - 6:15)

**→ VE A In [27]** — Sale: FLAML importado correctamente

"Importamos FLAML, que significa Fast and Lightweight AutoML, o sea
AutoML rapido y ligero. Es de Microsoft Research."

**→ VE A In [28]** — Sale: Datos de entrenamiento y test

"Usamos los mismos datos ya preparados de la seccion anterior."

**→ VE A In [29]** — Sale: Mejor modelo: xgboost, con 5 arboles

"FLAML ha probado varios algoritmos durante 2 minutos: LightGBM, Random
Forest, XGBoost... y ha elegido XGBoost como el mejor, pero con solo 5
arboles y una configuracion muy diferente a la nuestra. Es interesante
porque nosotros usamos 100 arboles y FLAML ha encontrado que con 5 ya
basta para este dataset."

**→ VE A In [32]** — Sale: tabla comparativa y diferencias

"En la comparativa XGBoost manual y FLAML dan el mismo accuracy, 0.94.
Pero FLAML tiene mejor recall, 0.94 frente a 0.91, o sea que detecta
mas compradores reales. Los resultados son muy parecidos, lo cual tiene
sentido con un dataset tan pequeno. La gracia de AutoML es que en un
proyecto real con muchos datos, lo que a nosotros nos llevo varias
practicas, FLAML lo hace en 2 minutos."

---

## 4. VALORES SHAP (6:15 - 9:15)

**→ VE A In [30]** — Sale: Matriz confusión verde + reporte FLAML

"La matriz de confusion de FLAML y su reporte. Accuracy 0.94, igual que
nuestro XGBoost manual."

**→ VE A In [31]** — Sale: Curva ROC de FLAML

"La curva ROC de FLAML, tambien muy buena."

**→ VE A In [33]** — Sale: Modelo guardado

"Guardamos el modelo por si queremos usarlo despues."

**→ VE A In [34]** — Sale: SHAP values calculados

"Inicializamos SHAP y calculamos los valores para el conjunto de test."

**→ VE A In [35]** — Sale: Aciertos: 94 | Fallos: 6

"El modelo tiene 94 aciertos y 6 fallos."

**→ VE A In [36]** — Sale: ACIERTO Obs 0, Age=30, Salary=87000, grafico azul

"Este usuario tiene 30 años y un salario de 87.000. Vemos que todo el
grafico es azul, las dos variables empujan hacia no compra. Tiene sentido:
una persona joven con un salario medio no es el perfil tipico de comprador
en este dataset. El modelo predice no compra y acierta."

**→ VE A In [37]** — Sale: ACIERTO Obs 50, Age=57, Salary=122000, grafico rojo

"Este otro tiene 57 años y un salario de 122.000. Aqui todo es rojo, las
dos variables empujan hacia compra. Es logico: una persona mayor con buen
salario tiene mas probabilidad de comprar. El modelo predice compra y
acierta."

**→ VE A In [38]** — Sale: FALLO Obs 9, Age=47, Salary=43000

"Y aqui el fallo. El usuario tiene 47 años y un salario de 43.000. El
modelo dice que va a comprar, pero no compro. Mirando el grafico SHAP se
ve que la edad empuja hacia compra porque 47 es bastante alto, pero el
salario es bajo. El modelo le ha dado mas peso a la edad que al salario
y se ha equivocado. Es un caso fronterizo: edad de comprador pero salario
de no comprador. SHAP nos permite entender exactamente por que ha fallado."

**→ VE A In [39]** — Sale: los 2 graficos de dependencia

"En el grafico de dependencia de la edad vemos un salto alrededor de los
35-40 años donde la probabilidad de compra sube bastante. Tiene sentido,
es gente con mas poder adquisitivo. En el del salario pasa algo parecido,
a partir de cierto nivel la probabilidad de compra se dispara."

**→ VE A In [40]** — Sale: el grafico de enjambre (beeswarm)

"El grafico resumen nos dice que variable pesa mas. Los puntos rojos a la
derecha son valores altos que empujan hacia compra, y se ve claramente que
ambas variables influyen pero una mas que la otra."

**→ VE A In [41]** — Sale: grafico de barras SHAP

"Lo mismo pero en barras, mas facil de leer. Muestra la importancia media
de cada variable."

**→ VE A In [42]** — Sale: waterfall plot

"El waterfall muestra paso a paso como se construye la prediccion: partiendo
del valor base, cada variable suma o resta hasta llegar al resultado final."

---

## 5. CONCLUSIONES (9:15 - 10:00)

**→ VE AL TITULO** — "3.2.2 Conclusiones - Dataset completo" (ultima celda markdown)

"Para resumir: XGBoost da un R² de 0.91 en regresion, superando al
ensemble de la UT5. En clasificacion un 0.94, mejor que los modelos de
la UT6. Hemos probado varias configuraciones de hiperparametros y nos
hemos quedado con la mejor. FLAML automatiza la busqueda en 2 minutos.
Y SHAP es lo que le da sentido: podemos explicar por que el modelo
predice lo que predice, incluso entender por que se equivoca en casos
como el del usuario de 47 años con salario bajo.

Eso es todo, gracias."

---

## CONSEJOS PARA GRABAR

- Graba con OBS Studio o el grabador de Windows (Win+G)
- Pon el notebook en pantalla completa en Colab
- Scrollea hasta la celda que toca ANTES de empezar a hablar de ella
- Habla tranquilo, no corras
- Si te equivocas sigue, no pares
- No leas el guion palabra por palabra, usalo como guia
- Si te pasas de tiempo salta In [37] (segundo acierto SHAP)
