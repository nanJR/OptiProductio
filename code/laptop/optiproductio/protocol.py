"""The text lines the UNO sends, and their MQTT/JSON form from the NodeMCU gateway.

Think of this file as the dictionary both sides agree on. If the UNO sketch
changes a line format, change it here too.

    E,<seq>,<ms>,<station>,<event>,<value>
    S,<seq>,<ms>,<wip>,<limit>,<gate>,<occ1>,<occ2>,<occ3>,<bn>,<released>,<done>,<buf_s>

The last status field (buffer time in seconds) is new in firmware v3. A v2 line
without it is still accepted; then "buf" is None.
"""
from __future__ import annotations

import json

EVENTS = {"BOOT", "IN", "OUT", "GATE", "HOLD", "LIMIT", "BUF", "BN", "STALL", "ERR", "RESET", "PONG"}
STATUS_KEYS = ("seq", "ms", "wip", "limit", "gate", "occ", "bn", "released", "done", "buf")


def parse_line(line: str) -> dict | None:
    """Turn one serial line into a dict, or None if it is a comment or garbage."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    f = line.split(",")
    try:
        if f[0] == "E" and len(f) == 6:
            if f[4] not in EVENTS:
                return None
            return {"type": "E", "seq": int(f[1]), "ms": int(f[2]), "st": int(f[3]),
                    "ev": f[4], "val": int(f[5])}
        if f[0] == "S" and len(f) in (12, 13):
            v = [int(x) for x in f[1:]]
            return {"type": "S", "seq": v[0], "ms": v[1], "wip": v[2], "limit": v[3],
                    "gate": v[4], "occ": v[5:8], "bn": v[8], "released": v[9], "done": v[10],
                    "buf": v[11] if len(v) > 11 else None}
    except ValueError:
        return None
    return None


def to_line(msg: dict) -> str:
    """The reverse of parse_line (used by the simulator)."""
    if msg["type"] == "E":
        return f"E,{msg['seq']},{msg['ms']},{msg['st']},{msg['ev']},{msg['val']}"
    o = msg["occ"]
    line = (f"S,{msg['seq']},{msg['ms']},{msg['wip']},{msg['limit']},{msg['gate']},"
            f"{o[0]},{o[1]},{o[2]},{msg['bn']},{msg['released']},{msg['done']}")
    if msg.get("buf") is not None:
        line += f",{msg['buf']}"
    return line


def to_mqtt(msg: dict, root: str) -> tuple[str, str, bool]:
    """What the NodeMCU publishes for a message: (topic, JSON payload, retained)."""
    if msg["type"] == "E":
        cell = "line" if msg["st"] == 0 else f"s{msg['st']}"
        body = {k: msg[k] for k in ("seq", "ms", "st", "ev", "val")}
        return f"{root}/{cell}/event", json.dumps(body, separators=(",", ":")), False
    body = {k: msg[k] for k in STATUS_KEYS if msg.get(k) is not None}
    return f"{root}/status", json.dumps(body, separators=(",", ":")), True


def from_mqtt(topic: str, payload: bytes | str, root: str) -> dict | None:
    """Turn an MQTT message from the gateway back into the same dict as parse_line."""
    if not topic.startswith(root + "/"):
        return None
    rest = topic[len(root) + 1:]
    try:
        if rest.endswith("/event"):
            d = json.loads(payload)
            if d.get("ev") not in EVENTS:
                return None
            return {"type": "E", "seq": int(d["seq"]), "ms": int(d["ms"]), "st": int(d["st"]),
                    "ev": d["ev"], "val": int(d["val"])}
        if rest == "status":
            d = json.loads(payload)
            return {"type": "S", "seq": int(d["seq"]), "ms": int(d["ms"]), "wip": int(d["wip"]),
                    "limit": int(d["limit"]), "gate": int(d["gate"]),
                    "occ": [int(x) for x in d["occ"]], "bn": int(d["bn"]),
                    "released": int(d["released"]), "done": int(d["done"]),
                    "buf": int(d["buf"]) if d.get("buf") is not None else None}
    except (ValueError, KeyError, TypeError):
        return None
    return None


def command_to_mqtt(cmd: str, root: str) -> tuple[str, str]:
    """'L,4' -> ('<root>/cmd/wip_limit', '4'); 'B,15' -> ('<root>/cmd/buffer', '15');
    'R' -> reset; 'P' -> ping."""
    c = cmd.strip().upper()
    if c.startswith("L"):
        return f"{root}/cmd/wip_limit", str(int(c[2:]))
    if c.startswith("B"):
        return f"{root}/cmd/buffer", str(int(c[2:]))
    if c == "R":
        return f"{root}/cmd/reset", "1"
    return f"{root}/cmd/ping", "1"
