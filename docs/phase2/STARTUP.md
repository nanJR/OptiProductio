# OptiProductio startup: every step and every command

**Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection**

Short version: **double-click `code\START_OptiProductio.bat`, then pick 1 (Wi-Fi) or 2 (USB).** The rest of this page explains each step behind that, and what to type if you prefer doing it by hand.

ELI5: starting the line is like opening a shop in the morning. First the electricity (power), then the cash register (UNO), then the phone line to head office (NodeMCU + Wi-Fi), then the post office that sorts the messages (Mosquitto), and last the manager's screen (dashboard). If you start them out of order, the manager's screen shows "no data" until everything behind it is up.

---

## Part 0. One-time installs (once per laptop, already done if the laptop worked yesterday)

| # | What | How | Check |
|---|---|---|---|
| 0.1 | Get the latest code | GitHub > nanJR/OptiProductio > green **Code** > **Download ZIP**, unzip. Or `git pull` in an existing clone. | `code\firmware\uno_line_controller\uno_line_controller.ino` says `v3.2` near the end. The script warns you if not. |
| 0.2 | Python 3.11+ | python.org. Tick **"Add python.exe to PATH"**. | `py --version` in Command Prompt |
| 0.3 | Python packages | Done by the script on first run. By hand: see Part 3. | script prints `[OK] Python environment ready` |
| 0.4 | Arduino IDE 2.x | arduino.cc | opens |
| 0.5 | UNO driver (CH340) | only if no COM port appears for the UNO | Device Manager > Ports shows `USB-SERIAL CH340 (COMx)` |
| 0.6 | ESP8266 board support | File > Preferences > Additional boards URL `https://arduino.esp8266.com/stable/package_esp8266com_index.json`, then Boards Manager > **esp8266** > Install | board "NodeMCU 1.0 (ESP-12E Module)" is listed |
| 0.7 | NodeMCU driver (CP2102) | Silicon Labs CP210x driver, only if no COM port appears | `Silicon Labs CP210x (COMy)` |
| 0.8 | PubSubClient library | Sketch > Include Library > Manage Libraries > **PubSubClient** (Nick O'Leary) | gateway sketch compiles |
| 0.9 | Mosquitto (Wi-Fi mode only) | mosquitto.org/download, Windows 64-bit installer, default folder | `C:\Program Files\mosquitto\mosquitto.exe` exists |
| 0.10 | Firewall + Mosquitto service | Right-click `START_OptiProductio.bat` > **Run as administrator** > option **7** | prints `[OK] Firewall open...` |

What option 7 runs, if you want to type it yourself (Command Prompt **as administrator**):
```
net stop mosquitto
sc config mosquitto start= demand
netsh advfirewall firewall add rule name="Mosquitto 1883" dir=in action=allow protocol=TCP localport=1883
netsh advfirewall firewall add rule name="OptiProductio dashboard 5000" dir=in action=allow protocol=TCP localport=5000
```
Why: the Windows Mosquitto service only listens to the laptop itself, so the NodeMCU cannot reach it. We stop it and run our own copy with `mosquitto.conf`, which listens on the hotspot network.

---

## Part 1. Flash the boards (once, and again only after a code change)

### 1.1 UNO (line controller)
1. Plug the UNO in by USB. Open `code\firmware\uno_line_controller\uno_line_controller.ino`.
2. Tools > Board > **Arduino Uno**. Tools > Port > the CH340 COM port.
3. Click **Verify** (✓), then **Upload** (→).
4. **Check:** LEDs all flash once, buzzer chirps, gate opens once, all three stations show **green steady**. Serial Monitor (115200 baud, line ending **Newline**) shows `# OptiProductio UNO line controller v3.2`.

### 1.2 NodeMCU (Wi-Fi gateway), only for Wi-Fi mode
1. Turn on the phone hotspot on **2.4 GHz**. Connect the laptop to it.
2. Find the laptop's IP: script option **6**, or `ipconfig` and read **IPv4 Address** under the Wi-Fi adapter.
3. Edit `code\firmware\nodemcu_gateway\config.h`: `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_HOST` = that IP.
4. Plug in the NodeMCU. Tools > Board > **NodeMCU 1.0 (ESP-12E Module)**, its COM port, **Upload**.
5. **Check:** Serial Monitor 115200 shows `Wi-Fi OK, my IP ...` then `MQTT connected` (only once Mosquitto is running, Part 2). Blue LED: solid = MQTT OK, slow blink = Wi-Fi only, fast blink = no Wi-Fi.

> The hotspot often gives the laptop a **new IP** each day. If `MQTT_HOST` no longer matches, re-flash the NodeMCU with the new IP, or use USB mode.

---

## Part 2. Start-up order on demo day

1. **Table power:** plug in the servo's separate 5 V adapter (GND joined to the UNO GND).
2. **Phone hotspot on** (2.4 GHz). Laptop joins it.
3. **UNO:** USB cable into the laptop. Lamp test, gate opens once, three green LEDs.
4. **Double-click `code\START_OptiProductio.bat`.**
5. Pick **1** for Wi-Fi or **2** for USB (details below).
6. **NodeMCU:** power it (USB to laptop or a phone charger). Within about 10 s the dashboard shows **NodeMCU online**.
7. Dashboard opens by itself at `http://localhost:5000`. Phones on the hotspot: `http://<laptop IP>:5000`.
8. On the dashboard, set the **buffer time of each station** (pick All stations / S1 / S2 / S3, set seconds, Apply; e.g. S1 8 s, S2 15 s, S3 6 s) and **WIP limit** (Off to start), press **Reset line counts** with the table empty, then put the boxes in the chute.

### What option 1 (Wi-Fi) does
1. Refuses to go on if the Mosquitto service is still running (run option 7 once as admin).
2. Prints the laptop IPv4 so you can compare it with `MQTT_HOST`.
3. If nothing is on port 1883 yet, opens a new window **"Mosquitto broker - keep open"** running
   `"C:\Program Files\mosquitto\mosquitto.exe" -c code\laptop\mosquitto\mosquitto.conf -v`
4. Starts the dashboard: `python run.py --source mqtt`

### What option 2 (USB backup) does
1. Lists COM ports (`python -m serial.tools.list_ports -v`). Look for the CH340 line.
2. Asks for the port (remembers the last one; just press Enter next time).
3. Starts: `python run.py --source usb --port COM5`
4. **Close the Arduino Serial Monitor first.** Only one program can open a COM port.

### Other menu options
| Option | Command it runs | Use |
|---|---|---|
| 3 | `python run.py --source sim` | rehearsal with no hardware |
| 4 | `python run.py --source sim --scenario breakdown --speed 4` | see the breakdown lock in 1 minute |
| 5 | `python -m pytest -q` | 19 automatic tests should pass |
| 6 | `ipconfig` + list COM ports | find the IP for `config.h` and the UNO port |
| 7 | firewall + stop Mosquitto service | once per laptop, as administrator |

> Simulator numbers are **simulated**. In the viva call them "simulator results", never the line's results.

---

## Part 3. The same thing by hand (if the script will not run)

Open **Command Prompt**:
```
cd C:\path\to\OptiProductio-main\code\laptop
py -m venv %LOCALAPPDATA%\OptiProductio\venv
%LOCALAPPDATA%\OptiProductio\venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```
Wi-Fi mode, window 1 (keep open):
```
"C:\Program Files\mosquitto\mosquitto.exe" -c C:\path\to\OptiProductio-main\code\laptop\mosquitto\mosquitto.conf -v
```
Wi-Fi mode, window 2 (venv active, in `code\laptop`):
```
python run.py --source mqtt
```
USB mode instead:
```
python run.py --source usb --port COM5
```
Useful extras:
```
python run.py --source sim --scenario breakdown --speed 4    simulator scenarios: normal, breakdown, shifting, starve, balanced
python -m optiproductio.simulator --mqtt 127.0.0.1           pretend NodeMCU, tests the whole MQTT path without hardware
python run.py --source mqtt --http-port 5001 --no-browser    other port, no browser pop-up
```

---

## Part 4. Commands the UNO understands

Type them in the Arduino Serial Monitor (115200, **Newline**). The dashboard buttons send the same commands.

| Type | Does | UNO answers |
|---|---|---|
| `B,15` | buffer time 15 s for **all** stations (saved in EEPROM). Red after 15 s, breakdown + line lock after 30 s | `E,...,1,BUF,15` `E,...,2,BUF,15` `E,...,3,BUF,15` |
| `B,2,20` | buffer time 20 s for **S2 only** (also `B,1,..` / `B,3,..`). Each station turns red after its own buffer and breaks down after 2 × its own buffer | `E,...,2,BUF,20` |
| `L,3` | WIP limit 3 (CONWIP). `L,0` = off, gate follows S1 only | `E,...,0,LIMIT,3` |
| `H` | show settings and this list | `# settings: ...` |
| `R` | reset counters (clear the table first) | `E,...,0,RESET,0` |
| `P` | ping (also re-sends the three buffers) | `E,...,0,PONG,...` + 3 BUF lines |

Events to recognise in the log: `IN`/`OUT` (box at a sensor), `GATE,1/0`, `BN,n` (bottleneck now Sn), `STALL` (breakdown suspected), `LOCK,mask` (line frozen: 1 = S1, 2 = S2, 4 = S3, 0 = running again), `HOLD` (WIP limit reached), `ERR,1` (OUT without IN: an IN sensor missed), `ERR,3` (S1 seen twice for one box, ignored).

---

## Part 5. Five-minute check before the examiners arrive

1. All 6 IR sensors: wave a box at each one, and the station LED / dashboard reacts. **Check S3 IN (pin D6)**: in the last run it never fired.
2. Gate: opens at power-up, closes when a box reaches S1.
3. Put one box through S1 → S2 → S3. **Good parts = 1, WIP back to 0.**
4. Hold a box on S2 for 2 × buffer. The banner says **Line LOCKED: breakdown at S2**, S1 and S3 show "Frozen", and waving a box at S1 or S3 changes nothing. Remove the box: the line runs again.
5. Press **Reset line counts** with the table empty, then start the real demo.

## Shutting down
Ctrl+C in the dashboard window, close the Mosquitto window, unplug the servo supply, then USB. The data stays in `code\laptop\data\historian.sqlite`.

## If something fails
| Symptom | Fix |
|---|---|
| Script says Python not found | Install Python with "Add to PATH" ticked, reopen the script |
| `[!] sketch is NOT v3.2` | Download the ZIP again from GitHub main |
| "Access is denied" on COM port | Close the Arduino Serial Monitor |
| Dashboard "no data" in Wi-Fi mode | Mosquitto window open? NodeMCU LED solid? `MQTT_HOST` = today's laptop IP? Option 7 done? If in doubt, switch to option 2 (USB): same data, 30 seconds |
| NodeMCU `MQTT failed, state -2` | wrong IP, firewall, or laptop on another Wi-Fi |
| WIP stuck high / gate never opens | a sensor missed boxes: clear the table, **Reset line counts** |
| UNO resets when the gate moves | servo must be on its own 5 V supply, GNDs joined |
