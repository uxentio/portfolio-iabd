# Tarea 7 - Control IoT con LLM local

autor - 1BDAT - Programacion para IA

Esta carpeta es la entrega entera. Para el **que** y el **porque**
de cada cosa, mirate `DocumentoTécnico.pdf`. Para hacerlo
funcionar, tira de este README.

---

## Que hace esto

Una app .NET MAUI donde le hablas (escribiendo o con voz) a un
LLM que va en local (LM Studio con Qwen3.5 0.8B). Cuando le pides
algo de las luces, el modelo llama a **una unica herramienta**
llamada `controlar_luces` con los parametros que haga falta. Esa llamada va por HTTP a Node-RED, Node-RED la
reempaqueta y la publica por MQTT al ESP32, y el ESP32 aplica lo
que toque en 3 LEDs fisicos y lo refleja en una pantalla OLED.

Lo que le puedes pasar (mas o menos):

- **verde / roja / azul**: estado de cada LED. Puede ser `off`,
  `on`, `dim` (brillo tenue), `blink` (parpadeo 400 ms), `fast`
  (parpadeo 150 ms), `slow` (parpadeo 1 s) o `fade` (respiracion).
- **modo_especial** (opcional): `semaforo`, `ola` o `morse`. Si
  eliges uno, los 3 parametros de arriba se ignoran.
- **texto_morse** y **color_morse**: solo si el modo es `morse`,
  indican el texto a emitir y por que LED.

Aparte hay un server MCP (LucesIoT.MCP) por si quieres controlar
las luces desde Claude Desktop u otro cliente MCP sin abrir la app.

---

## Que hay en esta carpeta

```
ARRANCAR_TODO.bat        <- script para arrancarlo todo con doble clic
DocumentoTecnico.pdf    <- memoria tecnica completa
LucesIoT.slnx            <- solucion de Visual Studio 2022
LucesIoT.MAUI/           <- app .NET MAUI (UI, voz, chat con el LLM)
LucesIoT.MCP/            <- servidor MCP
ESP32/                   <- firmware ESP32 (PlatformIO)
NodeRED/                 <- flow de Node-RED (importar en la UI)
```

---

## Que necesitas instalar

1. **Visual Studio 2022** con el workload de ".NET Multi-platform
   App UI development" (MAUI).
2. **LM Studio** (https://lmstudio.ai) y dentro cargar el modelo
   `qwen3.5-0.8b` (busca "unsloth/qwen3.5-0.8b-gguf Q8_0", pesa
   1,21 GB).
3. **Node.js** y Node-RED. En Windows lo mas facil es abrir una
   terminal y hacer `npm install -g node-red`.
4. **VS Code** con la extension **PlatformIO IDE** para compilar
   el firmware del ESP32 y flashearlo.

---

## Como ponerlo en marcha

### Lo mas rapido: doble clic en ARRANCAR_TODO.bat

El bat busca el CLI `lms` de LM Studio, carga el modelo y arranca
el servidor en el puerto 1234. Despues lanza Node-RED y la app.
Si alguna pieza no esta instalada te lo avisa.

Pre-requisito: haber flasheado el ESP32 al menos una vez con el
codigo de `ESP32/src/main.cpp`.

### Si prefieres hacerlo a mano (o el bat te falla)

1. Abre LM Studio, carga `qwen3.5-0.8b` y pulsa "Start Server"
   (puerto 1234).
2. En una terminal: `node-red`. Abre http://127.0.0.1:1880 e
   importa `NodeRED/flows.json` (menu -> Import -> seleccionar el
   fichero).
3. Compila y flashea el ESP32 con PlatformIO (abre la carpeta
   `ESP32/` en VS Code, pestaña PlatformIO, Upload). **Antes de
   flashear, edita en `main.cpp` las lineas `ssid` y `password`**
   con los de tu WiFi.
4. Abre `LucesIoT.slnx` en Visual Studio 2022, selecciona
   LucesIoT.MAUI como proyecto de inicio y dale a Run.

Si no los arrancas en ese orden (LM Studio, luego Node-RED, ESP32
y al final la app) a veces la app se queja al no encontrar a
alguno.

---

## Como usarlo

Cuando la app arranca tienes un chat y 3 circulitos que
representan los LEDs. Prueba a decirle cosas tipo:

- "enciende la luz verde"
- "pon la azul tenue y la roja parpadeando rapido"
- "haz que la verde respire"
- "verde lento, roja rapido, azul fija"
- "activa el modo semaforo"
- "haz la ola"
- "emite SOS en morse por la roja"
- "apaga todo"
- "¿que modos puedes controlar?" (responde con texto, no toca nada)

Tambien hay boton de microfono para voz (en español), y 4 botones
manuales por si quieres probar sin el modelo. Los botones de color
hacen ciclo off -> on -> blink -> off y solo afectan a su LED.

En la pestaña Ajustes puedes cambiar las IPs y el modelo sin
recompilar.

---

## Si algo no funciona

- **La app no conecta con LM Studio**: mira que LM Studio tenga el
  servidor arrancado y el puerto sea 1234.
- **Los comandos llegan a Node-RED pero no al ESP32**: mira que el
  ESP32 tenga WiFi y que el broker MQTT responda. El broker publico
  `test.mosquitto.org` a veces se cae, si eso pasa puedes cambiarlo
  a `broker.hivemq.com` en `main.cpp`.
- **La OLED no se enciende**: comprueba que la direccion I2C es
  0x3C. Casi todas las SSD1306 vienen asi, pero algunas clones son
  0x3D.
- **El modelo contesta con texto en vez de tocar la luz**: las
  palabras clave que detecta estan en `LmStudioService.cs`. Si
  uso alguna que no esta (ejemplo "ilumina" en vez de "enciende"),
  el modelo puede no activar el `tool_choice required`. La lista
  esta pensada para las intenciones habituales.

---

## Chuleta rapida de modos

| Estado | Que hace |
|---|---|
| off    | apagada |
| on     | encendida al maximo |
| dim    | tenue (PWM bajo) |
| blink  | parpadeo 400 ms |
| fast   | parpadeo 150 ms |
| slow   | parpadeo 1 s |
| fade   | respiracion (sinusoide PWM) |

| Modo especial | Que hace |
|---|---|
| semaforo | verde 3 s, ambar 1 s, rojo 3 s, en bucle |
| ola      | verde -> roja -> azul por turnos cada 500 ms |
| morse    | emite el texto_morse en puntos y rayas por el color_morse |
| ninguno  | no hace nada especial (se usan verde/roja/azul) |

---

Si te lias con algo, en el documento tecnico cuento mas en
detalle las movidas que me salieron mal y las librerias que acabe
usando.
