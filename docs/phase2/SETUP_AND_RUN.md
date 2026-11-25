# OptiProductio Phase 2: setup and run guide

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**

This guide takes you from "box of parts" to "live dashboard". Do the steps in order. Every step ends with a check, so you know it worked before you move on. Written for a Windows laptop.

> ELI5: the UNO is the line's **referee** (it watches every box and blows the whistle), the NodeMCU is the **reporter** (it radios the referee's calls to the press box), and the laptop is the **scoreboard + record book**.

```
6 IR sensors + servo gate + LEDs + buzzer
            │ wires
      Arduino UNO  ── USB cable ──────────────► laptop (backup path, "usb" mode)
            │ 2 wires + GND (19200 baud)
   NodeMCU ESP8266 ── Wi-Fi (phone hotspot) ──► Mosquitto broker ──► run.py ──► dashboard in the browser
                                                (all on the laptop)     │
                                                                SQLite historian
```

You can do **Part A (software)** today with no hardware at all, using the simulator.

---

## Part A. Laptop software (30 min, no hardware needed)

### A1. Get the code
Download the repo (green "Code" button > Download ZIP, or `git clone`). The folders you need:

| Folder | What is inside |
|---|---|
| `code/firmware/uno_line_controller/` | the real UNO sketch |
| `code/firmware/uno_hardware_test/` | a test sketch to check every wire |
| `code/firmware/nodemcu_gateway/` | the NodeMCU Wi-Fi gateway sketch + `config.h` |
| `code/laptop/` | Python server, simulator, dashboard, tests |
| `docs/phase2/` | this guide, wiring diagram, test checklist, how it works |

### A2. Install Python
1. Install Python 3.11 or newer from python.org. On the first screen tick **"Add python.exe to PATH"**.
2. Open **Command Prompt** and go to the laptop folder:
   ```
   cd C:\Users\<you>\Desktop\OptiProductio\code\laptop
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
**Check:** `python -m pytest -q` prints `10 passed`.

### A3. Run the simulator
```
python run.py --source sim
```
The browser opens `http://localhost:5000`. Boxes start moving within 2 seconds.
**Check:** "Simulator · live" at the top right, the Good parts number climbs, S2 turns orange (bottleneck).

Try the other scenarios (Ctrl+C stops the server first):
```
python run.py --source sim --scenario breakdown --speed 4     S2 freezes for 45 s: line goes DOWN, Pareto says "Breakdown suspected at S2"
python run.py --source sim --scenario shifting --speed 4      bottleneck moves from S2 to S3 halfway
python run.py --source sim --scenario starve --speed 4        boxes stop coming back: "Starved"
```
`--speed 4` runs 4 times faster than real life, handy for rehearsal.

> Note: numbers from the simulator are **simulated**. In slides and in the viva, call them "simulator results", never "our line's results".

### A4. Install Mosquitto (the MQTT broker)
ELI5: Mosquitto is a **post office** on the laptop. The NodeMCU drops letters in topic "boxes" (like `rvce/idealab/line1/s2/event`), and our Python program has a subscription to those boxes.

1. Download the Windows 64-bit installer from mosquitto.org/download and install it (default folder `C:\Program Files\mosquitto`).
2. The installer also adds a Windows **service** that only listens to the laptop itself. Stop it, because we start our own copy with our config. Open Command Prompt **as administrator**:
   ```
   net stop mosquitto
   ```
3. Allow other devices (the NodeMCU) to reach port 1883 through the Windows firewall (still as administrator):
   ```
   netsh advfirewall firewall add rule name="Mosquitto 1883" dir=in action=allow protocol=TCP localport=1883
   ```
4. Start the broker with our config (normal Command Prompt, keep this window open):
   ```
   "C:\Program Files\mosquitto\mosquitto.exe" -c C:\Users\<you>\Desktop\OptiProductio\code\laptop\mosquitto\mosquitto.conf -v
   ```
   **Check:** it prints `Opening ipv4 listen socket on port 1883`.
5. Test the whole MQTT path with a pretend gateway. In a second window (with the `.venv` active):
   ```
   python -m optiproductio.simulator --mqtt 127.0.0.1
   ```
   and in a third window:
   ```
   python run.py --source mqtt
   ```
   **Check:** dashboard shows "MQTT · live" and "NodeMCU online". Press **Apply limit** with a new value: within a second the run label changes to the new limit. That proves commands also travel back down.

Why `mosquitto.conf` matters: Mosquitto 2.x refuses outside connections unless the config has `listener 1883` and an auth setting. Ours has `listener 1883 0.0.0.0` and `allow_anonymous true` (fine on a private hotspot; see the comments in the file for the password version).

---

## Part B. Arduino IDE (20 min)

1. Install **Arduino IDE 2.x** from arduino.cc.
2. **UNO driver:** plug in the UNO. If no new COM port appears in Device Manager > Ports, install the **CH340** driver (clone boards use it).
3. **ESP8266 support:** File > Preferences > "Additional boards manager URLs", paste
   `https://arduino.esp8266.com/stable/package_esp8266com_index.json`.
   Then Tools > Board > Boards Manager, search **esp8266**, install "esp8266 by ESP8266 Community".
4. **NodeMCU driver:** our NodeMCU uses a **CP2102** chip. If its COM port does not appear, install the Silicon Labs CP210x driver.
5. **Library:** Sketch > Include Library > Manage Libraries, search **PubSubClient**, install the one by Nick O'Leary. (Servo, SoftwareSerial and EEPROM are already built in.)

**Check:** open `uno_hardware_test.ino`, board "Arduino Uno", press Verify (✓). It compiles.

---

## Part C. Build and test the electronics, one block at a time

Wire using `docs/phase2/WIRING.md` and `wiring_diagram.png`. **Unplug USB while you change wires.**

ELI5 for testing one block at a time: if you switch on a whole new house and the lights do not work, you do not know which of 50 wires is wrong. If you test each room as you wire it, you always know.

1. **Flash the test sketch.** Open `code/firmware/uno_hardware_test/uno_hardware_test.ino`, Tools > Board "Arduino Uno", Tools > Port (your COM port), Upload. Open Serial Monitor at **115200** baud, line ending "Newline".
2. **Sensors.** Wire the 6 FC-51. Type `s`. Each column shows 1 when a box is in front of that sensor. Tune each sensor's blue potentiometer with a small screwdriver until it turns on at 3 to 5 cm and off when the box leaves (the small LED on the module helps). Type any key to stop.
3. **LEDs.** Wire the 6 LEDs. Type `l`. They light in order: S1 green, S1 red, S2 green, S2 red, S3 green, S3 red.
4. **Servo gate.** Wire the servo with its **own 5 V adapter** and the 470 µF capacitor, and join the adapter's minus to the GND rail. Type `g`. The arm moves CLOSED/OPEN three times. If the UNO resets during this, the servo is not on its own supply or the GNDs are not joined. Adjust `GATE_CLOSED_DEG` / `GATE_OPEN_DEG` at the top of both sketches to suit your popsicle arm. Defaults: CLOSED = 95°, OPEN = 10°, so opening swings the arm to the right (looking down the lane). If CLOSED does not hang straight across the lane, pull the horn off the servo shaft while it sits at CLOSED and push it back on with the arm hanging straight down. Open swing too small: lower `GATE_OPEN_DEG` (not below 0). Too big: raise it.
5. **Buzzer.** Type `b`: two beeps.
6. **Gateway link** is tested in Part D.

---

## Part D. NodeMCU gateway (20 min)

1. Phone hotspot: turn it on and make sure it uses **2.4 GHz** (Android: Hotspot > Advanced > AP band 2.4 GHz; iPhone: turn on "Maximise Compatibility"). The ESP8266 cannot see 5 GHz.
2. Connect the **laptop** to the same hotspot. In Command Prompt run `ipconfig` and note the Wi-Fi adapter's **IPv4 Address** (for example 192.168.43.25). If Windows asks, mark the network as **Private**.
3. Open `code/firmware/nodemcu_gateway/config.h` and fill in `WIFI_SSID`, `WIFI_PASSWORD`, and `MQTT_HOST` = the laptop IP.
4. Plug the NodeMCU into the laptop with its micro-USB cable. Tools > Board > "NodeMCU 1.0 (ESP-12E Module)", choose its COM port, Upload.
5. Serial Monitor at 115200. **Check:** `Wi-Fi OK, my IP ...` then `MQTT connected`. The blue on-board LED stays on when MQTT is connected (slow blink = Wi-Fi only, fast blink = no Wi-Fi).
6. Wire the link (UNO unplugged): UNO A3 → 1 kΩ → NodeMCU D5, with 2.2 kΩ from D5 to GND; NodeMCU D6 → UNO A2; NodeMCU GND → GND rail.
7. With the UNO still running the **test sketch**, type `w` in the UNO's Serial Monitor. **Check:** lines like `# gw ok wifi=1 mqtt=1 ip=192.168.43.x` come back every second. Both directions work.

---

## Part E. Run the real line

1. Flash `code/firmware/uno_line_controller/uno_line_controller.ino` to the UNO. The LEDs flash once and the buzzer chirps (lamp test). The gate opens once and all three stations show **green steady** (empty).
   - First boot defaults: buffer time 10 s, WIP limit off (gate follows S1 only). Flashing v3 over v2 ignores the old saved limit once.
   - **Set the buffer time:** open Serial Monitor (115200, "Newline") and type `B,15` for 15 s. The UNO answers `E,...,0,BUF,15` and keeps it in EEPROM. Type `H` to see the current settings. (Close the Serial Monitor before `run.py --source usb`; the dashboard card does the same job.)
   - What you should see per box: box reaches S1 → gate closes, S1 green **blinks**; still on S1 after the buffer time → S1 **red steady** + one beep; box leaves S1 → S1 green steady, gate opens again after 1 s.
2. Start Mosquitto (A4 step 4), then:
   ```
   python run.py --source mqtt
   ```
3. Put 6 to 8 boxes in the chute. Students act as operators: hold a box on each station for a few seconds (pretend work), then push it past the OUT sensor to the next station.

**Backup path (no Wi-Fi needed):** stop `run.py`, close the Arduino Serial Monitor, then
```
python run.py --source usb --port COM5
```
(use your UNO's COM port; `python -m serial.tools.list_ports` lists them). The UNO sends the same lines on USB all the time, so switching takes 30 seconds.

Phones on the same hotspot can open the dashboard too: `http://<laptop IP>:5000`.

### Demo script for the evaluation (about 8 minutes)
1. **Normal flow (2 min), S1 gate, buffer 10 s:** WIP limit "Off". Show one box per opening and green blinking while a box is worked on. The S2 operator works a little slower than the others (about 12 s per box) so S2 turns red steady after 10 s. Point at the Bottleneck analysis chart.
2. **Change the buffer (1 min):** set 15 s from the dashboard (or `B,15` in the Serial Monitor): S2 now stays green blinking. Explain: different products need different station times, so the alarm threshold is a setting, not a fixed number.
3. **Turn on CONWIP (3 min):** set L = 3, Apply. The gate now also holds boxes when WIP hits 3 (amber banner, double beep). Show WIP and lead time dropping on the tiles while output per minute stays about the same.
4. **Breakdown (1 min):** keep a box on S2 for 2 × buffer time (20 s at 10 s). S2 stays red, triple beep, STALL event, line goes DOWN, the Pareto shows "Breakdown suspected at S2".
5. **Run report (2 min):** open "Run report". Compare the "S1 gate" run with the "L = 3" run: throughput, average WIP, lead time, and Little's law (WIP ≈ TH × LT).

Only claim what your own runs show. If the hardware misbehaves, switch to `--source usb`, and as a last resort show the simulator and say clearly that it is the simulator.

---

## Where things are saved
- `code/laptop/data/historian.sqlite`: every event (open with "DB Browser for SQLite" to show the raw historian).
- `code/laptop/data/settings.json`: dashboard settings (planned cycle time etc).
- CSV per run: Run report > CSV link.

## Common problems
| Symptom | Fix |
|---|---|
| `run.py --source usb` says "Access is denied" | Close the Arduino Serial Monitor; only one program can use the COM port. |
| Dashboard says "no data" in MQTT mode | Is Mosquitto running with our config? Is the NodeMCU LED solid? Is `MQTT_HOST` the laptop's IP **on the hotspot**? Firewall rule added? |
| NodeMCU prints `MQTT failed, state -2` | It cannot reach the laptop: wrong IP, firewall, or the laptop is on a different Wi-Fi. |
| A box is counted twice | Turn the FC-51 potentiometer down a little; or raise `IR_HOLDOFF_MS`. |
| Event log shows `ERR` "OUT without IN" | That station's IN sensor missed the box. Re-aim or re-tune it. Counts stay correct for the line. |
| WIP looks stuck high, gate never opens | A sensor missed boxes. Take all boxes off, put them back in the chute, press "Reset line counts". |
| UNO resets when the gate moves | Servo must be on the separate 5 V adapter; GNDs joined; capacitor polarity right. |
| Servo buzzes or jitters | Normal sketch detaches it after each move; check `SERVO_MOVE_MS` is not set too high. |
