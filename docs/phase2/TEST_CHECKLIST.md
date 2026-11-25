# OptiProductio test checklist

Tick each box. Part 1 needs **no hardware** (the simulator stands in for the UNO). Parts 2 and 3 need the table.

## Part 1. Without hardware (any laptop, 20 min)

Setup: `cd code\laptop`, `.venv\Scripts\activate`.

| # | Test | How | Pass when | ✓ |
|---|---|---|---|---|
| 1.1 | Automatic tests | `python -m pytest -q` | `14 passed` | ☐ |
| 1.2 | Dashboard opens | `python run.py --source sim` | page loads, "Simulator · live", no red banner after 20 s | ☐ |
| 1.3 | Bottleneck found | wait 2 min (or add `--speed 4`) | S2 lights go green blinking → red steady once S2 is busy > 10 s; Bottleneck analysis bar S2 highest | ☐ |
| 1.3b | Buffer time | set 30 s in "Buffer time and gate control", Apply | note says "UNO confirmed buffer time 30 s"; S2 now stays green blinking much longer before red | ☐ |
| 1.4 | CONWIP gate holds | set L = 2, Apply | amber "WIP has reached the limit" banner appears; WIP tile never shows more than 2 | ☐ |
| 1.5 | New run on limit change | after 1.4 | top-left label says "Run N: WIP limit 2" | ☐ |
| 1.6 | No-limit run | press "Off (S1 gate only)", Apply, wait 3 min | WIP average climbs above 4 | ☐ |
| 1.7 | Run report | open Run report | one row per run; L=2 row has lower WIP and lead time than "S1 gate, no WIP limit" | ☐ |
| 1.8 | Little's law | Run report | "TH x LT" within about 15 % of "WIP avg" for runs longer than 3 min | ☐ |
| 1.9 | Breakdown | `python run.py --source sim --scenario breakdown --speed 4` | after about 2 min of simulated time (30 s real time at speed 4): red "Line DOWN" banner, S2 card "Stalled", Pareto bar "Breakdown" | ☐ |
| 1.10 | Starved line | `--scenario starve --speed 4` | Pareto shows "Starved" as the top reason | ☐ |
| 1.11 | Shifting bottleneck | `--scenario shifting --speed 4` | after 2.5 min of simulated time S3 takes over as bottleneck; violet "shifting" parts appear | ☐ |
| 1.12 | Scrap entry | press "Mark last part scrap" | SQ = 1, QR below 100 %, event log shows SCRAP | ☐ |
| 1.13 | Reset | press "Reset line counts", confirm | counters go back to 0, a new run starts | ☐ |
| 1.14 | MQTT path | Mosquitto running; window 1: `python -m optiproductio.simulator --mqtt 127.0.0.1`; window 2: `python run.py --source mqtt` | "MQTT · live" and "NodeMCU online"; Apply limit changes the run label (command travelled down and the confirmation came back) | ☐ |
| 1.15 | Gateway lost | close window 1 (Ctrl+C) | "NodeMCU offline", "no data for N s" banner | ☐ |
| 1.16 | Historian | open `code\laptop\data\historian.sqlite` in DB Browser for SQLite | `events` table has rows with ms, st, ev, val | ☐ |
| 1.17 | CSV export | Run report > CSV | file opens in Excel | ☐ |
| 1.18 | Phone view | phone on the same Wi-Fi opens `http://<laptop IP>:5000` | page fits the screen | ☐ |
| 1.19 | Firmware compiles | Arduino IDE: Verify all three sketches | no errors | ☐ |
| 1.20 | Firmware logic on the PC (optional) | `cd code/firmware/uno_line_controller/host_test` then `sh run.sh` (needs g++) | `0 failure(s)` | ☐ |

## Part 2. Hardware bring-up (with `uno_hardware_test.ino`)

| # | Test | Pass when | ✓ |
|---|---|---|---|
| 2.1 | `s`: each of the 6 sensors | its column shows 1 only while a box is 3-5 cm in front; 0 otherwise | ☐ |
| 2.2 | Sensors in daylight / under tube lights | no flicker between 0 and 1 with no box | ☐ |
| 2.3 | `l`: LEDs | correct LED lights in order S1 g, S1 r, S2 g, S2 r, S3 g, S3 r | ☐ |
| 2.4 | `g`: gate | arm blocks the chute at CLOSED and lets one box slide at OPEN; UNO does not reset | ☐ |
| 2.5 | Gate holds a full chute | 8 boxes behind the closed arm: none slips through | ☐ |
| 2.6 | Chute | a released box slides all the way onto S1 every time (10 out of 10) | ☐ |
| 2.7 | `b`: buzzer | two beeps | ☐ |
| 2.8 | NodeMCU alone | its Serial Monitor shows "Wi-Fi OK" and "MQTT connected", blue LED solid | ☐ |
| 2.9 | `w`: link both ways | `# gw ok wifi=1 mqtt=1` lines appear | ☐ |

## Part 3. Full line (with `uno_line_controller.ino`)

| # | Test | Pass when | ✓ |
|---|---|---|---|
| 3.1 | Boot | lamp test flash + chirp; gate opens once; all stations green steady; event log shows BOOT and BUF | ☐ |
| 3.1b | Gate sequence | box reaches S1 → gate closes; box leaves S1 → gate reopens about 1 s later; never 2 boxes on S1 | ☐ |
| 3.1c | Buffer from Serial Monitor | type `B,5`: answer `BUF,5`; hold a box on S1: green blinks for 5 s, then red steady + one beep | ☐ |
| 3.2 | One box end to end | IN/OUT events for S1, S2, S3 in order; Done = 1; each OUT shows a cycle time close to a stopwatch | ☐ |
| 3.3 | 20 boxes | dashboard Done count = boxes counted by hand | ☐ |
| 3.4 | WIP limit 3 | gate never releases a 4th box while 3 are in the line; double beep on hold | ☐ |
| 3.5 | Limit from dashboard | Apply L = 2: UNO answers (LIMIT in the event log) within 1 s over MQTT | ☐ |
| 3.6 | Settings survive restart | press the UNO reset button: BOOT shows the same limit and BUF the same buffer time (EEPROM) | ☐ |
| 3.7 | Andon | empty stations green steady; a station with a box blinks green; red steady only after the buffer time | ☐ |
| 3.8 | Stall | hold a box on S2 for 2 × buffer (20 s at 10 s): S2 stays red, triple beep, STALL event, line DOWN | ☐ |
| 3.9 | Wi-Fi loss | turn the hotspot off for 20 s: line keeps working (gate, LEDs); dashboard warns; data resumes when hotspot returns | ☐ |
| 3.10 | USB backup | `python run.py --source usb --port COMx` shows the same live data | ☐ |
| 3.11 | Lost lines | top-right pill shows no "lines lost" during a 5 min run (or very few) | ☐ |
| 3.12 | A/B test | 4 min no limit, 4 min L = 3: Run report shows both rows; screenshot it for the slides | ☐ |
| 3.13 | Rehearsal | whole demo script (SETUP_AND_RUN.md, Part E) done twice in under 10 min | ☐ |
