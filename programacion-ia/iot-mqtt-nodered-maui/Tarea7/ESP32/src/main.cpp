/*
  Tarea 7 - firmware del ESP32

  Esto controla los 3 LEDs y la pantallita OLED segun lo que me
  llega por MQTT. Partiendo del ejemplo base (turn_on / turn_off)
  lo he ido rehaciendo y ampliando un monton de veces hasta esto:

    - 7 modos por LED (off, on, dim, blink, fast, slow, fade)
    - modos especiales: semaforo, ola y morse (texto en puntos/rayas)
    - todo con PWM para que dim y fade queden suaves
    - en la OLED escribo las cosas en cristiano, no abreviaturas raras
    - ACK de vuelta para que la app sepa que el comando llego bien

  Truquillos importantes que he aprendido por el camino:
    - Nada de delay() dentro del loop, todo con millis() o se bloquea MQTT
    - PWM por hardware (LEDC) para el brillo, sin parpadeo visible
    - snprintf en vez de String para no fragmentar el heap del ESP32
*/

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// ========== CONFIG ==========

const char* ssid     = "TU_SSID_AQUI";
const char* password = "TU_PASSWORD_AQUI";

// broker publico -- si mosquitto se cae (pasa a veces) usar broker.hivemq.com
const char* mqttServer = "test.mosquitto.org";
const int   mqttPort   = 1883;
const char* mqttTopic  = "iabd2425/esp32/led";
const char* ackTopic   = "iabd2425/esp32/ack";  // confirmacion de vuelta a la app

// ========== Pines ==========

const int LED_ROJO  = 15;
const int LED_VERDE = 2;
const int LED_AZUL  = 4;

// PWM (LEDC) para controlar brillo -- uno por LED
// ref: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html
const int CANAL_ROJO  = 0;
const int CANAL_VERDE = 1;
const int CANAL_AZUL  = 2;
const int FREC_PWM    = 5000;  // 5 kHz, no parpadea visible
const int RES_PWM     = 8;     // 0..255

// OLED 128x64 I2C
#define ANCHO_OLED 128
#define ALTO_OLED  64
#define DIR_OLED   0x3C

Adafruit_SSD1306 oled(ANCHO_OLED, ALTO_OLED, &Wire, -1);

WiFiClient espClient;
PubSubClient client(espClient);

// ========== Estados de los LEDs ==========
// 0=off, 1=dim, 2=on, 3=blink, 4=fast, 5=slow, 6=fade
enum EstadoLed { OFF = 0, DIM = 1, ON = 2, BLINK = 3, FAST = 4, SLOW = 5, FADE = 6 };

int estadoRojo  = OFF;
int estadoVerde = OFF;
int estadoAzul  = OFF;

int msgCount = 0;

// timings por modo (ms)
const unsigned long INTERVALO_BLINK = 400;
const unsigned long INTERVALO_FAST  = 150;
const unsigned long INTERVALO_SLOW  = 1000;

// niveles de brillo (0..255)
const int NIVEL_OFF  = 0;
const int NIVEL_DIM  = 20;   // bajito, casi vela
const int NIVEL_ON   = 255;

// control de parpadeo por LED (cada uno con su timer)
unsigned long ultimoCambioR = 0, ultimoCambioV = 0, ultimoCambioA = 0;
bool visibleR = true, visibleV = true, visibleA = true;

// fade: sinusoide comun para los 3 (suben y bajan juntos)
unsigned long inicioFade = 0;
const unsigned long PERIODO_FADE = 2000;

// presets
String preset = "ninguno";
unsigned long inicioPreset = 0;

// ========== Morse ==========
// el estandar (wikipedia) dice que raya=3 puntos, y los gaps son 3 y 7 puntos.
// lo respeto mas o menos: https://es.wikipedia.org/wiki/C%C3%B3digo_morse
const unsigned long UNIDAD_MORSE = 350;  // ms de un "punto" (mas lento para que se vea bien la diferencia con la raya)

String morseMensaje    = "";        // la cadena a emitir (en . - y espacios)
int    morsePaso       = 0;         // indice del simbolo actual dentro de la cadena
unsigned long morseUltimo = 0;      // cuando empezo el simbolo actual
bool   morseEncendido  = false;     // si ahora mismo el LED esta encendido o en gap
int    morseCanal      = CANAL_VERDE;  // canal PWM a usar para emitir

// tabla de morse (solo letras A-Z y numeros 0-9, suficiente para la demo)
const char* morseCode(char c) {
  switch (toupper(c)) {
    case 'A': return ".-";    case 'B': return "-...";  case 'C': return "-.-.";
    case 'D': return "-..";   case 'E': return ".";     case 'F': return "..-.";
    case 'G': return "--.";   case 'H': return "....";  case 'I': return "..";
    case 'J': return ".---";  case 'K': return "-.-";   case 'L': return ".-..";
    case 'M': return "--";    case 'N': return "-.";    case 'O': return "---";
    case 'P': return ".--.";  case 'Q': return "--.-";  case 'R': return ".-.";
    case 'S': return "...";   case 'T': return "-";     case 'U': return "..-";
    case 'V': return "...-";  case 'W': return ".--";   case 'X': return "-..-";
    case 'Y': return "-.--";  case 'Z': return "--..";
    case '0': return "-----"; case '1': return ".----"; case '2': return "..---";
    case '3': return "...--"; case '4': return "....-"; case '5': return ".....";
    case '6': return "-...."; case '7': return "--..."; case '8': return "---..";
    case '9': return "----.";
    case ' ': return " ";
    default:  return "";
  }
}

// convierte un texto ("SOS", "ANTONIO"...) en la cadena rara que usa
// actualizarMorse(). Uso '.' y '-' para los simbolos, 'g' para el gap dentro
// de la letra, '/' para el gap entre letras y espacio para el gap entre
// palabras. Lo de la 'g' lo meti a mano para que entre dos puntos seguidos
// de la misma letra hubiera un OFF visible, si no se veia todo pegado.
void prepararMorse(const char* texto) {
  morseMensaje = "";
  for (int i = 0; texto[i] != '\0' && i < 30; i++) {
    if (texto[i] == ' ') {
      morseMensaje += " ";
      continue;
    }
    const char* sim = morseCode(texto[i]);
    // meto cada simbolo con 'g' entre medias
    for (int j = 0; sim[j] != '\0'; j++) {
      morseMensaje += sim[j];
      if (sim[j+1] != '\0') morseMensaje += "g";  // gap entre simbolos
    }
    morseMensaje += "/";  // gap entre letras
  }
  morsePaso = 0;
  morseUltimo = millis();
  morseEncendido = false;
}

// ========== OLED ==========

const char* nombreEstado(int s) {
  switch (s) {
    case ON:    return "encendida";
    case DIM:   return "tenue";
    case BLINK: return "parpadea";
    case FAST:  return "rapido";
    case SLOW:  return "lento";
    case FADE:  return "respira";
    default:    return "apagada";
  }
}

void oledShow(const char* titulo, const char* texto) {
  oled.clearDisplay();
  oled.setTextSize(2);
  oled.setCursor(0, 0);
  oled.println(titulo);
  oled.drawLine(0, 20, 127, 20, SSD1306_WHITE);
  oled.setTextSize(1);
  oled.setCursor(0, 28);
  oled.println(texto);
  oled.display();
}

// la pantalla de siempre: bolita, nombre y lo que esta haciendo cada LED
void oledEstado() {
  oled.clearDisplay();

  oled.setTextSize(1);
  oled.setCursor(0, 0);
  if (preset == "semaforo") {
    oled.println("MODO: Semaforo");
  } else if (preset == "ola") {
    oled.println("MODO: Ola");
  } else if (preset == "morse") {
    oled.println("MODO: Morse");
  } else {
    oled.println("Tarea 7 - IoT");
  }
  oled.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  // en modo morse muestro lo que esta emitiendo en vez de los 3 LEDs
  if (preset == "morse") {
    oled.setCursor(0, 18);
    oled.print("Emitiendo:");
    oled.setTextSize(2);
    oled.setCursor(0, 30);
    // limpio el mensaje: quito las 'g' (gaps internos de una letra, no se
    // muestran) y los '/' los paso a espacio (gap entre letras). Muestro
    // hasta 10 chars porque en tam 2 no cabe mas
    String limpio = "";
    for (int i = 0; i < (int)morseMensaje.length() && limpio.length() < 10; i++) {
      char c = morseMensaje[i];
      if (c == 'g') continue;          // gap entre simbolos: no lo pinto
      if (c == '/') limpio += ' ';     // gap entre letras: espacio
      else          limpio += c;       // punto o raya
    }
    oled.print(limpio);
    oled.setTextSize(1);
  } else {
    int y = 16;
    int estados[3]   = { estadoVerde, estadoRojo, estadoAzul };
    const char* nombres[3] = { "VERDE", "ROJA ", "AZUL " };

    for (int i = 0; i < 3; i++) {
      if (estados[i] != OFF)
        oled.fillCircle(5, y + 3, 3, SSD1306_WHITE);
      else
        oled.drawCircle(5, y + 3, 3, SSD1306_WHITE);

      oled.setCursor(14, y);
      oled.print(nombres[i]);
      oled.print(" ");
      oled.print(nombreEstado(estados[i]));
      y += 11;
    }
  }

  oled.setCursor(0, 54);
  oled.print("Msgs recibidos: ");
  oled.print(msgCount);
  oled.display();
}

void oledAck() {
  oled.clearDisplay();
  oled.setTextSize(2);
  oled.setCursor(8, 10);
  oled.println("OK");
  oled.setTextSize(1);
  oled.setCursor(0, 40);
  oled.println("Comando recibido");
  oled.setCursor(0, 52);
  oled.print("y aplicado");
  oled.display();
}

// ========== Mandar los estados a los pines con PWM ==========

int nivelParaEstado(int estado, bool visible, int fadeLvl) {
  switch (estado) {
    case OFF:   return NIVEL_OFF;
    case DIM:   return NIVEL_DIM;
    case ON:    return NIVEL_ON;
    case BLINK:
    case FAST:
    case SLOW:  return visible ? NIVEL_ON : NIVEL_OFF;
    case FADE:  return fadeLvl;
    default:    return NIVEL_OFF;
  }
}

void aplicarLeds() {
  unsigned long t = millis() - inicioFade;
  float fase = (2.0f * PI * (t % PERIODO_FADE)) / (float)PERIODO_FADE;
  int fadeLvl = (int)((sin(fase) * 0.5f + 0.5f) * NIVEL_ON);

  ledcWrite(CANAL_VERDE, nivelParaEstado(estadoVerde, visibleV, fadeLvl));
  ledcWrite(CANAL_ROJO,  nivelParaEstado(estadoRojo,  visibleR, fadeLvl));
  ledcWrite(CANAL_AZUL,  nivelParaEstado(estadoAzul,  visibleA, fadeLvl));
}

int parseEstado(const char* str) {
  if (strcmp(str, "on")    == 0) return ON;
  if (strcmp(str, "dim")   == 0) return DIM;
  if (strcmp(str, "blink") == 0) return BLINK;
  if (strcmp(str, "fast")  == 0) return FAST;
  if (strcmp(str, "slow")  == 0) return SLOW;
  if (strcmp(str, "fade")  == 0) return FADE;
  return OFF;
}

// ========== Callback MQTT ==========

// el JSON puede traer:
//   {"verde":"on","roja":"off","azul":"blink"}   -> control por LED
//   {"preset":"semaforo"}                        -> modo secuencia
//   {"preset":"ninguno"}                         -> salir del preset
void callback(char* topic, byte* payload, unsigned int length) {
  char buf[256];
  unsigned int len = length < 255 ? length : 255;
  memcpy(buf, payload, len);
  buf[len] = '\0';

  Serial.print("MQTT [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(buf);
  msgCount++;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, buf);

  if (err) {
    Serial.print("Error parseando JSON: ");
    Serial.println(err.c_str());
    oledShow("JSON Error", err.c_str());
    return;
  }

  // rama 1: morse -- {"morse":"SOS","color":"verde"}
  // uso !isNull() en vez de is<const char*>() porque el segundo me fallaba en ArduinoJson v7
  if (!doc["morse"].isNull()) {
    // ojo: pido el string con default "" porque si el LLM me manda un numero o un null
    // casteo crudo devuelve nullptr y crashea. Me paso una vez, no vuelve a pasar.
    const char* textoMorse = doc["morse"] | "";
    const char* color = doc["color"] | "verde";
    if      (strcmp(color, "roja") == 0) morseCanal = CANAL_ROJO;
    else if (strcmp(color, "azul") == 0) morseCanal = CANAL_AZUL;
    else                                  morseCanal = CANAL_VERDE;
    preset = "morse";
    estadoRojo = estadoVerde = estadoAzul = OFF;  // apago todo antes de emitir
    aplicarLeds();
    prepararMorse(textoMorse);
    Serial.printf("-> morse: %s\n", textoMorse);
  }
  // rama 2: preset
  else if (!doc["preset"].isNull()) {
    const char* presetStr = doc["preset"] | "ninguno";  // mismo motivo que arriba
    preset = String(presetStr);
    if (preset == "semaforo" || preset == "ola") {
      inicioPreset = millis();
      Serial.printf("-> preset %s activado\n", preset.c_str());
    } else {
      estadoRojo = estadoVerde = estadoAzul = OFF;
    }
  }
  // rama 3: control por LED
  else {
    preset = "ninguno";
    estadoVerde = parseEstado(doc["verde"] | "off");
    estadoRojo  = parseEstado(doc["roja"]  | "off");
    estadoAzul  = parseEstado(doc["azul"]  | "off");
  }

  visibleR = visibleV = visibleA = true;
  ultimoCambioR = ultimoCambioV = ultimoCambioA = millis();
  inicioFade = millis();

  // feedback visual breve + ACK al topic de vuelta
  // ojo: NO uso delay() aqui porque dentro del callback bloquearia client.loop()
  // y el broker podria desconectarme. Muestro "OK" solo un frame y ya
  oledAck();
  aplicarLeds();
  oledEstado();

  char ackPayload[128];
  snprintf(ackPayload, sizeof(ackPayload),
           "{\"ok\":true,\"verde\":%d,\"roja\":%d,\"azul\":%d,\"preset\":\"%s\"}",
           estadoVerde, estadoRojo, estadoAzul, preset.c_str());
  client.publish(ackTopic, ackPayload);

  Serial.printf("-> R:%d V:%d A:%d preset:%s\n",
                estadoRojo, estadoVerde, estadoAzul, preset.c_str());
}

// ========== Reconexion MQTT (no bloqueante) ==========

unsigned long ultimoReintento = 0;

void reconnect() {
  if (client.connected()) return;
  if (millis() - ultimoReintento < 3000) return;
  ultimoReintento = millis();

  Serial.print("Conectando MQTT...");
  oledShow("MQTT", "Conectando...");

  char cid[20];
  snprintf(cid, sizeof(cid), "ESP32_%04X", (unsigned int)random(0xffff));

  if (client.connect(cid)) {
    Serial.println(" OK!");
    client.subscribe(mqttTopic);
    oledShow("MQTT OK!", "Esperando cmds...");
  } else {
    Serial.printf(" fallo (rc=%d)\n", client.state());
    oledShow("MQTT Error", "Reintentando...");
  }
}

// ========== Parpadeos por LED ==========

bool avanzarParpadeo(int estado, unsigned long &ultimo, bool &visible) {
  unsigned long intervalo = 0;
  switch (estado) {
    case BLINK: intervalo = INTERVALO_BLINK; break;
    case FAST:  intervalo = INTERVALO_FAST;  break;
    case SLOW:  intervalo = INTERVALO_SLOW;  break;
    default: return false;
  }
  if (millis() - ultimo >= intervalo) {
    ultimo = millis();
    visible = !visible;
    return true;
  }
  return false;
}

// ========== Presets ==========

// semaforo: verde 3s -> ambar (verde+rojo) 1s -> rojo 3s -> vuelve
void presetSemaforo(unsigned long t) {
  unsigned long fase = t % 7000;
  if (fase < 3000) {
    estadoVerde = ON;  estadoRojo = OFF; estadoAzul = OFF;
  } else if (fase < 4000) {
    estadoVerde = ON;  estadoRojo = ON;  estadoAzul = OFF;
  } else {
    estadoVerde = OFF; estadoRojo = ON;  estadoAzul = OFF;
  }
}

// ola: cada LED se enciende por turnos (tipo estadio), 500 ms cada uno
// verde -> roja -> azul -> verde ... -- da sensacion de movimiento
void presetOla(unsigned long t) {
  unsigned long paso = (t / 500) % 3;
  estadoVerde = (paso == 0) ? ON : OFF;
  estadoRojo  = (paso == 1) ? ON : OFF;
  estadoAzul  = (paso == 2) ? ON : OFF;
}

void actualizarPreset() {
  unsigned long t = millis() - inicioPreset;
  if      (preset == "semaforo") presetSemaforo(t);
  else if (preset == "ola")      presetOla(t);
}

// esto lo llamo desde el loop, va sacando simbolos uno a uno segun pasa el tiempo
void actualizarMorse() {
  if (preset != "morse" || morseMensaje.length() == 0) return;
  // cuando termino la cadena, la repito desde el principio. Asi el morse
  // se queda emitiendo hasta que el usuario mande apagar. El "/" final del
  // mensaje da un gap natural entre repeticiones.
  if (morsePaso >= (int)morseMensaje.length()) {
    morsePaso = 0;
    morseUltimo = millis();
    ledcWrite(morseCanal, 0);
    morseEncendido = false;
    return;
  }

  char simbolo = morseMensaje[morsePaso];
  unsigned long duracion = 0;
  bool encender = false;

  switch (simbolo) {
    case '.': duracion = UNIDAD_MORSE;     encender = true;  break;
    case '-': duracion = UNIDAD_MORSE * 3; encender = true;  break;
    case 'g': duracion = UNIDAD_MORSE;     encender = false; break;  // gap simbolo
    case '/': duracion = UNIDAD_MORSE * 3; encender = false; break;  // gap letra
    case ' ': duracion = UNIDAD_MORSE * 7; encender = false; break;  // gap palabra
    default:  duracion = UNIDAD_MORSE;     encender = false; break;
  }

  unsigned long t = millis() - morseUltimo;

  if (!morseEncendido && encender) {
    ledcWrite(morseCanal, NIVEL_ON);
    morseEncendido = true;
  } else if (morseEncendido && !encender) {
    ledcWrite(morseCanal, 0);
    morseEncendido = false;
  }

  if (t >= duracion) {
    // apago durante 1 unidad (gap entre puntos/rayas dentro de la misma letra)
    ledcWrite(morseCanal, 0);
    morseEncendido = false;
    morsePaso++;
    morseUltimo = millis();
  }
}

// ========== setup / loop ==========

void setup() {
  Serial.begin(115200);
  Serial.println("Tarea 7 - ESP32 IoT LED Control");

  Wire.begin(21, 22);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, DIR_OLED)) {
    Serial.println("No se encontro OLED, sigo sin ella");
  }
  oled.setTextColor(SSD1306_WHITE);
  oled.clearDisplay();
  oledShow("Tarea 7 IoT", "Iniciando...");

  // PWM: configuro canales y los asocio a los pines
  ledcSetup(CANAL_ROJO,  FREC_PWM, RES_PWM);
  ledcSetup(CANAL_VERDE, FREC_PWM, RES_PWM);
  ledcSetup(CANAL_AZUL,  FREC_PWM, RES_PWM);
  ledcAttachPin(LED_ROJO,  CANAL_ROJO);
  ledcAttachPin(LED_VERDE, CANAL_VERDE);
  ledcAttachPin(LED_AZUL,  CANAL_AZUL);
  ledcWrite(CANAL_ROJO, 0);
  ledcWrite(CANAL_VERDE, 0);
  ledcWrite(CANAL_AZUL, 0);

  Serial.print("Conectando WiFi");
  oledShow("WiFi", ssid);
  WiFi.begin(ssid, password);
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 40) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(" FALLO! Revisa SSID/password");
    oledShow("WiFi ERROR", "Revisa config");
    delay(5000);
    ESP.restart();
  }
  Serial.println(" conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  String ipStr = "IP: " + WiFi.localIP().toString();
  oledShow("WiFi OK!", ipStr.c_str());
  delay(2000);

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  reconnect();
  oledEstado();
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  if (preset == "semaforo" || preset == "ola") actualizarPreset();
  if (preset == "morse") actualizarMorse();

  bool cambio = false;
  cambio |= avanzarParpadeo(estadoRojo,  ultimoCambioR, visibleR);
  cambio |= avanzarParpadeo(estadoVerde, ultimoCambioV, visibleV);
  cambio |= avanzarParpadeo(estadoAzul,  ultimoCambioA, visibleA);

  bool hayFade = (estadoRojo == FADE || estadoVerde == FADE || estadoAzul == FADE);

  if (cambio || hayFade || preset == "semaforo" || preset == "ola") {
    aplicarLeds();
  }

  // refresco OLED solo si cambia algun estado macro
  static int lastR = -1, lastV = -1, lastA = -1;
  static String lastPreset = "";
  if (estadoRojo != lastR || estadoVerde != lastV || estadoAzul != lastA || preset != lastPreset) {
    oledEstado();
    lastR = estadoRojo; lastV = estadoVerde; lastA = estadoAzul; lastPreset = preset;
  }
}
