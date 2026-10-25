# OptiProductio

**Smart Production Workflow and Resource Optimization System**
IDEA Lab EL project, IEM. Team Optifiners.

OptiProductio is a small tabletop production line run by an Arduino UNO. IR sensors count parts leaving three stations, push buttons log a breakdown, an empty material bin or a rejected part, and an ultrasonic sensor watches how full the raw material bin is. The Arduino sends all of this over USB to a laptop, where a Python script saves it and a Streamlit dashboard shows the numbers a supervisor would care about: output, cycle time per station, downtime, scrap, and work in progress (WIP). If WIP goes over a cap we set, the line raises an alarm.

The dashboard can also run on a sample of the public Bosch Production Line dataset from Kaggle, so we can test it on real factory data and not only on our own model.

This is a student prototype, not a finished product.

## Folder layout

```
code/
  flowloop_line/flowloop_line.ino   Arduino sketch (sensors, buttons, LCD, buzzer, WIP alarm)
  serial_logger.py                  reads the Arduino over USB and writes CSVs into code/data/
  flowloop_metrics.py               works out the metrics (cycle time, downtime, WIP, scrap...)
  app.py                            Streamlit dashboard
  requirements.txt                  Python packages
  data/                             CSV files go here (not committed, see .gitignore)
docs/
  EL_Workflow_and_Requirements.md   our EL rules, rubric and steps
  phase1/                           Phase I deck (v1, v2) with preview PDFs, and the script that builds it
  brief/                            teammate project brief (v1) and the 3D demo-day views
  plans/                            growth roadmap (parked as future enhancement)
  research/                         research reports and the notes behind them
```

The code files still say "flowloop" in their names because that was the old project name. We kept the file names so the imports don't break.

## How to run

You need Python 3.10 or newer and the Arduino IDE.

1. **Install the Python packages**
   ```
   cd code
   pip install -r requirements.txt
   ```
2. **Upload the sketch.** Open `code/flowloop_line/flowloop_line.ino` in the Arduino IDE, install the `LiquidCrystal I2C` library from the Library Manager, pick the UNO board and port, and upload.
3. **Start the logger** (leave it running in its own terminal, from inside `code/`):
   ```
   python serial_logger.py COM3
   ```
   On Mac or Linux the port is something like `/dev/ttyACM0`. Close the Arduino Serial Monitor first, or the port will be busy.
4. **Start the dashboard** (second terminal, also inside `code/`):
   ```
   streamlit run app.py
   ```
   It opens in the browser. Pick "Live Arduino line" in the sidebar and move a part past a sensor.

### Running on the Bosch data

Download `train_date.csv` and `train_numeric.csv` from the Kaggle "Bosch Production Line Performance" competition and put them in `code/data/`. Then pick "Bosch sample" in the dashboard sidebar. The files are several GB, so they are kept out of git. The dashboard only reads the first 50,000 rows.

## Notes

- The build scripts in `docs/` (deck, brief and report PDFs) were written for our working folder and have some hard-coded paths, so check the paths before running them again.
- Docs are never overwritten. A new version is saved as v2, v3 and so on.
- Third-party documents we read for research (vendor PDFs and similar) are not in this repo. Only our own notes and reports about them are.
