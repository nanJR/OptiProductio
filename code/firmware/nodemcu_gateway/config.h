// OptiProductio NodeMCU gateway settings. EDIT THESE before you flash.

// Phone hotspot (must be 2.4 GHz; the ESP8266 cannot see 5 GHz networks)
#define WIFI_SSID      "OptiProductio-Hotspot"
#define WIFI_PASSWORD  "change-me"

// Laptop that runs Mosquitto. Find its IP on the hotspot with `ipconfig` (Windows)
// and look for "IPv4 Address" under the Wi-Fi adapter, for example 192.168.43.25
#define MQTT_HOST      "192.168.43.25"
#define MQTT_PORT      1883
#define MQTT_USER      ""            // leave "" if Mosquitto allows anonymous clients
#define MQTT_PASSWORD  ""

// ISA-95 style topic root: enterprise / site / line
#define TOPIC_ROOT     "rvce/idealab/line1"

// UNO link (SoftwareSerial). Must match GW_BAUD in the UNO sketch.
#define UNO_BAUD       19200
