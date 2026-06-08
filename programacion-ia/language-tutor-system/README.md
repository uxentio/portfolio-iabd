# Personal Language Tutor — Tutor de idiomas adaptativo (prompt de sistema)

**Asignatura:** Programación para IA · **Tipo:** ingeniería de prompts / diseño de agente LLM · **Fecha:** 2026-06

## 1. Objetivo

Un **prompt de sistema** que convierte cualquier LLM de chat en un tutor de idiomas
personal. La idea no es un chatbot que traduce, sino un profesor que se adapta a
UNA persona: su nivel real, sus objetivos, su ritmo y el tiempo que tiene cada día.
Enseña conversando, corrige sin cortar el ritmo y hace que el idioma sea usable
desde el primer día en vez de académico.

El entregable es el propio prompt (`system-prompt.md`). No hay backend ni
dependencias: se pega como mensaje de sistema en Claude, GPT o un modelo local y
funciona en una conversación larga por alumno.

## 2. Cómo se usa

1. Pega el contenido de [`system-prompt.md`](system-prompt.md) como **system
   message** del modelo.
2. Abre una conversación por alumno y mantenla viva (o engancha una capa de memoria
   externa que reinyecte el perfil en cada arranque).
3. La primera vez, el agente hace el onboarding de 10 preguntas (Step 1) y guarda el
   perfil. A partir de ahí cada sesión sigue la estructura warm-up → material nuevo →
   práctica → correcciones → cierre.

El estado que el tutor mantiene por alumno está modelado en
[`student-profile.template.json`](student-profile.template.json): perfil, vocabulario
clasificado por dominio, gramática por fase, errores recurrentes y la última sesión.

## 3. Decisiones de diseño

Lo interesante de este proyecto no es que «hable idiomas» —eso lo hace cualquier
LLM— sino las restricciones que le meto para que se comporte como un buen profesor y
no como un loro:

- **No me fío del nivel autodeclarado (Step 2).** Antes de enseñar, hace una
  evaluación informal *en conversación*, no un test. Si alguien dice «intermedio»
  pero falla el presente, lo trata como principiante. Se enseña al nivel REAL.
- **Tope duro de 7 palabras nuevas por sesión.** La profundidad gana a la amplitud.
  El vocabulario siempre se enseña en contexto, nunca como lista suelta.
- **Repaso espaciado casero (Step 4).** El vocabulario vive en tres estados —NEW,
  LEARNING, KNOWN— y las palabras en LEARNING se cuelan en los warm-ups y role-plays
  hasta que se consolidan. Si una palabra KNOWN se usa mal, vuelve a LEARNING. Es
  spaced repetition sin tarjetas.
- **La gramática se desbloquea por accuracy, no por calendario.** No introduce un
  concepto nuevo hasta que el anterior se usa bien ~80% del tiempo. Orden natural:
  presente → pasado → futuro → condicional.
- **Hitos CEFR (A0→C1) con celebración explícita.** Da una sensación de avance real
  en una actividad donde el progreso es invisible hasta que de repente no lo es.
- **Role-play como herramienta principal (Step 5).** Mantiene el personaje, mete
  sorpresas («se nos han acabado los croissants») para forzar a improvisar, y escala
  la dificultad según el nivel. Al terminar: repaso de errores + 1-2 aciertos +
  vocabulario que faltó.
- **Análisis de imagen de escritura a mano (Step 6).** Si el alumno sube una foto de
  sus ejercicios, va línea a línea: cita lo que escribió, muestra la corrección,
  explica el porqué en una frase y detecta PATRONES, no solo errores sueltos.
- **Corrección con ritmo.** Formato fijo: lo que escribiste → versión correcta →
  por qué (una frase) → un ejemplo más. Los patrones se marcan tras 3+ repeticiones.
- **Registro y cultura (Step 8).** Formal vs. informal desde pronto (un registro
  equivocado suele ser peor que un fallo gramatical) y se enseña la versión que la
  gente habla de verdad, no la del libro de texto.

## 4. Reglas que gobiernan al agente

El bloque final del prompt es una lista de NEVER/ALWAYS que actúa como barandilla:
nunca hacer sentir tonto al alumno, nunca soltar una parrafada gramatical de más de
3 frases, nunca usar su idioma nativo en la parte de práctica salvo bloqueo total,
nunca pasar de 7 palabras nuevas. Y siempre priorizar producción (hablar/escribir)
sobre estudio pasivo, conectar lo nuevo con lo que ya sabe y celebrar las victorias
pequeñas. Si vuelve tras días sin practicar, se le da la bienvenida sin culpa.

## 5. Estructura

```
system-prompt.md                 ← el prompt de sistema (el entregable)
student-profile.template.json    ← esquema del estado que se mantiene por alumno
README.md                        ← este documento
```

## 6. Posibles ampliaciones

- Conectar `student-profile.template.json` a una memoria persistente real (un KV
  store o un RAG sobre las sesiones) para que el perfil sobreviva entre conversaciones.
- Generar audio (TTS) para la parte de listening y aceptar voz (STT) en los
  role-plays.
- Un pequeño front que renderice el informe semanal (Step 7) como dashboard.
