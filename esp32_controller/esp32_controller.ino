// Nexus Connect controller registration client, Version 1.
// This sketch only registers the ESP32 and receives its player assignment.

#include <WiFi.h>
#include <PubSubClient.h>
#include "esp_mac.h"

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqttServer = "192.168.68.74";

const char* registerTopic = "controller/register";
const char* assignTopic = "controller/assign";

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

String controllerID = "";
int assignedPlayer = 0;
unsigned long lastRegistrationTime = 0;

String getControllerID() {
  uint8_t mac[6];

  esp_read_mac(mac, ESP_MAC_WIFI_STA);

  char id[18];

  snprintf(
    id,
    sizeof(id),
    "%02X:%02X:%02X:%02X:%02X:%02X",
    mac[0],
    mac[1],
    mac[2],
    mac[3],
    mac[4],
    mac[5]
  );

  return String(id);
}

String extractStringValue(String payload, String key) {
  String pattern = "\"" + key + "\":\"";
  int start = payload.indexOf(pattern);

  if (start < 0) {
    return "";
  }

  start += pattern.length();
  int end = payload.indexOf("\"", start);

  if (end < 0) {
    return "";
  }

  return payload.substring(start, end);
}

int extractIntValue(String payload, String key, int fallback) {
  String pattern = "\"" + key + "\":";
  int start = payload.indexOf(pattern);

  if (start < 0) {
    return fallback;
  }

  start += pattern.length();
  int end = payload.indexOf(",", start);

  if (end < 0) {
    end = payload.indexOf("}", start);
  }

  if (end < 0) {
    return fallback;
  }

  return payload.substring(start, end).toInt();
}

void publishRegistration() {
  String payload =
    String("{\"type\":\"register\",\"controller_id\":\"") +
    controllerID +
    "\"}";

  mqtt.publish(registerTopic, payload.c_str());

  Serial.print("Registration sent: ");
  Serial.println(payload);
}

void handleAssignment(String payload) {
  String type = extractStringValue(payload, "type");
  String assignedControllerID = extractStringValue(payload, "controller_id");
  int player = extractIntValue(payload, "player", 0);

  if (type != "assign_player") {
    return;
  }

  if (assignedControllerID != controllerID) {
    return;
  }

  assignedPlayer = player;

  Serial.print("Player ");
  Serial.print(assignedPlayer);
  Serial.println(" Assigned");
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  handleAssignment(message);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void connectToMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT...");

    if (mqtt.connect(controllerID.c_str())) {
      Serial.println("connected");
      mqtt.subscribe(assignTopic);
      publishRegistration();
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(". Trying again in 2 seconds.");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  controllerID = getControllerID();

  Serial.print("Controller ID: ");
  Serial.println(controllerID);

  connectToWiFi();

  mqtt.setServer(mqttServer, 1883);
  mqtt.setCallback(onMqttMessage);
}

void loop() {
  if (!mqtt.connected()) {
    connectToMQTT();
  }

  mqtt.loop();

  if (assignedPlayer == 0 && millis() - lastRegistrationTime > 5000) {
    publishRegistration();
    lastRegistrationTime = millis();
  }
}

