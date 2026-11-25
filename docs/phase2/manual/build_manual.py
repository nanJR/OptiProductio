"""Builds the OptiProductio assembly and setup manual (HTML -> PDF with Playwright).

    python build_manual.py            writes manual.html
    node render.js                    writes the PDF (needs Playwright + Chromium)
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = "Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection"

GLOSSARY = {
    "WIP": "Work in progress: boxes that have entered the line (passed S1 IN) but not yet left it (passed S3 OUT).",
    "CONWIP": "Constant WIP: a control rule that lets a new box in only while WIP is below a fixed limit.",
    "Bottleneck": "The station that limits how fast the whole line can produce.",
    "Active period": "A stretch of time when a station has a box on it (working or waiting to hand it on). Roser's method: the station with the longest current active period is the bottleneck.",
    "Cycle time": "Time a station spends on one box, from its IN sensor to its OUT sensor.",
    "Lead time": "Time one box spends in the whole line, from S1 IN to S3 OUT.",
    "Throughput": "Finished boxes per minute.",
    "Andon": "A status light or sound that shows a station's state at a glance.",
    "Buffer time": "User-set time (seconds) a station may stay busy before its LED turns red and it is flagged as the bottleneck. Set with B,n; saved in EEPROM.",
    "S1/S2/S3": "Station 1, Station 2, Station 3.",
    "OEE": "Overall equipment effectiveness = availability x performance x quality.",
    "KPI": "Key performance indicator: a number used to judge how well the line runs.",
    "Little's law": "WIP = throughput x lead time. Used to cross-check the measurements.",
    "Pareto chart": "Bar chart of causes sorted from biggest to smallest, with a running total line.",
    "Takt / planned cycle time": "The time per box the line is designed for (6 s in Settings by default).",
    "Historian": "A database that stores every machine event with its time (here: SQLite).",
    "MQTT": "A light publish/subscribe message protocol used in IIoT.",
    "Broker": "The MQTT 'post office' (Mosquitto) that passes messages between devices.",
    "IIoT": "Industrial Internet of Things: factory machines sending data over a network.",
    "ISA-95": "Standard that layers a factory into levels (machine, control, operations, business); our topic names follow its hierarchy.",
    "ISO 22400": "Standard that names manufacturing KPIs (availability, effectiveness, OEE...).",
    "Escapement": "A gate that lets exactly one item through each time it opens.",
    "FIFO": "First in, first out: the box that came in first leaves first.",
    "Rail (breadboard)": "The long red (+) and blue (-) strips along a breadboard's edges, used to share power and ground.",
    "Common GND": "All grounds wired together so every board measures voltage from the same zero.",
    "Voltage divider": "Two resistors in series that output a fixed fraction of the input voltage.",
    "Potentiometer (trim pot)": "A small screw-adjusted resistor; on the FC-51 it sets the detection distance.",
    "Debounce": "Ignoring the very short flickers of a sensor so one box is counted once.",
    "Baud": "Serial speed in bits per second (19200 between UNO and NodeMCU).",
    "SoftwareSerial": "A serial port made in software on ordinary pins, because the UNO has only one hardware port (used by USB).",
    "EEPROM": "Memory on the UNO that keeps data (the WIP limit) when power is off.",
    "Flash (verb)": "Upload a program (sketch) to a board.",
    "Sketch": "An Arduino program (.ino file).",
    "COM port": "The name Windows gives a USB serial device, e.g. COM5.",
    "Electrolytic capacitor": "A capacitor with + and - legs; the stripe marks the - leg. Here 470 uF stores charge for the servo.",
    "Brown-out": "A short voltage dip that makes a board reset.",
    "Hotspot": "Phone Wi-Fi network. Must be 2.4 GHz for the ESP8266.",
    "IP address": "A device's number on the network, e.g. 192.168.43.25.",
    "Last Will": "An MQTT message the broker sends for a device that disconnects without saying goodbye ('offline').",
    "Simulator": "Software that pretends to be the UNO and the line, for practice without hardware.",
    "Starved": "A station that is idle because no box is reaching it.",
    "Blocked": "A station that has finished but cannot hand its box on.",
    "Downtime": "Time the line produced nothing for longer than the 'line down' threshold.",
    "A/B test": "Running the same line twice with one change (e.g. WIP limit off vs 3) and comparing the results.",
    "Multimeter": "Meter for voltage, resistance and continuity (beep test).",
    "Continuity test": "Multimeter mode that beeps when two points are connected.",
    "Polarity": "Which side is + and which is -. Wrong polarity can damage parts.",
}


def gl(*keys):
    return list(keys)


def eli5(text):
    return f'<div class="eli5"><b>ELI5</b> {text}</div>'


def check(items):
    return '<ul class="check">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def steps(items, start=1):
    return f'<ol class="steps" start="{start}">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{r}</table>'


def warn(text):
    return f'<div class="warn"><b>Careful</b> {text}</div>'


def stop(text):
    return f'<div class="stopcheck"><b>CHECK before moving on</b> {text}</div>'


LAYOUT_SVG = """
<svg viewBox="0 0 1240 520" class="layout" xmlns="http://www.w3.org/2000/svg" font-family="Arial">
 <rect x="20" y="40" width="1200" height="450" fill="#fff" stroke="#0f172a" stroke-width="3"/>
 <text x="620" y="28" text-anchor="middle" font-size="18" font-weight="700">Base board 120 x 45 cm (top view, 1 px = 1 mm)</text>
 <!-- back strip -->
 <rect x="20" y="40" width="1200" height="90" fill="#f1f5f9"/>
 <text x="1210" y="62" text-anchor="end" font-size="14" fill="#475569">BACK STRIP 9 cm: LED panel standing up, sensors behind the lane</text>
 <!-- lane -->
 <rect x="20" y="130" width="1200" height="160" fill="#fefce8"/>
 <line x1="20" y1="150" x2="1220" y2="150" stroke="#2563eb" stroke-width="4"/>
 <line x1="350" y1="270" x2="1220" y2="270" stroke="#2563eb" stroke-width="4"/>
 <text x="1210" y="145" text-anchor="end" font-size="13" fill="#2563eb">back guide rail</text>
 <text x="1210" y="290" text-anchor="end" font-size="13" fill="#2563eb">front guide rail (12 cm lane)</text>
 <!-- chute -->
 <rect x="20" y="160" width="300" height="100" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
 <text x="170" y="205" text-anchor="middle" font-size="16" font-weight="700">CHUTE 30 x 10 cm</text>
 <text x="170" y="228" text-anchor="middle" font-size="13">high end on the left, 8-10 cm rise</text>
 <rect x="322" y="150" width="14" height="120" fill="#facc15" stroke="#854d0e"/>
 <text x="329" y="320" text-anchor="middle" font-size="13" font-weight="700">GATE</text>
 <rect x="300" y="88" width="40" height="40" fill="#3b82f6"/><text x="320" y="82" text-anchor="middle" font-size="12">servo</text>
 <!-- stations -->
 <g font-size="15" font-weight="700" text-anchor="middle">
  <rect x="380" y="145" width="130" height="130" fill="#cffafe" stroke="#0e7490" stroke-width="2"/><text x="445" y="215">S1</text>
  <rect x="630" y="145" width="130" height="130" fill="#fef3c7" stroke="#b45309" stroke-width="2"/><text x="695" y="215">S2</text>
  <rect x="880" y="145" width="130" height="130" fill="#dcfce7" stroke="#15803d" stroke-width="2"/><text x="945" y="215">S3</text>
  <rect x="1060" y="145" width="140" height="130" fill="#fed7aa" stroke="#9a3412" stroke-width="2"/><text x="1130" y="215">DONE BIN</text>
 </g>
 <g font-size="12" text-anchor="middle" fill="#334155">
  <text x="445" y="240">13 x 13 cm</text><text x="695" y="240">13 x 13 cm</text><text x="945" y="240">13 x 13 cm</text>
 </g>
 <!-- buffers -->
 <rect x="520" y="300" width="100" height="90" fill="none" stroke="#7c3aed" stroke-dasharray="6 5" stroke-width="2"/>
 <text x="570" y="340" text-anchor="middle" font-size="12" fill="#7c3aed">QUEUE</text><text x="570" y="356" text-anchor="middle" font-size="12" fill="#7c3aed">before S2</text>
 <rect x="770" y="300" width="100" height="90" fill="none" stroke="#7c3aed" stroke-dasharray="6 5" stroke-width="2"/>
 <text x="820" y="340" text-anchor="middle" font-size="12" fill="#7c3aed">QUEUE</text><text x="820" y="356" text-anchor="middle" font-size="12" fill="#7c3aed">before S3</text>
 <!-- sensors (on back rail, pointing to the front) -->
 <g fill="#1d4ed8">
  <rect x="368" y="112" width="22" height="30"/><rect x="512" y="112" width="22" height="30"/>
  <rect x="618" y="112" width="22" height="30"/><rect x="762" y="112" width="22" height="30"/>
  <rect x="868" y="112" width="22" height="30"/><rect x="1012" y="112" width="22" height="30"/>
 </g>
 <g font-size="11" text-anchor="middle" fill="#1d4ed8" font-weight="700">
  <text x="379" y="106">IN D2</text><text x="523" y="106">OUT D3</text><text x="629" y="106">IN D4</text>
  <text x="773" y="106">OUT D5</text><text x="879" y="106">IN D6</text><text x="1023" y="106">OUT D7</text>
 </g>
 <g stroke="#ef4444" stroke-width="2" stroke-dasharray="4 3" opacity=".8">
  <line x1="379" y1="142" x2="379" y2="270"/><line x1="523" y1="142" x2="523" y2="270"/><line x1="629" y1="142" x2="629" y2="270"/>
  <line x1="773" y1="142" x2="773" y2="270"/><line x1="879" y1="142" x2="879" y2="270"/><line x1="1023" y1="142" x2="1023" y2="270"/>
 </g>
 <!-- LEDs -->
 <g><circle cx="430" cy="70" r="9" fill="#22c55e"/><circle cx="460" cy="70" r="9" fill="#ef4444"/>
 <circle cx="680" cy="70" r="9" fill="#22c55e"/><circle cx="710" cy="70" r="9" fill="#ef4444"/>
 <circle cx="930" cy="70" r="9" fill="#22c55e"/><circle cx="960" cy="70" r="9" fill="#ef4444"/></g>
 <!-- front strip electronics -->
 <rect x="20" y="400" width="1200" height="90" fill="#f8fafc"/>
 <rect x="470" y="415" width="110" height="65" fill="#0891b2"/><text x="525" y="453" text-anchor="middle" font-size="14" fill="#fff" font-weight="700">UNO</text>
 <rect x="600" y="415" width="170" height="65" fill="#e5e7eb" stroke="#64748b"/><text x="685" y="453" text-anchor="middle" font-size="13" font-weight="700">breadboard 400</text>
 <rect x="790" y="420" width="90" height="55" fill="#0e7490"/><text x="835" y="452" text-anchor="middle" font-size="12" fill="#fff" font-weight="700">NodeMCU</text>
 <rect x="320" y="420" width="120" height="55" fill="#fff7ed" stroke="#c2410c"/><text x="380" y="445" text-anchor="middle" font-size="11">servo 5 V 2 A</text><text x="380" y="461" text-anchor="middle" font-size="11">+ 470 uF</text>
 <text x="1210" y="470" text-anchor="end" font-size="14" fill="#475569">FRONT STRIP 11 cm: electronics, buzzer, laptop USB</text>
 <!-- dims -->
 <g font-size="12" fill="#0f172a">
  <text x="30" y="510">0</text><text x="315" y="510">30 cm</text><text x="370" y="510">36</text><text x="620" y="510">61</text><text x="870" y="510">86</text><text x="1050" y="510">104</text><text x="1190" y="510">120</text>
 </g>
</svg>
"""

PAGES = []


def page(title, body, gloss, section=""):
    PAGES.append({"title": title, "body": body, "gloss": gloss, "section": section})


# ---------------- 1. Cover ----------------
page("", f"""
<div class="cover">
  <div class="kicker">IEM IDEA Lab EL · Phase 2 · OptiProductio</div>
  <h1 class="ctitle">{TITLE}</h1>
  <div class="csub">Assembly and setup manual: build the table, wire it, flash it, calibrate it, run the demo</div>
  <img src="img/topview.jpg" class="full">
  <div class="twocol">
   <div>
    <h3>What you are building</h3>
    <p>A tabletop production line. Boxes slide down a chute, a servo gate lets them in one at a time, and three people work at stations S1, S2 and S3. Six IR sensors watch every box enter and leave every station. The Arduino UNO keeps the WIP count, opens the gate only when S1 is empty (and, with a WIP limit set, only while WIP is below it), and turns a station's LED red once it has been busy longer than the buffer time you set. A NodeMCU sends everything over Wi-Fi to the laptop, which stores it and shows a live dashboard.</p>
   </div>
   <div>
    <h3>How to use this manual</h3>
    <p>Go page by page. Every block ends with a <b>CHECK</b>. Do not start the next block until the check passes: a fault found early takes 2 minutes to fix, a fault found at the end takes 2 hours.</p>
    <p>Grey <b>ELI5</b> boxes explain the idea in plain words. The glossary at the bottom of each page explains the terms used on that page.</p>
   </div>
  </div>
</div>""", gl("WIP", "S1/S2/S3", "Bottleneck", "IIoT"))

# ---------------- 2. Contents + plan ----------------
page("Contents and the 3-day plan", f"""
<div class="twocol">
<div>
<h3>Contents</h3>
<ol class="toc">
<li>Safety and golden rules</li><li>Parts check (receipt)</li><li>Tools and who does what</li>
<li>Build 1: base board and layout</li><li>Build 2: chute and servo gate</li><li>Build 3: stations, sensor mounts, LED panel</li>
<li>Wire 1: breadboard, power, UNO</li><li>Wire 2: six IR sensors</li><li>Wire 3: LEDs and buzzer</li>
<li>Wire 4: servo and its own 5 V supply</li><li>Wire 5: NodeMCU link</li><li>Full wiring diagram</li>
<li>Software 1: Arduino IDE, drivers, flashing</li><li>Calibration: sensors, gate, chute</li>
<li>Software 2: laptop, Mosquitto, hotspot, gateway</li><li>First power-on and self-test</li>
<li>Using the dashboard</li><li>Demo-day script</li><li>Troubleshooting</li><li>Quick reference card</li>
</ol>
</div>
<div>
<h3>Plan (eval Thursday 26 Nov)</h3>
{table(["Day", "Goal", "Done when"], [
 ["Tue 24", "Build the table (Build 1-3). Wire and test blocks 1-4. Laptop software installed, simulator running.", "Hardware test sketch passes sensors, LEDs, gate, buzzer"],
 ["Wed 25", "NodeMCU (Wire 5, Software 2). Calibrate. Full line runs over MQTT. Two full rehearsals. Record a backup video.", "Self-test sheet all ticked; A/B run report saved"],
 ["Thu 26", "Set up 45 min early. Self-test. Demo.", "Demo done"],
], "tight")}
{eli5("Build a house room by room and switch each room's lights on before you start the next room. Then when something does not work, you know which room to look in.")}
<h3>Files you need</h3>
<p>Everything is in the GitHub repo <b>nanJR/OptiProductio</b> (branch with Phase 2 code) and in the shared folder <code>optiproductio/code/</code>:</p>
{table(["Folder", "What"], [
 ["firmware/uno_hardware_test", "test sketch, flash this first"],
 ["firmware/uno_line_controller", "the real UNO program"],
 ["firmware/nodemcu_gateway", "Wi-Fi gateway + config.h"],
 ["laptop/", "Python server, simulator, dashboard"],
 ["docs/", "wiring diagram, test checklist, how it works"]], "tight")}
</div></div>""", gl("Flash (verb)", "Sketch", "Simulator", "A/B test"))

# ---------------- 3. Safety + parts ----------------
page("1. Safety and golden rules · 2. Parts check", f"""
<div class="twocol"><div>
<h3>Golden rules</h3>
<ol class="rules">
<li><b>Unplug everything</b> (USB and the servo adapter) before moving any wire.</li>
<li><b>All GNDs join together</b>: UNO GND, NodeMCU GND, servo adapter minus, every sensor GND.</li>
<li><b>Servo power never comes from the UNO 5V pin.</b> It comes from the 5 V 2 A adapter.</li>
<li><b>Never put 5 V into a NodeMCU pin.</b> UNO to NodeMCU goes through the 1 kΩ / 2.2 kΩ divider.</li>
<li><b>Capacitor polarity</b>: long leg +, striped leg -. Backwards, it can pop.</li>
<li><b>LED polarity</b>: long leg + (towards the resistor and the UNO pin), short leg to GND.</li>
<li><b>Hot glue gun and cutter</b>: one person uses it at a time, on a cutting mat, gun on its stand.</li>
<li>Test each block before the next (the CHECK boxes).</li>
</ol>
{eli5("GND is the 'sea level' that every board measures height from. If two boards have different sea levels, a 5 V signal from one can look like 2 V or 8 V to the other. Joining all GNDs gives everyone the same sea level.")}
</div><div>
<h3>Parts check (tick against the receipt)</h3>
{table(["✓", "Part", "Qty", "Used for"], [
 ["☐", "Arduino UNO (CH340) + USB cable", "1", "line controller"],
 ["☐", "FC-51 IR obstacle sensor", "6", "IN + OUT at S1, S2, S3"],
 ["☐", "SG90 micro servo + horns + screws", "1", "chute gate"],
 ["☐", "NodeMCU ESP8266 (CP2102)", "1", "Wi-Fi gateway"],
 ["☐", "5 mm LEDs red / green", "10", "6 used (3 + 3), 4 spare"],
 ["☐", "Resistor 220 Ω", "5", "5 LEDs"],
 ["☐", "Resistor 1 kΩ", "5", "6th LED (S3 green) + divider top"],
 ["☐", "Resistor 2.2 kΩ", "5", "divider bottom"],
 ["☐", "Active buzzer 5 V", "1", "audible alarm"],
 ["☐", "470 µF 16 V capacitor", "1", "servo supply buffer"],
 ["☐", "Breadboard 400 points", "1", "power rails + resistors"],
 ["☐", "Jumpers M-M and M-F", "2 sets", "all connections"],
 ["☐", "5 V 2 A adapter", "1", "servo power only"],
 ["☐", "Micro-USB cable", "1", "NodeMCU"],
 ["☐", "Foam board, popsicle sticks, glue, tape", "set", "table build"],
 ["☐", "8-10 light-coloured boxes about 6 cm", "8-10", "the 'products'"],
], "tight small")}
<p class="small">Resistor colour bands: 220 Ω = red red brown, 1 kΩ = brown black red, 2.2 kΩ = red red red (gold 4th band). Or measure with a multimeter.</p>
</div></div>""", gl("Common GND", "Polarity", "Electrolytic capacitor", "Rail (breadboard)", "Multimeter"))

# ---------------- 4. Tools + roles ----------------
page("3. Tools and who does what", f"""
<div class="twocol"><div>
<h3>Tools</h3>
{table(["Tool", "Why"], [
 ["Laptop (Windows) with 2 free USB ports", "flash boards, run broker + dashboard"],
 ["Phone hotspot (2.4 GHz)", "private Wi-Fi for NodeMCU + laptop"],
 ["Hot-glue gun + sticks", "mounts, chute, gate arm"],
 ["Cutter, steel ruler, cutting mat, pencil", "foam board"],
 ["Small flat screwdriver", "FC-51 trim pots, servo horn screw"],
 ["Multimeter (borrow from lab)", "check 5 V, continuity, adapter polarity"],
 ["Packing tape, double-sided tape, masking tape", "chute floor, fixing, labels"],
 ["Marker + masking-tape labels", "label every wire end"],
 ["Stopwatch (phone)", "cross-check cycle times"],
], "tight")}
<h3>About the 5 V 2 A adapter</h3>
<p>If it ends in a round barrel plug, either buy a <b>DC female barrel jack with screw terminals</b> (about ₹20 at any SP Road shop) or cut the plug off and strip the two wires. <b>Find + and - with the multimeter before connecting</b> (DC volts: red probe on the wire that reads +5 V). Mark + with red tape.</p>
{warn("Do not guess adapter polarity. Reversed 5 V into the servo or the capacitor can destroy them.")}
</div><div>
<h3>Who does what (from the Phase 2 work split)</h3>
{table(["Person", "Owns", "Pages"], [
 ["Rishith", "chute, servo gate, done bin, tests, backup video", "Build 2, Calibration, Self-test"],
 ["Syed", "station platforms, sensor mounts, LED panel, slides", "Build 1, Build 3"],
 ["Prem", "wiring, dashboard on the laptop", "Wire 1-5, Software 2"],
 ["Rohan", "Arduino code, integration, demo lead", "Software 1, Power-on, Demo script"],
], "tight")}
<p>Change the owners if you like, but keep one owner per block so nobody waits on "someone".</p>
{eli5("A pit crew changes four tyres in seconds because each person has one tyre. Four people on one tyre would be slower.")}
<h3>Label everything</h3>
<p>Put a masking-tape flag on <b>both ends</b> of every wire: "S1 IN", "S1 OUT", "S2 IN", ..., "SERVO SIG", "GW TX", "GW RX". At 9 pm the night before, an unlabelled wire costs 20 minutes.</p>
</div></div>""", gl("Hotspot", "Multimeter", "Polarity", "Continuity test"))

# ---------------- 5. Build 1 ----------------
page("4. Build 1: base board and layout", f"""
{LAYOUT_SVG}
<div class="twocol"><div>
{steps([
 "Tape 3 foam boards edge to edge (both sides, packing tape) into a 120 x 45 cm base. Put it on a flat table.",
 "Draw two lines along the length: <b>back strip</b> 9 cm from the back edge, <b>front strip</b> 11 cm from the front edge. The 25 cm between them is the working area.",
 "Mark the chute at the left end (0-30 cm), then the gate at 32 cm.",
 "Mark the 13 x 13 cm platforms: <b>S1 at 36-49 cm, S2 at 61-74 cm, S3 at 86-99 cm</b>, done bin 104-118 cm. The 12 cm gaps are the transfer zones.",
 "Glue foam strips (1.5 cm high) as <b>guide rails</b> so the lane is 12 cm wide (boxes are about 6 cm). Boxes always slide along the lane from left to right.",
 "Mark two dashed <b>QUEUE</b> squares on the front side of the lane, before S2 and before S3. Waiting boxes sit there, then get slid into the lane.",
])}
</div><div>
{eli5("The lane is a railway track. Boxes may only travel along it, left to right, because the sensors are like ticket gates at each station's entry and exit. A box lifted over a gate does not get counted.")}
<h3>Why these spacings</h3>
<ul>
<li>13 cm platforms fit one 6 cm box with room for hands.</li>
<li>Each platform has an IN sensor at its left edge and an OUT sensor at its right edge, so a box on the platform is <i>between</i> the two sensors.</li>
<li>12 cm gaps keep one station's OUT sensor from seeing the next station's box.</li>
<li>The 3D model shows a battery pack for the servo: we use the 5 V 2 A adapter instead.</li>
</ul>
{stop("Base is flat and stiff; platform and sensor positions are marked; a box slides freely along the full lane.")}
</div></div>""", gl("S1/S2/S3", "WIP", "Cycle time"))

# ---------------- 6. Build 2 ----------------
page("5. Build 2: chute and servo gate", f"""
<img src="img/chute.jpg" class="half right">
<h3>Chute</h3>
{steps([
 "Cut a foam strip 30 x 10 cm (floor) and two side walls 30 x 4 cm. Glue the walls on, inner width about 7.5 cm (box + 1.5 cm).",
 "Cover the floor with <b>packing tape</b>, shiny side up. Cardboard on bare foam board sticks; on tape it slides.",
 "Make a riser for the high (left) end. Start at <b>8 cm</b>. A 3-4 cm rise (about 7°) is usually too shallow for cardboard.",
 "Test with one box at a time: put it at the top and let go. It must slide all the way down <b>10 out of 10</b> times. If it stops, raise the riser 1 cm and retest. If it hits too hard and bounces, lower it or add a foam bumper.",
 "Glue the low end so the box leaves the chute level with the lane, straight into S1.",
], 1)}
<h3>Servo gate</h3>
{steps([
 "Glue a foam block (about 5 x 4 x 6 cm) beside the chute exit. Hot-glue the SG90 on top with its shaft pointing across the chute.",
 "<b>Do not fix the arm yet.</b> First the servo must be at its 'closed' angle: that is done in Calibration (section 14) with the test sketch.",
 "Then push the single-arm horn on, and hot-glue a popsicle stick to the horn so it hangs <b>down across the chute exit</b> (closed). When the servo turns, the stick swings up and one box slides out.",
 "Glue a small foam stop on the far side for the arm to rest against, so 8 boxes pushing on it cannot force it open.",
], 6)}
<div class="clear"></div>
{eli5("The gate is a nightclub bouncer with a clicker. While the club (the line) has fewer people (WIP) than the limit, the bouncer lets one person in. When it is full, nobody new gets in until someone leaves through the exit (S3 OUT).")}
{stop("Chute: 10/10 boxes slide all the way. Gate: servo glued firmly, arm NOT yet attached (it is set in Calibration).")}
""", gl("CONWIP", "Escapement", "WIP"))

# ---------------- 7. Build 3 ----------------
page("6. Build 3: stations, sensor mounts, LED panel, done bin", f"""
<div class="twocol"><div>
<h3>Platforms</h3>
<p>Glue a coloured 13 x 13 cm foam square at S1, S2, S3 (or just outline them with tape). Write S1, S2, S3 big on them.</p>
<h3>Sensor mounts (6)</h3>
{steps([
 "For each sensor cut a small foam block (3 x 3 x 4 cm). Glue it on the <b>back</b> side of the lane, just behind the back rail.",
 "Positions: S1 IN at 36 cm, S1 OUT at 50 cm, S2 IN at 61 cm, S2 OUT at 75 cm, S3 IN at 86 cm, S3 OUT at 100 cm (the dashed red lines in the layout).",
 "Fix each FC-51 to its block with double-sided tape or a dab of glue <b>on the PCB edge only</b>, the two LEDs (IR emitter and receiver) pointing straight across the lane at box mid-height (about 3 cm up).",
 "Cut a notch in the back rail in front of each sensor so the beam is not blocked. Keep the trim pot reachable with a screwdriver.",
 "Write the name on each sensor (S1 IN ...) with marker on tape.",
])}
{warn("Glue never touches the black and clear LEDs or the trim pot. Keep sensors out of direct sunlight; sunlight contains IR and blinds them. A short tube of black paper around the pair helps near windows.")}
</div><div>
<h3>LED panel</h3>
{steps([
 "Cut a foam strip 100 x 8 cm and stand it up along the back edge (glue + a foam triangle behind).",
 "For each station, push a green and a red LED through the panel above that station (green left, red right). Write S1, S2, S3 under them.",
 "Bend the legs behind the panel: <b>long leg (+)</b> on top, short leg (-) below, so you can tell them apart when wiring.",
 "Fix the buzzer on the front strip near the UNO, so the team hears it.",
], 6)}
<h3>Done bin</h3>
<p>A small open box (14 x 13 cm) at the right end. Finished boxes are carried back to the chute by hand.</p>
{eli5("Each station has two ticket gates: IN and OUT. The time between a box passing IN and passing OUT is how long the station worked on it (cycle time). With only one gate per station we could not tell working from waiting.")}
{stop("6 sensors mounted at the marked spots, all pointing across the lane, all labelled. LEDs pushed through the panel with + legs on top.")}
</div></div>""", gl("Cycle time", "Andon", "Potentiometer (trim pot)", "S1/S2/S3"))

# ---------------- 8. Wire 1 ----------------
page("7. Wire 1: breadboard, power and the UNO", f"""
<div class="twocol"><div>
<p>Place the UNO and the 400-point breadboard in the middle of the front strip (fix with double-sided tape). 20 cm jumpers are too short for the ends of the table: join one male-female and one male-male jumper (about 40 cm) where needed.</p>
<h3>The 400-point breadboard</h3>
<p>Each long edge has two rails: <b>red (+)</b> and <b>blue (-)</b>. In the middle, each short row of 5 holes is joined; the two halves are separate.</p>
{steps([
 "UNO <b>5V</b> → breadboard <b>red rail</b> (top edge).",
 "UNO <b>GND</b> → breadboard <b>blue rail</b> (top edge).",
 "Join the top and bottom blue rails with a short jumper, and the top and bottom red rails with another, so both edges have power.",
 "This red rail powers only the sensors and nothing else. The servo gets its own supply later.",
])}
{stop("Plug the UNO USB into the laptop. Multimeter on DC volts between red and blue rails: <b>4.7 to 5.1 V</b>. The UNO's ON LED is lit. Unplug again.")}
</div><div>
{table(["UNO pin", "Goes to"], [
 ["5V", "breadboard + (red) rail"],
 ["GND", "breadboard - (blue) rail"],
 ["D2 / D3", "S1 IN / S1 OUT sensor"],
 ["D4 / D5", "S2 IN / S2 OUT sensor"],
 ["D6 / D7", "S3 IN / S3 OUT sensor"],
 ["D8", "servo signal (orange)"],
 ["D9 / D10", "S1 green / red LED (220 Ω)"],
 ["D11 / D12", "S2 green / red LED (220 Ω)"],
 ["D13", "S3 green LED (1 kΩ)"],
 ["A0", "S3 red LED (220 Ω)"],
 ["A1", "buzzer +"],
 ["A2", "NodeMCU D6 (direct)"],
 ["A3", "1 kΩ → NodeMCU D5 (+2.2 kΩ to GND)"],
 ["A4, A5", "free"],
], "tight")}
{eli5("The breadboard rails are a power strip: plug the UNO's 5 V and GND into it once, and every sensor plugs into the strip instead of fighting for the UNO's single 5V pin.")}
</div></div>""", gl("Rail (breadboard)", "Common GND", "Multimeter"))

# ---------------- 9. Wire 2 ----------------
page("8. Wire 2: the six IR sensors", f"""
<div class="twocol"><div>
<p>Each FC-51 has 3 pins: <b>VCC, GND, OUT</b> (read the print on the board; some boards order them differently).</p>
{steps([
 "Use male-female jumpers (female end on the sensor). Use the same colours every time: red = VCC, black = GND, a signal colour for OUT.",
 "VCC → breadboard red rail. GND → breadboard blue rail.",
 "OUT → the UNO pin from the table. Do one sensor, then test it (step 5), then the next.",
 "Route the wires along the back strip and under the lane in a neat bundle; tape them down every 15 cm so a hand cannot pull them out.",
 "<b>Test each sensor as you go</b>: plug in the USB, flash the hardware test sketch (Software 1, section 13) and type <code>s</code>. Wave a box in front of the new sensor: its column goes 0 → 1. If it is always 1, turn its trim pot anticlockwise; if never 1, clockwise.",
])}
{table(["Sensor", "UNO pin", "Position"], [
 ["S1 IN", "D2", "36 cm"], ["S1 OUT", "D3", "50 cm"], ["S2 IN", "D4", "61 cm"],
 ["S2 OUT", "D5", "75 cm"], ["S3 IN", "D6", "86 cm"], ["S3 OUT", "D7", "100 cm"]], "tight")}
</div><div>
{eli5("The FC-51 is a tiny torch plus a tiny eye. The torch shines invisible infrared light; when a box is close, light bounces back into the eye and the OUT pin drops to LOW (0 V). The little green LED on the module lights when it sees something, which makes tuning easy.")}
<h3>How the UNO counts</h3>
<p>The program only counts the moment a sensor <b>changes</b> from 'nothing' to 'box' (an edge), and only if the signal stays steady for 25 ms. After a count, that sensor ignores itself for 0.4 s. So one box = one count, even if the sensor flickers at the box's edge.</p>
{warn("Plug the sensor in with power off. VCC and GND swapped will make the module hot within seconds: unplug at once.")}
{stop("With the test sketch: each of the 6 columns shows 1 only when a box passes its own sensor, and 0 the rest of the time.")}
</div></div>""", gl("Debounce", "Potentiometer (trim pot)", "Sketch", "Flash (verb)"))

# ---------------- 10. Wire 3 ----------------
page("9. Wire 3: LEDs and buzzer", f"""
<div class="twocol"><div>
<p>Each LED needs a resistor in series, or it burns out (and can damage the UNO pin).</p>
{steps([
 "Put each resistor in the breadboard's middle area, across two different 5-hole rows.",
 "UNO pin → one end of the resistor (jumper into the same 5-hole row).",
 "Other end of the resistor → LED <b>long leg (+)</b>, using a male-female jumper (or solder-free: twist and tape).",
 "LED <b>short leg (-)</b> → breadboard blue (GND) rail.",
 "Buzzer: <b>+</b> (longer leg or marked +) → UNO A1. <b>-</b> → blue rail.",
])}
{table(["LED", "UNO pin", "Resistor"], [
 ["S1 green", "D9", "220 Ω"], ["S1 red", "D10", "220 Ω"], ["S2 green", "D11", "220 Ω"],
 ["S2 red", "D12", "220 Ω"], ["S3 green", "D13", "1 kΩ (only 5 × 220 Ω bought)"], ["S3 red", "A0", "220 Ω"]], "tight")}
<p class="small">S3 green on 1 kΩ is a little dimmer. That is fine. D13 also has the UNO's on-board LED, so that one blinks along with S3 green.</p>
</div><div>
<h3>What the lights mean (andon)</h3>
{table(["Light", "Meaning"], [
 ["green steady", "station empty (S1: the gate may open)"],
 ["green blinking", "box on the station, WIP within the buffer time"],
 ["red steady", "box on the station longer than the buffer time: bottleneck"],
 ["1 short beep", "a station just turned red"],
 ["2 short beeps", "WIP hit the limit, gate holds the next box (CONWIP mode only)"],
 ["3 long beeps", "a station busy for 2 × buffer time: stalled (breakdown alarm)"],
], "tight")}
{eli5("The resistor is a narrow pipe in front of a garden hose (the LED): without it the water (current) blasts out and bursts the hose. 220 Ω lets about 13 mA through, which is bright but safe.")}
{stop("Test sketch, type <code>l</code>: the LEDs light one at a time in the order S1 green, S1 red, S2 green, S2 red, S3 green, S3 red. Type <code>b</code>: two beeps. If an LED stays dark, turn it round (legs swapped).")}
</div></div>""", gl("Andon", "Buffer time", "Bottleneck", "Polarity"))

# ---------------- 11. Wire 4 ----------------
page("10. Wire 4: the servo and its own 5 V supply", f"""
<div class="twocol"><div>
<p>The SG90 has 3 wires: <b>orange = signal, red = +5 V, brown = GND</b>.</p>
{steps([
 "Use the other (bottom) pair of breadboard rails as a separate <b>servo power rail</b>. First remove the jumper you added in Wire 1 between the top and bottom <b>red</b> rails. Keep the <b>blue</b> rails joined (common GND).",
 "Adapter <b>+</b> → bottom red rail. Adapter <b>-</b> → bottom blue rail (which is joined to the UNO GND).",
 "Push the 470 µF capacitor into the bottom rails: <b>long leg into red (+)</b>, striped leg into blue (-).",
 "Servo red → bottom red rail. Servo brown → blue rail. Servo orange → UNO D8.",
 "Double-check: the UNO 5V pin and the adapter + are <b>not</b> connected anywhere.",
])}
{warn("If the top and bottom red rails are still joined, the adapter's 5 V and the laptop USB's 5 V get tied together. Remove that jumper.")}
</div><div>
<h3>Why a separate supply</h3>
<p>When the SG90 starts moving it briefly draws several hundred mA. From the UNO's 5V pin that spike makes the voltage dip and the UNO <b>resets in the middle of the demo</b> (a brown-out). The 2 A adapter has plenty of current, and the capacitor covers the first instant of each spike.</p>
{eli5("The capacitor is a small water tank right next to the tap. When the servo suddenly drinks a lot, it drinks from the tank first, so the pressure for everyone else does not drop.")}
<p>The program also only sends position pulses for 0.45 s after each move, then lets the servo rest. That stops buzzing and jitter. Gear friction holds the arm in place.</p>
{stop("Plug in the adapter and the UNO USB. Test sketch, type <code>g</code>: the servo moves CLOSED → OPEN three times and the UNO does <b>not</b> reset (the test menu does not reprint by itself). Unplug both.")}
</div></div>""", gl("Brown-out", "Electrolytic capacitor", "Common GND", "Rail (breadboard)"))

# ---------------- 12. Wire 5 ----------------
page("11. Wire 5: the NodeMCU link", f"""
<div class="twocol"><div>
<p>The NodeMCU sits on the front strip next to the breadboard and gets its own power from its micro-USB cable (laptop or a power bank). It is <b>not</b> plugged into the breadboard (it is too wide for a 400-point board); use male-female jumpers to its pins.</p>
{steps([
 "Divider: put the <b>1 kΩ</b> across two rows of the breadboard (row A and row B). Put the <b>2.2 kΩ</b> from row B to the blue (GND) rail.",
 "UNO <b>A3</b> → row A (the 1 kΩ's free end).",
 "Row B (the point between the two resistors) → NodeMCU <b>D5</b>.",
 "NodeMCU <b>D6</b> → UNO <b>A2</b> (direct wire, no resistor).",
 "NodeMCU <b>GND</b> → breadboard blue rail.",
 "Do <b>not</b> connect the NodeMCU's 3V3 or Vin to anything.",
])}
<div class="mono">UNO A3 ──[1 kΩ]──●── NodeMCU D5<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.2 kΩ]<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;GND</div>
</div><div>
<h3>Why the divider</h3>
<p>The UNO speaks at 5 V; the ESP8266 chip on the NodeMCU is a 3.3 V chip. The divider turns 5 V into 5 × 2.2 / (1 + 2.2) ≈ <b>3.4 V</b>, which the ESP8266 reads as HIGH safely. The other direction needs nothing: the UNO reads 3.3 V as HIGH.</p>
{eli5("Two resistors share the 5 V like two friends sharing a pizza in proportion to their size: 1 slice for the 1 kΩ, 2.2 slices for the 2.2 kΩ. The NodeMCU only eats the 2.2 kΩ's share, about 3.4 V.")}
<h3>Why A2/A3 and not the UNO's TX/RX pins</h3>
<p>The UNO's real serial pins (D0/D1) are used by the USB cable to the laptop (our backup path). So the sketch makes a second serial port in software on A2/A3 at 19200 baud.</p>
{stop("Multimeter: with the UNO powered, measure between NodeMCU D5 and GND while the UNO is idle: about 3.3-3.4 V (serial lines rest HIGH). Never more than 3.6 V. The link test itself comes in Software 2.")}
</div></div>""", gl("Voltage divider", "SoftwareSerial", "Baud", "Common GND"))

# ---------------- 13. Wiring diagram ----------------
page("12. Full wiring diagram", """
<img src="img/wiring_rot.jpg" class="rot">
<p class="small">Turn the page a quarter turn clockwise to read it. Zoomable version: <code>docs/phase2/wiring_diagram.svg</code>. The short-leg wires from the LEDs to GND are not drawn, to keep it readable. The servo supply shares only GND with the rest.</p>
""", gl("Rail (breadboard)", "Voltage divider", "Common GND"))

# ---------------- 14. Software 1 ----------------
page("13. Software 1: Arduino IDE, drivers and flashing", f"""
<div class="twocol"><div>
<h3>Install once</h3>
{steps([
 "Install <b>Arduino IDE 2.x</b> from arduino.cc.",
 "Plug in the UNO. If no new COM port appears (Tools > Port, or Device Manager > Ports), install the <b>CH340 driver</b> (the clone UNO uses this USB chip) and replug.",
 "File > Preferences > <i>Additional boards manager URLs</i>: <code>https://arduino.esp8266.com/stable/package_esp8266com_index.json</code>. Then Tools > Board > Boards Manager: install <b>esp8266 by ESP8266 Community</b>.",
 "Plug in the NodeMCU. If no COM port appears, install the <b>Silicon Labs CP210x driver</b>.",
 "Sketch > Include Library > Manage Libraries: install <b>PubSubClient</b> by Nick O'Leary. (Servo, SoftwareSerial and EEPROM are built in.)",
])}
<h3>Flash the hardware test sketch to the UNO</h3>
{steps([
 "Open <code>firmware/uno_hardware_test/uno_hardware_test.ino</code>.",
 "Tools > Board: <b>Arduino Uno</b>. Tools > Port: the UNO's COM port.",
 "Click Upload (→). Wait for 'Done uploading'.",
 "Open Serial Monitor (magnifier icon), set <b>115200 baud</b> and <b>Newline</b>. The menu appears.",
], 6)}
</div><div>
{table(["Type", "Test"], [
 ["s", "live view of the 6 sensors (any key stops)"],
 ["l", "LEDs one by one"], ["g", "gate servo CLOSED/OPEN x3"],
 ["b", "buzzer"], ["w", "NodeMCU link (after Software 2)"], ["a", "LEDs + gate + buzzer"]], "tight")}
<h3>Flash the real program (after calibration)</h3>
<p>Open <code>firmware/uno_line_controller/uno_line_controller.ino</code>, same board and port, Upload. On start the LEDs flash and the buzzer chirps once.</p>
<h3>Upload fails?</h3>
<ul>
<li>"Port busy / access denied": close the Serial Monitor and any <code>run.py --source usb</code>.</li>
<li>"not in sync": wrong board or port selected, or a bad USB cable (some cables are charge-only).</li>
<li>Upload to the UNO with A2/A3 wired is fine; nothing is on D0/D1.</li>
</ul>
{eli5("Flashing is copying a recipe into the cook's memory. The UNO keeps the last recipe even when unplugged, so you only flash again when the recipe changes.")}
{stop("Test sketch menu shows in the Serial Monitor at 115200 baud.")}
</div></div>""", gl("Flash (verb)", "Sketch", "COM port", "Baud"))

# ---------------- 15. Calibration ----------------
page("14. Calibration: sensors, gate angles, chute", f"""
<div class="twocol"><div>
<h3>A. IR sensors (trim pots)</h3>
{steps([
 "Test sketch, type <code>s</code>.",
 "Put a box in the lane exactly where it passes the sensor. Turn the trim pot slowly until the module's green LED <b>just</b> turns on, then a little further (about 1/8 turn).",
 "Take the box away: the LED must go off and the column read 0. If it stays on, the sensor is seeing the far rail: turn back a little, or put black tape on the front rail opposite the sensor.",
 "Slide a box through at normal speed 5 times: the column must flick to 1 every time.",
 "Repeat for all 6. Check again with the room lights you will have on demo day.",
])}
<h3>B. Gate angles</h3>
{steps([
 "Type <code>g</code>. Watch which way the shaft turns. The sketch uses <b>10°</b> for closed and <b>95°</b> for open.",
 "With the servo resting at the closed position (end of the test), push the horn on and glue the popsicle arm so it hangs down across the chute exit.",
 "Type <code>g</code> again. If the arm does not fully block or open, change <code>GATE_CLOSED_DEG</code> / <code>GATE_OPEN_DEG</code> at the top of <b>both</b> sketches (test and line controller), re-upload, repeat.",
 "Load 8 boxes behind the closed arm: none may slip past.",
], 6)}
</div><div>
<h3>C. Chute + gate together</h3>
<p>Type <code>g</code> with boxes loaded: each opening must release the front box onto S1. (In the real program the gate closes as soon as S1 IN sees the box, so only one box goes.)</p>
<h3>D. Timing settings (only if needed)</h3>
<p><b>Buffer time</b> needs no re-upload: Serial Monitor (115200, Newline), type <code>B,15</code> for 15 s (<code>H</code> shows the settings), or use the dashboard. Saved in EEPROM.</p>
{table(["Setting (top of uno_line_controller.ino)", "Default", "Change if"], [
 ["IR_HOLDOFF_MS", "400", "a box is counted twice: raise to 600"],
 ["GATE_REOPEN_MS", "1000", "S1 empty this long before the gate reopens; raise if boxes bump at S1"],
 ["DEFAULT_BUFFER_S", "10", "first-boot buffer time (later B,n, saved in EEPROM)"],
 ["DEFAULT_WIP_LIMIT", "0", "0 = S1 gate only; n = CONWIP limit (later L,n)"],
], "tight small")}
{eli5("Tuning a sensor is like adjusting a motion-sensor light in a corridor: sensitive enough to see someone walking past, but not so sensitive that it sees the wall opposite.")}
{stop("All 6 sensors: 5/5 passes counted, 0 false counts with the lane empty. Gate holds 8 boxes and releases exactly the front one.")}
</div></div>""", gl("Potentiometer (trim pot)", "Escapement", "EEPROM", "Debounce"))

# ---------------- 16. Software 2 ----------------
page("15. Software 2: laptop, Mosquitto, hotspot and gateway", f"""
<div class="twocol"><div>
<h3>A. Python (once)</h3>
{steps([
 "Install Python 3.11+ from python.org; tick <b>Add python.exe to PATH</b>.",
 "Command Prompt: <code>cd ...\\OptiProductio\\code\\laptop</code>",
 "<code>py -m venv .venv</code> then <code>.venv\\Scripts\\activate</code>",
 "<code>pip install -r requirements.txt</code>",
 "Check: <code>python -m pytest -q</code> → <b>10 passed</b>. Try <code>python run.py --source sim</code>: the dashboard opens with a simulated line.",
])}
<h3>B. Mosquitto (MQTT broker)</h3>
{steps([
 "Install from mosquitto.org/download (Windows 64-bit).",
 "As administrator: <code>net stop mosquitto</code> (the installed service only listens to the laptop itself).",
 "As administrator: <code>netsh advfirewall firewall add rule name=\"Mosquitto 1883\" dir=in action=allow protocol=TCP localport=1883</code>",
 "Start it with our config and leave the window open:<br><code>\"C:\\Program Files\\mosquitto\\mosquitto.exe\" -c code\\laptop\\mosquitto\\mosquitto.conf -v</code>",
], 6)}
</div><div>
<h3>C. Hotspot and gateway</h3>
{steps([
 "Phone hotspot on <b>2.4 GHz</b> (Android: AP band 2.4 GHz; iPhone: Maximise Compatibility). Connect the laptop to it; if Windows asks, choose <b>Private</b> network.",
 "<code>ipconfig</code> → note the Wi-Fi <b>IPv4 Address</b>, e.g. 192.168.43.25.",
 "Edit <code>firmware/nodemcu_gateway/config.h</code>: WIFI_SSID, WIFI_PASSWORD, MQTT_HOST = that IP.",
 "Arduino IDE: Board <b>NodeMCU 1.0 (ESP-12E Module)</b>, the NodeMCU's port, Upload.",
 "Serial Monitor 115200: <b>Wi-Fi OK</b> then <b>MQTT connected</b>. Blue on-board LED solid = connected (slow blink = Wi-Fi only, fast blink = no Wi-Fi).",
 "Link test: UNO running the test sketch, type <code>w</code>: lines <code># gw ok wifi=1 mqtt=1</code> come back.",
], 10)}
{eli5("Mosquitto is a post office on the laptop. The NodeMCU drops letters into labelled boxes like rvce/idealab/line1/s2/event; our Python program has a subscription to all of line1's boxes. The dashboard sends 'change the WIP limit' letters back the same way.")}
{stop("pytest 10 passed; Mosquitto window shows 'Opening ipv4 listen socket on port 1883'; NodeMCU says MQTT connected; <code>w</code> test returns 'gw ok'.")}
</div></div>""", gl("MQTT", "Broker", "Hotspot", "IP address", "Simulator"))

# ---------------- 17. Power-on + self-test ----------------
page("16. First power-on and the self-test", f"""
<div class="twocol"><div>
<h3>Start-up order (every time)</h3>
{steps([
 "Phone hotspot on. Laptop on the hotspot.",
 "Mosquitto window started (section 15, B4).",
 "<code>.venv\\Scripts\\activate</code> then <code>python run.py --source mqtt</code>. Browser opens <code>http://localhost:5000</code>.",
 "Plug in the servo adapter, then the NodeMCU USB, then the UNO USB (UNO running <b>uno_line_controller</b>).",
 "UNO lamp test: all LEDs flash, buzzer chirps. Gate opens once; all stations green steady.",
 "Dashboard top right: <b>MQTT · live</b> and <b>NodeMCU online</b>.",
])}
<h3>Backup path (no Wi-Fi)</h3>
<p>Stop run.py (Ctrl+C), close any Serial Monitor, then <code>python run.py --source usb --port COM5</code> (your UNO port; <code>python -m serial.tools.list_ports</code> lists them). Takes 30 seconds.</p>
{eli5("Like a cricket match with TV and radio: if the TV feed (Wi-Fi) drops, switch to the radio (USB cable). The match (the UNO running the gate) never stops.")}
</div><div>
<h3>Self-test sheet (do before every rehearsal and the demo)</h3>
{table(["✓", "Test", "Pass"], [
 ["☐", "One box end to end", "event log: S1 IN, S1 OUT, S2 IN, S2 OUT, S3 IN, S3 OUT; Done = 1"],
 ["☐", "Cycle time", "OUT event cycle time close to a phone stopwatch (± 0.5 s)"],
 ["☐", "20 boxes", "Done count on dashboard = hand count"],
 ["☐", "Gate sequence", "box reaches S1 → gate closes; S1 empty → gate reopens ~1 s later"],
 ["☐", "Buffer time", "B,5: S1 green blinks 5 s with a box, then red steady + 1 beep"],
 ["☐", "WIP limit 3", "gate never lets a 4th box in; 2 beeps; amber banner"],
 ["☐", "Limit from dashboard", "Apply L = 2 → LIMIT in the event log within 1 s"],
 ["☐", "Settings kept", "UNO reset button → BOOT/BUF show the same limit and buffer"],
 ["☐", "Stall", "box held on S2 for 2 × buffer → stays red, 3 beeps, Line DOWN"],
 ["☐", "Wi-Fi loss", "hotspot off 20 s: line still runs; dashboard warns; resumes"],
 ["☐", "USB backup", "--source usb shows the same data"],
 ["☐", "Lost lines", "no (or very few) 'lines lost' in 5 min"],
 ["☐", "Little's law", "Run report: TH x LT close to WIP avg (within ~15 %)"],
], "tight small")}
{stop("Every box ticked twice on Wednesday. If one fails, Troubleshooting (section 19).")}
</div></div>""", gl("Little's law", "Andon", "Downtime", "Last Will"))

# ---------------- 18. Dashboard ----------------
page("17. Using the dashboard", f"""
<img src="img/dashboard.jpg" class="dash">
<div class="twocol"><div>
<ul class="tightlist">
<li><b>Top tiles</b> (scoreboard, idea from Vorne XL): good parts vs target, OEE with A/E/QR, throughput, WIP now / limit and gate state, bottleneck now, lead time with the Little's law check.</li>
<li><b>Line view</b>: each station's lights copy the real LEDs; numbers between stations = boxes waiting.</li>
<li><b>Buffer time and gate control</b>: set the buffer time (5 to 60 s presets) and press <b>Apply buffer</b>. Pick a WIP limit (Off = S1 gate only, 2, 3, 4, 6) and press <b>Apply limit</b>. A new run starts automatically. "Mark last part scrap" logs a reject. "Reset line counts" only after all boxes are back in the chute.</li>
</ul>
</div><div>
<ul class="tightlist">
<li><b>Timeline</b>: last 10 min of each station's active periods, orange = bottleneck, violet = shifting bottleneck, red = line down (hover for the reason), gate openings, WIP vs limit.</li>
<li><b>Bottleneck analysis</b> (Roser), <b>Downtime Pareto</b>, <b>Output per minute</b>, <b>KPI table</b> with formulas (ISO 22400 names).</li>
<li><b>Run report</b> (button top right): one row per run, for the A/B comparison; CSV download; print to PDF.</li>
</ul>
{eli5("The dashboard is a cricket scorecard: the big numbers are the score, the timeline is the ball-by-ball, and the run report compares innings.")}
</div></div>""", gl("OEE", "Throughput", "Lead time", "Pareto chart", "Active period", "ISO 22400"))

# ---------------- 19. Demo script ----------------
page("18. Demo-day script", f"""
<div class="twocol"><div>
<h3>Roles during the demo</h3>
{table(["Person", "Does"], [
 ["Operator S1", "takes each released box, 'works' 3-4 s, slides it past S1 OUT into the queue"],
 ["Operator S2", "the bottleneck station: 'works' 6-8 s per box"],
 ["Operator S3", "'works' 4 s, slides into the done bin, carries finished boxes back to the chute"],
 ["Presenter", "laptop + explaining; reads numbers off the dashboard"],
], "tight")}
<p>Operators always slide boxes along the lane past the sensors. Never lift a box over a sensor.</p>
<h3>Arrive 45 min early</h3>
{check(["Hotspot on, laptop joined, Mosquitto, run.py --source mqtt", "Hardware power-on order (section 16)", "Self-test: one box end to end + limit change", "Reset line counts with all boxes in the chute", "Backup video on the laptop desktop", "Run report from Wednesday's A/B test open in a tab"])}
</div><div>
<h3>The 8-minute run</h3>
{table(["Time", "Do", "Say (precise words)"], [
 ["0:00", "Show the table and the architecture", "UNO is the line controller; the NodeMCU is an MQTT gateway; ISA-95 style topics; SQLite historian."],
 ["0:45", "Limit <b>Off</b>, buffer 10 s; run 2 min", "Gate lets one box onto S1 at a time. Green blinks = work in progress; the S2 operator takes ~12 s per box, so S2 turns red after the 10 s buffer time (set per product). S2 has the longest active periods: bottleneck (Roser)."],
 ["3:00", "Apply <b>L = 3</b>; run 3 min", "Closed-loop CONWIP: the gate releases only while WIP < 3. The loop runs on the UNO, the laptop only sets the limit."],
 ["5:30", "Hold a box on S2 for 2 × buffer (20 s)", "Stall alarm; line DOWN; the Pareto attributes the loss to S2."],
 ["6:30", "Open Run report", "Compare throughput, average WIP and lead time; check Little's law."],
 ["7:30", "Questions", "Only quote numbers from our own runs."],
], "tight small")}
{warn("If Wi-Fi fails: switch to USB (30 s). If hardware fails: show the backup video. Show the simulator only as 'the simulator', never as the real line.")}
</div></div>""", gl("CONWIP", "Bottleneck", "Active period", "A/B test", "ISA-95", "Historian"))

# ---------------- 20. Troubleshooting ----------------
page("19. Troubleshooting", table(["Symptom", "Likely cause", "Fix"], [
    ["UNO resets when the gate moves", "servo on UNO 5V, GNDs not joined, capacitor missing", "servo on adapter rail only; join blue rails; check capacitor polarity"],
    ["Sensor always 1", "range too long / sees the far rail / sunlight", "trim pot anticlockwise; black tape on far rail; shade the sensor"],
    ["Sensor never 1", "range too short, wrong pin, VCC/GND swapped", "trim pot clockwise; check the pin table; check wiring"],
    ["Box counted twice", "sensor flickers at the box edge", "tune pot; raise IR_HOLDOFF_MS to 600"],
    ["Event log shows ERR 'OUT without IN'", "that station's IN sensor missed the box", "re-aim / re-tune the IN sensor; operator slid the box past IN?"],
    ["WIP stuck high, gate never opens", "missed counts", "all boxes back to the chute, press Reset line counts"],
    ["Gate lets 2 boxes through", "gate too slow / boxes too close", "raise GATE_REOPEN_MS; check S1 IN sees the box quickly"],
    ["Boxes stop in the chute", "too shallow, sticky floor", "raise riser 1 cm; fresh packing tape"],
    ["Servo buzzes / jitters", "pulses not stopping", "check SERVO_MOVE_MS (450); adapter gives 5 V"],
    ["An LED never lights", "LED backwards / no resistor contact", "turn the LED round; reseat the resistor"],
    ["Upload fails 'access denied'", "port in use", "close Serial Monitor and run.py --source usb"],
    ["No COM port", "driver / charge-only cable", "CH340 (UNO) or CP210x (NodeMCU) driver; another cable"],
    ["NodeMCU fast blink", "no Wi-Fi", "hotspot 2.4 GHz? SSID/password in config.h right?"],
    ["NodeMCU 'MQTT failed, state -2'", "cannot reach the laptop", "MQTT_HOST = laptop's hotspot IP; firewall rule; Mosquitto started with our config"],
    ["Dashboard 'no data for N s'", "source down", "USB plugged? NodeMCU LED solid? Mosquitto window open?"],
    ["Dashboard 'lines lost' climbing", "UNO-NodeMCU link noisy", "check divider values, short wires, common GND"],
    ["Dashboard page will not open", "run.py not running / wrong address", "start run.py; use http://localhost:5000"],
    ["Phones cannot open the dashboard", "firewall", "allow Python on Private networks when Windows asks; use http://laptop-IP:5000"],
    ["pytest fails", "packages not installed / wrong folder", "activate .venv; run from code\\laptop; pip install -r requirements.txt"],
], "tight small") + eli5("Debug like a doctor: find the symptom in the left column, check the most likely cause first, and change one thing at a time."),
    gl("COM port", "Debounce", "Common GND", "Brown-out", "Hotspot", "IP address"))

# ---------------- 21. Quick reference ----------------
page("20. Quick reference card (print and tape to the table)", f"""
<div class="twocol"><div>
{table(["UNO pin", "Connection"], [
 ["5V / GND", "top rails (sensors only)"], ["D2 D3", "S1 IN, S1 OUT"], ["D4 D5", "S2 IN, S2 OUT"], ["D6 D7", "S3 IN, S3 OUT"],
 ["D8", "servo orange"], ["D9 D10", "S1 green, red"], ["D11 D12", "S2 green, red"], ["D13 A0", "S3 green (1 kΩ), red"],
 ["A1", "buzzer +"], ["A2", "← NodeMCU D6"], ["A3", "→ 1 kΩ → NodeMCU D5 (2.2 kΩ to GND)"],
 ["Adapter 5 V 2 A", "bottom rails: servo red + 470 µF (+ long leg)"]], "tight")}
<h3>Commands</h3>
<div class="mono">python run.py --source sim<br>python run.py --source mqtt<br>python run.py --source usb --port COM5<br>python run.py --source sim --scenario breakdown --speed 4<br>python -m optiproductio.simulator --mqtt 127.0.0.1<br>python -m pytest -q</div>
<p>Dashboard <b>http://localhost:5000</b> · Run report <b>/report</b></p>
</div><div>
{table(["Serial line (UNO → laptop)", "Meaning"], [
 ["E,seq,ms,st,ev,val", "one event (IN, OUT, GATE, HOLD, BN, STALL, LIMIT, BUF, BOOT, ERR)"],
 ["S,seq,ms,wip,limit,gate,o1,o2,o3,bn,in,done,buf", "status, every second"],
 ["B,s / L,n / H / R / P", "commands: buffer time, limit, help, reset, ping"]], "tight small")}
{table(["MQTT topic", "Content"], [
 ["rvce/idealab/line1/s1..s3/event", "station events (JSON)"], ["rvce/idealab/line1/line/event", "gate, hold, bottleneck, limit"],
 ["rvce/idealab/line1/status", "status (retained)"], ["rvce/idealab/line1/cmd/wip_limit, cmd/buffer", "laptop → UNO"],
 ["rvce/idealab/line1/gateway/state", "online / offline (Last Will)"]], "tight small")}
{table(["Light / sound", "Meaning"], [
 ["green steady / blinking", "empty / box within buffer"], ["red steady", "busy > buffer: bottleneck"], ["3 beeps", "stalled > 2 × buffer"], ["2 beeps", "WIP at limit, gate holding"]], "tight small")}
</div></div>""", gl("MQTT", "Baud", "Last Will", "WIP", "Andon"))


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', Arial, Helvetica, sans-serif; color: #0f172a; font-size: 9.6pt; line-height: 1.38; }
.page { width: 210mm; height: 297mm; padding: 11mm 12mm 8mm; position: relative; page-break-after: always; display: flex; flex-direction: column; overflow: hidden; }
.hdr { display: flex; justify-content: space-between; border-bottom: 2px solid #0f766e; padding-bottom: 3px; margin-bottom: 6px; font-size: 8pt; color: #475569; }
.hdr b { color: #0f766e; }
h2 { font-size: 15pt; margin: 2px 0 8px; color: #0f172a; }
h3 { font-size: 10.5pt; margin: 8px 0 4px; color: #0f766e; }
p { margin: 3px 0 6px; }
.content { flex: 1 1 auto; min-height: 0; }
.twocol { display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; }
ol.steps { padding-left: 18px; margin: 3px 0 6px; } ol.steps li { margin-bottom: 3px; }
ol.rules li { margin-bottom: 3px; } ol.toc { padding-left: 20px; } ol.toc li { margin-bottom: 1px; }
ul { padding-left: 16px; margin: 3px 0 6px; } ul li { margin-bottom: 2px; }
ul.check { list-style: none; padding-left: 2px; } ul.check li::before { content: "☐  "; }
table { border-collapse: collapse; width: 100%; margin: 4px 0 7px; }
th { background: #0f766e; color: #fff; text-align: left; font-weight: 600; padding: 3px 5px; font-size: 8.6pt; }
td { border-bottom: 1px solid #e2e8f0; padding: 3px 5px; vertical-align: top; }
table.small td, table.small th { font-size: 8.2pt; padding: 2px 4px; }
.eli5 { background: #f1f5f9; border-left: 4px solid #64748b; padding: 5px 8px; margin: 6px 0; border-radius: 4px; font-size: 9pt; }
.eli5 b { display: inline-block; background: #64748b; color: #fff; padding: 0 5px; border-radius: 3px; margin-right: 5px; font-size: 7.5pt; }
.warn { background: #fef2f2; border-left: 4px solid #dc2626; padding: 5px 8px; margin: 6px 0; border-radius: 4px; font-size: 9pt; }
.warn b { color: #b91c1c; margin-right: 4px; }
.stopcheck { background: #ecfdf5; border: 1.5px solid #059669; padding: 5px 8px; margin: 6px 0; border-radius: 5px; font-size: 9pt; }
.stopcheck b { color: #047857; margin-right: 4px; display: block; font-size: 8pt; letter-spacing: .5px; }
code, .mono { font-family: Consolas, 'Courier New', monospace; font-size: 8.4pt; background: #f1f5f9; padding: 0 3px; border-radius: 3px; }
.mono { display: block; padding: 5px 7px; margin: 5px 0; line-height: 1.5; }
img.full { width: 100%; border-radius: 6px; border: 1px solid #e2e8f0; margin: 4px 0 8px; }
img.half { width: 48%; border-radius: 6px; border: 1px solid #e2e8f0; }
img.right { float: right; margin: 0 0 6px 10px; }
img.dash { width: 100%; height: 125mm; object-fit: cover; object-position: top; border-radius: 6px; border: 1px solid #e2e8f0; }
.clear { clear: both; }
img.rot { display: block; height: 218mm; margin: 0 auto 4px; border: 1px solid #e2e8f0; border-radius: 6px; }
.twocol > div { min-width: 0; }
code { word-break: break-all; }
svg.layout { width: 100%; margin-bottom: 6px; }
.small { font-size: 8.4pt; color: #475569; }
.tightlist li { margin-bottom: 4px; }
.gloss { border-top: 1.5px solid #94a3b8; padding-top: 4px; margin-top: 6px; font-size: 7.7pt; color: #334155; column-count: 2; column-gap: 8mm; flex: 0 0 auto; }
.gloss .gt { font-weight: 700; font-size: 7.7pt; color: #0f766e; column-span: all; margin-bottom: 2px; letter-spacing: .5px; }
.gloss div { break-inside: avoid; margin-bottom: 1.5px; }
.foot { font-size: 7.5pt; color: #94a3b8; display: flex; justify-content: space-between; margin-top: 3px; flex: 0 0 auto; }
.cover .kicker { color: #0f766e; font-weight: 700; letter-spacing: 1px; font-size: 9pt; margin-top: 6mm; }
.cover .ctitle { font-size: 24pt; line-height: 1.15; margin: 4px 0 6px; }
.cover .csub { font-size: 12pt; color: #475569; margin-bottom: 8px; }
"""


def build():
    out = [f"<!doctype html><html><head><meta charset='utf-8'><title>OptiProductio assembly and setup manual</title><style>{CSS}</style></head><body>"]
    n = len(PAGES)
    for i, pg in enumerate(PAGES, 1):
        gloss = "".join(f"<div><b>{html.escape(k)}:</b> {html.escape(GLOSSARY[k])}</div>" for k in pg["gloss"])
        hdr = "" if i == 1 else f'<div class="hdr"><span><b>OptiProductio</b> · assembly and setup manual</span><span>{TITLE}</span></div>'
        title = f"<h2>{pg['title']}</h2>" if pg["title"] else ""
        out.append(f"""<section class="page">{hdr}<div class="content">{title}{pg['body']}</div>
<div class="gloss"><div class="gt">GLOSSARY FOR THIS PAGE</div>{gloss}</div>
<div class="foot"><span>IEM IDEA Lab EL · Phase 2 · manual v2 · 24 Nov 2026</span><span>page {i} of {n}</span></div></section>""")
    out.append("</body></html>")
    with open(os.path.join(HERE, "manual.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"{n} pages")


if __name__ == "__main__":
    build()
