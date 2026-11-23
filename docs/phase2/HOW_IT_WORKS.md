# How OptiProductio works (ELI5 + the exact technical terms)

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**

Each idea has three parts: the plain-English picture, what the code actually does, and the technical words to use in the viva. Phase 1 feedback asked for precise terms, so say the "Viva wording" lines, not the analogies.

---

## 1. WIP (work in progress: boxes inside the line)
**Picture:** a dosa counter. Orders taken but not yet served are "WIP". Too many and every order waits longer.
**Code:** `WIP = boxes in at S1 (Station 1) − boxes out at S3`. Counted on the UNO from the S1 IN sensor (D2) and the S3 OUT sensor (D7).
**Viva wording:** "WIP is computed on the controller as cumulative releases minus cumulative completions, from discrete IR edge events, and published once a second in the status telegram."

## 2. CONWIP gate (constant WIP: a fixed cap on boxes inside the line)
**Picture:** a nightclub bouncer with a clicker. Nobody new gets in until someone leaves.
**Code (`updateGate()` in the UNO sketch):** the servo opens only when `WIP < limit` **and** S1 is empty **and** 1.5 s have passed since it last closed. When the S1 IN sensor sees the box, the gate closes at once (escapement: one box per opening). The limit is saved in EEPROM, so it survives a reset.
**Why it helps:** Little's law (below): with the same throughput, less WIP means shorter lead time.
**Viva wording:** "Closed-loop CONWIP release control. The control loop runs locally on the UNO; the supervisory layer (laptop) only writes the setpoint L over MQTT, the same split as PLC control versus MES in ISA-95."
**Honest claim:** CONWIP release over MQTT on a lab line is published (Thürer et al. 2023); we do not claim the gate as new. Our combination is the gate + active-period bottleneck detection + historian + ISO 22400 KPIs on low-cost hardware.

## 3. Cycle time (time a station spends on one box)
**Picture:** a stopwatch started when a plate reaches a cook and stopped when it leaves.
**Code:** each station keeps a small queue (FIFO: first in, first out) of IN times. On OUT, cycle time = now − oldest IN time. Sent as the value of the `OUT` event, in ms.
**Why 6 sensors and not 3:** exit-only sensors cannot tell working time from waiting time.

## 4. Bottleneck by the active-period method (Roser)
**Picture:** in a relay race, the runner who holds the baton the longest without handing it over is slowing the team.
**Code:** a station is **active** while a box is on it (working, or finished but not yet taken away = blocked) and **idle** while empty (starved). At any instant the bottleneck is the station whose current active period is the longest (`updateBottleneck()` on the UNO lights its red LED; `analytics.roser()` on the laptop does the full analysis).
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
- Breakdown suspected at Sx: one station active for longer than the stall limit (20 s).
- Slow station Sx: otherwise, the station busiest in that interval.
The Pareto chart sorts reasons by lost seconds with a cumulative % line (the 80/20 rule).

## 6. KPIs with ISO 22400-2 names (KPI: key performance indicator)
| Symbol | Name | Formula |
|---|---|---|
| PBT | Planned busy time | run end − run start |
| ADOT | Actual unit down time | sum of DOWN intervals |
| APT | Actual production time | PBT − ADOT |
| PQ / SQ / GQ | Produced / scrap / good quantity | GQ = PQ − SQ |
| PRI | Planned run time per item | set in Settings (6 s default) |
| A | Availability | APT / PBT |
| E | Effectiveness (performance) | PRI × PQ / APT, capped at 100 % |
| QR | Quality ratio | GQ / PQ |
| OEE | OEE index (overall equipment effectiveness) | A × E × QR |
| TR | Throughput rate | PQ / APT |
We cite ISO 22400-2 for the names and structure; the formulas are the standard textbook forms (we could not read the paywalled text word by word). Say exactly that if asked. TR uses APT where ISO uses order execution time.

## 7. Little's law
**Picture:** a queue at a ticket counter. If 2 people are served per minute and each spends 5 minutes in the queue, there are about 10 people in it.
**Formula:** WIP = TH × LT (throughput × lead time). The dashboard and run report show both sides. If they disagree a lot, a sensor is missing boxes.
**Viva wording:** "We validate the measurement chain with Little's law: time-averaged WIP against throughput times mean flow time."

## 8. The IIoT chain (IIoT: Industrial Internet of Things)
**Picture:** referee (UNO) → reporter with a walkie-talkie (NodeMCU) → newsroom post office (Mosquitto) → editors (Python) → newspaper (dashboard) + archive (SQLite).
- **Serial telegram:** one CSV line per event `E,seq,ms,station,event,value`, and a status line `S,...` every second. `seq` counts lines so the laptop can detect lost lines (shown as "lines lost").
- **Why 19200 baud:** both ends use SoftwareSerial (bit-banged in software). At 9600 one byte takes about 1 ms with interrupts blocked, which can make the UNO's millisecond clock miss ticks; at 19200 it is about 0.5 ms. Faster than ~38400 gets unreliable for SoftwareSerial reception.
- **MQTT topics (ISA-95 style hierarchy enterprise/site/line/cell):** `rvce/idealab/line1/s2/event`, `rvce/idealab/line1/status`, commands on `rvce/idealab/line1/cmd/wip_limit`. The gateway uses an MQTT **Last Will** so the dashboard shows "NodeMCU offline" if it drops.
- **QoS:** the PubSubClient library publishes at QoS 0 (at most once). We make up for it with sequence numbers (loss is visible) and the USB backup path. Commands are subscribed at QoS 1.
- **Edge autonomy:** if Wi-Fi or the laptop fails, the UNO keeps running the gate, LEDs and buzzer.
- **Historian:** SQLite tables `sessions`, `runs`, `events`, `samples`, `commands`. All analysis uses the UNO clock, so Wi-Fi delay never changes a cycle time.
- **Scaling story:** a second line = another UNO + NodeMCU publishing under `rvce/idealab/line2/...`. No change to the broker; the laptop software would need a line selector.

## 9. Small design details examiners may ask about
- **Debounce + hold-off:** a sensor must be stable for 25 ms and cannot fire again within 400 ms, so one box = one count.
- **Servo detach:** the sketch powers the servo pulses for 450 ms after each move, then detaches. This stops jitter caused by SoftwareSerial interrupts and saves current. The gate arm stays put by gear friction.
- **Separate servo supply + 470 µF:** prevents brown-out resets of the UNO.
- **Voltage divider 1 k / 2.2 k:** 5 V → about 3.4 V for the ESP8266 input.
- **ERR events:** OUT without IN means an IN sensor missed a box; the line count stays correct because S3 OUT still counts.
- **Runs:** changing the limit starts a new run automatically, so A/B comparisons are clean.

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
