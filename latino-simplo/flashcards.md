# Flashcards — mazo de repaso de Latino Simplo

El archivo [`flashcards.csv`](flashcards.csv) contiene **~145 palabras nucleares** del
Latino Simplo (las más frecuentes: pronombres, partículas, números, naturaleza, familia,
cuerpo, comida, verbos de uso diario…). Con ellas puedes entender y formar la mayoría de
las frases cotidianas.

## Formato

Tres columnas, separadas por comas, con cabecera:

```
latino_simplo,espanol,english
io,yo,I
aqua,agua,water
...
```

## Cómo usarlo

### Opción A — Anki (recomendado)

1. Abre **Anki** → *Archivo → Importar* → elige `flashcards.csv`.
2. Separador: **coma**. Marca *"Las primeras líneas son cabecera"* / ignora la fila de
   cabecera.
3. Asigna los campos:
   - **Anverso (pregunta):** `espanol` (o `english`).
   - **Reverso (respuesta):** `latino_simplo`.
4. Para practicar **las dos direcciones** (leer y escribir), importa el mismo archivo en
   un tipo de nota *Básico (y tarjeta invertida)*: así Anki genera tanto
   *español → Latino Simplo* como *Latino Simplo → español*.

### Opción B — hoja de cálculo

Ábrelo en Excel, LibreOffice o Google Sheets (separador: coma) y tápate una columna
para autoevaluarte.

### Opción C — Quizlet u otras apps

La mayoría aceptan importación CSV/TSV. Usa `latino_simplo` como término y `espanol` o
`english` como definición.

## Consejo de estudio

Aprende primero **las partículas y los 50 verbos y sustantivos más frecuentes**: con la
gramática invariable de Latino Simplo (ver [`gramatica.md`](gramatica.md)), eso ya te
permite construir cientos de frases. Para ampliar, pasa a [`lexico.md`](lexico.md) y
[`lexico-moderno.md`](lexico-moderno.md).
