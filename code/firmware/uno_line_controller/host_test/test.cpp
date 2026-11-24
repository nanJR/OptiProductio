// Scripted test of the UNO sketch: fake sensor pulses in, LED/servo/serial checked. Run with run.sh.
#include "sketch.cpp"
#include <cassert>
int fails = 0;
#define CHECK(c, msg) do { if (!(c)) { printf("FAIL: %s (t=%lu ms)\n", msg, g_ms); fails++; } else printf("ok:   %s\n", msg); } while (0)
void run(unsigned long ms) { for (unsigned long i = 0; i < ms; i++) { g_ms++; loop(); } }
void pass(uint8_t pin) { g_pin[pin] = LOW; run(120); g_pin[pin] = HIGH; run(30); }
bool has(const char* s) { for (auto &l : Serial.out) if (l.find(s) != std::string::npos) return true; return false; }
// sample a station LED over 1 s: 'G' steady green, 'B' blinking green, 'R' steady red
char led(int i) {
  int gOn = 0, gOff = 0, rOn = 0, rOff = 0;
  for (int k = 0; k < 1000; k++) { g_ms++; loop(); (g_out[LED_GREEN_PIN[i]] ? gOn : gOff)++; (g_out[LED_RED_PIN[i]] ? rOn : rOff)++; }
  if (rOn && !rOff && !gOn) return 'R';
  if (gOn && !gOff && !rOn) return 'G';
  if (gOn && gOff && !rOn) return 'B';
  return '?';
}
int main() {
  for (int i = 0; i < 20; i++) g_pin[i] = HIGH;
  setup();
  run(20);
  CHECK(gateOpen && gateServo.angle == GATE_OPEN_DEG, "gate opens once at start");
  CHECK(bufferS == 10 && wipLimit == 0, "first boot defaults: buffer 10 s, WIP limit off");
  CHECK(led(0) == 'G' && led(1) == 'G' && led(2) == 'G', "all stations empty -> green steady");
  Serial.feed("B,3"); run(5);
  CHECK(bufferS == 3 && has(",BUF,3"), "B,3 from Serial Monitor sets buffer 3 s");
  pass(IR_IN_PIN[0]);
  CHECK(!gateOpen && gateServo.angle == GATE_CLOSED_DEG, "box enters S1 -> gate closes");
  CHECK(led(0) == 'B', "S1 box inside buffer -> green blinking");
  run(500);    // now ~2.6 s on S1 (each led() check samples 1 s)
  CHECK(led(0) == 'B' && bottleneck == 0, "still green blinking before 3 s, no bottleneck");
  run(800);
  CHECK(led(0) == 'R' && bottleneck == 1, "after 3 s -> red steady, S1 is the bottleneck");
  pass(IR_OUT_PIN[0]);
  CHECK(st[0].count == 0 && !gateOpen, "S1 empty -> gate still closed for the settle time");
  CHECK(led(0) == 'G', "S1 empty -> green steady again");
  CHECK(gateOpen, "gate reopened ~1 s after S1 became empty");
  pass(IR_IN_PIN[1]);
  CHECK(led(1) == 'B', "box enters S2 -> S2 green blinking");
  pass(IR_IN_PIN[0]);
  CHECK(!gateOpen, "second box at S1 -> gate closes");
  run(3500);
  CHECK(led(0) == 'R' && led(1) == 'R', "both over buffer -> both red");
  CHECK(bottleneck == 2, "bottleneck = S2 (busy the longest, Roser)");
  run(3000);
  CHECK(has(",2,STALL,"), "S2 busy > 2 x buffer -> STALL event");
  // CONWIP mode
  Serial.feed("L,2"); run(5);
  pass(IR_OUT_PIN[0]);  // S1 empties, WIP = 2 (S2 + box in transit)
  run(1500);
  CHECK(!gateOpen && has(",HOLD,2"), "CONWIP L=2: WIP 2 -> gate held even though S1 is empty");
  pass(IR_OUT_PIN[1]); pass(IR_IN_PIN[2]); pass(IR_OUT_PIN[2]);  // one box leaves the line
  run(50);
  CHECK(gateOpen, "WIP drops below 2 -> gate opens");
  Serial.feed("H"); run(5);
  CHECK(has("# settings: buffer=3 s, WIP limit=2"), "H prints settings");
  // reboot: settings come back from EEPROM
  bufferS = 0; wipLimit = 9; Serial.out.clear();
  setup(); run(20);
  CHECK(bufferS == 3 && wipLimit == 2, "buffer and limit survive a reboot (EEPROM)");
  printf("\n%d failure(s)\nLast lines:\n", fails);
  for (auto &l : Serial.out) printf("  %s\n", l.c_str());
  return fails;
}
