# Latino Simplo

**Un latín sin flexiones, transparente para hablantes de lenguas romances y de inglés.**

> En la tradición del *Latino sine Flexione* de Giuseppe Peano (1903), de *Interlingua*
> y de *Lingua Franca Nova*: conservar el **sabor del latín** eliminando lo que más
> cuesta aprender (declinaciones, conjugaciones, géneros y concordancias).

> **Documentos del proyecto:**
> - 📘 Este `README.md` — introducción, filosofía y resumen.
> - 📖 [`gramatica.md`](gramatica.md) — gramática completa (tiempos, aspecto, afijos).
> - 📚 [`lexico.md`](lexico.md) — diccionario temático (varios cientos de palabras).
> - 📝 [`textos.md`](textos.md) — diálogos, fábulas y proverbios con traducción.

---

## 1. Filosofía de diseño

Tres reglas de oro guían cada decisión:

1. **Cero memorización de tablas.** No hay declinaciones, ni conjugaciones por persona,
   ni género gramatical, ni concordancias. Las palabras son **invariables**; el significado
   gramatical lo aportan el **orden** (Sujeto–Verbo–Objeto) y unas pocas **palabras-herramienta**.
2. **Transparencia máxima.** Cada palabra se elige de forma que un hablante de español,
   italiano, portugués, francés, catalán, rumano **o inglés** la reconozca casi sin estudiar.
   El inglés hereda ~60 % de su vocabulario culto del latín, así que sirve de puente.
3. **Esencia latina.** Las raíces, el alfabeto, el imperativo desnudo (`Veni!`, `Ama!`),
   los saludos (`Salve!`) y textos clásicos siguen sonando inconfundiblemente a latín.

---

## 2. Sonidos y escritura

- Alfabeto latino, **sin acentos ni diacríticos**. Cinco vocales puras: `a e i o u`.
- Cada letra, un sonido. Reglas mínimas:

| Letra | Sonido | Ejemplo |
|------|--------|---------|
| `c` | siempre /k/ | `casa` (kasa), `centro` (kentro) |
| `g` | siempre /g/ | `gente` (guente) |
| `h` | muda | `homine` (omine) |
| `j` | /y/ como en *yes* | `jam` (yam) |
| `qu` | /kw/ | `quando` (kwando) |
| `v` | /v/ o /b/ | `vita` |
| `z` | /ts/ o /s/ | `zero` |

- **Acento tónico**: por defecto en la penúltima sílaba (`a-MA`, `ho-MI-ne`, `na-TU-ra`).
  No se escribe nunca.

---

## 3. Sustantivos: una sola forma

No hay casos. El sustantivo se toma del **tema latino** (a menudo coincide con el ablativo
de Peano), en una forma única que vale para sujeto, objeto y complemento.

| Latín clásico | Latino Simplo | Español / English |
|---------------|---------------|-------------------|
| homo, hominis | `homine` | hombre / man |
| tempus, temporis | `tempore` | tiempo / time |
| nomen, nominis | `nomine` | nombre / name |
| rosa, rosae | `rosa` | rosa / rose |
| annus, anni | `anno` | año / year |
| nox, noctis | `nocte` | noche / night |

**Plural**: se añade **`-s`** (reconocible en español, portugués, francés, catalán e inglés).

```
uno homine  → multo homines
le anno     → tres annos
```

> Si la palabra ya termina en `-s` o consonante, se añade `-es`: `flore → flores`, `rege → reges`.

---

## 4. Sin género gramatical

Las cosas **no tienen género**. Los adjetivos **nunca cambian**. Solo se distingue el
género natural en los pronombres y, si hace falta, con `mas` (macho) / `femina` (hembra):

```
un gato grande      (no "gata grande")
un gato femina      = una gata
```

---

## 5. Artículos (opcionales)

El latín no tenía artículos; aquí son **opcionales** pero disponibles, derivados de `ille`:

| | Singular | Plural |
|---|---|---|
| Definido (*the / el*) | `le` | `les` |
| Indefinido (*a / un*) | `un` | `unos` |

```
le casa      = la casa / the house
un libro     = un libro / a book
casa         = (sin artículo, válido) casa
```

---

## 6. Pronombres

| Persona | Sujeto / objeto | Posesivo |
|---------|-----------------|----------|
| yo / I | `io` | `meo` |
| tú / you | `tu` | `tuo` |
| él / he | `illo` | `suo` |
| ella / she | `illa` | `suo` |
| nosotros / we | `nos` | `nostro` |
| vosotros / you | `vos` | `vostro` |
| ellos / they | `illos` / `illas` | `suo` |

El mismo pronombre vale como sujeto y como objeto: `io vide te`, `tu ama me`.
El posesivo es invariable y va antes o después del nombre: `meo patre` o `patre meo`.

---

## 7. Verbos: el corazón del sistema

Cada verbo tiene **una sola raíz invariable** (el infinitivo latino menos `-re`):
`amare → ama`, `videre → vide`, `dicere → dice`, `audire → audi`, `ire → i`.

El tiempo se marca con una **partícula antepuesta**, igual para todas las personas:

| Tiempo | Marca | Ejemplo | Traducción |
|--------|-------|---------|------------|
| Presente | — | `io ama` | yo amo / I love |
| Pasado | `ia` | `io ia ama` | yo amé / I loved |
| Futuro | `va` | `io va ama` | yo amaré / I will love |
| Condicional | `ave` | `io ave ama` | yo amaría / I would love |
| Perfecto (matiz) | `habe` | `io habe ama` | yo he amado / I have loved |

> El sistema completo de tiempos, aspecto, voz pasiva y formación de palabras está en
> [`gramatica.md`](gramatica.md).

- **Negación**: `non` antes del verbo → `io non ama`.
- **Imperativo**: la raíz desnuda → `Ama!`, `Veni!`, `Audi!` (puro latín).
- **Infinitivo**: forma en `-re`, tras un verbo modal → `io vole amare`.
- **Verbos modales** (invariables, transparentes):
  `pote` (poder), `debe` (deber), `vole` (querer) → `io pote ire`, `tu debe studia`.
- **Ser/estar**: `es` para todas las personas → `io es`, `illos es`. Pasado `ia es`.
- **Haber / hay**: `habe` → `habe multo gente hic` (*hay mucha gente aquí*).
- **Voz pasiva**: `es` + participio en `-to` → `le libro es scripto` (*el libro está escrito*).

Conjugación completa de `amare` en presente — **una sola forma**:

```
io ama · tu ama · illo ama · nos ama · vos ama · illos ama
```

---

## 8. Adjetivos y comparación

Invariables, normalmente tras el nombre (orden romance), aunque el orden es flexible.

| Grado | Marca | Ejemplo |
|-------|-------|---------|
| Comparativo (*más*) | `plus` | `plus magno que…` (más grande que…) |
| Comparativo (*menos*) | `minus` | `minus caro` |
| Superlativo | `le plus` / `maxime` | `le plus bono`, `maxime rapido` |
| Igualdad | `tanto … quanto` | `tanto alto quanto tu` |

---

## 9. Palabras-herramienta esenciales

| Latino Simplo | Significado | Latino Simplo | Significado |
|---------------|-------------|---------------|-------------|
| `et` | y / and | `o` | o / or |
| `non` | no / not | `si` | sí / if |
| `in` | en / in | `de` | de / of |
| `a / ad` | a / to | `con` | con / with |
| `pro` | para / for | `sine` | sin / without |
| `super` | sobre | `sub` | bajo |
| `que` | que (relativo) | `quando` | cuando |
| `ubi` | dónde | `quo` | adónde |
| `quia` | porque | `como` | cómo / como |
| `hic` | aquí | `ibi` | allí |
| `nunc` | ahora | `tunc` | entonces |
| `hodie` | hoy | `cras` | mañana |
| `multo` | mucho | `poco` | poco |
| `omne` | todo | `nihil` | nada |

**Números**: `uno, duo, tres, quatro, quinque, sex, septe, octo, nove, dece`,
`centu` (100), `mille` (1000).

---

## 10. Vocabulario básico (muestra)

| Latino Simplo | Español | English | Latino Simplo | Español | English |
|---------------|---------|---------|---------------|---------|---------|
| `aqua` | agua | water | `terra` | tierra | earth |
| `sole` | sol | sun | `luna` | luna | moon |
| `homine` | hombre | man | `femina` | mujer | woman |
| `patre` | padre | father | `matre` | madre | mother |
| `casa` | casa | house | `via` | camino | way |
| `manu` | mano | hand | `corde` | corazón | heart |
| `die` | día | day | `nocte` | noche | night |
| `magno` | grande | big | `parvo` | pequeño | small |
| `bono` | bueno | good | `malo` | malo | bad |
| `ama` | amar | love | `vide` | ver | see |
| `dice` | decir | say | `face` | hacer | make/do |
| `i` (ire) | ir | go | `veni` | venir | come |

---

## 11. Frases de ejemplo

```
Salve!                              ¡Hola! / Greetings!
Como tu es?                         ¿Cómo estás? / How are you?
Io es bono, gratias.               Estoy bien, gracias.
Que es tuo nomine?                  ¿Cómo te llamas? / What is your name?
Meo nomine es Antonio.             Me llamo Antonio.
Io ama te.                          Te amo. / I love you.
Nos va i a le mercato cras.        Iremos al mercado mañana.
Illa ia dice le verita.            Ella dijo la verdad.
Habe multo aqua in le rivo.        Hay mucha agua en el río.
Tu pote veni con nos?              ¿Puedes venir con nosotros?
Io non sci ubi es le casa.         No sé dónde está la casa.
```

---

## 12. Texto demostrativo

Un fragmento clásico, para que se vea la **esencia latina** intacta a la vez que la
transparencia total (comparar con el latín original):

> **Latino Simplo:**
> Patre nostro, que es in le celo, sanctificato es tuo nomine.
> Veni tuo regno. Tuo voluntate es facto in le terra como in le celo.
> Da a nos hodie nostro pane de omne die.

> **Latín clásico:**
> Pater noster, qui es in caelis, sanctificetur nomen tuum.
> Adveniat regnum tuum. Fiat voluntas tua sicut in caelo et in terra.
> Panem nostrum quotidianum da nobis hodie.

Un hablante de español, italiano, portugués, francés **o** inglés culto entiende el
texto en *Latino Simplo* prácticamente a primera vista, sin haber estudiado ni una
sola declinación.

---

## 13. Resumen en una tarjeta

| Aspecto | Regla |
|---------|-------|
| Orden | Sujeto – Verbo – Objeto |
| Sustantivos | invariables; plural `-s` |
| Género | no existe |
| Artículos | `le` / `un`, opcionales |
| Adjetivos | invariables, sin concordancia |
| Verbos | raíz única + partícula `ia` (pasado) / `va` (futuro) |
| Negación | `non` antes del verbo |
| Comparación | `plus` / `minus` / `le plus` |

> **En una línea:** toma una raíz latina, no la declines nunca, ordénala como en inglés
> o en español, y marca el tiempo con `ia` o `va`. Eso es el *Latino Simplo*.
