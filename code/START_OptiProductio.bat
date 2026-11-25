@echo off
setlocal EnableExtensions
title OptiProductio launcher
rem ============================================================================
rem  OptiProductio - one-click startup (Windows)
rem  Double-click this file. It lives in the "code" folder of the repo.
rem
rem  What it does for you:
rem    - finds Python, makes a venv in %LOCALAPPDATA%\OptiProductio and installs the packages (first time only)
rem    - checks the UNO sketch in this folder is v3.2 (per-station buffers)
rem    - Wi-Fi mode: starts Mosquitto with our config in its own window,
rem      shows the laptop IP for config.h, then starts the dashboard
rem    - USB mode: lists COM ports, remembers your choice, starts the dashboard
rem    - Simulator, tests, and a one-time admin setup (firewall + Mosquitto service)
rem  Close the Arduino Serial Monitor before USB mode (only one program per COM port).
rem ============================================================================

set "CODE=%~dp0"
set "LAPTOP=%CODE%laptop"
rem The venv lives outside OneDrive/Desktop so OneDrive does not sync thousands of files
set "VENV=%LOCALAPPDATA%\OptiProductio\venv"
set "PY=%VENV%\Scripts\python.exe"
set "MOSQ_CONF=%LAPTOP%\mosquitto\mosquitto.conf"
set "MOSQ_EXE=C:\Program Files\mosquitto\mosquitto.exe"
if not exist "%MOSQ_EXE%" set "MOSQ_EXE=C:\Program Files (x86)\mosquitto\mosquitto.exe"
set "PORT_FILE=%LAPTOP%\data\last_com_port.txt"

if not exist "%LAPTOP%\run.py" (
  echo [X] Cannot find laptop\run.py next to this file.
  echo     Keep START_OptiProductio.bat inside the "code" folder of the repo.
  pause & exit /b 1
)

rem ---------- 1. Python + virtual environment (first run only) ----------
if exist "%PY%" goto :have_venv
echo [..] First run: setting up Python environment. This takes 1-2 minutes.
set "BASEPY="
where py >nul 2>&1 && set "BASEPY=py -3"
if not defined BASEPY ( where python >nul 2>&1 && set "BASEPY=python" )
if not defined BASEPY (
  echo [X] Python not found. Install Python 3.11+ from python.org and tick
  echo     "Add python.exe to PATH" on the first screen. Then run this again.
  pause & exit /b 1
)
%BASEPY% -m venv "%VENV%"
if errorlevel 1 ( echo [X] Could not create the virtual environment. & pause & exit /b 1 )
"%PY%" -m pip install --upgrade pip >nul
"%PY%" -m pip install -r "%LAPTOP%\requirements.txt"
if errorlevel 1 ( echo [X] pip install failed. Is the laptop online? & pause & exit /b 1 )
echo [OK] Python environment ready.
:have_venv
"%PY%" -c "import flask, paho.mqtt, serial" >nul 2>&1
if errorlevel 1 (
  echo [..] Installing missing packages...
  "%PY%" -m pip install -r "%LAPTOP%\requirements.txt"
)
if not exist "%LAPTOP%\data" mkdir "%LAPTOP%\data"

rem ---------- 2. Is the sketch in this folder the latest? ----------
findstr /C:"line controller v3.2" "%CODE%firmware\uno_line_controller\uno_line_controller.ino" >nul 2>&1
if errorlevel 1 (
  echo.
  echo [!] The UNO sketch in this folder is NOT v3.2 ^(per-station buffers^).
  echo     Download the repo ZIP again from GitHub ^(main branch^) before the demo.
  echo.
)

:menu
echo.
echo  ==================== OptiProductio ====================
echo   1  Real line over Wi-Fi  ^(UNO - NodeMCU - Mosquitto^)   [main demo]
echo   2  Real line over USB cable                           [backup]
echo   3  Simulator, normal line   ^(no hardware^)
echo   4  Simulator, breakdown at S2, 4x speed
echo   5  Run the automatic tests
echo   6  Show laptop IP ^(for config.h^) and COM ports
echo   7  One-time admin setup ^(firewall + stop Mosquitto service^)
echo   0  Exit
echo  =======================================================
set "CH="
set /p "CH=Choose 1-7: "
if "%CH%"=="1" goto :wifi
if "%CH%"=="2" goto :usb
if "%CH%"=="3" goto :sim
if "%CH%"=="4" goto :simbd
if "%CH%"=="5" goto :tests
if "%CH%"=="6" goto :info
if "%CH%"=="7" goto :admin
if "%CH%"=="0" exit /b 0
goto :menu

rem ---------- Wi-Fi (MQTT) ----------
:wifi
if not exist "%MOSQ_EXE%" (
  echo [X] Mosquitto not installed. Get the Windows 64-bit installer from mosquitto.org/download
  echo     then run option 7 once as administrator. Use option 2 ^(USB^) meanwhile.
  pause & goto :menu
)
sc query mosquitto 2>nul | find "RUNNING" >nul
if not errorlevel 1 (
  echo [!] The Windows Mosquitto service is running. It only listens to this laptop,
  echo     so the NodeMCU cannot connect. Run this file as administrator and pick 7 once.
  pause & goto :menu
)
call :show_ip
echo     ^(this must equal MQTT_HOST in firmware\nodemcu_gateway\config.h^)
netstat -an | find ":1883 " | find "LISTENING" >nul
if errorlevel 1 (
  echo [..] Starting Mosquitto in a new window ^(keep it open^)...
  start "Mosquitto broker - keep open" "%MOSQ_EXE%" -c "%MOSQ_CONF%" -v
  timeout /t 2 /nobreak >nul
) else (
  echo [OK] Something is already listening on port 1883 ^(Mosquitto running^).
)
echo [..] Starting dashboard: http://localhost:5000   ^(Ctrl+C to stop^)
cd /d "%LAPTOP%"
"%PY%" run.py --source mqtt
pause & goto :menu

rem ---------- USB ----------
:usb
echo COM ports on this laptop:
"%PY%" -m serial.tools.list_ports -v
set "LASTPORT="
if exist "%PORT_FILE%" set /p LASTPORT=<"%PORT_FILE%"
set "COMP="
if defined LASTPORT (
  set /p "COMP=UNO port [Enter = %LASTPORT%]: "
) else (
  set /p "COMP=UNO port, e.g. COM5: "
)
if not defined COMP set "COMP=%LASTPORT%"
if not defined COMP goto :usb
> "%PORT_FILE%" echo %COMP%
echo [..] Close the Arduino Serial Monitor if it is open.
echo [..] Starting dashboard on %COMP%: http://localhost:5000   ^(Ctrl+C to stop^)
cd /d "%LAPTOP%"
"%PY%" run.py --source usb --port %COMP%
pause & goto :menu

rem ---------- Simulator ----------
:sim
echo [!] Simulator numbers are SIMULATED. Never present them as the line's results.
cd /d "%LAPTOP%"
"%PY%" run.py --source sim
pause & goto :menu
:simbd
echo [!] Simulator numbers are SIMULATED. Never present them as the line's results.
cd /d "%LAPTOP%"
"%PY%" run.py --source sim --scenario breakdown --speed 4
pause & goto :menu

rem ---------- Tests ----------
:tests
cd /d "%LAPTOP%"
"%PY%" -m pytest -q
pause & goto :menu

rem ---------- Info ----------
:info
call :show_ip
echo.
"%PY%" -m serial.tools.list_ports -v
pause & goto :menu

rem ---------- One-time admin setup ----------
:admin
net session >nul 2>&1
if errorlevel 1 (
  echo [X] Not administrator. Right-click START_OptiProductio.bat ^> "Run as administrator", then pick 7.
  pause & goto :menu
)
sc query mosquitto >nul 2>&1
if not errorlevel 1 (
  net stop mosquitto >nul 2>&1
  sc config mosquitto start= demand >nul
  echo [OK] Mosquitto Windows service stopped and set to manual.
)
netsh advfirewall firewall show rule name="Mosquitto 1883" >nul 2>&1
if errorlevel 1 netsh advfirewall firewall add rule name="Mosquitto 1883" dir=in action=allow protocol=TCP localport=1883 >nul
netsh advfirewall firewall show rule name="OptiProductio dashboard 5000" >nul 2>&1
if errorlevel 1 netsh advfirewall firewall add rule name="OptiProductio dashboard 5000" dir=in action=allow protocol=TCP localport=5000 >nul
echo [OK] Firewall open for port 1883 ^(NodeMCU^) and 5000 ^(phones can open the dashboard^).
echo     Also set the hotspot network to "Private" in Windows Wi-Fi settings.
pause & goto :menu

:show_ip
echo Laptop IPv4 addresses ^(use the Wi-Fi / hotspot one^):
ipconfig | findstr /R /C:"IPv4"
exit /b 0
