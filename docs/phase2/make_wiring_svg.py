"""Draws docs/phase2/wiring_diagram.svg. Run: python make_wiring_svg.py"""
W, H = 1500, 1110
o = []
def add(s): o.append(s)
def rect(x, y, w, h, fill, stroke="#334155", rx=10, sw=2):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def text(x, y, s, size=14, fill="#0f172a", anchor="start", weight=400, fam="Segoe UI, Arial, sans-serif"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}">{s}</text>')
def wire(pts, color, sw=3, dash=None):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{da}/>')
def dot(x, y, c): add(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>')
def res(x, y, label, vertical=False):
    if vertical:
        rect(x - 9, y, 18, 40, "#fde68a", "#92400e", 4, 1.5); text(x + 16, y + 25, label, 12, "#92400e")
    else:
        rect(x, y - 9, 44, 18, "#fde68a", "#92400e", 4, 1.5); text(x + 22, y - 14, label, 12, "#92400e", "middle")

RED, BLK, SIG, GRN, ORG, BLU, PUR = "#dc2626", "#111827", "#2563eb", "#16a34a", "#ea580c", "#0891b2", "#7c3aed"
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(30, 40, "OptiProductio wiring diagram", 26, weight=700)
text(30, 66, "Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection · Arduino UNO + 6 FC-51 + SG90 + NodeMCU ESP8266", 15, "#475569")

# rails
RAIL_Y = {"5v": 110, "gnd": 135}
wire([(260, RAIL_Y["5v"]), (1470, RAIL_Y["5v"])], RED, 4); text(1470, RAIL_Y["5v"] - 7, "breadboard + rail = UNO 5V", 13, RED, "end", 600)
wire([(200, RAIL_Y["gnd"]), (1470, RAIL_Y["gnd"])], BLK, 4); text(1470, RAIL_Y["gnd"] + 20, "breadboard - rail = GND (shared by everything)", 13, BLK, "end", 600)

# UNO
UX, UY, UW, UH = 60, 260, 260, 640
rect(UX, UY, UW, UH, "#e0f2fe", "#0369a1", 16, 3)
text(UX + UW / 2, UY + 34, "Arduino UNO", 22, "#0c4a6e", "middle", 700)
text(UX + UW / 2, UY + 56, "line controller", 13, "#0369a1", "middle")
right_pins = ["D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13"]
pin_y = {}
for i, p in enumerate(right_pins):
    y = UY + 95 + i * 40
    pin_y[p] = y
    dot(UX + UW, y, "#0369a1"); text(UX + UW - 12, y + 5, p, 14, "#0c4a6e", "end", 600)
left_pins = ["5V", "GND", "A0", "A1", "A2", "A3"]
for i, p in enumerate(left_pins):
    y = UY + 120 + i * 70
    pin_y[p] = y
    dot(UX, y, "#0369a1"); text(UX + 12, y + 5, p, 14, "#0c4a6e", "start", 600)
text(UX + UW / 2, UY + UH - 18, "USB to laptop (power + backup data)", 12, "#0369a1", "middle")
# UNO 5V / GND to rails
wire([(UX, pin_y["5V"]), (40, pin_y["5V"]), (40, RAIL_Y["5v"]), (260, RAIL_Y["5v"])], RED)
wire([(UX, pin_y["GND"]), (25, pin_y["GND"]), (25, RAIL_Y["gnd"]), (200, RAIL_Y["gnd"])], BLK)

# sensors
SX = 560
sensors = [("S1 IN", "D2"), ("S1 OUT", "D3"), ("S2 IN", "D4"), ("S2 OUT", "D5"), ("S3 IN", "D6"), ("S3 OUT", "D7")]
for i, (name, pin) in enumerate(sensors):
    y = pin_y[pin]
    bx, by = SX, y - 15
    rect(bx, by, 150, 32, "#f1f5f9", "#475569", 7, 1.5)
    text(bx + 10, by + 21, f"FC-51 {name}", 13, weight=600)
    # OUT
    wire([(UX + UW, y), (bx, y)], SIG, 2.5)
    text(bx - 8, y - 6, "OUT", 11, SIG, "end")
    # VCC, GND up to rails
    vx, gx = bx + 160 + i * 14, bx + 250 + i * 14
    wire([(bx + 150, y - 6), (vx, y - 6), (vx, RAIL_Y["5v"])], RED, 1.8)
    wire([(bx + 150, y + 6), (gx, y + 6), (gx, RAIL_Y["gnd"])], BLK, 1.8)
    dot(vx, RAIL_Y["5v"], RED); dot(gx, RAIL_Y["gnd"], BLK)
text(340, pin_y["D2"] - 45, "6 × FC-51: VCC → + rail, GND → − rail", 13, "#475569")

# servo
y8 = pin_y["D8"]
rect(SX, y8 - 22, 150, 46, "#fef3c7", "#b45309", 8, 1.5)
text(SX + 10, y8 - 2, "SG90 servo (gate)", 13, weight=600); text(SX + 10, y8 + 15, "orange · red · brown", 11, "#92400e")
wire([(UX + UW, y8), (SX, y8)], ORG, 2.5); text(SX - 8, y8 - 6, "signal", 11, ORG, "end")

# separate servo supply
PX, PY = 1080, 560
rect(PX, PY, 360, 150, "#fff7ed", "#c2410c", 12, 2)
text(PX + 16, PY + 28, "5 V 2 A adapter (servo only)", 15, "#9a3412", weight=700)
text(PX + 16, PY + 50, "+5V goes ONLY to the servo red wire.", 12, "#9a3412")
text(PX + 16, PY + 68, "Its - joins the shared GND rail.", 12, "#9a3412")
# 470uF cap
add(f'<g transform="translate({PX+240},{PY+85})"><rect x="0" y="0" width="34" height="48" rx="6" fill="#1e293b"/><text x="17" y="28" font-size="10" fill="#fff" text-anchor="middle" font-family="Arial">470µF</text></g>')
text(PX + 16, PY + 100, "470 µF across + and -", 12, "#9a3412"); text(PX + 16, PY + 118, "(long leg +, stripe leg -)", 12, "#9a3412")
wire([(SX + 150, y8 - 10), (980, y8 - 10), (980, PY + 30), (PX, PY + 30)], RED, 2.5)
text(985, PY + 22, "servo red", 11, RED)
wire([(SX + 150, y8 + 10), (960, y8 + 10), (960, RAIL_Y["gnd"])], BLK, 2.2); dot(960, RAIL_Y["gnd"], BLK)
text(965, y8 + 26, "servo brown", 11, BLK)
wire([(PX + 360, PY + 120), (1480, PY + 120), (1480, RAIL_Y["gnd"])], BLK, 2.5); dot(1480, RAIL_Y["gnd"], BLK)
text(1475, PY + 140, "adapter -", 11, BLK, "end")

# LEDs
leds = [("D9", "S1 green", GRN, "220 Ω"), ("D10", "S1 red", RED, "220 Ω"), ("D11", "S2 green", GRN, "220 Ω"),
        ("D12", "S2 red", RED, "220 Ω"), ("D13", "S3 green", GRN, "1 kΩ")]
for pin, name, col, r in leds:
    y = pin_y[pin]
    if pin == "D8":
        continue
    x0 = UX + UW
    wire([(x0, y), (390, y)], col, 2.2)
    res(390, y, r)
    wire([(434, y), (470, y)], col, 2.2)
    add(f'<polygon points="470,{y-9} 470,{y+9} 486,{y}" fill="{col}"/><line x1="487" y1="{y-9}" x2="487" y2="{y+9}" stroke="{col}" stroke-width="3"/>')
    text(492, y + 4, name, 12, col, weight=600)
text(390, pin_y["D13"] + 40, "Each LED: pin → resistor → long leg; short leg → GND rail", 12, "#475569")
text(390, pin_y["D13"] + 56, "(short-leg wires to GND not drawn, to keep it readable)", 12, "#94a3b8")

# left side: A0 LED, A1 buzzer, A2/A3 NodeMCU
ya0 = pin_y["A0"]
wire([(UX, ya0), (30, ya0)], RED, 2.2)
text(UX + 16, ya0 + 26, "A0 → 220 Ω → S3 red LED → GND", 12, RED, "start", 600)
ya1 = pin_y["A1"]
wire([(UX, ya1), (30, ya1)], PUR, 2.2)
text(UX + 16, ya1 + 26, "A1 → buzzer + (− to GND)", 12, PUR, "start", 600)

# NodeMCU
NX, NY = 1080, 790
rect(NX, NY, 360, 190, "#ecfeff", "#0e7490", 14, 3)
text(NX + 16, NY + 30, "NodeMCU ESP8266 (Wi-Fi gateway)", 16, "#155e75", weight=700)
text(NX + 16, NY + 52, "powered by its own micro-USB (laptop or power bank)", 12, "#0e7490")
for i, (p, note) in enumerate([("D5", "RX  ← from UNO A3 via divider"), ("D6", "TX  → to UNO A2 (direct)"), ("GND", "→ shared GND rail")]):
    y = NY + 90 + i * 34
    dot(NX, y, "#0e7490"); text(NX + 14, y + 5, f"{p}", 14, "#155e75", weight=700); text(NX + 60, y + 5, note, 12, "#155e75")
ya2, ya3 = pin_y["A2"], pin_y["A3"]
# A3 -> 1k -> mid -> D5 ; mid -> 2.2k -> GND
wire([(UX, ya3), (18, ya3), (18, 1030), (700, 1030)], BLU, 2.5)
res(700, 1030, "1 kΩ")
wire([(744, 1030), (820, 1030)], BLU, 2.5); dot(820, 1030, BLU)
wire([(820, 1030), (1000, 1030), (1000, NY + 90), (NX, NY + 90)], BLU, 2.5)
wire([(820, 1030), (820, 990)], BLU, 2.5)
res(820, 950, "2.2 kΩ", vertical=True)
wire([(820, 950), (820, 935)], BLK, 2); text(828, 930, "to GND rail", 11, BLK)
text(330, 1072, "UNO A3 (TX, 5 V) → 1 kΩ → ● → NodeMCU D5   ·   ● → 2.2 kΩ → GND   (≈3.4 V, safe for the ESP8266)", 12, BLU, weight=600)
wire([(UX, ya2), (10, ya2), (10, 1048), (1020, 1048), (1020, NY + 124), (NX, NY + 124)], "#059669", 2.5)
text(330, 1094, "NodeMCU D6 (3.3 V) → UNO A2 directly: the UNO reads 3.3 V as HIGH", 12, "#059669", weight=600)
wire([(NX, NY + 158), (1050, NY + 158), (1050, 760), (1460, 760), (1460, RAIL_Y["gnd"])], BLK, 2); dot(1460, RAIL_Y["gnd"], BLK)

# legend
LX, LY = 1080, 180
rect(LX, LY, 360, 150, "#f8fafc", "#cbd5e1", 10, 1.5)
text(LX + 16, LY + 26, "Wire colours in this drawing", 14, weight=700)
for i, (c, t) in enumerate([(RED, "+5 V"), (BLK, "GND"), (SIG, "sensor signal"), (ORG, "servo signal"), (BLU, "UNO → NodeMCU data"), ("#059669", "NodeMCU → UNO data")]):
    yy = LY + 50 + (i % 3) * 30
    xx = LX + 16 + (i // 3) * 175
    wire([(xx, yy), (xx + 28, yy)], c, 4); text(xx + 36, yy + 5, t, 12)
text(LX, LY + 180, "Rules: 1) every GND is connected together.", 13, "#b91c1c", weight=600)
text(LX, LY + 200, "2) never power the servo from the UNO 5V pin.", 13, "#b91c1c", weight=600)
text(LX, LY + 220, "3) never feed 5 V straight into a NodeMCU pin.", 13, "#b91c1c", weight=600)
add("</svg>")
import os
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiring_diagram.svg"), "w", encoding="utf-8").write("\n".join(o))
print("ok")
