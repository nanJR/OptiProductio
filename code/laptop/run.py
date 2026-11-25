"""Start OptiProductio on the laptop.

  python run.py --source sim                       no hardware, simulated line
  python run.py --source usb --port COM5           UNO on a USB cable (backup path)
  python run.py --source mqtt                      UNO -> NodeMCU -> Wi-Fi -> Mosquitto (main path)

Then open http://localhost:5000 (phones on the same hotspot: http://<laptop IP>:5000).
"""
import argparse
import logging
import os
import threading
import webbrowser

from optiproductio.engine import Engine
from optiproductio.server import make_app
from optiproductio import sources

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser(description="OptiProductio laptop server")
    ap.add_argument("--source", choices=["sim", "usb", "mqtt"], default="sim")
    ap.add_argument("--port", help="USB serial port, e.g. COM5 (Windows) or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--broker", default="127.0.0.1", help="Mosquitto host (the laptop itself)")
    ap.add_argument("--broker-port", type=int, default=1883)
    ap.add_argument("--mqtt-user")
    ap.add_argument("--mqtt-password")
    ap.add_argument("--root", default="rvce/idealab/line1", help="ISA-95 topic root")
    ap.add_argument("--scenario", default="normal", help="simulator: normal, breakdown, shifting, starve, balanced")
    ap.add_argument("--speed", type=float, default=1.0, help="simulator speed (2 = twice real time)")
    ap.add_argument("--db", default=os.path.join(HERE, "data", "historian.sqlite"))
    ap.add_argument("--http-port", type=int, default=5000)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()

    os.makedirs(os.path.dirname(a.db), exist_ok=True)
    if a.source == "usb":
        if not a.port:
            ap.error("--source usb needs --port, e.g. --port COM5 (see Device Manager > Ports)")
        src = sources.SerialSource(a.port, a.baud)
    elif a.source == "mqtt":
        src = sources.MqttSource(a.broker, a.broker_port, a.root, a.mqtt_user, a.mqtt_password)
    else:
        src = sources.SimSource(a.scenario, a.speed)

    engine = Engine(src, a.db, os.path.join(os.path.dirname(a.db), "settings.json"))
    engine.start()
    app = make_app(engine)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    url = f"http://localhost:{a.http_port}"
    print(f"\nOptiProductio running. Source: {src.info}\nDashboard: {url}   Run report: {url}/report\n"
          f"Historian: {a.db}\nPress Ctrl+C to stop.\n")
    if not a.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=a.http_port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
