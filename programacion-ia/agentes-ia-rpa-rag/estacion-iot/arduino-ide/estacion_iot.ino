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
 *
 *  LIBRERIAS NECESARIAS (instalar desde Gestor de Bibliotecas):
 *  - DHT sensor library (Adafruit)
 *  - Adafruit Unified Sensor
 *  - ArduinoJson (Benoit Blanchon)
 *  - Adafruit SSD1306
 *  - Adafruit GFX Library
 *
 *  PLACA: ESP32 Dev Module
 * ============================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WebServer.h>

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

// LED RGB
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
WebServer servidor(80);

unsigned long ultimoEnvio = 0;
bool oledDisponible = false;
String ciudadActual = "";
String nivelAlerta = "STANDBY";

// ==========================================
//  ESTRUCTURAS DE DATOS
// ==========================================

struct DatosSensores {
  float temperatura;
  float humedad;
  int   luz;
  int   luzPorcentaje;
  bool  presencia;
  float distancia;
  bool  valido;
};

// ==========================================
//  FUNCIONES DE SENSORES
// ==========================================

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

  // --- LDR: Nivel de luz (ADC 12 bits: 0=mucha luz, 4095=oscuro, invertido) ---
  datos.luz = analogRead(LDR_PIN);
  datos.luzPorcentaje = map(datos.luz, 4095, 0, 0, 100);
  datos.luzPorcentaje = constrain(datos.luzPorcentaje, 0, 100);

  // --- PIR: Presencia (HIGH si detecta movimiento) ---
  datos.presencia = digitalRead(PIR_PIN) == HIGH;

  // --- HC-SR04: Distancia por ultrasonidos ---
  // Pulso de 10 us en TRIG, mido el ancho del pulso en ECHO
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout 30 ms = ~5 m maximo (el HC-SR04 llega a 4 m en teoria)
  long duracion = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duracion == 0) {
    datos.distancia = -1;  // Sin eco = objeto fuera de rango o sensor desconectado
  } else {
    // Velocidad del sonido ~340 m/s = 0.034 cm/us, dividido entre 2 (ida y vuelta)
    datos.distancia = duracion * 0.034 / 2.0;
  }

  return datos;
}

// ==========================================
//  FUNCIONES DE ACTUADORES
// ==========================================

void setLedColor(int r, int g, int b) {
  analogWrite(LED_ROJO, r);
  analogWrite(LED_VERDE, g);
  analogWrite(LED_AZUL, b);
}

void setAlertaLED(const String& nivel) {
  if (nivel == "VERDE") {
    setLedColor(0, 255, 0);
  } else if (nivel == "AMARILLO") {
    setLedColor(255, 255, 0);
  } else if (nivel == "ROJO") {
    setLedColor(255, 0, 0);
    // Pitido corto para alertas rojas
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
  } else {
    // STANDBY o nivel no reconocido -> azul tenue
    setLedColor(0, 0, 50);
  }
}

void mostrarOLED(DatosSensores datos, String ciudad) {
  if (!oledDisponible) return;

  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);

  oled.setCursor(0, 0);
  oled.println("== ESTACION IoT ==");

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

  oled.setCursor(0, 24);
  oled.print("Luz: ");
  oled.print(datos.luzPorcentaje);
  oled.print("%");
  oled.print("  PIR: ");
  oled.println(datos.presencia ? "SI" : "NO");

  oled.setCursor(0, 36);
  if (datos.distancia > 0) {
    oled.print("Dist: ");
    oled.print(datos.distancia, 1);
    oled.println(" cm");
  } else {
    oled.println("Dist: ---");
  }

  oled.setCursor(0, 48);
  oled.print("Ubic: ");
  oled.println(ciudad.length() > 0 ? ciudad : "Sin ubicacion");

  oled.display();
}

// ==========================================
//  FUNCIONES DE COMUNICACION
// ==========================================

void conectarWiFi() {
  Serial.print("[WiFi] Conectando a ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
    setLedColor(0, 0, 100);
    delay(250);
    setLedColor(0, 0, 0);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("[WiFi] Conectado! IP: ");
    Serial.println(WiFi.localIP());
    setLedColor(0, 255, 0);
    delay(1000);
  } else {
    Serial.println();
    Serial.println("[WiFi] ERROR: No se pudo conectar");
    setLedColor(255, 0, 0);
  }
}

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
  http.setTimeout(10000);

  JsonDocument doc;
  doc["temp"]       = datos.temperatura;
  doc["hum"]        = datos.humedad;
  doc["luz"]        = datos.luzPorcentaje;
  doc["presencia"]  = datos.presencia;
  doc["distancia"]  = datos.distancia;
  doc["valido"]     = datos.valido;
  doc["ip"]         = WiFi.localIP().toString();
  doc["rssi"]       = WiFi.RSSI();
  doc["uptime"]     = millis() / 1000;

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
//  SERVIDOR WEB
// ==========================================

void handleAlerta() {
  if (servidor.hasArg("plain")) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, servidor.arg("plain"));

    if (!error) {
      nivelAlerta = doc["nivel"].as<String>();
      ciudadActual = doc["ciudad"].as<String>();
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

  // Pines
  pinMode(PIR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AZUL, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);

  digitalWrite(BUZZER_PIN, LOW);
  setLedColor(0, 0, 0);

  // DHT11
  dht.begin();
  Serial.println("[OK] DHT11 iniciado");

  // OLED
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

  // WiFi
  conectarWiFi();

  // Servidor web
  servidor.on("/alerta", HTTP_POST, handleAlerta);
  servidor.on("/estado", HTTP_GET, handleEstado);
  servidor.begin();
  Serial.print("[OK] Servidor web en http://");
  Serial.println(WiFi.localIP());

  // Esperar PIR
  Serial.println("[INFO] Estabilizando PIR (2s)...");
  delay(2000);

  // Pantalla inicial
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
  servidor.handleClient();

  unsigned long ahora = millis();
  if (ahora - ultimoEnvio >= INTERVALO_ENVIO) {
    ultimoEnvio = ahora;

    // 1. Leer sensores
    DatosSensores datos = leerSensores();

    // 2. Mostrar en OLED
    mostrarOLED(datos, ciudadActual);

    // 3. Debug Serial
    Serial.println("--- Lectura sensores ---");
    Serial.print("  Temp: "); Serial.print(datos.temperatura); Serial.println(" C");
    Serial.print("  Hum:  "); Serial.print(datos.humedad); Serial.println(" %");
    Serial.print("  Luz:  "); Serial.print(datos.luzPorcentaje); Serial.println(" %");
    Serial.print("  PIR:  "); Serial.println(datos.presencia ? "Movimiento" : "Nada");
    Serial.print("  Dist: "); Serial.print(datos.distancia); Serial.println(" cm");
    Serial.println("------------------------");

    // 4. Enviar a n8n
    String respuesta = enviarDatos(datos);

    // 5. Procesar respuesta
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

  delay(10);
}
