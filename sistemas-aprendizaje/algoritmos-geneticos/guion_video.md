# Guion para el Vídeo - RA2T1

**Duración estimada: ~9 minutos**

> El guion sigue el cuaderno celda a celda, de arriba a abajo.
> Cada paso te dice qué celda ejecutar con Shift+Enter y qué decir.
> No tienes que saltar ni buscar nada, solo ir bajando.

---

## INTRO (30 seg)

*Antes de empezar: abre el cuaderno en Jupyter con todas las celdas sin ejecutar.*

DI: "Buenas, soy Antonio. Voy a explicar cómo he resuelto el problema de asignación de tareas usando un algoritmo genético."

---

## SECCIÓN 1 — Comprensión del problema (1 min)

**Celda 1 → Markdown "1. Comprensión del problema"**
*Baja con scroll para que se vea el texto y la tablita del ejemplo 3x3.*

DI: "El problema es este: tenemos N trabajadores y N tareas. Cada trabajador tiene un coste distinto para cada tarea y hay que repartirlas para que el coste total sea el mínimo. Es parecido al Problema del Viajero de la Sesión 3, pero con costes de asignación en vez de distancias. Con 10 trabajadores hay más de 3 millones de combinaciones, así que probarlas todas no es viable."

---

## SECCIÓN 2 — Modelado de la solución (30 seg)

**Celda 2 → Markdown "2. Modelado de la solución"**
*Scroll para que se vea el texto.*

DI: "Cada solución es una permutación: la posición es el trabajador y el valor es la tarea. Como es una permutación, cada tarea aparece una sola vez, así que la solución siempre es válida."

---

## SECCIÓN 3 — Diseño del algoritmo genético

### Imports

**Celda 3 → Código: imports (numpy, matplotlib, random)**
*Shift+Enter*

DI: "Aquí importo las librerías: numpy, matplotlib y random. No necesito nada más."

---

### 3.1 Matriz de costes

**Celda 4 → Markdown "3.1 Definición del problema"**
*Scroll para ver el texto.*

**Celda 5 → Código: genera la matriz de costes**
*Shift+Enter → aparece la matriz 10x10*

DI: "Genero una matriz de costes 10x10 con semilla fija. Por ejemplo el trabajador 0 haciendo la tarea 0 cuesta 52, pero haciendo la tarea 2 cuesta solo 15."

---

### 3.2 Población inicial

**Celda 6 → Markdown "3.2 Inicialización de la población"**
*Scroll para ver el texto.*

**Celda 7 → Código: genera 5 individuos de ejemplo**
*Shift+Enter → aparecen los 5 individuos*

DI: "Cada individuo es una permutación generada con np.random.permutation. El primero, [1, 4, 2, 3, 5, 7, 6, 9, 0, 8], quiere decir que el trabajador 0 hace la tarea 1, el trabajador 1 la tarea 4, y así."

---

### 3.3 Fitness

**Celda 8 → Markdown "3.3 Función de fitness"**
*Scroll para ver el texto.*

**Celda 9 → Código: función fitness + ejemplo**
*Shift+Enter → sale "Coste total: 474"*

DI: "El fitness es la suma de costes de la asignación. Aquí el individuo de ejemplo tiene un coste de 474. Como queremos minimizar, cuanto menos mejor."

---

### 3.4 Selección

**Celda 10 → Markdown "3.4 Selección"**
*Scroll para ver el texto.*

**Celda 11 → Código: función selección por torneo**
*Shift+Enter (no tiene output, solo define la función)*

DI: "Selección por torneo con k=3, sacado de la Sesión 3. Cojo 3 al azar y me quedo con el de menor coste."

---

### 3.5 Cruce OX

**Celda 12 → Markdown "3.5 Cruce"**
*Scroll para ver el texto.*

**Celda 13 → Código: función cruce OX + ejemplo**
*Shift+Enter → salen Padre 1, Padre 2 y el Hijo [3, 2, 1, 0, 4, 5, 6, 7, 9, 8]*

DI: "El cruce es OX, Order Crossover. Se coge un trozo de un padre y se rellena el resto con el otro padre en orden. Aquí se ve: el hijo sale [3, 2, 1, 0, 4, 5, 6, 7, 9, 8], que es una permutación válida."

---

### 3.6 Mutación

**Celda 14 → Markdown "3.6 Mutación"**
*Scroll para ver el texto.*

**Celda 15 → Código: función mutación swap + ejemplo**
*Shift+Enter → sale Original y Mutado [5, 1, 2, 3, 4, 0, 6, 7, 8, 9]*

DI: "Mutación swap: se intercambian dos posiciones. Aquí la posición 0 y la 5 se han cambiado. La permutación sigue siendo válida."

---

### 3.7 y 3.8 Reemplazo y Parada

**Celda 16 → Markdown "3.7 Estrategia de reemplazo"**
*Scroll para ver el texto.*

**Celda 17 → Markdown "3.8 Estrategia de finalización"**
*Scroll para ver el texto.*

DI: "Reemplazo generacional con elitismo, sacado de la Sesión 4. El mejor siempre pasa a la siguiente generación. Y para cuando lleva 40 generaciones sin mejorar o llega a 200, eso viene de la Sesión 5."

---

### 3.9 Algoritmo completo

**Celda 18 → Markdown "3.9 Algoritmo completo"**

**Celda 19 → Código: función algoritmo_genetico**
*Shift+Enter (no tiene output, solo define la función)*

DI: "Aquí está todo junto en una sola función: población inicial, bucle de generaciones con selección, cruce, mutación, elitismo y parada por estancamiento."

---

## SECCIÓN 4 — Experimentación (2 min)

**Celda 20 → Markdown "4. Experimentación"**
*Scroll para ver el texto.*

**Celda 21 → Código: 3 ejecuciones con semillas 10, 77, 200**
*Shift+Enter → espera unos segundos → salen los 3 resultados*

DI: "Lo ejecuto 3 veces con semillas distintas. La primera da coste 148, la segunda 154 y la tercera 145. Son bastante parecidos."

---

### 4.1 Gráficas

**Celda 22 → Markdown "4.1 Gráficas de convergencia"**

**Celda 23 → Código: gráfica de mejor fitness**
*Shift+Enter → aparece la gráfica*

DI: "Aquí se ve la convergencia del mejor fitness. Baja rápido al principio y luego se queda plano."

**Celda 24 → Código: gráfica de fitness medio**
*Shift+Enter → aparece la gráfica*

DI: "Y esta es la evolución del fitness medio de la población."

**Celda 25 → Código: gráfica mejor vs medio**
*Shift+Enter → aparece la gráfica*

DI: "Y aquí se ve cómo la media se va acercando al mejor. La población entera va convergiendo."

---

### 4.2 Resumen

**Celda 26 → Markdown "4.2 Análisis de resultados"**

**Celda 27 → Código: resumen de las 3 ejecuciones**
*Shift+Enter → aparece la tabla resumen*

DI: "El mejor coste es 145, el peor 154, la media 149 y la desviación típica solo 3.74. Es bastante estable."

**Celda 28 → Código: detalle de la mejor solución**
*Shift+Enter → aparece el detalle trabajador por trabajador*

DI: "Aquí el detalle de la mejor asignación, la de la ejecución 3 con coste 145. Por ejemplo el trabajador 1 hace la tarea 9 que solo cuesta 2, y el trabajador 4 hace la tarea 5 que cuesta 7."

---

### 4.3 Análisis

**Celda 29 → Markdown "4.3 Análisis de estabilidad..."**
*Scroll para que se vea el texto del análisis.*

DI: "Aquí analizo los resultados. El algoritmo es estable porque los 3 costes son muy parecidos. Y en calidad, si asignas al azar esperarías un coste de unos 500, y el AG lo baja a 149."

---

## SECCIÓN 5 — Conclusiones (1 min)

**Celda 30 → Markdown "5. Conclusiones"**
*Scroll despacio para que se vea todo.*

DI: "El algoritmo converge rápido y es estable. He usado los operadores y estrategias de los cuadernos de la asignatura: torneo, OX, swap, elitismo y parada por estancamiento."

"Como mejoras se podría probar el modelo mu+lambda de la Sesión 4, la entropía genética de la Sesión 5, o el meta-GA de la Sesión 6 para ajustar parámetros automáticamente."

---

## DESPEDIDA (15 seg)

DI: "Bueno, eso es todo. Gracias."

---

## TIPS PARA GRABAR
- Graba pantalla con OBS (gratis)
- Abre el cuaderno con TODAS las celdas sin ejecutar
- Ve dándole Shift+Enter a cada celda mientras hablas
- Este guion va en el mismo orden que el cuaderno, solo tienes que ir bajando
- Tenlo en otro monitor o impreso, no lo leas
- Si te equivocas, sigue hablando o corta y repite esa parte
