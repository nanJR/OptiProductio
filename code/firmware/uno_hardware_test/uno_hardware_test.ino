/*
  OptiProductio - UNO hardware test (flash this FIRST, before the real sketch)

  Open Tools > Serial Monitor, set 115200 baud and "Newline", then type a letter:
    s  = live sensor view: shows 0/1 for the 6 IR sensors 5 times a second
         (1 = sees a box). Wave your hand in front of each sensor. Type any key to stop.
    l  = LED test: S1 green, S1 red, S2 green ... one at a time
    g  = gate test: servo goes CLOSED -> OPEN -> CLOSED three times
    b  = buzzer: two short beeps
    w  = gateway link test: sends "P" to the NodeMCU every second and prints
         anything that comes back (flash the NodeMCU gateway first). Any key stops.
    a  = run all of l, g, b

  Same pins as the line controller sketch.
*/
#include <Servo.h>
#include <SoftwareSerial.h>

const uint8_t IR_PIN[6] = {2, 3, 4, 5, 6, 7};
const char* IR_NAME[6]  = {"S1-IN", "S1-OUT", "S2-IN", "S2-OUT", "S3-IN", "S3-OUT"};
const uint8_t SERVO_PIN = 8;
const uint8_t LED_PIN[6]  = {9, 10, 11, 12, 13, A0};
const char* LED_NAME[6] = {"S1 green", "S1 red", "S2 green", "S2 red", "S3 green", "S3 red"};
const uint8_t BUZZER_PIN = A1;
const uint8_t GATE_CLOSED_DEG = 95;  // arm hangs across the lane (keep same as line controller)
const uint8_t GATE_OPEN_DEG = 10;    // smaller angle = arm swings RIGHT (looking down the lane)

Servo gate;
SoftwareSerial gw(A2, A3);

void menu() {
  Serial.println(F("\n--- OptiProductio hardware test ---"));
  Serial.println(F("s = sensors, l = LEDs, g = gate servo, b = buzzer, w = gateway link, a = all"));
}

bool keyPressed() {
  if (Serial.available()) { while (Serial.available()) Serial.read(); return true; }
  return false;
}

void testSensors() {
  Serial.println(F("Sensors (1 = box seen). Any key to stop."));
  for (uint8_t i = 0; i < 6; i++) { Serial.print(IR_NAME[i]); Serial.print('\t'); }
  Serial.println();
  while (!keyPressed()) {
    for (uint8_t i = 0; i < 6; i++) {
      Serial.print(digitalRead(IR_PIN[i]) == LOW ? "  1" : "  0");
      Serial.print("\t");
    }
    Serial.println();
    delay(200);
  }
}

void testLeds() {
  for (uint8_t i = 0; i < 6; i++) {
    Serial.print(F("LED ")); Serial.println(LED_NAME[i]);
    digitalWrite(LED_PIN[i], HIGH); delay(700); digitalWrite(LED_PIN[i], LOW);
  }
}

void testGate() {
  gate.attach(SERVO_PIN);
  for (uint8_t k = 0; k < 3; k++) {
    Serial.println(F("Gate CLOSED")); gate.write(GATE_CLOSED_DEG); delay(800);
    Serial.println(F("Gate OPEN"));   gate.write(GATE_OPEN_DEG);   delay(800);
  }
  gate.write(GATE_CLOSED_DEG); delay(500);
  gate.detach();
  Serial.println(F("If the UNO reset during this test, the servo is not on its own 5 V supply."));
}

void testBuzzer() {
  for (uint8_t k = 0; k < 2; k++) { digitalWrite(BUZZER_PIN, HIGH); delay(120); digitalWrite(BUZZER_PIN, LOW); delay(150); }
}

void testGateway() {
  Serial.println(F("Sending P to the NodeMCU every second. Any key to stop."));
  unsigned long last = 0;
  while (!keyPressed()) {
    if (millis() - last > 1000) { last = millis(); gw.println("E,0,0,0,PONG,0"); }
    while (gw.available()) Serial.write(gw.read());
  }
}

void setup() {
  Serial.begin(115200);
  gw.begin(19200);
  for (uint8_t i = 0; i < 6; i++) { pinMode(IR_PIN[i], INPUT); pinMode(LED_PIN[i], OUTPUT); }
  pinMode(BUZZER_PIN, OUTPUT);
  menu();
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 's': testSensors(); break;
    case 'l': testLeds(); break;
    case 'g': testGate(); break;
    case 'b': testBuzzer(); break;
    case 'w': testGateway(); break;
    case 'a': testLeds(); testGate(); testBuzzer(); break;
    default: return;     // ignore newlines
  }
  menu();
}
