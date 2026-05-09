# Sistema Experto de Control Climatico de Edificios

## Documentacion Tecnica - UT3T1

---

## 1. Diseño del sistema

### 1.1 Dominio elegido

He elegido el control climatico de un edificio porque encaja muy bien con lo que hemos visto en clase:

- Los datos de sensores se pueden representar como hechos con Field (como en el ejemplo de Persona de la sesion 1bis)
- Hay una cadena natural de inferencia: los datos brutos se clasifican en categorias, y esas categorias disparan acciones. Esto es justo lo que hace el encadenamiento hacia adelante que explica la guia tecnica
- Las emergencias tienen que ir primero, asi que el uso de salience tiene sentido real
- Se puede integrar un modelo predictivo como un hecho mas

### 1.2 Dinamica de actuacion

El sistema sigue el ciclo de inferencia que explica la guia tecnica del profesor (capitulo 6):

1. **Inicializacion** con `reset()`: se crea el InitialFact automatico y se ejecutan los `@DefFacts`, que declaran `EstadoSistema(modo="normal")`
2. **Declaracion de hechos** con `declare()`: se meten los datos de los sensores como hechos tipados
3. **Ciclo de inferencia** con `run()`: el motor repite este bucle hasta que no queden reglas por disparar:
   - Busca que reglas coinciden con los hechos en memoria (match)
   - Si hay varias, elige la de mayor salience (resolucion de conflictos)
   - Ejecuta la regla elegida, que puede declarar nuevos hechos
   - Los nuevos hechos pueden activar mas reglas, y asi sigue la cadena

### 1.3 Estructura de hechos

He definido 11 tipos de hechos usando Field con validacion (igual que en la sesion 1bis con Persona y Pago):

**Sensores (datos de entrada):**
- `SensorTemperatura`: zona (str), valor (float), timestamp (str)
- `SensorHumedad`: zona (str), valor (float)
- `SensorOcupacion`: zona (str), personas (int)
- `SensorCO2`: zona (str), ppm (float)
- `PrediccionTemperatura`: zona (str), valor_futuro (float), horizonte_min (int) - viene del modelo de series temporales

**Hechos derivados (los crean las reglas):**
- `NivelConfort`: zona, nivel (frio/optimo/caluroso)
- `NivelCalidadAire`: zona, nivel (bueno/regular/malo)
- `RiesgoEnergetico`: zona, nivel

**Salida:**
- `AccionControl`: zona, sistema, accion, intensidad
- `Alerta`: zona, tipo, mensaje, prioridad
- `EstadoSistema`: modo (normal/ahorro/emergencia)

### 1.4 Cadena de inferencia multinivel

La inferencia funciona en varios niveles, cada uno construye sobre el anterior:

```
Nivel 0: Datos de sensores + PrediccionTemperatura
    |
    | [salience=100] Reglas de emergencia
    | Si temp >45 o <0, o CO2 >5000 -> Alerta critica + parada
    |
    v
Nivel 1: NivelConfort, NivelCalidadAire
    |
    | [salience=50] Reglas de clasificacion
    | Temperatura -> frio/optimo/caluroso
    | CO2 -> bueno/regular/malo
    |
    v
Nivel 2: RiesgoEnergetico
    |
    | [salience=50] Ocupacion alta + temp no optima -> riesgo
    |
    v
Nivel 3: AccionControl, Alerta
    |
    | [salience=20] Reglas de control
    | Confort + ocupacion -> calefaccion/refrigeracion/ventilacion
    |
    v
Nivel 4: Acciones ajustadas
    |
    | [salience=10] Reglas de optimizacion
    | Conflicto confort vs energia -> bajar intensidad con modify()
    | Humedad alta + calor -> deshumidificador
```

Lo importante es que sin este orden por salience no funciona. Al principio lo hice sin separar clasificacion y control, y las reglas de control no encontraban los NivelConfort porque todavia no se habian creado.

---

## 2. Representacion y simulacion de comportamiento

### 2.1 Reglas del sistema

El sistema tiene 17 reglas en 4 niveles de prioridad:

**Emergencias (salience=100) - 2 reglas:**
- `emergencia_temp`: si la temperatura es mayor de 45 o menor de 0, declara alerta critica y parada de emergencia. Usa `P(lambda t: t > 45 or t < 0)`
- `emergencia_co2`: si el CO2 supera 5000 ppm, declara alerta y ventilacion de emergencia

**Clasificacion (salience=50) - 7 reglas:**
- 3 reglas para clasificar el confort termico (frio <19, optimo 19-26, caluroso >26). Usan `NOT(Alerta(...))` para no clasificar durante emergencias
- 3 reglas para clasificar la calidad del aire (bueno <=400, regular 401-1000, malo 1001-5000)
- 1 regla de riesgo energetico: si hay mas de 30 personas y el confort no es optimo. Usa `OR()` para capturar frio o caluroso en una sola regla

**Control (salience=20) - 5 reglas:**
- Calefaccion si hace frio y hay gente
- Refrigeracion si hace calor y hay gente
- Ventilacion forzada si el aire es malo
- Modo ahorro si la zona esta vacia y la temp es optima
- Pre-enfriamiento si la prediccion dice que va a subir de 28C (esta es la que usa series temporales)

Todas usan `NOT()` para evitar duplicar acciones, que era un problema que tenia al principio.

**Optimizacion (salience=10) - 3 reglas:**
- Conflicto confort vs energia: si hay refrigeracion a intensidad alta y riesgo energetico, baja a moderada con `modify()` (lo aprendi del ejemplo de prestamos de la sesion 1bis)
- Si hay calor + humedad >70% activa deshumidificador
- Ventilacion preventiva si hay bastante gente y el aire es regular

### 2.2 Operadores usados

He usado los operadores que vimos en clase:

- **`P(lambda x: ...)`**: para comprobaciones numericas. Por ejemplo `P(lambda t: t > 45 or t < 0)` para detectar temperaturas extremas. Es como el ejemplo de la sesion 1bis con `P(lambda x: x >= 18)`
- **`L("valor")`**: para comparar con valores exactos. Por ejemplo `L("critica")` o `L("frio")`
- **`NOT()`**: para comprobar que NO existe un hecho. Lo uso para evitar acciones duplicadas y para que las reglas de clasificacion no actuen durante emergencias
- **`OR()`**: en la regla de riesgo energetico para capturar `NivelConfort(frio)` o `NivelConfort(caluroso)` con una sola regla
- **`AS.accion << AccionControl(...)`**: para capturar el hecho en una variable y despues poder modificarlo con `self.modify()`. Esto es igual que `AS.cs << Fact(credito=...)` del ejemplo de prestamos
- **`MATCH.zona`**: para enlazar el campo zona a una variable y que las reglas actuen sobre la zona correcta

---

## 3. Analisis de la variacion de caracteristicas

### 3.1 Variacion de temperatura

He hecho un barrido de -5C a 54C con CO2=500 y ocupacion=10 para ver como cambia el comportamiento:

| Rango | Confort | Accion | Emergencia |
|-------|---------|--------|------------|
| T < 0C | N/A (no clasifica) | parada_emergencia | SI |
| 0C - 18C | frio | calefaccion | NO |
| 19C - 26C | optimo | ninguna | NO |
| 27C - 44C | caluroso | refrigeracion | NO |
| T > 45C | N/A (no clasifica) | parada_emergencia | SI |

Cosas que se ven:
- Las transiciones son limpias, no hay solapamiento entre rangos
- El 19 es inclusivo en optimo (19 <= T <= 26)
- En emergencias las reglas de clasificacion NO se disparan porque tienen `NOT(Alerta(prioridad="critica"))`, asi no se mezclan acciones contradictorias

### 3.2 Variacion del CO2

| Rango | Calidad | Ventilacion | Emergencia |
|-------|---------|-------------|------------|
| <= 400 ppm | bueno | NO | NO |
| 401-1000 ppm | regular | solo si >15 personas | NO |
| 1001-5000 ppm | malo | SI (forzada) | NO |
| > 5000 ppm | N/A | SI (emergencia) | SI |

La ventilacion preventiva (aire regular + mucha gente) es un ejemplo de como las reglas interactuan entre si: necesita datos de CO2 Y de ocupacion para decidir.

### 3.3 Efecto de la ocupacion

La ocupacion influye en varias reglas:
- 0 personas -> modo ahorro (si la temp es optima)
- \> 0 personas -> se permiten calefaccion y refrigeracion
- \> 15 personas -> ventilacion preventiva (con aire regular)
- \> 30 personas -> riesgo energetico (si la temp no es optima)

### 3.4 Efecto de la prediccion

| Prediccion (30 min) | Temp actual | Accion |
|---------------------|------------|--------|
| < 28C | optima (22C) | ninguna |
| >= 28C | optima (22C) | pre-enfriamiento |
| >= 28C | calurosa (30C) | refrigeracion (no pre-enfriamiento) |

Lo interesante es que el pre-enfriamiento solo se activa si ahora la temp esta bien pero se predice que va a subir. Si ya hace calor, la refrigeracion directa tiene prioridad. Esto pasa porque la regla de control predictivo requiere `NivelConfort(optimo)`.

---

## 4. Estrategias de control y objetivos

### 4.1 Jerarquia de prioridades

Como explica la guia tecnica, experta ejecuta primero las reglas con mayor salience. He usado 4 niveles:

**salience=100 (Emergencias):**
El objetivo es la seguridad. Si hay una temperatura peligrosa (>45C o <0C) o CO2 toxico (>5000 ppm), lo primero es generar una alerta critica. Ademas, estas alertas bloquean las reglas de clasificacion con `NOT()`, evitando que el sistema intente climatizar una zona que hay que evacuar.

**salience=50 (Clasificacion):**
El objetivo es transformar los datos de los sensores en categorias que las reglas de control puedan usar. Si esto no se ejecuta antes que el control, las reglas de control no encontrarian hechos como `NivelConfort` y no harian nada. Esto es lo que me paso al principio cuando no usaba salience.

**salience=20 (Control):**
El objetivo es generar acciones concretas basandose en las clasificaciones. Todas usan `NOT()` para no crear acciones duplicadas.

**salience=10 (Optimizacion):**
El objetivo es ajustar las acciones cuando hay conflictos. Por ejemplo, si hace calor pero hay mucha gente y el gasto energetico seria alto, en vez de quitar la refrigeracion la baja a intensidad moderada usando `modify()`.

### 4.2 Resolucion del conflicto confort vs energia

Este es el conflicto mas interesante del sistema. Cuando hay calor + mucha gente:

1. Se clasifica como caluroso (salience=50)
2. Se genera riesgo energetico alto porque hay >30 personas con temp no optima (salience=50)
3. Se activa refrigeracion a intensidad alta (salience=20)
4. La regla de optimizacion detecta que hay refrigeracion alta + riesgo energetico y usa `modify()` para bajar la intensidad a moderada (salience=10)

Usa `AS.accion << AccionControl(...)` para capturar el hecho y `self.modify(accion, intensidad="moderada")` para cambiarlo sin borrarlo. Esto es lo mismo que hace el ejemplo de la sesion 1bis cuando modifica el credito.

---

## 5. Series temporales

### 5.1 Datos y modelo

Genero datos sinteticos de temperatura para 7 dias (168 registros, 1 por hora) que simulan:
- Ciclo dia/noche (sube por el dia, baja por la noche)
- Efecto fin de semana (2 grados menos por menor actividad)
- Tendencia ascendente (simula que se acerca el verano)
- Ruido aleatorio

Para el modelo uso `PolynomialFeatures(degree=3)` con `LinearRegression` de scikit-learn. Las features son:
- `hora_sin` y `hora_cos`: codificacion ciclica de la hora para que el modelo sepa que las 23h estan cerca de las 0h
- `dia_semana`: numero del dia (0-6)
- `es_finde`: binario, 1 si es sabado o domingo

### 5.2 Integracion con el sistema experto

La prediccion se mete como un hecho `PrediccionTemperatura` antes de ejecutar el motor:

```python
temp_predicha = predecir_temp(modelo, hora_actual + 0.5, dia_semana)
engine.declare(PrediccionTemperatura(zona="oficina", valor_futuro=temp_predicha, horizonte_min=30))
```

La regla `control_predictivo` solo se activa si:
1. La prediccion es mayor de 28C
2. La temperatura actual es optima (si ya hace calor, se activa refrigeracion directa)
3. Hay personas en la zona

Esto permite al sistema actuar 30 minutos antes de que suba la temperatura, en vez de esperar a que pase.

---

## 6. Plan de pruebas

### 6.1 Casos de prueba

He hecho 12 tests que cubren distintas situaciones:

| ID | Tipo | Que prueba | Entrada | Salida esperada |
|----|------|-----------|---------|-----------------|
| T01 | Normal | Temp baja activa calefaccion | Temp=15, Ocup=5 | AccionControl(calefaccion) |
| T02 | Normal | Temp alta activa refrigeracion | Temp=32, Ocup=3 | AccionControl(refrigeracion) |
| T03 | Normal | CO2 alto activa ventilacion | CO2=1500 | AccionControl(ventilacion) |
| T04 | Normal | Condiciones optimas, sin accion | Temp=22, CO2=400, Ocup=5 | NivelConfort(optimo), sin HVAC |
| T05 | Multinivel | Sensor -> clasificacion -> accion | Temp=15, Ocup=3 | NivelConfort(frio) + calefaccion |
| T06 | Multinivel | Riesgo energetico baja intensidad | Temp=30, Ocup=50 | RiesgoEnergetico + refrigeracion moderada |
| T07 | Multinivel | Prediccion activa pre-enfriamiento | Temp=24, Pred=30 | AccionControl(pre_enfriamiento) |
| T08 | Prioridad | Emergencia va primero | Temp=50 | Alerta critica |
| T09 | Prioridad | Modo ahorro zona vacia | Temp=22, Ocup=0 | AccionControl(modo_ahorro) |
| T10 | Limite | Umbral exacto temp=19.0 | Temp=19.0 | NivelConfort(optimo) |
| T11 | Robustez | Datos incompletos (sin temp) | Solo Ocup=5 | Sin acciones ni alertas |
| T12 | Robustez | Dos zonas a la vez | Zona A fria, Zona B caliente | Calefaccion en A, refrigeracion en B |

### 6.2 Que cubre cada grupo

- **T01-T04 (operacion normal)**: comprueban que las reglas basicas funcionan bien
- **T05-T07 (inferencia multinivel)**: comprueban que los hechos derivados disparan nuevas reglas. T05 verifica la cadena sensor->confort->accion, T06 verifica que el riesgo energetico modifica la intensidad, T07 verifica que la prediccion temporal activa el pre-enfriamiento
- **T08-T09 (prioridades)**: comprueban que el salience funciona correctamente
- **T10 (caso limite)**: verifica que el valor exacto 19.0 se clasifica como optimo (es el limite del rango)
- **T11-T12 (robustez)**: T11 comprueba que sin datos de temperatura el sistema no falla ni genera acciones incorrectas. T12 comprueba que dos zonas con condiciones opuestas se manejan de forma independiente

Todos los tests pasan correctamente.
