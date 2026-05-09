# Cargar codigo en la ESP32 con PlatformIO (VS Code)

Guia generica para dejar listo VS Code y subir cualquier proyecto
PlatformIO a una ESP32. Da igual como hayas llamado a tus carpetas o a los
archivos: lo importante es donde esta el `platformio.ini`.

---

## 1. Que necesitas

- **VS Code** -> https://code.visualstudio.com/
- **ESP32** (DevKit V1 o similar)
- **Cable USB** de datos (no sirven los de solo carga)
- Tu proyecto PlatformIO: cualquier carpeta que contenga un archivo
  `platformio.ini` en la raiz y una subcarpeta `src/` con el codigo
  (tipicamente `main.cpp` o `main.ino`)

> Como reconocer una carpeta PlatformIO: dentro tiene `platformio.ini` y
> `src/`. Si no los ves, esa no es la carpeta que tienes que abrir.

---

## 2. Instalar PlatformIO en VS Code

1. Abre VS Code.
2. `Ctrl+Shift+X` para ir a Extensiones.
3. Busca **PlatformIO IDE** (icono del alien naranja) e instala.
4. Tarda bastante la primera vez porque descarga su propio Python.
   Dejalo terminar.
5. **Reinicia VS Code** cuando acabe.
6. Al volver a abrir, en la barra lateral izquierda veras un icono de
   alien: esa es la pestana de PlatformIO.

### Drivers USB de la ESP32

Windows a veces no reconoce la placa. Instala el driver segun el chip USB
que lleve tu ESP32:

- **CP210x** (lo mas habitual) ->
  https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **CH340 / CH341** (placas clonicas baratas) ->
  https://www.wch-ic.com/downloads/CH341SER_ZIP.html

Para saber cual tienes: enchufa la placa y mira el Administrador de
Dispositivos de Windows. Si sale un dispositivo con `!` o como "USB
Serial", no tienes el driver. Prueba primero con CP210x.

Cuando este bien, aparece algo tipo `Silicon Labs CP210x (COM5)` o
`USB-SERIAL CH340 (COM3)`.

---

## 3. Abrir el proyecto

**Abre la carpeta que contiene `platformio.ini` como raiz.** Esto es
importante: si abres la carpeta padre, PlatformIO no detectara el proyecto.

1. En VS Code: **File > Open Folder**
2. Navega hasta la carpeta donde esta tu `platformio.ini`
3. Seleccionala y pulsa Aceptar

Si has hecho bien la apertura, en la barra azul de estado de abajo
apareceran los iconos de PlatformIO:

- Casa -> PIO Home
- Tick -> Build (compilar)
- Flecha "->" -> Upload (subir a la placa)
- Papelera -> Clean
- Enchufe -> Serial Monitor

Si no aparecen, cierra la carpeta y vuelve a abrirla apuntando al sitio
correcto.

---

## 4. Librerias

**No hay que instalarlas a mano.** Todas las librerias que necesite el
proyecto van declaradas dentro del `platformio.ini`, en la seccion
`lib_deps`. Por ejemplo:

```ini
[env:esp32]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps =
    knolleary/PubSubClient@^2.8
    adafruit/Adafruit SSD1306@^2.5.7
    adafruit/Adafruit GFX Library@^1.11.5
```

La primera vez que compiles, PlatformIO **las descarga solas** y las deja
en una carpeta oculta `.pio/libdeps/` dentro de tu proyecto. No tocas nada.

### Forzar la descarga sin compilar

Si quieres bajarlas antes de darle a Build, abre la terminal integrada
(`` Ctrl+` ``) y ejecuta:

```
pio pkg install
```

Veras como se baja cada una con su version. Si falla alguna normalmente es
por internet o firewall; reintentalo.

---

## 5. Configurar cosas tipicas antes de subir

Segun tu proyecto, probablemente tengas que editar algo en `src/main.cpp`
(o como se llame tu archivo principal) antes de subirlo. Los dos casos mas
comunes:

**WiFi** -> busca dos lineas parecidas a:
```cpp
const char* ssid = "TU_WIFI";
const char* password = "TU_PASSWORD";
```
Pon tu red y contrasena. **Tiene que ser una red de 2,4 GHz**, la ESP32
DevKit V1 no soporta 5 GHz.

**Broker MQTT** (si el proyecto usa MQTT) -> suele haber una linea con el
servidor, algo tipo:
```cpp
const char* mqtt_server = "test.mosquitto.org";
```
Normalmente no hace falta tocarlo.

---

## 6. Conectar la placa

1. Enchufa la ESP32 por USB.
2. En la barra azul de PlatformIO, al lado del icono del enchufe, deberia
   salir el puerto COM. Si no, abre **PIO Home > Devices** para ver que
   puertos detecta el sistema.
3. Si no sale ningun puerto, o no tienes el driver (paso 2) o el cable es
   de solo carga. Prueba con otro cable.

---

## 7. Compilar y subir

Desde los iconos de la barra azul de abajo:

1. **Tick (Build)** -> compila. La primera vez tarda varios minutos porque
   descarga toolchain y librerias. Las siguientes son mucho mas rapidas.
2. Cuando acabe con "SUCCESS" en verde, dale a la **flecha "->" (Upload)**.
   Compila (si hay cambios) y sube el binario a la placa.
3. Si durante el upload se queda atascado en "Connecting..." mas de 10
   segundos, **manten pulsado el boton BOOT** de la placa hasta que
   empiecen a salir los puntitos de progreso. Algunas DevKit lo necesitan.

Tambien puedes hacerlo desde la terminal integrada:

```
pio run              # solo compilar
pio run -t upload    # compilar y subir
```

---

## 8. Ver que funciona: monitor serie

Despues de subir, dale al **icono del enchufe** (Serial Monitor). Se abre
una terminal a la velocidad que indique tu `platformio.ini` en
`monitor_speed` (normalmente 115200).

Veras los mensajes que el codigo imprima con `Serial.println(...)`. Aqui
es donde confirmas que conecta a WiFi, a MQTT, o lo que sea que haga el
programa.

Para salir del monitor: `Ctrl+C`.

Desde la terminal:

```
pio device monitor
```

---

## 9. Problemas tipicos

- **"Error: Please specify upload_port"** -> no hay driver USB o la placa
  no esta conectada. Vuelve al paso 2.
- **Se queda en "Connecting..." al subir** -> manten pulsado BOOT hasta
  que empiece la subida.
- **"platformio.ini not found" o no salen los iconos** -> abriste la
  carpeta equivocada. Cierra y abre la carpeta que contiene directamente
  el `platformio.ini`.
- **Compila pero no conecta al WiFi** -> tu red es de 5 GHz, o el SSID
  o la contrasena estan mal escritos.
- **Librerias no se descargan** -> ejecuta `pio pkg install` en terminal
  para forzar. Si sigue fallando, borra la carpeta oculta `.pio/` del
  proyecto entera y vuelve a darle a Build.
- **Errores de compilacion raros despues de cambiar de rama o proyecto**
  -> icono de la papelera (Clean) y vuelve a Build.

Cualquier cosa me preguntas.
