"""Where the line data comes from. Three plugs, same shape:

  MqttSource    the real IIoT path: UNO -> NodeMCU -> Wi-Fi -> Mosquitto -> here
  SerialSource  the backup path: UNO USB cable straight into the laptop
  SimSource     no hardware at all: the simulator pretends to be the UNO

Each one calls on_msg(dict) for every parsed line and has send(cmd) for "L,4", "R", "P".
"""
from __future__ import annotations

import threading
import time

from . import protocol


class Source:
    kind = "?"

    def __init__(self):
        self.on_msg = None
        self.connected = False
        self.last_rx = None
        self.rx_count = 0
        self.bad_count = 0
        self.info = ""
        self.gateway = None      # MQTT only: "online"/"offline" from the gateway's state topic
        self.gateway_stats = None

    def _deliver(self, msg):
        if msg is None:
            self.bad_count += 1
            return
        self.rx_count += 1
        self.last_rx = time.time()
        if self.on_msg:
            self.on_msg(msg)

    def start(self, on_msg):
        self.on_msg = on_msg

    def send(self, cmd: str):
        raise NotImplementedError

    def describe(self):
        return {"kind": self.kind, "connected": self.connected, "info": self.info,
                "last_rx_age_s": None if self.last_rx is None else round(time.time() - self.last_rx, 1),
                "rx": self.rx_count, "bad": self.bad_count, "gateway": self.gateway,
                "gateway_stats": self.gateway_stats}


class SerialSource(Source):
    kind = "usb"

    def __init__(self, port: str, baud: int = 115200):
        super().__init__()
        self.port, self.baud = port, baud
        self.ser = None
        self.info = f"{port} @ {baud}"

    def start(self, on_msg):
        super().start(on_msg)
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        import serial
        while True:
            try:
                self.ser = serial.Serial(self.port, self.baud, timeout=1)
                self.connected = True
                while True:
                    raw = self.ser.readline()
                    if not raw:
                        continue
                    line = raw.decode("ascii", errors="replace").strip()
                    if line.startswith("#") or not line:
                        continue
                    self._deliver(protocol.parse_line(line))
            except Exception as e:      # unplugged, wrong port, ...
                self.connected = False
                self.info = f"{self.port}: {e}"
                time.sleep(2)

    def send(self, cmd):
        if self.ser and self.connected:
            self.ser.write((cmd.strip() + "\n").encode())


class MqttSource(Source):
    kind = "mqtt"

    def __init__(self, host="127.0.0.1", port=1883, root="rvce/idealab/line1", user=None, password=None):
        super().__init__()
        import paho.mqtt.client as mqtt
        self.root = root
        self.info = f"{host}:{port} {root}/#"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"optiproductio-laptop-{int(time.time())}")
        if user:
            self.client.username_pw_set(user, password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.host, self.port = host, port

    def _on_connect(self, c, u, flags, rc, props=None):
        self.connected = (rc == 0)
        c.subscribe(f"{self.root}/#", qos=1)

    def _on_disconnect(self, *a):
        self.connected = False

    def _on_message(self, c, u, m):
        t = m.topic
        if t == f"{self.root}/gateway/state":
            self.gateway = m.payload.decode(errors="replace")
            return
        if t == f"{self.root}/gateway/stats":
            try:
                import json
                self.gateway_stats = json.loads(m.payload)
            except ValueError:
                pass
            return
        if "/cmd/" in t:
            return
        if m.retain:            # an old retained status from before we started: skip it
            return
        self._deliver(protocol.from_mqtt(t, m.payload, self.root))

    def start(self, on_msg):
        super().start(on_msg)
        self.client.connect_async(self.host, self.port, keepalive=10)
        self.client.loop_start()

    def send(self, cmd):
        topic, payload = protocol.command_to_mqtt(cmd, self.root)
        self.client.publish(topic, payload, qos=1)


class SimSource(Source):
    kind = "sim"

    def __init__(self, scenario="normal", speed=1.0, limit=0, buffer_s=10):
        super().__init__()
        from .simulator import SimLine
        self.speed = speed
        self.info = f"simulator, scenario '{scenario}', speed x{speed}"
        self._args = (scenario, limit, buffer_s)
        self._SimLine = SimLine
        self.sim = None

    def _line(self, line):
        # go through the text form on purpose, so the parser is tested too
        self._deliver(protocol.parse_line(line))

    def start(self, on_msg):
        super().start(on_msg)
        self.sim = self._SimLine(self._line, *self._args)   # created here so its BOOT line is not lost
        self.connected = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        dt = 50
        while True:
            self.sim.step(dt)
            time.sleep(dt / 1000 / self.speed)

    def send(self, cmd):
        self.sim.command(cmd)
