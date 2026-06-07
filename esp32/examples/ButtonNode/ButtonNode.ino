// Button ESP32 node for the physical board game system.
// Publishes button.press events to the Raspberry Pi MQTT broker.

#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqttServer = "192.168.68.74";

const char* nodeId = "button_1";
const char* baseTopic = "boardgame";

const int BUTTON_PIN = D2;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

bool lastButtonState = HIGH;
unsigned long lastPressTime = 0;
unsigned long lastHeartbeatTime = 0;

String nodeTopic(const char* suffix) {
  return String(baseTopic) + "/nodes/" + nodeId + "/" + suffix;
}

void publishRegistration() {
  String payload =
    "{"
    "\"type\":\"register\","
    "\"node_id\":\"button_1\","
    "\"role\":\"input\","
    "\"name\":\"Button Node 1\","
    "\"firmware\":\"0.1.0\","
    "\"capabilities\":["
      "{"
      "\"id\":\"main_button\","
      "\"type\":\"button\","
      "\"events\":[\"button.press\",\"button.release\"]"
      "}"
    "]"
    "}";

  mqtt.publish(nodeTopic("register").c_str(), payload.c_str(), true);
}

void publishHeartbeat() {
  String payload =
    String("{\"type\":\"heartbeat\",\"node_id\":\"") + nodeId +
    "\",\"uptime_ms\":" + millis() + "}";

  mqtt.publish(nodeTopic("heartbeat").c_str(), payload.c_str());
}

void publishButtonPress() {
  String payload =
    "{"
    "\"type\":\"event\","
    "\"node_id\":\"button_1\","
    "\"event\":\"button.press\","
    "\"control\":\"main_button\","
    "\"value\":1"
    "}";

  mqtt.publish(nodeTopic("event").c_str(), payload.c_str());
}

void connectToWiFi() {
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void connectToMQTT() {
  while (!mqtt.connected()) {
    if (mqtt.connect(nodeId)) {
      publishRegistration();
    } else {
      delay(1000);
    }
  }
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  connectToWiFi();
  mqtt.setServer(mqttServer, 1883);
}

void loop() {
  if (!mqtt.connected()) {
    connectToMQTT();
  }

  mqtt.loop();

  bool buttonState = digitalRead(BUTTON_PIN);

  if (lastButtonState == HIGH && buttonState == LOW) {
    unsigned long now = millis();

    if (now - lastPressTime > 250) {
      publishButtonPress();
      lastPressTime = now;
    }
  }

  lastButtonState = buttonState;

  if (millis() - lastHeartbeatTime > 5000) {
    publishHeartbeat();
    lastHeartbeatTime = millis();
  }
}

