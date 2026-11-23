/*
  OptiProductio - UNO line controller
  Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection

  What this sketch does (the UNO is the "PLC" of our line):
    1. Reads 6 FC-51 IR sensors: one at the entry (IN) and one at the exit (OUT)
       of each station S1, S2, S3.
    2. Keeps WIP (work in progress: boxes inside the line) = boxes in at S1 - boxes out at S3.
    3. Runs the CONWIP gate (constant WIP): the SG90 servo at the chute only releases
       a new box when WIP < WIP limit. The laptop can change the limit; the loop
       itself runs here, so the line keeps working if Wi-Fi or the laptop drops.
    4. Finds the momentary bottleneck (Roser active-period method): the station
       that has been busy without a break for the longest time right now.
    5. Drives one green + one red LED per station (andon lights) and a buzzer.
    6. Sends every event as one text line to USB (laptop backup) AND to the
       NodeMCU ESP8266 Wi-Fi gateway (SoftwareSerial on A2/A3).

  Serial protocol (same lines on USB at 115200 baud and on the gateway link at 19200):
    E,<seq>,<ms>,<station>,<event>,<value>          one event
    S,<seq>,<ms>,<wip>,<limit>,<gate>,<occ1>,<occ2>,<occ3>,<bn>,<released>,<done>
                                                    status, once a second
    station 0 = whole line, 1..3 = S1..S3
    events: BOOT, IN, OUT, GATE, HOLD, LIMIT, BN, STALL, ERR, RESET, PONG
  Commands the UNO accepts (from USB or from the gateway), one per line:
    L,<n>   set WIP limit to n (0 = no limit). Saved in EEPROM.
    R       reset all counters (clear the boxes off the table first)
    P       ping, answered with E,...,PONG

  Libraries: Servo, SoftwareSerial, EEPROM (all built into the Arduino IDE).
  Board: Arduino UNO (clone with CH340 is fine).
*/

#include <Servo.h>
#include <SoftwareSerial.h>
#include <EEPROM.h>

// ---------------- Pins (see docs/phase2/WIRING.md) ----------------
const uint8_t IR_IN_PIN[3]  = {2, 4, 6};   // S1 IN, S2 IN, S3 IN
const uint8_t IR_OUT_PIN[3] = {3, 5, 7};   // S1 OUT, S2 OUT, S3 OUT
const uint8_t SERVO_PIN     = 8;
const uint8_t LED_GREEN_PIN[3] = {9, 11, 13};
const uint8_t LED_RED_PIN[3]   = {10, 12, A0};
const uint8_t BUZZER_PIN    = A1;          // active 5 V buzzer (+ to A1, - to GND)
const uint8_t GW_RX_PIN     = A2;          // <- NodeMCU D6 (3.3 V is read as HIGH, no divider needed)
const uint8_t GW_TX_PIN     = A3;          // -> 1k/2.2k divider -> NodeMCU D5

// ---------------- Settings you can tune ----------------
const uint8_t  DEFAULT_WIP_LIMIT = 4;      // used on first boot; later read from EEPROM
const uint8_t  IR_ACTIVE         = LOW;    // FC-51 output goes LOW when it sees a box
const uint16_t IR_DEBOUNCE_MS    = 25;     // signal must be stable this long
const uint16_t IR_HOLDOFF_MS     = 400;    // ignore a second trigger from the same box
const uint8_t  GATE_CLOSED_DEG   = 10;     // servo angle that blocks the chute
const uint8_t  GATE_OPEN_DEG     = 95;     // servo angle that lets one box slide
const uint16_t SERVO_MOVE_MS     = 450;    // power the servo this long, then detach (no jitter)
const uint16_t GATE_REOPEN_MS    = 1500;   // wait after closing before the next release
const bool     RELEASE_ONLY_WHEN_S1_EMPTY = true;  // S1 platform holds one box
const uint32_t STALL_MS          = 20000;  // a station busy this long = suspected breakdown
const uint16_t STATUS_EVERY_MS   = 1000;
const long     USB_BAUD          = 115200;
const long     GW_BAUD           = 19200;  // slow enough for SoftwareSerial on both ends
const uint8_t  FIFO_N            = 6;      // max boxes remembered per station

// ---------------- Objects ----------------
Servo gateServo;
SoftwareSerial gw(GW_RX_PIN, GW_TX_PIN);   // RX, TX

// ---------------- State ----------------
struct IrSensor {
  uint8_t pin;
  uint8_t lastRaw;
  uint8_t stable;
  unsigned long changedAt;
  unsigned long lastTrigger;
};

struct Station {
  unsigned long inTimes[FIFO_N];  // when each box on the station came in (FIFO)
  uint8_t head;
  uint8_t count;                  // boxes on the station now (occupancy)
  unsigned long activeSince;      // start of the current active period
  bool stallSent;
};

IrSensor irIn[3], irOut[3];
Station st[3];

uint16_t seq = 0;
unsigned long released = 0;       // boxes that entered S1 (released into the line)
unsigned long done = 0;           // boxes that left S3 (finished)
uint8_t wipLimit = DEFAULT_WIP_LIMIT;  // 0 = no limit

bool gateOpen = false;
bool servoAttached = false;
unsigned long servoDetachAt = 0;
unsigned long gateClosedAt = 0;
bool holdSent = false;

uint8_t bottleneck = 0;           // 0 = none, 1..3 = station
unsigned long lastStatus = 0;

// buzzer (non-blocking beeps)
uint8_t beepsLeft = 0;
bool beepOn = false;
uint16_t beepOnMs = 100;
const uint16_t BEEP_OFF_MS = 120;
unsigned long beepNextAt = 0;

// command buffers
char usbBuf[24];  uint8_t usbLen = 0;
char gwBuf[24];   uint8_t gwLen = 0;

// ---------------- Output ----------------
void emit(const char* line) {
  Serial.println(line);
  gw.println(line);
}

void sendEvent(uint8_t station, const char* ev, long value) {
  char buf[56];
  snprintf(buf, sizeof(buf), "E,%u,%lu,%u,%s,%ld",
           seq++, millis(), station, ev, value);
  emit(buf);
}

long wip() {
  return (released > done) ? (long)(released - done) : 0L;
}

void sendStatus() {
  char buf[80];
  snprintf(buf, sizeof(buf), "S,%u,%lu,%ld,%u,%u,%u,%u,%u,%u,%lu,%lu",
           seq++, millis(), wip(), wipLimit, gateOpen ? 1 : 0,
           st[0].count, st[1].count, st[2].count, bottleneck, released, done);
  emit(buf);
}

// ---------------- Buzzer ----------------
void beep(uint8_t times, uint16_t onMs) {
  if (beepsLeft > 0 || beepOn) return;   // a pattern is already playing
  beepsLeft = times;
  beepOnMs = onMs;
  beepNextAt = millis();
}

void updateBuzzer() {
  unsigned long now = millis();
  if (now < beepNextAt) return;
  if (beepOn) {
    digitalWrite(BUZZER_PIN, LOW);
    beepOn = false;
    if (beepsLeft > 0) beepsLeft--;
    beepNextAt = now + BEEP_OFF_MS;
  } else if (beepsLeft > 0) {
    digitalWrite(BUZZER_PIN, HIGH);
    beepOn = true;
    beepNextAt = now + beepOnMs;
  }
}

// ---------------- Servo gate ----------------
void moveServo(uint8_t deg) {
  if (!servoAttached) {
    gateServo.attach(SERVO_PIN);
    servoAttached = true;
  }
  gateServo.write(deg);
  servoDetachAt = millis() + SERVO_MOVE_MS;
}

void setGate(bool open) {
  if (open == gateOpen) return;
  gateOpen = open;
  moveServo(open ? GATE_OPEN_DEG : GATE_CLOSED_DEG);
  if (!open) gateClosedAt = millis();
  sendEvent(0, "GATE", open ? 1 : 0);
}

void updateServoPower() {
  if (servoAttached && (long)(millis() - servoDetachAt) >= 0) {
    gateServo.detach();          // stops the pulses: no buzzing, no jitter from SoftwareSerial
    servoAttached = false;
  }
}

// CONWIP rule: release only while WIP < limit (and S1 is free)
void updateGate() {
  long w = wip();
  bool limitOk = (wipLimit == 0) || (w < (long)wipLimit);
  bool s1Free = !RELEASE_ONLY_WHEN_S1_EMPTY || st[0].count == 0;

  if (!limitOk) {
    if (!holdSent) {                    // tell everyone once per hold
      sendEvent(0, "HOLD", w);
      beep(2, 80);
      holdSent = true;
    }
  } else {
    holdSent = false;
  }

  if (gateOpen) {
    if (!limitOk || !s1Free) setGate(false);
  } else {
    if (limitOk && s1Free && millis() - gateClosedAt >= GATE_REOPEN_MS) setGate(true);
  }
}

// ---------------- Stations ----------------
void onIn(uint8_t i) {
  unsigned long now = millis();
  Station &s = st[i];
  if (s.count < FIFO_N) {
    s.inTimes[(s.head + s.count) % FIFO_N] = now;
    s.count++;
  } else {
    sendEvent(i + 1, "ERR", 2);         // more boxes than we can remember: sensor noise?
  }
  if (s.count == 1) {                   // idle -> active: a new active period starts
    s.activeSince = now;
    s.stallSent = false;
  }
  if (i == 0) {
    released++;
    setGate(false);                     // escapement: one box per opening
  }
  sendEvent(i + 1, "IN", s.count);
}

void onOut(uint8_t i) {
  unsigned long now = millis();
  Station &s = st[i];
  long cycleMs = 0;
  if (s.count == 0) {
    sendEvent(i + 1, "ERR", 1);         // OUT without IN: the IN sensor missed the box
  } else {
    cycleMs = (long)(now - s.inTimes[s.head]);
    s.head = (s.head + 1) % FIFO_N;
    s.count--;
  }
  if (i == 2) done++;                   // a box left the line, count it even after ERR
  sendEvent(i + 1, "OUT", cycleMs);     // value = cycle time of that box in ms (0 = unknown)
}

// Roser momentary bottleneck: the active station with the longest current active period
void updateBottleneck() {
  unsigned long now = millis();
  uint8_t bn = 0;
  unsigned long best = 0;
  for (uint8_t i = 0; i < 3; i++) {
    if (st[i].count > 0) {
      unsigned long d = now - st[i].activeSince;
      if (bn == 0 || d > best) { best = d; bn = i + 1; }
    }
  }
  if (bn != bottleneck) {
    bottleneck = bn;
    sendEvent(0, "BN", bn);
  }
  for (uint8_t i = 0; i < 3; i++) {
    if (st[i].count > 0 && !st[i].stallSent && now - st[i].activeSince > STALL_MS) {
      st[i].stallSent = true;
      sendEvent(i + 1, "STALL", (long)(now - st[i].activeSince));
      beep(3, 250);
    }
  }
}

// ---------------- Sensors ----------------
// returns true once when a box arrives in front of the sensor
bool readIr(IrSensor &s) {
  unsigned long now = millis();
  uint8_t raw = digitalRead(s.pin);
  if (raw != s.lastRaw) { s.lastRaw = raw; s.changedAt = now; }
  if (now - s.changedAt >= IR_DEBOUNCE_MS && raw != s.stable) {
    s.stable = raw;
    if (raw == IR_ACTIVE && now - s.lastTrigger >= IR_HOLDOFF_MS) {
      s.lastTrigger = now;
      return true;
    }
  }
  return false;
}

void initIr(IrSensor &s, uint8_t pin) {
  s.pin = pin;
  pinMode(pin, INPUT);                  // FC-51 has its own pull-up
  s.lastRaw = digitalRead(pin);
  s.stable = s.lastRaw;
  s.changedAt = millis();
  s.lastTrigger = 0;
}

// ---------------- LEDs (andon) ----------------
//   green on        = station working
//   green blinking  = station idle (waiting for a box)
//   red on          = this station is the bottleneck right now
//   red fast blink  = stalled longer than STALL_MS (suspected breakdown)
void updateLeds() {
  unsigned long now = millis();
  bool slowBlink = (now / 500) % 2;
  bool fastBlink = (now / 125) % 2;
  for (uint8_t i = 0; i < 3; i++) {
    bool active = st[i].count > 0;
    bool stalled = active && st[i].stallSent;
    bool isBn = bottleneck == i + 1;
    bool g, r;
    if (stalled)      { g = false; r = fastBlink; }
    else if (isBn)    { g = false; r = true; }
    else if (active)  { g = true;  r = false; }
    else              { g = slowBlink; r = false; }
    digitalWrite(LED_GREEN_PIN[i], g ? HIGH : LOW);
    digitalWrite(LED_RED_PIN[i], r ? HIGH : LOW);
  }
}

// ---------------- Commands ----------------
void saveLimit() {
  EEPROM.update(0, 0xA5);               // marker: "a limit has been saved"
  EEPROM.update(1, wipLimit);
}

void loadLimit() {
  if (EEPROM.read(0) == 0xA5 && EEPROM.read(1) <= 20) wipLimit = EEPROM.read(1);
  else wipLimit = DEFAULT_WIP_LIMIT;
}

void resetLine() {
  released = 0;
  done = 0;
  for (uint8_t i = 0; i < 3; i++) {
    st[i].head = 0; st[i].count = 0; st[i].stallSent = false;
  }
  bottleneck = 0;
  holdSent = false;
  sendEvent(0, "RESET", 0);
}

void handleCommand(char* cmd) {
  // accepts "L,4", "L 4", "R", "P" (upper or lower case)
  char c = cmd[0];
  if (c >= 'a' && c <= 'z') c -= 32;
  if (c == 'L') {
    int n = atoi(cmd + 2);
    if (n < 0) n = 0;
    if (n > 20) n = 20;
    wipLimit = (uint8_t)n;
    saveLimit();
    sendEvent(0, "LIMIT", wipLimit);
  } else if (c == 'R') {
    resetLine();
  } else if (c == 'P') {
    sendEvent(0, "PONG", wipLimit);
  }
}

void readCommands(Stream &port, char* buf, uint8_t &len) {
  while (port.available()) {
    char ch = port.read();
    if (ch == '\n' || ch == '\r') {
      if (len > 0) { buf[len] = 0; handleCommand(buf); len = 0; }
    } else if (len < 22) {
      buf[len++] = ch;
    } else {
      len = 0;                          // line too long: drop it
    }
  }
}

// ---------------- Main ----------------
void setup() {
  Serial.begin(USB_BAUD);
  gw.begin(GW_BAUD);
  for (uint8_t i = 0; i < 3; i++) {
    initIr(irIn[i], IR_IN_PIN[i]);
    initIr(irOut[i], IR_OUT_PIN[i]);
    pinMode(LED_GREEN_PIN[i], OUTPUT);
    pinMode(LED_RED_PIN[i], OUTPUT);
    st[i].head = 0; st[i].count = 0; st[i].stallSent = false;
  }
  pinMode(BUZZER_PIN, OUTPUT);
  loadLimit();

  // start with the gate closed
  gateOpen = false;
  moveServo(GATE_CLOSED_DEG);
  gateClosedAt = millis();

  // lamp test: all LEDs on for half a second
  for (uint8_t i = 0; i < 3; i++) { digitalWrite(LED_GREEN_PIN[i], HIGH); digitalWrite(LED_RED_PIN[i], HIGH); }
  digitalWrite(BUZZER_PIN, HIGH);
  delay(150);
  digitalWrite(BUZZER_PIN, LOW);
  delay(350);

  Serial.println(F("# OptiProductio UNO line controller v2.0"));
  sendEvent(0, "BOOT", wipLimit);
}

void loop() {
  for (uint8_t i = 0; i < 3; i++) {
    if (readIr(irIn[i]))  onIn(i);
    if (readIr(irOut[i])) onOut(i);
  }
  updateGate();
  updateBottleneck();
  updateLeds();
  updateBuzzer();
  updateServoPower();
  readCommands(Serial, usbBuf, usbLen);
  readCommands(gw, gwBuf, gwLen);

  if (millis() - lastStatus >= STATUS_EVERY_MS) {
    lastStatus = millis();
    sendStatus();
  }
}
