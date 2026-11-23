# OptiProductio

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**
IEM IDEA Lab EL project (topic: Smart Production Workflow and Resource Optimization System).

OptiProductio is a tabletop production line with three hand-operated stations (S1, S2, S3). An Arduino UNO reads six IR sensors (one at the entry and one at the exit of each station), so it knows how many boxes are inside the line (WIP: work in progress) and how long each station holds each box (cycle time). A servo gate at the chute releases a new box only while WIP is below a limit (CONWIP: constant WIP). The UNO finds the bottleneck with Roser's active-period method and shows it on red/green LEDs. A NodeMCU ESP8266 sends every event over Wi-Fi as MQTT messages (ISA-95 style topics) to a Mosquitto broker on a laptop, where a Python program stores them in an SQLite historian and serves a live dashboard with ISO 22400 KPI names, a timeline, a downtime Pareto and a run report for comparing WIP limits.

This is a student prototype.

## Start here
| You want to | Read |
|---|---|
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
    uno_line_controller/      the UNO sketch: sensors, WIP, CONWIP gate, bottleneck LEDs, buzzer, serial telegrams
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
  phase2/                     setup guide, wiring, test checklist, how it works
  phase1/ brief/ plans/ research/   earlier decks, brief, roadmap and research
```

## Hardware
Arduino UNO (CH340), 6 × FC-51 IR sensors, SG90 servo with its own 5 V 2 A adapter and a 470 µF capacitor, NodeMCU ESP8266 (CP2102), 3 red + 3 green LEDs with 5 × 220 Ω and 1 × 1 kΩ, 1 kΩ / 2.2 kΩ divider, 5 V active buzzer, 400-point breadboard, jumpers. Laptop runs Mosquitto, Python and the browser.

## Notes
- Firmware compile-checked: UNO sketches with avr-gcc against the official Arduino AVR core; the gateway with arduino-cli and ESP8266 core 3.1.2 + PubSubClient 2.8. Python tested with the built-in simulator over the direct, USB-serial (virtual port) and Mosquitto MQTT paths.
- Simulator numbers are simulated. Present them as such.
- Docs are never overwritten. A new version is saved as v2, v3 and so on.
