/*
  OptiProductio - UNO line controller
  Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection

  What this sketch does (the UNO is the "PLC" of our line):
    1. Reads 6 FC-51 IR sensors: one at the entry (IN) and one at the exit (OUT)
       of each station S1, S2, S3.
    2. Keeps WIP (work in progress: boxes inside the line) = boxes in at S1 - boxes out at S3.
    3. Runs the servo gate at the chute (one box at a time):
         - at power-up the gate opens once and lets a box slide to S1,
         - the moment that box reaches S1 (S1 IN sensor) the gate closes,
         - when S1 is empty again (S1 OUT sensor) the gate opens for the next box.
       Optional CONWIP mode (constant WIP): with a WIP limit n > 0 the gate ALSO
       waits until WIP < n. Limit 0 (the default) = only the S1 rule above.
       The rule runs here, so the line keeps working if Wi-Fi or the laptop drops.
    4. Buffer time (user setting, seconds, saved in EEPROM): how long a station may
       stay busy before we call it a bottleneck. Different products need different
       times, so it is a setting, not a constant.
    5. Finds the momentary bottleneck (Roser active-period method): among the
       stations busy longer than the buffer time, the one busy the longest without a break.
    6. Drives one green + one red LED per station (andon lights) and a buzzer:
         green steady   = station empty
         green blinking = box on the station, work in progress, still inside the buffer time
         red steady     = box on the station for longer than the buffer time (bottleneck)
    7. Sends every event as one text line to USB (laptop backup) AND to the
       NodeMCU ESP8266 Wi-Fi gateway (SoftwareSerial on A2/A3).

  Serial protocol (same lines on USB at 115200 baud and on the gateway link at 19200):
    E,<seq>,<ms>,<station>,<event>,<value>          one event
    S,<seq>,<ms>,<wip>,<limit>,<gate>,<occ1>,<occ2>,<occ3>,<bn>,<released>,<done>,<buf_s>
                                                    status, once a second
    station 0 = whole line, 1..3 = S1..S3
    events: BOOT, IN, OUT, GATE, HOLD, LIMIT, BUF, BN, STALL, ERR, RESET, PONG
  Commands the UNO accepts (from USB or from the gateway), one per line.
  In the Arduino IDE Serial Monitor: 115200 baud, line ending "Newline", then type e.g. B,15
    B,<s>   set the buffer time to s seconds (1..3600). Saved in EEPROM.
    L,<n>   set WIP limit to n (0 = off: one box at S1 only). Saved in EEPROM.
    H       print the current settings and this command list
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
const uint8_t  DEFAULT_WIP_LIMIT = 0;      // 0 = gate follows S1 only (open when S1 empty). First boot only.
const uint16_t DEFAULT_BUFFER_S  = 10;     // buffer time in seconds. First boot only; then from EEPROM.
const uint16_t MAX_BUFFER_S      = 3600;
const uint8_t  IR_ACTIVE         = LOW;    // FC-51 output goes LOW when it sees a box
const uint16_t IR_DEBOUNCE_MS    = 25;     // signal must be stable this long
const uint16_t IR_HOLDOFF_MS     = 400;    // ignore a second trigger from the same box
const uint8_t  GATE_CLOSED_DEG   = 95;     // servo angle that blocks the chute (arm hangs across the lane)
// OPEN is a SMALLER angle than CLOSED so the arm swings to the RIGHT (looking down the lane).
// Swing too small: lower GATE_OPEN_DEG (min 0). Swing too big: raise it toward GATE_CLOSED_DEG.
const uint8_t  GATE_OPEN_DEG     = 10;     // servo angle that lets one box slide
const uint16_t SERVO_MOVE_MS     = 450;    // power the servo this long, then detach (no jitter)
const uint16_t GATE_REOPEN_MS    = 1000;   // S1 must stay empty this long before the gate reopens
                                           // (lets the box leaving S1 clear the platform)
const uint8_t  STALL_FACTOR      = 2;      // busy for 2 x buffer time = suspected breakdown (buzzer + STALL event)
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
  bool over;                      // busy longer than the buffer time (red LED)
  bool stallSent;
};

IrSensor irIn[3], irOut[3];
Station st[3];

uint16_t seq = 0;
unsigned long released = 0;       // boxes that entered S1 (released into the line)
unsigned long done = 0;           // boxes that left S3 (finished)
uint8_t wipLimit = DEFAULT_WIP_LIMIT;  // 0 = no limit
uint16_t bufferS = DEFAULT_BUFFER_S;   // buffer time in seconds

bool gateOpen = false;
bool servoAttached = false;
unsigned long servoDetachAt = 0;
unsigned long s1EmptySince = 0;   // when S1 last became empty
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
  char buf[90];
  snprintf(buf, sizeof(buf), "S,%u,%lu,%ld,%u,%u,%u,%u,%u,%u,%lu,%lu,%u",
           seq++, millis(), wip(), wipLimit, gateOpen ? 1 : 0,
           st[0].count, st[1].count, st[2].count, bottleneck, released, done, bufferS);
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
  sendEvent(0, "GATE", open ? 1 : 0);
}

void updateServoPower() {
  if (servoAttached && (long)(millis() - servoDetachAt) >= 0) {
    gateServo.detach();          // stops the pulses: no buzzing, no jitter from SoftwareSerial
    servoAttached = false;
  }
}

// Gate rule:
//   open  when S1 has been empty for GATE_REOPEN_MS (and, in CONWIP mode, WIP < limit)
//   close as soon as a box reaches S1 (done in onIn) or the WIP limit is reached
void updateGate() {
  long w = wip();
  bool limitOk = (wipLimit == 0) || (w < (long)wipLimit);
  bool s1Free = st[0].count == 0;
  bool s1Settled = s1Free && (millis() - s1EmptySince >= GATE_REOPEN_MS);

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
    if (limitOk && s1Settled) setGate(true);
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
    s.over = false;
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
  if (s.count == 0) {
    s.over = false;                     // empty again: back to green steady
    if (i == 0) s1EmptySince = now;     // the gate may reopen after GATE_REOPEN_MS
  }
  if (i == 2) done++;                   // a box left the line, count it even after ERR
  sendEvent(i + 1, "OUT", cycleMs);     // value = cycle time of that box in ms (0 = unknown)
}

// A station is "over buffer" when it has been busy without a break (one active period)
// for longer than the buffer time. Its red LED turns on.
// Roser momentary bottleneck: of the over-buffer stations, the one with the longest
// current active period. 0 = no station is over the buffer time.
void updateBottleneck() {
  unsigned long now = millis();
  unsigned long bufMs = (unsigned long)bufferS * 1000UL;
  uint8_t bn = 0;
  unsigned long best = 0;
  for (uint8_t i = 0; i < 3; i++) {
    if (st[i].count == 0) continue;
    unsigned long d = now - st[i].activeSince;
    if (!st[i].over && d > bufMs) {
      st[i].over = true;
      beep(1, 120);                     // one short beep when a station turns red
    }
    if (st[i].over && (bn == 0 || d > best)) { best = d; bn = i + 1; }
  }
  if (bn != bottleneck) {
    bottleneck = bn;
    sendEvent(0, "BN", bn);
  }
  unsigned long stallMs = bufMs * STALL_FACTOR;
  for (uint8_t i = 0; i < 3; i++) {
    if (st[i].count > 0 && !st[i].stallSent && now - st[i].activeSince > stallMs) {
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
//   green steady    = station empty (and for S1: the gate may open)
//   green blinking  = box on the station, work in progress, inside the buffer time
//   red steady      = box on the station longer than the buffer time (bottleneck)
void updateLeds() {
  bool blink = (millis() / 400) % 2;
  for (uint8_t i = 0; i < 3; i++) {
    bool g, r;
    if (st[i].count == 0)  { g = true;  r = false; }
    else if (st[i].over)   { g = false; r = true; }
    else                   { g = blink; r = false; }
    digitalWrite(LED_GREEN_PIN[i], g ? HIGH : LOW);
    digitalWrite(LED_RED_PIN[i], r ? HIGH : LOW);
  }
}

// ---------------- Commands ----------------
// EEPROM layout: [0] marker 0xA6, [1] WIP limit, [2..3] buffer time (s).
// The marker changed from v2 (0xA5), so an old saved limit is ignored once.
const uint8_t EE_MARK = 0xA6;

void saveSettings() {
  EEPROM.update(0, EE_MARK);
  EEPROM.update(1, wipLimit);
  EEPROM.update(2, bufferS & 0xFF);
  EEPROM.update(3, bufferS >> 8);
}

void loadSettings() {
  wipLimit = DEFAULT_WIP_LIMIT;
  bufferS = DEFAULT_BUFFER_S;
  if (EEPROM.read(0) != EE_MARK) { saveSettings(); return; }
  if (EEPROM.read(1) <= 20) wipLimit = EEPROM.read(1);
  uint16_t b = EEPROM.read(2) | ((uint16_t)EEPROM.read(3) << 8);
  if (b >= 1 && b <= MAX_BUFFER_S) bufferS = b;
}

void printHelp() {
  char buf[64];
  snprintf(buf, sizeof(buf), "# settings: buffer=%u s, WIP limit=%u (0=off)", bufferS, wipLimit);
  emit(buf);
  emit("# commands: B,<seconds> buffer | L,<n> WIP limit | H help | R reset | P ping");
}

void resetLine() {
  released = 0;
  done = 0;
  for (uint8_t i = 0; i < 3; i++) {
    st[i].head = 0; st[i].count = 0; st[i].over = false; st[i].stallSent = false;
  }
  bottleneck = 0;
  holdSent = false;
  s1EmptySince = millis() - GATE_REOPEN_MS;   // S1 is empty: the gate may open right away
  sendEvent(0, "RESET", 0);
}

void handleCommand(char* cmd) {
  // accepts "B,15", "B 15", "L,4", "L 4", "H", "R", "P" (upper or lower case)
  char c = cmd[0];
  if (c >= 'a' && c <= 'z') c -= 32;
  if (c == 'B') {
    long n = atol(cmd + 1 + (cmd[1] == ',' || cmd[1] == ' ' ? 1 : 0));
    if (n < 1) n = 1;
    if (n > MAX_BUFFER_S) n = MAX_BUFFER_S;
    bufferS = (uint16_t)n;
    saveSettings();
    sendEvent(0, "BUF", bufferS);
  } else if (c == 'L') {
    int n = atoi(cmd + 1 + (cmd[1] == ',' || cmd[1] == ' ' ? 1 : 0));
    if (n < 0) n = 0;
    if (n > 20) n = 20;
    wipLimit = (uint8_t)n;
    saveSettings();
    sendEvent(0, "LIMIT", wipLimit);
  } else if (c == 'H' || c == '?') {
    printHelp();
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
    st[i].head = 0; st[i].count = 0; st[i].over = false; st[i].stallSent = false;
  }
  pinMode(BUZZER_PIN, OUTPUT);
  loadSettings();

  // gate starts closed; updateGate() opens it once right after boot (S1 is empty)
  gateOpen = false;
  moveServo(GATE_CLOSED_DEG);

  // lamp test: all LEDs on for half a second
  for (uint8_t i = 0; i < 3; i++) { digitalWrite(LED_GREEN_PIN[i], HIGH); digitalWrite(LED_RED_PIN[i], HIGH); }
  digitalWrite(BUZZER_PIN, HIGH);
  delay(150);
  digitalWrite(BUZZER_PIN, LOW);
  delay(350);

  Serial.println(F("# OptiProductio UNO line controller v3.0"));
  s1EmptySince = millis() - GATE_REOPEN_MS;
  sendEvent(0, "BOOT", wipLimit);
  sendEvent(0, "BUF", bufferS);
  printHelp();
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
