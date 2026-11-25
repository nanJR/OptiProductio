// OptiProductio dashboard. Polls /api/state once a second and redraws.
// Plain JavaScript and hand-drawn SVG, so it runs with no internet.
"use strict";

const $ = (id) => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const fmt = (v, d = 1) => (v === null || v === undefined || Number.isNaN(v)) ? "-" : Number(v).toFixed(d);
const pct = (v) => (v === null || v === undefined) ? "-" : Math.round(v * 100) + "%";

let state = null;
let limitDraft = null;
let bufDraft = null;
let settingsLoaded = false;

// ---------- theme ----------
try { const t = localStorage.getItem("op-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
$("themeBtn").onclick = () => {
  const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("op-theme", next); } catch (e) {}
  if (state) render(state);
};

// ---------- API ----------
async function post(url, body) {
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  return r.json();
}
async function poll() {
  try {
    const r = await fetch("/api/state", { cache: "no-store" });
    state = await r.json();
    render(state);
  } catch (e) {
    $("srcDot").className = "dot bad";
    $("srcText").textContent = "laptop server not reachable";
  }
}
setInterval(poll, 1000);
poll();

// ---------- controls ----------
function currentLimit() { return state && state.status ? state.status.limit : 0; }
function showLimit() { $("limVal").textContent = limitDraft === 0 ? "Off" : limitDraft; }
$("limMinus").onclick = () => { limitDraft = Math.max(0, (limitDraft ?? currentLimit()) - 1); showLimit(); };
$("limPlus").onclick = () => { limitDraft = Math.min(20, (limitDraft ?? currentLimit()) + 1); showLimit(); };
$("limApply").onclick = async () => {
  if (limitDraft === null) limitDraft = currentLimit();
  await post("/api/limit", { limit: limitDraft });
  $("limNote").textContent = `Sent WIP limit ${limitDraft === 0 ? "off" : limitDraft}. Waiting for the UNO to confirm...`;
};
const presets = [["Off", 0], ["2", 2], ["3", 3], ["4", 4], ["6", 6]];
for (const [label, n] of presets) {
  const b = document.createElement("button");
  b.className = "btn small"; b.textContent = label === "Off" ? "Off (S1 gate only)" : "L = " + label; b.dataset.n = n;
  b.onclick = () => { limitDraft = n; showLimit(); };
  $("presets").appendChild(b);
}
// Buffer time per station: pick "All stations" or S1/S2/S3, set the seconds, Apply.
let bufStation = 0;                                       // 0 = all stations, 1..3 = one station
function stationBufs() {
  const k = state && state.kpi;
  if (k && k.cfg && k.cfg.buffers_s) return k.cfg.buffers_s;
  const b = state && state.status && state.status.buf != null ? state.status.buf : 10;
  return [b, b, b];
}
function currentBuf() { const b = stationBufs(); return Math.round(bufStation ? b[bufStation - 1] : b[0]); }
function showBuf() { $("bufVal").textContent = bufDraft; }
const bufStep = (v) => (v >= 60 ? 10 : 1);
$("bufMinus").onclick = () => { const v = bufDraft ?? currentBuf(); bufDraft = Math.max(1, v - bufStep(v - 1)); showBuf(); };
$("bufPlus").onclick = () => { const v = bufDraft ?? currentBuf(); bufDraft = Math.min(3600, v + bufStep(v)); showBuf(); };
$("bufApply").onclick = async () => {
  if (bufDraft === null) bufDraft = currentBuf();
  await post("/api/buffer", { buffer_s: bufDraft, station: bufStation });
  $("bufNote").textContent = `Sent buffer time ${bufDraft} s for ${bufStation ? "S" + bufStation : "all stations"}. Waiting for the UNO to confirm...`;
};
for (const [n, label] of [[0, "All stations"], [1, "S1"], [2, "S2"], [3, "S3"]]) {
  const b = document.createElement("button");
  b.className = "btn small" + (n === 0 ? " active" : ""); b.textContent = label; b.dataset.st = n;
  b.onclick = () => {
    bufStation = n; bufDraft = currentBuf(); showBuf();
    document.querySelectorAll("#bufStations .btn").forEach((x) => x.classList.toggle("active", Number(x.dataset.st) === n));
  };
  $("bufStations").appendChild(b);
}
for (const n of [5, 10, 15, 30, 60]) {
  const b = document.createElement("button");
  b.className = "btn small"; b.textContent = n + " s"; b.dataset.n = n;
  b.onclick = () => { bufDraft = n; showBuf(); };
  $("bufPresets").appendChild(b);
}
$("newRun").onclick = () => post("/api/run", {});
$("scrap").onclick = () => post("/api/scrap", {});
$("pingBtn").onclick = () => post("/api/ping", {});
$("resetBtn").onclick = () => {
  if (confirm("Reset all counts on the UNO? Take every box off the table and put them back in the chute first.")) post("/api/reset", {});
};
$("settings").onsubmit = async (e) => {
  e.preventDefault();
  const f = new FormData(e.target), body = {};
  for (const [k, v] of f.entries()) body[k] = Number(v);
  await post("/api/config", body);
};

// ---------- SVG helpers ----------
function el(tag, attrs, parent, text) {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (text !== undefined) n.textContent = text;
  if (parent) parent.appendChild(n);
  return n;
}
function clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); return svg; }
function width(svg) { return svg.getBoundingClientRect().width || 600; }

// ---------- render ----------
function render(s) {
  const src = s.source || {};
  const age = src.last_rx_age_s;
  const live = age !== null && age !== undefined && age < 3;
  $("srcDot").className = "dot " + (live ? "ok" : (src.connected ? "warn" : "bad"));
  const kindName = { mqtt: "MQTT", usb: "USB serial", sim: "Simulator" }[src.kind] || src.kind;
  $("srcText").textContent = `${kindName} · ${live ? "live" : (age == null ? "no data yet" : "no data for " + Math.round(age) + " s")}` + (s.lost_lines ? ` · ${s.lost_lines} lines lost` : "");
  if (src.kind === "mqtt") {
    $("gwPill").classList.remove("hidden");
    const on = src.gateway === "online";
    $("gwDot").className = "dot " + (on ? "ok" : "bad");
    const rssi = src.gateway_stats && src.gateway_stats.rssi;
    $("gwText").textContent = "NodeMCU " + (src.gateway || "unknown") + (rssi ? ` · ${rssi} dBm` : "");
  } else {
    $("gwPill").classList.add("hidden");
  }
  $("runLabel").textContent = s.run ? `Run ${s.run.id}: ${s.run.label}` : "waiting for data";

  const k = s.kpi, st = s.status;
  if (!settingsLoaded && s.cfg) {
    for (const key in s.cfg) { const i = document.querySelector(`[name=${key}]`); if (i) i.value = s.cfg[key]; }
    settingsLoaded = true;
  }
  if (limitDraft === null && st) { limitDraft = st.limit; showLimit(); }
  document.querySelectorAll("#presets .btn").forEach((b) => b.classList.toggle("active", st && Number(b.dataset.n) === st.limit));
  const bufs = stationBufs();
  if (bufDraft === null && st) { bufDraft = currentBuf(); showBuf(); }
  document.querySelectorAll("#bufPresets .btn").forEach((b) => b.classList.toggle("active", Number(b.dataset.n) === bufDraft));
  $("bufNow").textContent = "Now: " + bufs.map((b, i) => `S${i + 1} ${Math.round(b)} s`).join(" · ");
  if (st && s.pending_buffer === null && $("bufNote").textContent.startsWith("Sent")) {
    $("bufNote").textContent = `UNO confirmed: ${bufs.map((b, i) => `S${i + 1} ${Math.round(b)} s`).join(", ")}. Saved in its EEPROM.`;
  }
  if (st && s.pending_limit === null && $("limNote").textContent.startsWith("Sent")) {
    $("limNote").textContent = `UNO confirmed WIP limit ${st.limit === 0 ? "off" : st.limit}. A new run started.`;
  }

  const banner = $("banner");
  if (!k || !st) { banner.className = "banner"; banner.classList.remove("hidden"); return; }
  const lockSt = [1, 2, 3].filter((n) => k.lock_now & (1 << (n - 1)));
  if (lockSt.length) {
    banner.className = "banner alert";
    banner.textContent = `Line LOCKED: breakdown at ${lockSt.map((n) => "S" + n).join(", ")}. Sensors of the other stations are ignored and the gate stays closed until the stuck box leaves.`;
  } else if (k.line_down_now) {
    banner.className = "banner alert";
    banner.textContent = `Line DOWN: ${k.down_reason_now}. No box has left S3 for more than ${s.cfg.down_after_s} s.`;
  } else if (!live) {
    banner.className = "banner alert";
    banner.textContent = "No data from the line for " + Math.round(age) + " s. Check the USB cable, Wi-Fi hotspot or Mosquitto.";
  } else if (st.limit > 0 && st.wip >= st.limit) {
    banner.className = "banner hold";
    banner.textContent = `WIP ${st.wip} has reached the limit ${st.limit}: the gate is holding the next box until one leaves S3.`;
  } else {
    banner.className = "banner hidden";
  }

  // scoreboard
  $("tGood").innerHTML = `${k.good}<small>/ ${Math.floor(k.target)} target</small>`;
  $("tGoodSub").textContent = `efficiency ${k.efficiency_pct == null ? "-" : k.efficiency_pct + "%"} · ${k.breakdown_parts || 0} breakdown · ${k.scrap} scrap · run ${fmtDur(k.pbt_s)}`;
  $("tOee").textContent = pct(k.oee);
  [["A", k.availability], ["E", k.effectiveness], ["Q", k.quality]].forEach(([n, v]) => {
    $("t" + n).textContent = pct(v); $("b" + n).style.width = (v == null ? 0 : v * 100) + "%";
  });
  $("tTh").innerHTML = `${fmt(k.th_per_min, 1)}<small>pcs/min</small>`;
  $("tThSub").textContent = `${k.produced} out of S3 · ${k.released} released into S1`;
  $("tWip").innerHTML = `${st.wip}<small>/ ${st.limit === 0 ? "no limit" : st.limit}</small>`;
  const gateCls = st.gate ? "open" : (st.limit > 0 && st.wip >= st.limit ? "hold" : "closed");
  const gateTxt = st.gate ? "OPEN" : (gateCls === "hold" ? "HELD BY LIMIT" : (st.occ[0] > 0 ? "CLOSED: S1 BUSY" : "CLOSED"));
  for (const id of ["tGate", "fGate"]) { $(id).className = "chip " + gateCls; $(id).textContent = gateTxt; }
  $("tWipAvg").textContent = ` · avg ${fmt(k.wip_avg, 2)}`;
  // every station over the buffer time right now, longest first (Roser: the first one is the main bottleneck)
  const bnList = k.bn_list || (k.bn_now ? [k.bn_now] : []);
  $("tBn").textContent = bnList.length ? bnList.map((n) => "S" + n).join(", ") : "none";
  $("tBnSub").textContent = (bnList.length
    ? bnList.map((n) => { const x = k.stations[n - 1]; return `S${n} ${fmt(x.active_now_s, 0)} s > ${fmt(x.buffer_s, 0)} s${x.stalled ? " (breakdown)" : ""}`; }).join(" · ") + " · "
    : "no station over its buffer · ") + (k.bn_overall ? `run: S${k.bn_overall}` : "");
  $("tLt").innerHTML = `${fmt(k.lead_avg_s, 1)}<small>s</small>`;
  $("tLtSub").textContent = k.little_rhs == null ? "Little's law check -" : `TH x LT = ${fmt(k.little_rhs, 2)} vs WIP ${fmt(k.wip_avg, 2)}`;

  // line view
  for (let i = 0; i < 3; i++) renderStation(i, k.stations[i], k.bn_now === i + 1, k.stations[i].buffer_s ?? k.cfg.buffer_s);
  $("buf1").textContent = k.transit[0]; $("buf2").textContent = k.transit[1];
  $("doneN").textContent = k.produced;

  drawTimeline(k);
  drawRoser(k);
  drawPareto(k);
  drawMinutes(k);
  renderTables(k);
  renderLog(s.events || []);
}

function fmtDur(sec) {
  sec = Math.max(0, Math.round(sec));
  const m = Math.floor(sec / 60), r = sec % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

// Same rule as the UNO LEDs: green steady = empty, green blinking = WIP within buffer, red steady = over buffer
function renderStation(i, x, isBn, bufS) {
  const box = $("st" + (i + 1));
  const led = x.led || (x.occ > 0 ? "blink" : "green");
  box.className = "station" + (led === "red" ? " isbn" : "") + (x.stalled ? " stall" : "") + (x.frozen ? " frozen" : "");
  const g = led === "green" ? "on" : (led === "blink" ? "on blink" : "");
  const r = led === "red" ? "on" : "";
  let stateTxt = "Empty: waiting for a box";
  if (led === "blink") stateTxt = `<b>Working</b> ${fmt(x.active_now_s, 0)} of ${fmt(bufS, 0)} s buffer`;
  if (led === "red") stateTxt = `<b>${isBn ? "Bottleneck" : "Over buffer"}</b> · busy ${fmt(x.active_now_s, 1)} s`;
  if (x.stalled) stateTxt = `<b>Stalled</b> ${fmt(x.active_now_s, 0)} s (2 x buffer): suspected breakdown`;
  if (x.frozen) stateTxt = `<b>Frozen</b>: breakdown at another station, sensors ignored, timer paused` + (x.occ ? ` at ${fmt(x.active_now_s, 0)} s` : "");
  box.innerHTML = `
    <div class="head"><span class="name">S${i + 1}</span>
      <span class="lights"><span class="lamp g ${g}"></span><span class="lamp r ${r}"></span></span></div>
    <div class="box-slot">${'<span class="box"></span>'.repeat(Math.min(x.occ, 3))}</div>
    <div class="state">${stateTxt}</div>
    <div class="kv num">
      <span>Last cycle</span><span>${fmt(x.ct_last_s)} s</span>
      <span>Avg cycle</span><span>${fmt(x.ct_avg_s)} s</span>
      <span>Busy</span><span>${Math.round(x.busy_ratio * 100)}%</span>
      <span>Done</span><span>${x.count}</span>
    </div>`;
}

function drawTimeline(k) {
  const svg = clear($("timeline")), W = width(svg);
  const tl = k.timeline, L = 64, R = W - 8, span = Math.max(1, tl.t1 - tl.t0);
  const x = (t) => L + (R - L) * (t - tl.t0) / span;
  const rows = [["S1", 10], ["S2", 42], ["S3", 74], ["Line", 106], ["Gate", 138]];
  const rh = 22;
  for (const [name, y] of rows) {
    el("rect", { x: L, y, width: R - L, height: rh, rx: 4, fill: css("--idle"), opacity: 0.55 }, svg);
    el("text", { x: 0, y: y + 15 }, svg, name);
  }
  tl.stations.forEach((segs, i) => {
    for (const [a, b] of segs) el("rect", { x: x(a), y: rows[i][1], width: Math.max(1, x(b) - x(a)), height: rh, fill: css("--run"), opacity: 0.55 }, svg);
  });
  for (const [s, a, b] of tl.bn) el("rect", { x: x(a), y: rows[s - 1][1] + 14, width: Math.max(1, x(b) - x(a)), height: 8, fill: css("--bn") }, svg);
  for (const [sa, sb, a, b] of tl.shift) for (const s of [sa, sb]) el("rect", { x: x(a), y: rows[s - 1][1] + 14, width: Math.max(1, x(b) - x(a)), height: 8, fill: css("--shift") }, svg);
  el("rect", { x: L, y: rows[3][1], width: R - L, height: rh, rx: 4, fill: css("--run"), opacity: 0.35 }, svg);
  for (const [a, b, reason] of tl.down) {
    const r = el("rect", { x: x(a), y: rows[3][1], width: Math.max(1, x(b) - x(a)), height: rh, fill: css("--down") }, svg);
    el("title", {}, r, reason);
  }
  for (const [a, b] of tl.gate) el("rect", { x: x(a), y: rows[4][1], width: Math.max(1.5, x(b) - x(a)), height: rh, fill: css("--accent") }, svg);

  // WIP step chart
  const y0 = 200, hW = 38;
  const maxW = Math.max(2, ...tl.wip.map((p) => p[1]), (state.status && state.status.limit) || 0);
  const y = (w) => y0 - hW * w / maxW;
  el("text", { x: 0, y: y0 - 14 }, svg, "WIP");
  el("line", { x1: L, x2: R, y1: y0, y2: y0, stroke: css("--line") }, svg);
  let d = "";
  tl.wip.forEach(([t, w], i) => {
    const X = x(Math.max(t, tl.t0));
    d += i === 0 ? `M${X},${y(w)}` : `H${X}V${y(w)}`;
  });
  d += `H${R}`;
  el("path", { d, fill: "none", stroke: css("--text"), "stroke-width": 1.6 }, svg);
  const lim = state.status && state.status.limit;
  if (lim) {
    el("line", { x1: L, x2: R, y1: y(lim), y2: y(lim), stroke: css("--hold"), "stroke-dasharray": "4 4" }, svg);
    el("text", { x: R - 60, y: y(lim) - 4, fill: css("--hold") }, svg, "limit " + lim);
  }
  // time axis: minutes ago
  const mins = span / 60000;
  const step = mins > 6 ? 2 : 1;
  for (let m = 0; m <= mins; m += step) {
    const X = x(tl.t1 - m * 60000);
    el("line", { x1: X, x2: X, y1: 6, y2: y0 + 4, stroke: css("--line"), "stroke-dasharray": "2 4" }, svg);
    el("text", { x: X - 14, y: y0 + 22 }, svg, m === 0 ? "now" : `-${m} min`);
  }
  $("tlHint").textContent = `Last ${Math.round(mins)} min. Each station row is filled while a box is on it (active period). The thin orange strip marks the bottleneck at that moment, violet the shifting bottleneck. Hover a red block for the downtime reason.`;
}

function barChart(svg, items, opts) {
  // items: [{label, parts:[{v, color}], text}]
  clear(svg);
  const W = width(svg), H = Number(svg.getAttribute("height")), L = 30, B = H - 26, T = 10;
  const max = opts.max || Math.max(1, ...items.map((it) => it.parts.reduce((a, p) => a + p.v, 0)));
  const n = Math.max(items.length, 1), bw = Math.min(56, (W - L) / n * 0.6);
  for (let g = 0; g <= 4; g++) {
    const yy = B - (B - T) * g / 4;
    el("line", { x1: L, x2: W, y1: yy, y2: yy, stroke: css("--line") }, svg);
    el("text", { x: 0, y: yy + 4 }, svg, opts.tick ? opts.tick(max * g / 4) : Math.round(max * g / 4));
  }
  items.forEach((it, i) => {
    const cx = L + (W - L) * (i + 0.5) / n;
    let acc = 0;
    for (const p of it.parts) {
      const h = (B - T) * p.v / max;
      el("rect", { x: cx - bw / 2, y: B - (B - T) * acc / max - h, width: bw, height: Math.max(0, h), rx: 3, fill: p.color }, svg);
      acc += p.v;
    }
    el("text", { x: cx, y: H - 8, "text-anchor": "middle" }, svg, it.label);
    if (it.text) el("text", { x: cx, y: B - (B - T) * acc / max - 6, "text-anchor": "middle", fill: css("--text") }, svg, it.text);
  });
  return { L, B, T, W, max, n };
}

function drawRoser(k) {
  const items = k.stations.map((s) => ({
    label: "S" + s.st,
    parts: [{ v: s.sole_pct, color: css("--bn") }, { v: s.shift_pct, color: css("--shift") }],
    text: Math.round(s.sole_pct + s.shift_pct) + "%",
  }));
  barChart($("roser"), items, { max: 100, tick: (v) => Math.round(v) + "%" });
  const avg = k.stations.map((s) => `S${s.st} ${fmt(s.avg_active_period_s)} s`).join(" · ");
  $("roserNote").textContent = k.bn_overall
    ? `Primary bottleneck this run: S${k.bn_overall}. Average active period: ${avg} (largest = S${k.bn_avg_method}).`
    : "Not enough data yet.";
}

function drawPareto(k) {
  const svg = $("pareto");
  const rows = k.pareto.slice(0, 5);
  if (!rows.length) {
    clear(svg);
    el("text", { x: 10, y: 40 }, svg, "No downtime in this run yet.");
    $("paretoNote").textContent = "";
    return;
  }
  const short = (r) => r.replace("Breakdown suspected at", "Breakdown").replace("Slow station", "Slow").replace(/Starved.*/, "Starved").replace(/Start-up.*/, "Start-up");
  const g = barChart(svg, rows.map((r) => ({ label: short(r.reason), parts: [{ v: r.s, color: css("--down") }], text: Math.round(r.s) + " s" })),
    { tick: (v) => Math.round(v) + "s" });
  // cumulative % line
  let d = "";
  rows.forEach((r, i) => {
    const cx = g.L + (g.W - g.L) * (i + 0.5) / g.n, cy = g.B - (g.B - g.T) * r.cum_pct / 100;
    d += (i ? "L" : "M") + cx + "," + cy;
    el("circle", { cx, cy, r: 3, fill: css("--hold") }, svg);
  });
  el("path", { d, fill: "none", stroke: css("--hold"), "stroke-width": 1.5 }, svg);
  $("paretoNote").textContent = `Total down ${fmt(k.adot_s, 0)} s. Top reason: ${rows[0].reason}. Amber line = cumulative %.`;
}

function drawMinutes(k) {
  const svg = $("minutes");
  const ms = k.minutes;
  if (!ms.length) { clear(svg); return; }
  const tgt = ms[0].target;
  const g = barChart(svg, ms.map((m) => ({ label: m.partial ? "now" : String(m.k), parts: [{ v: m.count, color: css("--accent") }] })),
    { max: Math.max(tgt * 1.2, ...ms.map((m) => m.count)) });
  const yy = g.B - (g.B - g.T) * tgt / g.max;
  el("line", { x1: g.L, x2: g.W, y1: yy, y2: yy, stroke: css("--hold"), "stroke-dasharray": "5 4", "stroke-width": 1.5 }, svg);
  el("text", { x: g.W - 70, y: yy - 5, fill: css("--hold") }, svg, `target ${fmt(tgt, 1)}/min`);
}

function renderTables(k) {
  const row = (r) => `<tr><td class="sym">${r.sym}</td><td>${r.name}</td><td class="f">${r.formula}</td><td class="v num">${r.value === null ? "-" : (typeof r.value === "number" && !Number.isInteger(r.value) ? fmt(r.value, 2) : r.value)} ${r.unit}</td></tr>`;
  const head = `<tr><th>Symbol</th><th>KPI</th><th>Formula</th><th style="text-align:right">Value</th></tr>`;
  $("kpiTable").innerHTML = head + k.kpis.map(row).join("");
  $("flowTable").innerHTML = head + k.flow.map(row).join("");
  $("stTable").innerHTML = `<tr><th>Station</th><th>Avg cycle</th><th>Min / max</th><th>Busy</th><th>Avg active period</th><th style="text-align:right">Bottleneck share</th></tr>` +
    k.stations.map((s) => `<tr><td class="sym">S${s.st}</td><td class="num">${fmt(s.ct_avg_s)} s</td><td class="num">${fmt(s.ct_min_s)} / ${fmt(s.ct_max_s)} s</td><td class="num">${Math.round(s.busy_ratio * 100)}%</td><td class="num">${fmt(s.avg_active_period_s)} s</td><td class="v num">${fmt(s.sole_pct + s.shift_pct, 0)}%</td></tr>`).join("");
}

const EV_TEXT = {
  IN: (e) => `box in (on station: ${e.val})`, OUT: (e) => e.val ? `box out, cycle ${(e.val / 1000).toFixed(1)} s` : "box out (cycle unknown)",
  GATE: (e) => e.val ? "gate opened" : "gate closed", HOLD: (e) => `gate held: WIP ${e.val} at limit`,
  BN: (e) => e.val ? `bottleneck is now S${e.val} (over buffer time)` : "no station over the buffer time", LIMIT: (e) => `WIP limit set to ${e.val || "off (S1 gate only)"}`,
  BUF: (e) => `${e.st ? "S" + e.st : "all stations"} buffer time ${e.val} s`,
  STALL: (e) => `stalled ${(e.val / 1000).toFixed(0)} s`, ERR: (e) => e.val === 1 ? "OUT without IN (check IN sensor)" : (e.val === 3 ? "S1 IN seen twice for one box, ignored" : "too many boxes (sensor noise?)"),
  LOCK: (e) => e.val ? `line locked: breakdown at ${[1, 2, 3].filter((n) => e.val & (1 << (n - 1))).map((n) => "S" + n).join(", ")}` : "breakdown cleared, line running",
  BOOT: (e) => `UNO started, limit ${e.val}`, RESET: () => "counters reset", PONG: () => "UNO answered ping", SCRAP: () => "operator marked scrap",
};
function renderLog(events) {
  $("log").innerHTML = events.map((e) => `<div><span class="t">${(e.ms / 1000).toFixed(1)}</span><span>${e.st ? "S" + e.st : "line"}</span><span class="ev">${e.ev}</span><span>${(EV_TEXT[e.ev] || (() => ""))(e)}</span></div>`).join("");
}
window.addEventListener("resize", () => state && render(state));
