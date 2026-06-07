// Generic ESP32 node template for the physical board game system.
// Copy this sketch when adding a new controller.

#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqttServer = "192.168.68.74";

const char* nodeId = "new_node_1";
const char* baseTopic = "boardgame";

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastHeartbeatTime = 0;

String nodeTopic(const char* suffix) {
  return String(baseTopic) + "/nodes/" + nodeId + "/" + suffix;
}

void publishRegistration() {
  String payload =
    "{"
    "\"type\":\"register\","
    "\"node_id\":\"new_node_1\","
    "\"role\":\"custom\","
    "\"name\":\"New Node 1\","
    "\"firmware\":\"0.1.0\","
    "\"capabilities\":[]"
    "}";

  mqtt.publish(nodeTopic("register").c_str(), payload.c_str(), true);
}

void publishHeartbeat() {
  String payload =
    String("{\"type\":\"heartbeat\",\"node_id\":\"") + nodeId +
    "\",\"uptime_ms\":" + millis() + "}";

  mqtt.publish(nodeTopic("heartbeat").c_str(), payload.c_str());
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // Handle commands here.
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
      mqtt.subscribe(nodeTopic("cmd").c_str());
      publishRegistration();
    } else {
      delay(1000);
    }
  }
}

void setup() {
  connectToWiFi();

  mqtt.setServer(mqttServer, 1883);
  mqtt.setCallback(onMqttMessage);
}

void loop() {
  if (!mqtt.connected()) {
    connectToMQTT();
  }

  mqtt.loop();

  if (millis() - lastHeartbeatTime > 5000) {
    publishHeartbeat();
    lastHeartbeatTime = millis();
  }
}

