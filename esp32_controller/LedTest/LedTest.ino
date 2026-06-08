// Simple LED test for Nexus controllers.
// Upload this sketch to one ESP32 to verify the LED wiring.

const int LED_PIN = D10;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
