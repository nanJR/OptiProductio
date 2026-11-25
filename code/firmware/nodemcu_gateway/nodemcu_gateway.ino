/*
  OptiProductio - NodeMCU ESP8266 IIoT gateway
  Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection

  Job: a "translator" between the UNO and the laptop.
    UNO text line  --(SoftwareSerial 19200, D5)-->  NodeMCU  --(Wi-Fi, MQTT)-->  Mosquitto on the laptop
    laptop command --(MQTT)--> NodeMCU --(D6)--> UNO

  Topics (ISA-95 style: enterprise/site/line/cell):
    rvce/idealab/line1/s1/event   {"seq":12,"ms":34567,"st":1,"ev":"IN","val":1}
    rvce/idealab/line1/line/event events for the whole line (GATE, HOLD, BN, LIMIT, BOOT...)
    rvce/idealab/line1/status     {"seq":..,"ms":..,"wip":3,"limit":4,"gate":0,"occ":[1,0,1],"bn":1,"released":20,"done":17,"buf":10}
    rvce/idealab/line1/gateway/state  "online" / "offline" (retained, offline is the Last Will)
    rvce/idealab/line1/gateway/stats  {"rssi":-55,"lines":1234,"bad":0,"up_s":600}
  Commands it listens to:
    rvce/idealab/line1/cmd/wip_limit   payload "4"  -> sends "L,4" to the UNO
    rvce/idealab/line1/cmd/buffer      payload "15" -> sends "B,15" (all stations 15 s);
                                       payload "20015" -> "B,20015" = station 2 only, 15 s (UNO v3.2 splits it)
    rvce/idealab/line1/cmd/reset       any payload  -> sends "R"
    rvce/idealab/line1/cmd/ping        any payload  -> sends "P"

  Board: "NodeMCU 1.0 (ESP-12E Module)" from the ESP8266 board package (esp8266 by ESP8266 Community).
  Library: PubSubClient by Nick O'Leary (Library Manager). SoftwareSerial comes with the ESP8266 package.
  Edit config.h first.
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>
#include "config.h"

SoftwareSerial uno;               // RX = D5 (GPIO14), TX = D6 (GPIO12)
WiFiClient net;
PubSubClient mqtt(net);

char lineBuf[100];
uint8_t lineLen = 0;
unsigned long linesOk = 0, linesBad = 0;
unsigned long lastMqttTry = 0, lastStats = 0, lastBlink = 0;
String root = TOPIC_ROOT;
char clientId[32];

// ---------- MQTT -> UNO ----------
void onMqtt(char* topic, byte* payload, unsigned int length) {
  char msg[16];
  unsigned int n = length < sizeof(msg) - 1 ? length : sizeof(msg) - 1;
  memcpy(msg, payload, n);
  msg[n] = 0;
  String t = topic;
  if (t.endsWith("/cmd/wip_limit")) {
    int limit = atoi(msg);
    uno.print("L,"); uno.println(limit);
    Serial.printf("cmd -> UNO: L,%d\n", limit);
  } else if (t.endsWith("/cmd/buffer")) {
    long b = atol(msg);
    uno.print("B,"); uno.println(b);
    Serial.printf("cmd -> UNO: B,%ld\n", b);
  } else if (t.endsWith("/cmd/reset")) {
    uno.println("R");
    Serial.println("cmd -> UNO: R");
  } else if (t.endsWith("/cmd/ping")) {
    uno.println("P");
  }
}

bool connectMqtt() {
  String willTopic = root + "/gateway/state";
  bool ok;
  if (strlen(MQTT_USER) > 0)
    ok = mqtt.connect(clientId, MQTT_USER, MQTT_PASSWORD, willTopic.c_str(), 1, true, "offline");
  else
    ok = mqtt.connect(clientId, willTopic.c_str(), 1, true, "offline");
  if (ok) {
    mqtt.publish(willTopic.c_str(), "online", true);
    mqtt.subscribe((root + "/cmd/#").c_str(), 1);
    Serial.println("MQTT connected");
  } else {
    Serial.printf("MQTT failed, state %d (is Mosquitto running and the IP in config.h right?)\n", mqtt.state());
  }
  return ok;
}

// ---------- UNO -> MQTT ----------
// split "a,b,c" in place; returns the number of fields
uint8_t splitCsv(char* s, char* fields[], uint8_t maxFields) {
  uint8_t n = 0;
  fields[n++] = s;
  for (char* p = s; *p && n < maxFields; p++) {
    if (*p == ',') { *p = 0; fields[n++] = p + 1; }
  }
  return n;
}

void handleLine(char* line) {
  Serial.println(line);                       // echo for debugging in the Serial Monitor
  if (line[0] == '#' || line[0] == 0) return;
  char copy[100];
  strncpy(copy, line, sizeof(copy));
  copy[sizeof(copy) - 1] = 0;
  char* f[14];
  uint8_t n = splitCsv(copy, f, 14);
  char json[200];
  String topic;

  if (f[0][0] == 'E' && n == 6) {
    int stn = atoi(f[3]);
    snprintf(json, sizeof(json), "{\"seq\":%s,\"ms\":%s,\"st\":%d,\"ev\":\"%s\",\"val\":%s}",
             f[1], f[2], stn, f[4], f[5]);
    topic = root + (stn == 0 ? String("/line") : String("/s") + stn) + "/event";
    // the hardware test sketch pings us: answer so the UNO side can see the link works
    if (strcmp(f[4], "PONG") == 0) {
      uno.printf("# gw ok wifi=%d mqtt=%d ip=%s\n", WiFi.status() == WL_CONNECTED,
                 mqtt.connected(), WiFi.localIP().toString().c_str());
    }
  } else if (f[0][0] == 'S' && (n == 12 || n == 13)) {
    // n == 13: firmware v3 adds the buffer time (s) as the last field
    snprintf(json, sizeof(json),
             "{\"seq\":%s,\"ms\":%s,\"wip\":%s,\"limit\":%s,\"gate\":%s,\"occ\":[%s,%s,%s],\"bn\":%s,\"released\":%s,\"done\":%s%s%s}",
             f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11],
             n == 13 ? ",\"buf\":" : "", n == 13 ? f[12] : "");
    topic = root + "/status";
  } else {
    linesBad++;
    return;
  }
  linesOk++;
  if (mqtt.connected()) mqtt.publish(topic.c_str(), json, topic.endsWith("/status"));
}

void readUno() {
  while (uno.available()) {
    char c = uno.read();
    if (c == '\n') {
      lineBuf[lineLen] = 0;
      if (lineLen > 0 && lineBuf[lineLen - 1] == '\r') lineBuf[lineLen - 1] = 0;
      handleLine(lineBuf);
      lineLen = 0;
    } else if (lineLen < sizeof(lineBuf) - 1) {
      lineBuf[lineLen++] = c;
    } else {
      lineLen = 0;                            // garbage or a lost newline: start again
      linesBad++;
    }
  }
}

void setup() {
  Serial.begin(115200);
  uno.begin(UNO_BAUD, SWSERIAL_8N1, 14, 12, false, 256);  // 14 = D5 (RX), 12 = D6 (TX); numbers work on any ESP8266 board setting
  pinMode(LED_BUILTIN, OUTPUT);
  snprintf(clientId, sizeof(clientId), "optiproductio-gw-%06x", ESP.getChipId());

  Serial.printf("\nOptiProductio gateway, connecting to Wi-Fi \"%s\"\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 20000) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    delay(250);
  }
  if (WiFi.status() == WL_CONNECTED)
    Serial.printf("Wi-Fi OK, my IP %s, RSSI %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  else
    Serial.println("Wi-Fi not connected yet, will keep trying (check SSID, password, 2.4 GHz)");

  net.setTimeout(2000);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqtt);
  mqtt.setKeepAlive(10);
  mqtt.setSocketTimeout(3);
}

void loop() {
  readUno();

  if (WiFi.status() == WL_CONNECTED) {
    if (!mqtt.connected() && millis() - lastMqttTry > 3000) {
      lastMqttTry = millis();
      connectMqtt();
    }
    mqtt.loop();
  }

  // on-board LED: solid = MQTT OK, slow blink = Wi-Fi only, fast blink = no Wi-Fi (LED is active LOW)
  unsigned long period = mqtt.connected() ? 0 : (WiFi.status() == WL_CONNECTED ? 1000 : 200);
  if (period == 0) digitalWrite(LED_BUILTIN, LOW);
  else if (millis() - lastBlink > period) { lastBlink = millis(); digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN)); }

  if (mqtt.connected() && millis() - lastStats > 10000) {
    lastStats = millis();
    char json[100];
    snprintf(json, sizeof(json), "{\"rssi\":%d,\"lines\":%lu,\"bad\":%lu,\"up_s\":%lu}",
             WiFi.RSSI(), linesOk, linesBad, millis() / 1000);
    mqtt.publish((root + "/gateway/stats").c_str(), json);
  }
}
