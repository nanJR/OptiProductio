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
  CHECK(bufferS[0] == 10 && bufferS[2] == 10 && wipLimit == 0, "first boot defaults: buffer 10 s, WIP limit off");
  CHECK(led(0) == 'G' && led(1) == 'G' && led(2) == 'G', "all stations empty -> green steady");
  Serial.feed("B,3"); run(5);
  CHECK(bufferS[0] == 3 && bufferS[1] == 3 && bufferS[2] == 3 && has(",3,BUF,3"), "B,3 from Serial Monitor sets all buffers to 3 s");
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
  // breakdown lock: S2 is broken, S1 and S3 are frozen
  CHECK(lockMask == 2 && has(",0,LOCK,2"), "S2 stalled -> LOCK,2 (line frozen)");
  CHECK(st[0].frozen && !st[1].frozen && st[2].frozen, "S1 and S3 frozen, S2 live");
  pass(IR_OUT_PIN[0]); pass(IR_IN_PIN[2]);
  CHECK(st[0].count == 1 && st[2].count == 0, "frozen S1 OUT and S3 IN sensors are ignored");
  unsigned long s1Before = activeMs(0, g_ms);
  run(4000);
  CHECK(activeMs(0, g_ms) == s1Before && !has(",1,STALL,"), "S1 timer paused while frozen: no false S1 breakdown");
  CHECK(!gateOpen, "gate stays closed during the lock");
  pass(IR_OUT_PIN[1]);   // repair done: the stuck box leaves S2
  run(5);
  CHECK(lockMask == 0 && has(",0,LOCK,0") && !st[0].frozen, "stuck box leaves S2 -> LOCK,0, line running again");
  CHECK(activeMs(0, g_ms) < s1Before + 300, "S1 timer resumes where it stopped");
  // S1 re-trigger: the box on S1 seen twice by the IN sensor is counted once
  unsigned long relBefore = released;
  pass(IR_IN_PIN[0]);
  CHECK(released == relBefore && st[0].count == 1 && has(",1,ERR,3"), "second S1 IN with gate closed is ignored (ERR,3)");
  pass(IR_IN_PIN[2]); pass(IR_OUT_PIN[2]);   // the S2 box goes through S3
  // CONWIP mode
  Serial.feed("L,1"); run(5);
  pass(IR_OUT_PIN[0]);  // S1 empties, WIP = 1 (box in transit to S2)
  run(1500);
  CHECK(!gateOpen && has(",HOLD,1"), "CONWIP L=1: WIP 1 -> gate held even though S1 is empty");
  pass(IR_IN_PIN[1]); pass(IR_OUT_PIN[1]); pass(IR_IN_PIN[2]); pass(IR_OUT_PIN[2]);  // the box leaves the line
  run(50);
  CHECK(gateOpen, "WIP drops below 1 -> gate opens");
  Serial.feed("H"); run(5);
  CHECK(has("# settings: buffer S1=3 S2=3 S3=3 s, WIP limit=1"), "H prints settings");
  Serial.feed("B,2,7"); run(5);
  CHECK(bufferS[0] == 3 && bufferS[1] == 7 && bufferS[2] == 3 && has(",2,BUF,7"), "B,2,7 sets only S2 to 7 s");
  Serial.feed("B,30012"); run(5);
  CHECK(bufferS[2] == 12 && bufferS[1] == 7, "B,30012 (gateway form) sets only S3 to 12 s");
  Serial.feed("b 1 4"); run(5);
  CHECK(bufferS[0] == 4, "b 1 4 also works");
  // reboot: settings come back from EEPROM
  bufferS[0] = bufferS[1] = bufferS[2] = 0; wipLimit = 9; Serial.out.clear();
  setup(); run(20);
  CHECK(bufferS[0] == 4 && bufferS[1] == 7 && bufferS[2] == 12 && wipLimit == 1, "per-station buffers and limit survive a reboot (EEPROM)");
  // in-flight box: the gate let a box go, then a breakdown locks the line before it lands on S1
  Serial.feed("L,0"); Serial.feed("R"); run(1200);
  CHECK(gateOpen, "after reset the gate opens");
  pass(IR_IN_PIN[1]); run(14500);                 // S2 box stuck > 2 x 7 s -> lock (gate closes)
  CHECK(lockMask == 2 && !gateOpen, "S2 breakdown locks the line");
  pass(IR_IN_PIN[0]);                             // the already-released box lands on frozen S1
  CHECK(st[0].count == 1 && released == 1, "box released before the lock is still counted at S1");
  run(8000);
  CHECK(activeMs(0, g_ms) < 1000 && !st[0].over, "its clock stays paused near 0 s (no false red / stall)");
  pass(IR_IN_PIN[0]);
  CHECK(st[0].count == 1 && released == 1, "a second S1 IN while frozen is ignored");
  // each station turns red on its own buffer: S1 4 s, S2 7 s
  Serial.feed("L,0"); Serial.feed("R"); run(1200);
  pass(IR_IN_PIN[1]); pass(IR_IN_PIN[0]);
  run(4500);
  CHECK(st[0].over && !st[1].over, "after ~4.6 s: S1 (buffer 4 s) red, S2 (buffer 7 s) still blinking");
  run(2600);
  CHECK(st[1].over, "after ~7.2 s on S2: S2 red too");
  printf("\n%d failure(s)\nLast lines:\n", fails);
  for (auto &l : Serial.out) printf("  %s\n", l.c_str());
  return fails;
}
