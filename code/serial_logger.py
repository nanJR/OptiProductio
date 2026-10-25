"""OptiProductio serial logger: reads the Arduino over USB and writes CSV files
that the dashboard reads. Run:  python serial_logger.py COM3   (Mac/Linux: /dev/ttyACM0)"""
import csv
import sys
import time
from pathlib import Path

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM3"
DATA = Path("data")
EVENTS = DATA / "live_events.csv"
STATUS = DATA / "live_status.csv"
CAP_FILE = DATA / "cap.txt"          # the dashboard writes the WIP cap here

DATA.mkdir(exist_ok=True)
with open(EVENTS, "w", newline="") as f:
    csv.writer(f).writerow(["t", "event", "station", "reason", "source"])
with open(STATUS, "w", newline="") as f:
    csv.writer(f).writerow(["t", "c1", "c2", "c3", "scrap", "wip", "bin_parts", "state", "cap"])

arduino = serial.Serial(PORT, 9600, timeout=1)
time.sleep(2)                         # the UNO restarts when the port opens
print("Logging from", PORT, "- press Ctrl+C to stop")
sent_cap = None

while True:
    line = arduino.readline().decode(errors="ignore").strip()
    if line.startswith("E,"):
        _, ms, event, detail = line.split(",")
        station = detail if detail.isdigit() else ""
        reason = "" if detail.isdigit() else detail
        with open(EVENTS, "a", newline="") as f:
            csv.writer(f).writerow([int(ms) / 1000, event, station, reason, "arduino"])
        print(line)
    elif line.startswith("S,"):
        parts = line.split(",")
        with open(STATUS, "a", newline="") as f:
            csv.writer(f).writerow([int(parts[1]) / 1000] + parts[2:])

    if CAP_FILE.exists():
        cap = CAP_FILE.read_text().strip()
        if cap.isdigit() and cap != sent_cap:
            arduino.write(f"CAP {cap}\n".encode())
            sent_cap = cap
