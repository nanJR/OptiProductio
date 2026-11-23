// OptiProductio mini production line - Arduino UNO
// Counts parts at 3 stations, logs scrap and stop reasons, watches the
// raw material bin, and raises a WIP-cap alarm. Sends everything over USB.

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------- Pins ----------
const byte IR_PIN[3]  = {2, 3, 4};   // IR sensors at the exit of S1, S2, S3
const byte BTN_PIN[3] = {5, 6, 7};   // Breakdown, No material, Reject
const byte LED_GREEN = 8;
const byte LED_RED   = 9;
const byte BUZZER    = 10;
const byte US_TRIG   = 11;
const byte US_ECHO   = 12;

// ---------- Settings you can change ----------
int   wipCap        = 5;       // max parts allowed inside the line
const float EMPTY_CM = 20.0;   // sensor-to-bin-floor distance when the bin is empty
const float PART_CM  = 2.0;    // height of one block in the bin stack
const unsigned long IR_GAP_MS  = 400;   // ignore repeat triggers from the same part
const unsigned long BTN_GAP_MS = 200;   // button debounce

LiquidCrystal_I2C lcd(0x27, 16, 2);    // use 0x3F if the screen stays blank

// ---------- State ----------
long count[3] = {0, 0, 0};             // parts that left S1, S2, S3 (S3 = good parts)
long scrap = 0;
byte lastIr[3]  = {HIGH, HIGH, HIGH};
byte lastBtn[3] = {HIGH, HIGH, HIGH};
unsigned long irTime[3]  = {0, 0, 0};
unsigned long btnTime[3] = {0, 0, 0};
char downReason = 'R';                 // 'R' running, 'B' breakdown, 'M' no material
unsigned long lastStatus = 0;
unsigned long buzzerOffAt = 0;
int binParts = 0;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50);
  for (byte i = 0; i < 3; i++) {
    pinMode(IR_PIN[i], INPUT);
    pinMode(BTN_PIN[i], INPUT_PULLUP);
  }
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(US_TRIG, OUTPUT);
  pinMode(US_ECHO, INPUT);
  lcd.init();
  lcd.backlight();
  lcd.print("OptiProductio");
  Serial.println("# OptiProductio started");
}

long wip() {
  return count[0] - count[2] - scrap;  // released into the line minus parts that left it
}

void sendEvent(const char* type, char detail) {
  // Format: E,<ms>,<type>,<station or reason>
  Serial.print("E,");
  Serial.print(millis());
  Serial.print(',');
  Serial.print(type);
  Serial.print(',');
  Serial.println(detail);
}

void readIrSensors() {
  for (byte i = 0; i < 3; i++) {
    byte now = digitalRead(IR_PIN[i]);
    if (lastIr[i] == HIGH && now == LOW && millis() - irTime[i] > IR_GAP_MS) {
      count[i]++;
      irTime[i] = millis();
      sendEvent("PASS", '1' + i);
    }
    lastIr[i] = now;
  }
}

void readButtons() {
  for (byte i = 0; i < 3; i++) {
    byte now = digitalRead(BTN_PIN[i]);
    if (lastBtn[i] == HIGH && now == LOW && millis() - btnTime[i] > BTN_GAP_MS) {
      btnTime[i] = millis();
      if (i == 2) {                              // Reject button
        scrap++;
        sendEvent("SCRAP", '3');
      } else {                                   // a stop-reason button
        char reason = (i == 0) ? 'B' : 'M';
        if (downReason == 'R') {                 // line was running: stop it
          downReason = reason;
          sendEvent("DOWN", reason);
        } else if (downReason == reason) {       // same button again: restart
          sendEvent("UP", reason);
          downReason = 'R';
        }
      }
    }
    lastBtn[i] = now;
  }
}

int readBinParts() {
  digitalWrite(US_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(US_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(US_TRIG, LOW);
  unsigned long echo = pulseIn(US_ECHO, HIGH, 25000);  // give up after 25 ms
  if (echo == 0) return binParts;                      // no echo: keep last value
  float cm = echo / 58.0;
  int parts = round((EMPTY_CM - cm) / PART_CM);
  return max(parts, 0);
}

void readCommands() {
  // The laptop can send "CAP 6" to change the WIP cap
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    if (line.startsWith("CAP ")) {
      wipCap = line.substring(4).toInt();
      Serial.print("# cap set to ");
      Serial.println(wipCap);
    }
  }
}

void updateOutputs() {
  bool overCap = wip() >= wipCap;
  bool stopped = downReason != 'R';
  digitalWrite(LED_GREEN, (!overCap && !stopped) ? HIGH : LOW);
  digitalWrite(LED_RED, (overCap || stopped) ? HIGH : LOW);
  if (millis() > buzzerOffAt) digitalWrite(BUZZER, LOW);
}

void sendStatusAndLcd() {
  bool overCap = wip() >= wipCap;
  if (overCap) {                       // short beep, once a second
    digitalWrite(BUZZER, HIGH);
    buzzerOffAt = millis() + 150;
  }
  binParts = readBinParts();

  // Format: S,<ms>,<c1>,<c2>,<c3>,<scrap>,<wip>,<bin parts>,<state>,<cap>
  Serial.print("S,");
  Serial.print(millis());
  for (byte i = 0; i < 3; i++) { Serial.print(','); Serial.print(count[i]); }
  Serial.print(','); Serial.print(scrap);
  Serial.print(','); Serial.print(wip());
  Serial.print(','); Serial.print(binParts);
  Serial.print(','); Serial.print(downReason);
  Serial.print(','); Serial.println(wipCap);

  char row[17];
  snprintf(row, sizeof(row), "G%-3ld S%-2ld WIP%-2ld%s", count[2], scrap, wip(), overCap ? "!" : " ");
  lcd.setCursor(0, 0); lcd.print(row);
  const char* state = downReason == 'R' ? "RUN " : (downReason == 'B' ? "BRKD" : "NMAT");
  snprintf(row, sizeof(row), "B%-3d %s CAP%-2d", binParts, state, wipCap);
  lcd.setCursor(0, 1); lcd.print(row);
}

void loop() {
  readIrSensors();
  readButtons();
  readCommands();
  updateOutputs();
  if (millis() - lastStatus >= 1000) {
    lastStatus = millis();
    sendStatusAndLcd();
  }
}
