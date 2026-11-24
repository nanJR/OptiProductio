#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <deque>
typedef bool boolean;
#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1
#define A0 14
#define A1 15
#define A2 16
#define A3 17
#define F(x) (x)
unsigned long g_ms = 0;
int g_pin[20];
int g_out[20];
unsigned long millis() { return g_ms; }
void pinMode(uint8_t, uint8_t) {}
int digitalRead(uint8_t p) { return g_pin[p]; }
void digitalWrite(uint8_t p, int v) { g_out[p] = v; }
void loop();
void delay(unsigned long d) { g_ms += d; }
struct Stream {
  std::deque<char> in; std::vector<std::string> out; std::string cur;
  int available() { return in.size(); }
  int read() { char c = in.front(); in.pop_front(); return c; }
  void begin(long) {}
  void println(const char* s) { out.push_back(s); }
  void print(const char* s) { cur += s; }
  void feed(const char* s) { for (const char* p = s; *p; p++) in.push_back(*p); in.push_back('\n'); }
};
struct SoftwareSerial : Stream { SoftwareSerial(int, int) {} };
Stream Serial;
struct Servo { int angle = -1; bool att = false; void attach(int) { att = true; } void write(int a) { angle = a; } void detach() { att = false; } };
struct EEPROMClass { uint8_t m[1024]; EEPROMClass() { memset(m, 0xFF, sizeof m); } uint8_t read(int a) { return m[a]; } void update(int a, uint8_t v) { m[a] = v; } } EEPROM;
