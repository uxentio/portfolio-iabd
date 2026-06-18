# CW4EVER · Entrenador de código Morse

Entrenador de código Morse (CW) que funciona **100% en el navegador**, sin
dependencias ni servidor. Inspirado en el entrenador de
[cw4ever.eu/trainer](https://cw4ever.eu/trainer/).

## Características

- **Método Koch**: introduce los caracteres de forma progresiva (empezando por
  `K` y `M`) y sube de nivel automáticamente cuando aciertas ≥ 90 %.
- **Temporización Farnsworth** (estándar ARRL): velocidad de carácter y
  velocidad efectiva independientes, para aprender a velocidad real con huecos
  ampliados.
- **Modos de práctica**: Koch, solo letras, solo números, mixto, abreviaturas /
  código Q e indicativos (callsigns) generados al azar.
- **Práctica de copia**: escucha el Morse, escribe lo que oigas y obtén la
  corrección carácter a carácter con porcentaje de aciertos.
- **Audio limpio** con la Web Audio API: tono ajustable (400–1000 Hz) y
  envolvente para evitar *clicks*.
- **Tabla de referencia** y **estadísticas** de sesión.
- Ajustes persistentes en `localStorage`.

## Uso

No requiere compilación. Al usar módulos ES, sírvelo desde un servidor local
(abrir el `index.html` con `file://` bloquea los módulos en algunos navegadores):

```bash
cd cw4ever-trainer
python3 -m http.server 8000
# abre http://localhost:8000
```

### Atajos

| Tecla | Acción |
|---|---|
| `Espacio` | Reproducir la sesión actual |
| `N` | Generar nueva sesión |
| `Ctrl/Cmd + Enter` | Comprobar la copia (en el cuadro de texto) |

## Arquitectura

| Archivo | Responsabilidad |
|---|---|
| `js/morse.js` | Tabla Morse, orden Koch, cálculo de temporización Farnsworth y conversión texto → eventos de audio. |
| `js/audio.js` | Motor de tono CW con la Web Audio API (programación de envolventes, *sidetone* manual). |
| `js/app.js` | Lógica de la app: generación de sesiones, corrección, progreso Koch, estadísticas y UI. |
| `index.html` / `css/style.css` | Interfaz. |

## Temporización (referencia)

Con velocidad de carácter `C` y efectiva `S` (WPM):

```
dit   = 1.2 / C            (s)
dah   = 3 · dit
td    = (60/S − 37.2/C) / 19   → unidad de espaciado Farnsworth
hueco entre caracteres = 3 · td
hueco entre palabras   = 7 · td
```

A 20 WPM el dit dura 60 ms y la palabra de referencia `PARIS ` dura 3,0 s,
como marca el estándar.
