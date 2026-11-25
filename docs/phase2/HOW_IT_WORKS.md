# How OptiProductio works (ELI5 + the exact technical terms)

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**

Each idea has three parts: the plain-English picture, what the code actually does, and the technical words to use in the viva. Phase 1 feedback asked for precise terms, so say the "Viva wording" lines, not the analogies.

---

## 1. WIP (work in progress: boxes inside the line)
**Picture:** a dosa counter. Orders taken but not yet served are "WIP". Too many and every order waits longer.
**Code:** `WIP = boxes in at S1 (Station 1) − boxes out at S3`. Counted on the UNO from the S1 IN sensor (D2) and the S3 OUT sensor (D7).
**Viva wording:** "WIP is computed on the controller as cumulative releases minus cumulative completions, from discrete IR edge events, and published once a second in the status telegram."

## 2. The servo gate: S1 sequence (default) and CONWIP mode (constant WIP: a fixed cap on boxes inside the line)
**Picture (default):** a lift that takes one passenger at a time. The door opens when the lift is empty, closes once someone steps in, and opens again when they step out.
**Code (`updateGate()` in the UNO sketch), WIP limit 0 = default:**
1. At power-up S1 is empty, so the gate opens once and a box slides down.
2. The moment the S1 IN sensor sees the box, the gate closes (escapement: one box per opening).
3. When the S1 OUT sensor sees the box leave and S1 has stayed empty for 1 s (`GATE_REOPEN_MS`, lets the box clear the platform), the gate opens again. Repeat.

**Picture (CONWIP mode):** a nightclub bouncer with a clicker. Nobody new gets in until someone leaves.
**Code, WIP limit n > 0 (`L,n`):** the same S1 rule **and** `WIP < n`. If the line already holds n boxes the gate stays shut even with S1 empty (HOLD event, double beep). Both settings are saved in EEPROM, so they survive a reset.
**Trade-off to say openly:** the default S1 rule only looks at S1, so boxes can still pile up in front of a slow S2 or S3. CONWIP looks at the whole line. Phase 1 named the CONWIP gate as part of our USP, so in the demo show the default first, then switch on L = 3 and compare in the run report.
**Why CONWIP helps:** Little's law (below): with the same throughput, less WIP means shorter lead time.
**Viva wording:** "Closed-loop CONWIP release control. The control loop runs locally on the UNO; the supervisory layer (laptop) only writes the setpoint L over MQTT, the same split as PLC control versus MES in ISA-95."
**Honest claim:** CONWIP release over MQTT on a lab line is published (Thürer et al. 2023); we do not claim the gate as new. Our combination is the gate + active-period bottleneck detection + historian + ISO 22400 KPIs on low-cost hardware.

## 3. Cycle time (time a station spends on one box)
**Picture:** a stopwatch started when a plate reaches a cook and stopped when it leaves.
**Code:** each station keeps a small queue (FIFO: first in, first out) of IN times. On OUT, cycle time = now − oldest IN time. Sent as the value of the `OUT` event, in ms.
**Why 6 sensors and not 3:** exit-only sensors cannot tell working time from waiting time.

## 3b. Buffer time and the station LEDs (andon lights)
**Picture:** a pizza oven timer. A pizza that is still inside its 10 minutes is fine; only after the timer runs out do you shout. A thin-crust shop sets 5 minutes, a deep-dish shop 15. Same rule, different number.
**Code:** the buffer time is a user setting in seconds (default 10 s, range 1 to 3600 s). Set it in the Arduino Serial Monitor (115200 baud, "Newline", type `B,15`), or from the dashboard ("Buffer time and gate control" card), or over MQTT `.../cmd/buffer`. The UNO saves it in EEPROM and confirms with a `BUF` event.
| LED on the station | Meaning |
|---|---|
| green steady | station empty (for S1 this is also when the gate may open) |
| green blinking | box on the station, WIP (work in progress) within the buffer time |
| red steady | station busy without a break for longer than the buffer time: bottleneck |
- One short beep when a station turns red. If a station stays busy for 2 × the buffer time the UNO sends `STALL` (suspected breakdown) with a triple beep; the LED stays red steady.
- "Busy" is measured as the current active period (next section), so a station with a queue of boxes that never empties also turns red.
**Viva wording:** "The buffer time is a configurable tolerance on the active-period length before a station is flagged; it is stored in EEPROM and set through the serial command interface or MQTT."

## 3c. Breakdown lock (firmware v3.1)
**Picture:** a factory "stop the line" cord. When one machine breaks, the whole line stops: nobody upstream feeds it more work, nobody downstream starts anything new, and nobody's stopwatch keeps running while they wait for the repair.
**Code (`updateLock()` in the UNO sketch):** a station is **broken** once it has held a box for 2 × buffer time (`STALL`). Then:
1. The UNO sends `LOCK,<mask>` (bit 0 = S1, bit 1 = S2, bit 2 = S3; e.g. `LOCK,2` = S2 broken).
2. The sensors of every other station (upstream and downstream) are **ignored**. Only the broken station's own sensors still work.
3. The gate stays closed, so no new box enters.
4. The frozen stations' timers are **paused**, so a box waiting on S1 while S2 is broken does not turn red or get its own false breakdown.
5. When the stuck box leaves the broken station (its OUT sensor), the UNO sends `LOCK,0`, shifts the frozen timers forward by the frozen time, and the line runs again.
One exception: a box the gate had already let go just before the lock still lands on S1 and is counted (its clock starts paused at 0 s); otherwise WIP would be one short for the rest of the run.
The laptop reads the `LOCK` events and pauses the same timers, so the dashboard and the LEDs agree. The banner shows "Line LOCKED" and frozen stations are drawn dashed.
**Viva wording:** "On a suspected breakdown the controller latches a line-stop interlock: upstream and downstream inputs are inhibited, release is blocked, and the blocked/starved stations' active-period clocks are suspended until the faulted station clears."

## 4. Bottleneck by the active-period method (Roser)
**Picture:** in a relay race, the runner who holds the baton the longest without handing it over is slowing the team.
**Code:** a station is **active** while a box is on it (working, or finished but not yet taken away = blocked) and **idle** while empty (starved). At any instant the bottleneck is the station whose current active period is the longest. On the UNO (`updateBottleneck()`) and on the live dashboard tile only stations already over the buffer time can be named, so a box that has just arrived is never called a bottleneck. `analytics.roser()` on the laptop does the full run analysis with the textbook method (no buffer), so the percentages stay comparable with Roser's papers.
- **Sole bottleneck:** only one station's period is the longest.
- **Shifting bottleneck:** when the longest period passes from station A to station B and their periods overlap, the overlap time counts as "shifting" for both.
- The bar chart shows % of run time each station was sole/shifting bottleneck. The station with the largest total is the primary bottleneck. The "average active period" ranking (Roser's original 2001 method) is shown too.
**Viva wording:** "Momentary bottleneck by the active-period method, sole and shifting bottleneck percentages over the run, computed from controller timestamps with 0.1 to 0.2 s resolution."
**Why not just "slowest average cycle time"?** That misses shifting bottlenecks and breakdowns; the active-period method uses states, which a busy/idle sensor pair gives us directly.

## 5. Downtime and the Pareto chart
**Picture:** a shop's register: if no sale has rung up for a long time, something is wrong. Then you ask why.
**Code:** the line is DOWN when no box has left S3 for longer than "line down after" (18 s by default, 3 × planned cycle). The lost time counts from one planned cycle after the last box (Vorne XL style). Each down interval gets a reason from what the stations were doing:
- Start-up: no box out yet in this run.
- Starved: stations mostly idle (chute empty or gate held).
- Breakdown suspected at Sx: one station active for longer than the stall limit (2 × buffer time, 20 s at the default 10 s).
- Slow station Sx: otherwise, the station busiest in that interval.
The Pareto chart sorts reasons by lost seconds with a cumulative % line (the 80/20 rule).

## 6. KPIs with ISO 22400-2 names (KPI: key performance indicator)
| Symbol | Name | Formula |
|---|---|---|
| PBT | Planned busy time | run end − run start |
| ADOT | Actual unit down time | sum of DOWN intervals |
| APT | Actual production time | PBT − ADOT |
| PQ | Produced quantity | boxes out of S3 |
| SQ | Scrap quantity | boxes marked scrap by the operator |
| BDQ | Breakdown parts | boxes out of S3 that stayed on any one station longer than 2 × buffer time |
| GQ | Good quantity | GQ = PQ − SQ − BDQ |
| PRI | Planned run time per item | set in Settings (6 s default) |
| A | Availability | APT / PBT |
| E | Effectiveness (performance) | PRI × PQ / APT, capped at 100 % |
| QR | Quality ratio | GQ / PQ |
| OEE | OEE index (overall equipment effectiveness) | A × E × QR |
| TR | Throughput rate | PQ / APT |
**Good-part rule:** a box is good if it left every station before that station was declared broken (its cycle time at each station ≤ 2 × buffer time). A slow box that turned the LED red (over the buffer) is still good. The laptop follows each box through S1 → S2 → S3 in FIFO order to apply this.
We cite ISO 22400-2 for the names and structure; the formulas are the standard textbook forms (we could not read the paywalled text word by word). Say exactly that if asked. TR uses APT where ISO uses order execution time.

## 7. Little's law
**Picture:** a queue at a ticket counter. If 2 people are served per minute and each spends 5 minutes in the queue, there are about 10 people in it.
**Formula:** WIP = TH × LT (throughput × lead time). The dashboard and run report show both sides. If they disagree a lot, a sensor is missing boxes.
**Viva wording:** "We validate the measurement chain with Little's law: time-averaged WIP against throughput times mean flow time."

## 8. The IIoT chain (IIoT: Industrial Internet of Things)
**Picture:** referee (UNO) → reporter with a walkie-talkie (NodeMCU) → newsroom post office (Mosquitto) → editors (Python) → newspaper (dashboard) + archive (SQLite).
- **Serial telegram:** one CSV line per event `E,seq,ms,station,event,value`, and a status line `S,...` every second. `seq` counts lines so the laptop can detect lost lines (shown as "lines lost").
- **Why 19200 baud:** both ends use SoftwareSerial (bit-banged in software). At 9600 one byte takes about 1 ms with interrupts blocked, which can make the UNO's millisecond clock miss ticks; at 19200 it is about 0.5 ms. Faster than ~38400 gets unreliable for SoftwareSerial reception.
- **MQTT topics (ISA-95 style hierarchy enterprise/site/line/cell):** `rvce/idealab/line1/s2/event`, `rvce/idealab/line1/status`, commands on `rvce/idealab/line1/cmd/wip_limit` and `rvce/idealab/line1/cmd/buffer`. The status line now ends with the buffer time in seconds. The gateway uses an MQTT **Last Will** so the dashboard shows "NodeMCU offline" if it drops.
- **QoS:** the PubSubClient library publishes at QoS 0 (at most once). We make up for it with sequence numbers (loss is visible) and the USB backup path. Commands are subscribed at QoS 1.
- **Edge autonomy:** if Wi-Fi or the laptop fails, the UNO keeps running the gate, LEDs and buzzer.
- **Historian:** SQLite tables `sessions`, `runs`, `events`, `samples`, `commands`. All analysis uses the UNO clock, so Wi-Fi delay never changes a cycle time.
- **Scaling story:** a second line = another UNO + NodeMCU publishing under `rvce/idealab/line2/...`. No change to the broker; the laptop software would need a line selector.

## 9. Small design details examiners may ask about
- **Debounce + hold-off + re-arm:** a sensor must be stable for 25 ms, cannot fire again within 400 ms, and must have seen nothing for 300 ms before it can count a new box, so a box wobbling under a sensor is one count.
- **S1 one-box rule:** S1 can only hold one box (the gate closes on the first S1 IN). A second S1 IN before the gate has opened again is the same box re-triggering the sensor: it is ignored and logged as `ERR,3`. This stops WIP from being inflated.
- **Servo detach:** the sketch powers the servo pulses for 450 ms after each move, then detaches. This stops jitter caused by SoftwareSerial interrupts and saves current. The gate arm stays put by gear friction.
- **Separate servo supply + 470 µF:** prevents brown-out resets of the UNO.
- **Voltage divider 1 k / 2.2 k:** 5 V → about 3.4 V for the ESP8266 input.
- **ERR events:** OUT without IN means an IN sensor missed a box; the line count stays correct because S3 OUT still counts.
- **Runs:** changing the limit starts a new run automatically, so A/B comparisons are clean. Changing the buffer time does not start a new run, because it changes only the alarm, not the flow of boxes.

## 10. What is borrowed from industry products (say it openly)
- Scoreboard tiles, good count vs target, efficiency: Vorne XL.
- Timeline/chronogram of states, downtime Pareto: Vorne XL and Evocon.
- Andon lights per station: Toyota Production System practice, stack lights in MachineMetrics/Vorne.
- End-of-run report: Vorne XL "run report" idea.
- Visual style: velotic.com (GE Vernova's industrial software brand): dark, big numerals, calm panels.

## References to cite
- Roser, C., Nakano, M., Tanaka, M. (2001, 2002). Active-period bottleneck detection and shifting bottleneck papers.
- Hopp, W. J., Spearman, M. L. Factory Physics (CONWIP, Little's law).
- Thürer, M. et al. (2023). ConWIP on a LEGO model line with MQTT (prior work).
- ISO 22400-2:2014. KPIs for manufacturing operations management.
- IEC 62264 / ISA-95. Enterprise-control system integration (topic hierarchy idea).
