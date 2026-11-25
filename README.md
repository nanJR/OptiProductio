# OptiProductio

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**

IDEA Lab EL project, IEM, batch 2. EL topic: Smart Production Workflow and Resource Optimization System.

OptiProductio is a tabletop production line with three hand-operated stations (S1, S2, S3). An Arduino UNO reads six IR sensors (one at the entry and one at the exit of each station), so it knows how many boxes are inside the line (WIP: work in progress) and how long each station holds each box (cycle time). A servo gate at the chute lets one box onto S1 at a time: it opens when S1 is empty and closes as soon as a box arrives. An optional WIP limit adds CONWIP (constant WIP: the gate also waits until fewer than n boxes are inside the line). Each station has a user-set buffer time (seconds, saved in EEPROM): its green LED is steady when empty, blinks while a box is worked on, and its red LED turns steady once the station has been busy longer than the buffer time. Among those red stations the UNO names the bottleneck with Roser's active-period method. A NodeMCU ESP8266 sends every event over Wi-Fi as MQTT messages (ISA-95 style topics) to a Mosquitto broker on a laptop, where a Python program stores them in an SQLite historian and serves a live dashboard with ISO 22400 KPI names, a timeline, a downtime Pareto and a run report for comparing WIP limits.

This is a student prototype.

## Start here
| You want to | Read |
|---|---|
| Start the line on demo day (one-click `code/START_OptiProductio.bat`) | [docs/phase2/STARTUP.md](docs/phase2/STARTUP.md) |
| Set up and run everything, step by step | [docs/phase2/SETUP_AND_RUN.md](docs/phase2/SETUP_AND_RUN.md) |
| Wire the hardware | [docs/phase2/WIRING.md](docs/phase2/WIRING.md) and `docs/phase2/wiring_diagram.png` |
| Test without hardware, then with it | [docs/phase2/TEST_CHECKLIST.md](docs/phase2/TEST_CHECKLIST.md) |
| Understand it (ELI5 + viva wording) | [docs/phase2/HOW_IT_WORKS.md](docs/phase2/HOW_IT_WORKS.md) |

Quick try with no hardware:
```
cd code/laptop
pip install -r requirements.txt
python run.py --source sim
```
Then open http://localhost:5000.

## Folder layout
```
code/
  firmware/
    uno_line_controller/      the UNO sketch: sensors, WIP, S1/CONWIP gate, buffer time, bottleneck LEDs, buzzer, serial telegrams
      host_test/              runs the real sketch logic on a PC with fake pins (g++), no board needed
    uno_hardware_test/        flash first: tests each sensor, LED, the servo, buzzer and the gateway link
    nodemcu_gateway/          NodeMCU ESP8266: serial -> MQTT gateway (edit config.h)
  laptop/
    run.py                    start here: --source sim | usb | mqtt
    optiproductio/            protocol, simulator, sources, SQLite historian, analytics (KPIs, Roser), web server
    static/                   dashboard (index.html, app.js, style.css) and run report
    mosquitto/mosquitto.conf  broker config that accepts the NodeMCU
    tests/                    automatic tests (python -m pytest -q)
  legacy_phase1/              the Phase 1 sketch and Streamlit dashboard (kept for reference)
docs/
  EL_Workflow_and_Requirements.md   our EL rules, rubric and steps
  phase2/                           startup guide, setup guide, wiring, test checklist, how it works
  phase1/                           Phase I decks with preview PDFs (latest: IDEA_LAB_Phase-I v3, team and method deck v7, Phase I deck v4) and build scripts
  brief/                            teammate project brief (latest v3) and the 3D demo-day views
  plans/                            growth roadmap (latest v2, parked as future enhancement)
  research/                         research reports (latest: industry report v4, WIP research v2) and the notes behind them
```

## Hardware
Arduino UNO (CH340), 6 × FC-51 IR sensors, SG90 servo with its own 5 V 2 A adapter and a 470 µF capacitor, NodeMCU ESP8266 (CP2102), 3 red + 3 green LEDs with 5 × 220 Ω and 1 × 1 kΩ, 1 kΩ / 2.2 kΩ divider, 5 V active buzzer, 400-point breadboard, jumpers. Laptop runs Mosquitto, Python and the browser.

## Notes
- Firmware compile-checked: UNO sketches with avr-gcc against the official Arduino AVR core; the gateway with arduino-cli and ESP8266 core 3.1.2 + PubSubClient 2.8. Python tested with the built-in simulator over the direct, USB-serial (virtual port) and Mosquitto MQTT paths.
- Simulator numbers are simulated. Present them as such.
- Docs are never overwritten. A new version is saved as v2, v3 and so on.
