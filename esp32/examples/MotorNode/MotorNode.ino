// Motor ESP32 node for the physical board game system.
// Receives motor commands from the Raspberry Pi MQTT broker.

#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqttServer = "192.168.68.74";

const char* nodeId = "motor_1";
const char* baseTopic = "boardgame";

const int AIN1 = D2;
const int AIN2 = D3;
const int PWMA = D4;
const int STBY = D5;

const int DEFAULT_SPEED = 220;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastHeartbeatTime = 0;

String nodeTopic(const char* suffix) {
  return String(baseTopic) + "/nodes/" + nodeId + "/" + suffix;
}

void motorStop() {
  analogWrite(PWMA, 0);
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
}

void motorForward(int speed) {
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  analogWrite(PWMA, speed);
}

void motorReverse(int speed) {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
  analogWrite(PWMA, speed);
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

void handleMotorCommand(String payload) {
  String command = extractStringValue(payload, "command");
  String value = extractStringValue(payload, "value");
  int speed = extractIntValue(payload, "speed", DEFAULT_SPEED);

  if (command != "motor.set") {
    return;
  }

  if (value == "forward") {
    motorForward(speed);
  } else if (value == "reverse") {
    motorReverse(speed);
  } else if (value == "stop") {
    motorStop();
  }
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  handleMotorCommand(message);
}

void publishRegistration() {
  String payload =
    "{"
    "\"type\":\"register\","
    "\"node_id\":\"motor_1\","
    "\"role\":\"motor\","
    "\"name\":\"Motor Node 1\","
    "\"firmware\":\"0.1.0\","
    "\"capabilities\":["
      "{"
      "\"id\":\"drive_motor\","
      "\"type\":\"motor\","
      "\"commands\":[\"motor.set\"],"
      "\"values\":[\"forward\",\"reverse\",\"stop\"],"
      "\"speed_range\":[0,255]"
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
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);
  motorStop();

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

