#!/bin/sh
# Runs the real uno_line_controller.ino logic on a PC with fake pins, servo, EEPROM and serial.
# Needs g++ (Linux/macOS, or Windows with MSYS2/WSL). Not a replacement for testing on the table.
cd "$(dirname "$0")"
sed -e 's/#include <Servo.h>/#include "Arduino_mock.h"/' -e '/#include <SoftwareSerial.h>/d' -e '/#include <EEPROM.h>/d' \
  ../uno_line_controller.ino > sketch.cpp
g++ -std=c++17 -Wall -Wno-unused -o host_test test.cpp && ./host_test
status=$?
rm -f sketch.cpp host_test
exit $status
