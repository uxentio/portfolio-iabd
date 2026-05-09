/*
 * ============================================
 *  ESTACION IoT INTELIGENTE - ESP32
 * ============================================
 *  Proyecto: Estacion de monitorizacion ambiental
 *  Sensores: DHT11, PIR, LDR, HC-SR04
 *  Actuadores: OLED 0.96", LED RGB, Buzzer
 *  Comunicacion: WiFi + HTTP POST a n8n
 *
 *  Alumno: autor
 *  Asignatura: Programacion para IA - CE en IA y Big Data
 * ============================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==========================================
//  CONFIGURACION - MODIFICA ESTOS VALORES
// ==========================================

// WiFi
const char* WIFI_SSID     = "Archer";
const char* WIFI_PASSWORD = "Antain81";

// n8n Webhook URL
// Cambiar segun donde este corriendo n8n:
//   - Servidor del profesor (cuando este disponible):
//     "https://progian8n.duckdns.org/webhook/estacion-iot"
//   - n8n local en Docker + ngrok (lo que uso yo):
const char* N8N_WEBHOOK_URL = "https://tapping-widget-entering.ngrok-free.dev/webhook/estacion-iot";

// Intervalo de envio de datos (milisegundos)
const unsigned long INTERVALO_ENVIO = 30000; // 30 segundos

// ==========================================
//  PINES - SENSORES
// ==========================================

// DHT11 - Temperatura y Humedad
#define DHT_PIN     4
#define DHT_TYPE    DHT11

// PIR HC-SR501 - Deteccion de presencia
#define PIR_PIN     15

// LDR - Fotorresistencia (luz ambiente)
#define LDR_PIN     34  // Pin analogico

// HC-SR04 - Sensor ultrasonico (distancia)
#define TRIG_PIN    5
#define ECHO_PIN    18

// ==========================================
//  PINES - ACTUADORES
// ==========================================

// LED RGB (anodo comun o catodo comun)
#define LED_ROJO    2
#define LED_VERDE   16
#define LED_AZUL    17

// Buzzer activo
#define BUZZER_PIN  19

// OLED 0.96" I2C
#define OLED_WIDTH  128
#define OLED_HEIGHT 64
#define OLED_ADDR   0x3C

// ==========================================
//  OBJETOS GLOBALES
// ==========================================

DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 oled(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);

unsigned long ultimoEnvio = 0;
bool oledDisponible = false;

// ==========================================
//  ESTRUCTURAS DE DATOS
// ==========================================

struct DatosSensores {
  float temperatura;
  float humedad;
  int   luz;          // 0-4095 (0=mucha luz, 4095=oscuro)
  int   luzPorcentaje; // 0-100% (0=oscuro, 100=mucha luz)
  bool  presencia;
  float distancia;    // cm
  bool  valido;       // si la lectura es correcta
};

// ==========================================
//  FUNCIONES DE SENSORES
// ==========================================

// Lee todos los sensores y devuelve struct con datos
DatosSensores leerSensores() {
  DatosSensores datos;
  datos.valido = true;

  // --- DHT11: Temperatura y Humedad ---
  datos.temperatura = dht.readTemperature();
  datos.humedad = dht.readHumidity();

  if (isnan(datos.temperatura) || isnan(datos.humedad)) {
    Serial.println("[ERROR] Fallo al leer DHT11");
    datos.temperatura = -999;
    datos.humedad = -999;
    datos.valido = false;
  }

  // --- LDR: Nivel de luz ---
  datos.luz = analogRead(LDR_PIN);
  // Convertir a porcentaje (invertido: mas valor analogico = menos luz)
  datos.luzPorcentaje = map(datos.luz, 4095, 0, 0, 100);
  datos.luzPorcentaje = constrain(datos.luzPorcentaje, 0, 100);

  // --- PIR: Presencia ---
  datos.presencia = digitalRead(PIR_PIN) == HIGH;

  // --- HC-SR04: Distancia ---
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duracion = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30ms
  if (duracion == 0) {
    datos.distancia = -1; // sin eco
  } else {
    datos.distancia = duracion * 0.034 / 2.0; // cm
  }

  return datos;
}

// ==========================================
//  FUNCIONES DE ACTUADORES
// ==========================================

// Establece color del LED RGB (0-255 cada canal)
void setLedColor(int r, int g, int b) {
  analogWrite(LED_ROJO, r);
  analogWrite(LED_VERDE, g);
  analogWrite(LED_AZUL, b);
}

// LED segun nivel de alerta
void setAlertaLED(const String& nivel) {
  if (nivel == "VERDE") {
    setLedColor(0, 255, 0);       // Todo bien
  } else if (nivel == "AMARILLO") {
    setLedColor(255, 255, 0);     // Atencion
  } else if (nivel == "ROJO") {
    setLedColor(255, 0, 0);       // Alerta
    // Buzzer suena en alerta roja
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
  } else {
    setLedColor(0, 0, 50);        // Azul tenue = standby
  }
}

// Muestra datos en OLED
void mostrarOLED(DatosSensores datos, String ciudad) {
  if (!oledDisponible) return;

  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);

  // Linea 1: Titulo
  oled.setCursor(0, 0);
  oled.println("== ESTACION IoT ==");

  // Linea 2: Temperatura y Humedad
  oled.setCursor(0, 12);
  if (datos.temperatura != -999) {
    oled.print("Temp: ");
    oled.print(datos.temperatura, 1);
    oled.print("C  Hum: ");
    oled.print(datos.humedad, 0);
    oled.println("%");
  } else {
    oled.println("Temp: ERROR");
  }

  // Linea 3: Luz
  oled.setCursor(0, 24);
  oled.print("Luz: ");
  oled.print(datos.luzPorcentaje);
  oled.print("%");

  // Linea 4: Presencia
  oled.print("  PIR: ");
  oled.println(datos.presencia ? "SI" : "NO");

  // Linea 5: Distancia
  oled.setCursor(0, 36);
  if (datos.distancia > 0) {
    oled.print("Dist: ");
    oled.print(datos.distancia, 1);
    oled.println(" cm");
  } else {
    oled.println("Dist: ---");
  }

  // Linea 6: Ciudad (de geolocalizacion)
  oled.setCursor(0, 48);
  oled.print("Ubic: ");
  oled.println(ciudad.length() > 0 ? ciudad : "Sin ubicacion");

  oled.display();
}

// ==========================================
//  FUNCIONES DE COMUNICACION
// ==========================================

// Conecta al WiFi
void conectarWiFi() {
  Serial.print("[WiFi] Conectando a ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;

    // Parpadeo azul mientras conecta
    setLedColor(0, 0, 100);
    delay(250);
    setLedColor(0, 0, 0);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("[WiFi] Conectado! IP: ");
    Serial.println(WiFi.localIP());
    setLedColor(0, 255, 0); // Verde = conectado
    delay(1000);
  } else {
    Serial.println();
    Serial.println("[WiFi] ERROR: No se pudo conectar");
    setLedColor(255, 0, 0); // Rojo = error
  }
}

// Envia datos a n8n por HTTP POST
String enviarDatos(DatosSensores datos) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] Sin WiFi, reconectando...");
    conectarWiFi();
    if (WiFi.status() != WL_CONNECTED) {
      return "ERROR_WIFI";
    }
  }

  HTTPClient http;
  http.begin(N8N_WEBHOOK_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000); // 10 segundos timeout

  // Construir JSON
  JsonDocument doc;
  doc["temp"]       = datos.temperatura;
  doc["hum"]        = datos.humedad;
  doc["luz"]        = datos.luzPorcentaje;
  doc["presencia"]  = datos.presencia;
  doc["distancia"]  = datos.distancia;
  doc["valido"]     = datos.valido;
  doc["ip"]         = WiFi.localIP().toString();
  doc["rssi"]       = WiFi.RSSI(); // Fuerza senal WiFi
  doc["uptime"]     = millis() / 1000; // Segundos encendido

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("[HTTP] Enviando: ");
  Serial.println(jsonString);

  int httpCode = http.POST(jsonString);
  String respuesta = "";

  if (httpCode > 0) {
    respuesta = http.getString();
    Serial.print("[HTTP] Respuesta (");
    Serial.print(httpCode);
    Serial.print("): ");
    Serial.println(respuesta);
  } else {
    Serial.print("[HTTP] Error: ");
    Serial.println(http.errorToString(httpCode));
    respuesta = "ERROR_HTTP";
  }

  http.end();
  return respuesta;
}

// ==========================================
//  SERVIDOR WEB PARA RECIBIR ORDENES
// ==========================================

#include <WebServer.h>
WebServer servidor(80);

String ciudadActual = "";
String nivelAlerta = "STANDBY";

// Endpoint: n8n envia alerta y color LED
void handleAlerta() {
  if (servidor.hasArg("plain")) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, servidor.arg("plain"));

    if (!error) {
      nivelAlerta = doc["nivel"].as<String>();   // VERDE, AMARILLO, ROJO
      ciudadActual = doc["ciudad"].as<String>(); // Ciudad detectada

      setAlertaLED(nivelAlerta);

      Serial.print("[ALERTA] Nivel: ");
      Serial.print(nivelAlerta);
      Serial.print(" | Ciudad: ");
      Serial.println(ciudadActual);

      servidor.send(200, "application/json", "{\"ok\":true}");
    } else {
      servidor.send(400, "application/json", "{\"error\":\"JSON invalido\"}");
    }
  } else {
    servidor.send(400, "application/json", "{\"error\":\"Sin body\"}");
  }
}

// Endpoint: estado actual de los sensores
void handleEstado() {
  DatosSensores datos = leerSensores();

  JsonDocument doc;
  doc["temp"]      = datos.temperatura;
  doc["hum"]       = datos.humedad;
  doc["luz"]       = datos.luzPorcentaje;
  doc["presencia"] = datos.presencia;
  doc["distancia"] = datos.distancia;
  doc["alerta"]    = nivelAlerta;
  doc["ciudad"]    = ciudadActual;
  doc["uptime"]    = millis() / 1000;

  String json;
  serializeJson(doc, json);
  servidor.send(200, "application/json", json);
}

// ==========================================
//  SETUP
// ==========================================

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("=============================");
  Serial.println(" ESTACION IoT - Iniciando...");
  Serial.println("=============================");

  // Inicializar pines
  pinMode(PIR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AZUL, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);

  // Buzzer apagado
  digitalWrite(BUZZER_PIN, LOW);

  // LED RGB apagado
  setLedColor(0, 0, 0);

  // Inicializar DHT11
  dht.begin();
  Serial.println("[OK] DHT11 iniciado");

  // Inicializar OLED
  if (oled.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    oledDisponible = true;
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setTextColor(SSD1306_WHITE);
    oled.setCursor(10, 25);
    oled.println("Conectando WiFi...");
    oled.display();
    Serial.println("[OK] OLED iniciado");
  } else {
    Serial.println("[AVISO] OLED no detectado, continuando sin pantalla");
  }

  // Conectar WiFi
  conectarWiFi();

  // Iniciar servidor web (para recibir ordenes de n8n)
  servidor.on("/alerta", HTTP_POST, handleAlerta);
  servidor.on("/estado", HTTP_GET, handleEstado);
  servidor.begin();
  Serial.print("[OK] Servidor web en http://");
  Serial.println(WiFi.localIP());

  // Esperar 2 seg para que el PIR se estabilice
  Serial.println("[INFO] Esperando estabilizacion PIR (2s)...");
  delay(2000);

  // Mostrar pantalla inicial
  if (oledDisponible) {
    oled.clearDisplay();
    oled.setCursor(10, 10);
    oled.println("ESTACION IoT");
    oled.setCursor(10, 25);
    oled.print("IP: ");
    oled.println(WiFi.localIP());
    oled.setCursor(10, 40);
    oled.println("Listo!");
    oled.display();
  }

  setAlertaLED("VERDE");
  Serial.println("=============================");
  Serial.println(" ESTACION IoT - LISTA!");
  Serial.println("=============================");
}

// ==========================================
//  LOOP PRINCIPAL
// ==========================================

void loop() {
  // Atender peticiones web (alertas de n8n)
  servidor.handleClient();

  // Enviar datos cada INTERVALO_ENVIO milisegundos
  unsigned long ahora = millis();
  if (ahora - ultimoEnvio >= INTERVALO_ENVIO) {
    ultimoEnvio = ahora;

    // 1. Leer sensores
    DatosSensores datos = leerSensores();

    // 2. Mostrar en OLED
    mostrarOLED(datos, ciudadActual);

    // 3. Mostrar en Serial (debug)
    Serial.println("--- Lectura sensores ---");
    Serial.print("  Temp: "); Serial.print(datos.temperatura); Serial.println(" C");
    Serial.print("  Hum:  "); Serial.print(datos.humedad); Serial.println(" %");
    Serial.print("  Luz:  "); Serial.print(datos.luzPorcentaje); Serial.println(" %");
    Serial.print("  PIR:  "); Serial.println(datos.presencia ? "Movimiento" : "Nada");
    Serial.print("  Dist: "); Serial.print(datos.distancia); Serial.println(" cm");
    Serial.println("------------------------");

    // 4. Enviar a n8n
    String respuesta = enviarDatos(datos);

    // 5. Procesar respuesta de n8n (si devuelve alerta)
    if (respuesta != "ERROR_WIFI" && respuesta != "ERROR_HTTP" && respuesta.length() > 2) {
      JsonDocument respDoc;
      DeserializationError error = deserializeJson(respDoc, respuesta);
      if (!error && respDoc.containsKey("nivel")) {
        nivelAlerta = respDoc["nivel"].as<String>();
        ciudadActual = respDoc["ciudad"].as<String>();
        setAlertaLED(nivelAlerta);
      }
    }
  }

  // Pequena pausa para no saturar CPU
  delay(10);
}
