# Industrial IoT platforms as references for OptiProductio: AWS IoT TwinMaker (Cookie Factory v2), PTC ThingWorx, Azure IoT Central

Research date: 2026-10-24. Sources: AWS docs and pricing pages, the aws-iot-twinmaker-samples repo (sparse git clone of `src/workspaces/cookiefactoryv2`, read directly), PTC help pages, trade press, and the local PDF `/home/claude/refdocs/Azure_IoT_Central.pdf` (cited as "Azure PDF p.N", page numbers from pdftotext page breaks).

## Q1. What is each platform, in plain words with an analogy? Core concepts and how they would model a 3-station line

### Takeaway
All three platforms do the same basic job: they hold a digital "registry" of machines, each machine described by a reusable template/type, with live sensor values attached and rules or alarms on top. TwinMaker's distinguishing feature is a 3D scene where each tag is linked to live data. ThingWorx is a low-code app builder for industrial IoT, built around Things, Thing Templates and Thing Shapes. Azure IoT Central is a ready-made SaaS-style web app: device templates, dashboards and rules, all point-and-click.

### Cited Findings

**AWS IoT TwinMaker: what it is**
- AWS: "an AWS IoT service that you can use to build operational digital twins of physical and digital systems... using measurements and analysis from a variety of real-world sensors, cameras, and enterprise applications". AWS defines a digital twin as "a live digital representation of a system... dynamically updated with data to mimic the true structure, state, and behavior of the system." — [What is AWS IoT TwinMaker?](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- Capabilities: (1) an "entity component system knowledge graph" for modelling devices, equipment, spaces and processes; (2) built-in connectors for AWS IoT SiteWise and Kinesis Video Streams, plus custom connectors; (3) a 3D "scene composer" that uses uploaded .gltf/.glb models; (4) a plug-in for Grafana / Amazon Managed Grafana for dashboards. — [What is TwinMaker](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Workspace**: the top-level container and security boundary. It is linked to an S3 bucket, and access is controlled with IAM roles. — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Entity**: a digital representation of a piece of equipment, a concept or a process. Entities can be arranged in custom hierarchies. — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Component**: provides context and data for an entity. A component is defined by a JSON document and reaches external data through a Lambda function. Built-in types are Document, Time series (e.g. SiteWise), Alarms, Video (Kinesis Video Streams) and Custom. — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Properties** come in three kinds: static single values, time-series properties (TwinMaker stores only a reference to the time-series store), and relationship properties (references to other entities, e.g. `seen_by`). They are read through a "unified data query interface". — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Scenes / nodes / tags**: a scene is a 3D view built from one or more glTF/glb models. A **tag** is "an annotation added to a specific x,y,z coordinate position of a scene" that "connects this scene part to the knowledge graph by using an entity property", and it can set appearance (e.g. alarm colour). — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- **Data connectors**: "AWS IoT TwinMaker supports first-party connectors for AWS IoT SiteWise". Other stores (Timestream, DynamoDB, Snowflake) require Lambda connectors that implement the TwinMaker data connector interface. — [Data connector interface](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/data-connector-interface.html)
- Two kinds of data source: hierarchy connectors (sync an external model) and time-series connectors. — [What is TwinMaker](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- AWS says TwinMaker "should not be used as a substitute for human monitoring of physical systems" in safety-critical settings. — [same](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)

**Cookie Factory v2 sample: what it builds** (read from the cloned repo, [cookiefactoryv2 folder](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2))
- The README title is "Bakersville Cookie Factory Digital Twin Monitoring Application powered by AWS IoT TwinMaker". — [README](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)
- The app is a **React web app built on iot-app-kit** (folder `CookieFactoryDemo/`, served at `https://localhost:8080` with `npm run dev`). It does not use Grafana. Grafana is used by the original (v1) Cookie Factory getting-started sample. — [repo root README](https://github.com/aws-samples/aws-iot-twinmaker-samples) ("For a sample Digital Twin application built with a React application on iot-app-kit check out CookieFactoryV2"; the v1 getting-started sample ends with "the following dashboard running in Grafana")
- Folder structure:
  - `tmdt_project/`: TwinMaker Development Tools project. It holds `tmdt.json`, 10 component-type JSONs, `entities.json`, and 2 scenes (`CookieFactory.json`, `Mixer.json`), and references 4 glb models (environment, mixer, line, water tank).
  - `cdk/`: AWS CDK (TypeScript) stack, Lambda data connectors (`synthetic_replay_connector/`, Timestream reader), and a custom-resource handler.
  - `CookieFactoryDemo/`: the React app.
  - `COGNITO_SAMPLE_SETUP_CONSOLE.md`.
  - Source: [cookiefactoryv2](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)
- **Entities**: `entities.json` has 132 entities, arranged as a hierarchy of Factory, Spaces (offices, warehouse rooms), Equipment, Mixers (Mixer_0 to Mixer_24) and cookie lines. Line equipment includes COOKIE_FORMER, FREEZER_TUNNEL, VERTICAL_CONVEYOR, CONVEYOR_STRAIGHT/LEFT_TURN/RIGHT_TURN, PLASTIC_LINER, BOX_ERECTOR, LABELING_BELT and BOX_SEALER, each a child of a COOKIE_LINE entity. — [entities.json](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/tmdt_project)
- **Components**: line machines carry `CookieLineComponent` + `EquipmentComponent`, and mixers carry `AlarmComponent` + `MixerComponent` + `SpecSheets`. Component type `com.example.cookiefactory.cookieline` extends `com.amazon.iottwinmaker.alarm.basic` and `com.example.synthetic-telemetry`. Its time-series properties are `Speed`, `Temperature`, `AlarmMessage`, `alarm_status` and `Resources` (map, e.g. Dough, Boxes, Tape). `com.example.cookiefactory.processstep` has a `flowTo` list property, which encodes the process-flow order between steps. — [tmdt_project](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/tmdt_project)
- **Simulated data**: the `syntheticDataUDQ` Lambda (`synthetic_udq_reader.py`) loads a JSON-lines file (`demoTelemetryData.json`, `telemetryData.json` or `allAlarmTelemetryData.json`) into pandas and replays it as time series at a default 10 s interval. Example row: `{"Speed":6,"Temperature":30,"Alarm Message":"Normal","Resources":{"Dough":120},"Alarming":false,"Name":"cookieFormer"}`. A second Lambda reads a Timestream table loaded from `telemetry.csv`, and two sample MKV videos are pushed to Kinesis Video Streams for the mixer-room cameras. — [cdk/ and tmdt.json](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)
- **Alarms**: modelled as properties (`alarm_status`, `AlarmMessage`) on component types that extend the built-in `com.amazon.iottwinmaker.alarm.basic`. They are not a separate rules engine; the replayed data file contains the alarm states. — [component types](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/tmdt_project)
- **Knowledge graph demo**: the README verifies the deployment with an `execute-query` graph query (`MATCH (cookieLine)<-[:isChildOf]-(processStepParent)<-[:isChildOf]-(processStep)-[r1]-(e)-[r2]-(equipment)`). — [README](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)
- **Deployment**:
  - Prerequisites: an AWS account and CLI, Node 16+, AWS CDK ≥ 2.76 (`cdk bootstrap`), and Docker 20+. The sample runs only in us-east-1, us-west-2 or eu-west-1.
  - Steps: create a TwinMaker workspace in the console (auto-create the S3 bucket and IAM role), then `cdk deploy --context stackName="CookieFactoryDemo" ...`.
  - Next, set the Cognito user's password, fill in `sites.ts`, `cognito.ts` and `users.ts`, and run `npm run dev`.
  - Cleanup is `cdk destroy`, then deleting the workspace and S3 bucket (or `tmdt destroy`).
  - Source: [README](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)
- The CDK stack creates TwinMaker component types, entities and scenes; S3 assets; Cognito UserPool/IdentityPool/user; a Timestream database and table; 3 Python Lambdas (custom resource with an OpenCV layer, Timestream reader, synthetic data reader); and IAM roles. — [cookiefactory_v2_stack.ts](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/cdk/lib)

**PTC ThingWorx**
- "Things are representations of physical devices, assets, products, systems, people, or processes". "It is a best practice to create a Thing Template to describe a Thing". A Thing "can inherit other properties, services, events, and subscriptions from its Thing Template and Thing Shapes". Thing data is used in "applications, reports, and mashups". — [ThingWorx Help: Things](https://support.ptc.com/help/thingworx_hc/thingworx_8_hc/en/ThingWorx/Help/Composer/Things/Things.html)
- A Thing Shape is "a set of characteristics represented as properties, services, events, and subscriptions". A Thing Template can implement one or more Thing Shapes (compared to multiple inheritance in C++), and changes to a shape propagate to the Templates and Things that implement it. — [ThingWorx Help: Thing Shapes](https://support.ptc.com/help/thingworx/platform/r9/en/ThingWorx/Help/Composer/ThingShapes.html)
- Data Shapes (table/record schemas) are also a core concept. — [ThingWorx 9.5 Help: Data Shapes](https://support.ptc.com/help/thingworx/platform/r9.5/en/ThingWorx/Help/Composer/DataShapes.html)
- The assigned PTC Welcome page (`.../index.html#page/ThingWorx/Welcome.html`) is a JavaScript shell. Fetching it returned no content.

**Azure IoT Central**
- "IoT Central is an application platform as a service (aPaaS) that reduces the burden and cost of developing, managing, and maintaining cloud-based IoT solutions." Its web UI lets users "connect devices, monitor device telemetry, create rules, and manage devices". — Azure PDF p.4 (Microsoft Learn "What is Azure IoT Central?", dated 05/09/2025)
- **Device template**: "the blueprint that defines the characteristics and behavior of a type of device". It covers telemetry, properties (read-only device properties, writable properties, cloud/business properties), commands, plus views and forms. — Azure PDF p.5
- **Dashboards**: use a prebuilt dashboard or build custom ones, shared or private. **Rules and actions**: custom rules on device state and telemetry, with actions to notify people. **Jobs**: bulk property updates and commands. **Data export** and **REST API** for integration. — Azure PDF p.6–7, p.25
- Rule example (quickstart): target devices by device template, set a telemetry condition with time aggregation (e.g. 5-minute minimum of Acceleration/Z < −9), and add an email action. — Azure PDF p.35–36
- Application templates: generic, Retail, Energy, Government, Healthcare. — Azure PDF p.4

### Inferences
- Plain-language analogies (mine):
  - **TwinMaker** is like a "Google Maps for a factory". There is a 3D map of the plant, every pin (tag) on it is bound to a live reading, and a database of who-is-inside-what (knowledge graph) sits behind it.
  - **ThingWorx** is like LEGO for industrial apps. You define a brick type once (Thing Shape/Template), stamp out many machines (Things), and snap screens together (Mashups).
  - **IoT Central** is like a pre-furnished rental flat. Plug devices in and the dashboard, rules and email alerts are already there; you just arrange the furniture.
- Modelling the 3-station OptiProductio line in each platform:
  - **TwinMaker**:
    - Entities `Line_1`, then `Station_1/2/3` and `Buffer_1-2`, `Buffer_2-3` as children.
    - A custom component type `optiproductio.station` with time-series properties `count`, `cycle_time_s`, `state` and `alarm_status`, plus a `flowTo` relationship. This copies the cookie factory's `processstep.flowTo`.
    - A `line` component with `wip`, `throughput` and `oee_proxy`, plus a CONWIP alarm extending `alarm.basic`.
    - A scene built from a glb export of the three.js model, with one tag per station.
  - **ThingWorx**:
    - A Thing Shape `CountingStation` (properties count/cycleTime/state, service `ResetCount`, event `CycleComplete`) and a Thing Template `StationTemplate`.
    - Things `Station1..3`, plus a `Line1` Thing with WIP/throughput properties and a subscription that fires an alert when WIP > cap.
    - A Mashup as the dashboard.
  - **IoT Central**:
    - One device template `ArduinoStation` (telemetry: count, cycle_time; property: state; command: reset) and 3 devices.
    - A dashboard with tiles, and a rule "WIP > cap", which would need WIP computed and sent as telemetry from a line-level device or gateway.
- Every platform uses the same "type, then instance" pattern (component type → entity; Thing Template/Shape → Thing; device template → device). OptiProductio can copy this idea in plain Python, e.g. a `StationType` dataclass with one instance per station.

### Gaps
- No primary PTC page was retrieved that defines Mashups, Value Streams, Alerts, Kepware or ThingWorx Analytics. Treat these one-line descriptions as my background knowledge, not cited facts: Mashups are drag-and-drop web UIs; Kepware (KEPServerEX) is an OPC/industrial-protocol connectivity server; ThingWorx Analytics is an ML add-on.
- The Cookie Factory v2 README contains no screenshot description beyond `docs/MonitoringApplication.png`, so the exact React UI panels were not verified.

## Q2. Can a student use them for free? Any retirement or deprecation?

### Takeaway
**Azure IoT Central can no longer be created by new users.** New application creation stopped on 23 Sept 2026, and existing apps shut down after 20 Sept 2029, so it is a reference only. **AWS IoT TwinMaker** is still offered and I found no end-of-support notice. It has a 12-month free tier for API calls but needs a credit-card AWS account. Its Cookie Factory sample pulls in several billable services, and **AWS IoT Events** (an older AWS alarm service) reached end of support on 20 May 2026. **ThingWorx** is still sold, but PTC sold it (with Kepware) to TPG; the deal was announced Nov 2025 and completed by March 2026. Free student access exists only through old trial and academic channels whose current status I could not confirm.

### Cited Findings

**Azure IoT Central: retirement (confirmed)**
- "On September 23, 2026, Microsoft announced guidance that helps Azure IoT Central customers migrate their solutions to use new features of Azure IoT Hub and Microsoft Fabric... Existing users can continue using their Azure IoT Central solution as-is until September 20, 2029". — Azure PDF p.9 ("Azure IoT Central is evolving", last updated 09/23/2026, p.12)
- Key dates: "New Azure IoT Central application creation is unavailable starting September 23, 2026. Existing Azure IoT Central applications continue to work as-is through September 20, 2029. After September 20, 2029, Azure IoT Central applications are no longer available." — Azure PDF p.10
- Recommended replacement: Azure IoT Hub + Device Provisioning Service + Microsoft Fabric Real-Time Intelligence / Power BI, with Azure Device Registry (in preview) and Event Grid / Functions / Logic Apps / Fabric Activator for rules. — Azure PDF p.10. Migration playbook: https://aka.ms/AzureIoTCentralMigrationPlaybook, guidance: https://aka.ms/AzureIoTCentralEvolution (Azure PDF p.11–12)
- Pricing (historical): per-device Standard 0/1/2 plans, "with the first two devices being free". — Azure PDF p.4. The quickstart used the Standard 2 plan (Azure PDF p.28) and required an Azure subscription ("Create an account for free", Azure PDF p.27).
- I did not run a separate online search for the retirement notice. The PDF is itself the Microsoft Learn export dated 09/23/2026 and carries the notice above.

**AWS IoT TwinMaker: status and pricing**
- No end-of-support or availability-change notice was found:
  - neither the TwinMaker user guide "What is" page nor the data-connector page carries a banner — [What is TwinMaker](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md), [Data connector interface](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/data-connector-interface.html);
  - the pricing page "contains no end-of-support notice" — [TwinMaker pricing](https://aws.amazon.com/iot-twinmaker/pricing/);
  - two searches ("end of support", "no longer open to new customers", "availability change 2025 2026") returned only GA-era (2022) articles for TwinMaker.
- Contrast with related AWS IoT services that were retired: "AWS IoT Events will no longer accept new customers beginning May 20, 2025" and "On May 20, 2026, AWS will end support for AWS IoT Events". — [IoT Events end of support](https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-end-of-support.html). The searches also surfaced end-of-support / availability-change pages for AWS IoT Analytics and AWS IoT FleetWise ([IoT Analytics migration guide](https://docs.aws.amazon.com/iotanalytics/latest/userguide/mig-guide.html), [FleetWise availability change](https://docs.aws.amazon.com/ja_jp/iot-fleetwise/latest/developerguide/iotfleetwise-availability-change.html)), but I did not open them.
- Pricing:
  - Free tier: 50 million data-access API calls/month free for the first 12 months. New customers from 15 July 2025 also get up to $200 in Free Tier credits, usable within 12 months.
  - Standard plan: $0.05 per entity per month, $1.50 per million unified data-access API calls (each up to 20 KB), and $0.50 per 10K knowledge-graph queries.
  - A tiered bundle requires a 3-month commitment (pricing examples: $220/month for 800 entities, $650/month for 5,000).
  - Source: [TwinMaker pricing](https://aws.amazon.com/iot-twinmaker/pricing/)
- The Cookie Factory v2 deployment also creates Timestream, Kinesis Video Streams (two camera streams), Lambda, Cognito and S3 resources, and needs Docker and CDK bootstrap. It is region-locked to us-east-1, us-west-2 or eu-west-1, so there is no Mumbai region. — [cookiefactoryv2 README and CDK stack](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2)

**PTC ThingWorx: ownership and access**
- TPG agreed to buy Kepware and ThingWorx from PTC for up to $725M in cash ($565M or $600M upfront plus a $125M earn-out). The deal was reported in early November 2025, with closing expected in H1 2026. TPG plans to combine them with GE Vernova's Proficy business. — [RCR Wireless, 11 Nov 2025](https://www.rcrwireless.com/20251111/internet-of-things/ptc-sells-kepware-thingworx)
- ARC Advisory (17 Mar 2026): PTC "has completed the sale". PTC received $523M cash at closing (about $375M net after tax and costs). — [ARC Advisory](https://www.arcweb.com/blog/ptc-completes-sale-kepware-thingworx-tpg)
- Trial: a PTC support article titled "Where to find free trial versions of ThingWorx Foundation" applies to ThingWorx 8.3–9.5 and was last modified 27-Apr-2022. It does not state the duration or current availability. — [PTC CS323525](https://www.ptc.com/en/support/article/CS323525). PTC Community posts refer to a "120-day Trial ThingWorx" download for education — [PTC Education Forum](https://community.thingworx.com/t5/PTC-Education-Forum/Downloading-and-Deploying-120-day-Trial-ThingWorx-pdf/m-p/533470/highlight/true) (not opened; title only).
- Education:
  - "Educator Extension for ThingWorx" gave educators a multi-tenant ThingWorx instance for themselves and "up to 100 students", plus courseware and Raspberry Pi projects. That article is from July 2017 and does not say whether access is free. — [Studica blog, 21 Jul 2017](https://www.studica.com/blog/educator-extension-thingworx/)
  - In 2015 PTC said 200+ universities offered its IoT Academic Program. — [PTC investor news, 2015](https://investor.ptc.com/resources/news/news-details/2015/Over-200-Global-Universities-and-Colleges-Now-Offer-the-PTC-Internet-of-Things-Academic-Program/default.aspx) (title only)

### Inferences
- For a first-year student in Oct 2026:
  - **IoT Central** is effectively closed to them, since new apps cannot be created.
  - **TwinMaker** is technically usable. A 5–6 entity model would cost about $0.25–0.30/month in entity fees, with API calls inside the free tier. But it needs an AWS account with a card, and the full Cookie Factory sample spins up paid side services (Timestream, KVS video, Lambda) in US/EU regions. The real risk is a forgotten resource running up a bill, so run `cdk destroy` right after the demo.
  - **ThingWorx** free access depends on the old trial or academic routes still working after the TPG sale. The student would have to ask PTC/TPG or the RVCE department directly.
- The retirements of IoT Events (2026) and IoT Central (creation stopped 2026), and the ThingWorx divestiture, all point the same way. Big vendors are pulling back from turnkey industrial IoT application platforms toward lower-level building blocks. That makes deep investment in any one of them risky for a short student project.

### Gaps
- No primary AWS statement confirms TwinMaker's long-term roadmap. "No notice found" is not a guarantee of continuity.
- Exact Azure IoT Central per-device prices and free-trial terms were not checked; they are moot for new users.
- Current (post-TPG) ThingWorx trial or academic licence terms are unknown. The PTC pages found are from 2017–2022.
- Whether Amazon Timestream (used by the sample) is still open to new customers was not verified in this session.

## Q3. What can OptiProductio borrow, and is it worth actually using one versus open-source equivalents?

### Takeaway
Borrow the ideas, not the platforms. The four worth copying:
1. A typed data model (station type → station instances, with a `flowTo` link).
2. Alarm-as-a-property (`alarm_status` + `alarm_message` per station and for the line).
3. 3D tags bound to live data (colour a station in three.js from the latest reading).
4. A replay/simulator data source like the cookie factory's synthetic connector, for demos when the Arduino isn't plugged in.

Actually deploying TwinMaker is optional "wow" work that adds cost and complexity for little learning gain. IoT Central is closed to new users, and ThingWorx access is uncertain.

### Cited Findings
- The Cookie Factory models process order with a `processstep` component whose `flowTo` property is a list, and models machine telemetry (`Speed`, `Temperature`, `Resources`) plus `alarm_status`/`AlarmMessage` on each line machine. — [tmdt_project component types](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/tmdt_project)
- Its synthetic connector replays a JSON-lines file through pandas at a fixed interval (default 10 s), which is a ready pattern for a demo/replay mode. — [synthetic_udq_reader.py](https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2/cdk/synthetic_replay_connector)
- TwinMaker scene tags bind an x,y,z point in a glTF/glb scene to an entity property and can change appearance for alarms. Scenes require glTF/glb models. — [What is TwinMaker](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.md)
- IoT Central rules use time aggregation (e.g. a 5-minute window) to avoid alert spam: "you receive a maximum of one email for each device every five minutes". — Azure PDF p.36
- ThingWorx's shape/template inheritance means one change to a shape propagates to every Thing. — [Thing Shapes](https://support.ptc.com/help/thingworx/platform/r9/en/ThingWorx/Help/Composer/ThingShapes.html)
- The Cookie Factory v2 front end is built on the open-source iot-app-kit, a React component library. — [repo README](https://github.com/aws-samples/aws-iot-twinmaker-samples)

### Inferences
- Concrete borrowings for OptiProductio:
  - **Data model**: a `stations.json`/YAML config listing `{id, name, type, flow_to, sensor_pin, ideal_cycle_time}`, plus a `line` object with `wip_cap`. The Streamlit dashboard and the three.js model both read this one file, the way TwinMaker's `entities.json` feeds both the app and the scene.
  - **Alarm states**: a per-station `state` (RUNNING/IDLE/BLOCKED/STARVED) and a line-level `alarm_status` (NORMAL/ACTIVE) for the CONWIP cap, each with a message string. Hold for N seconds (debounce) before raising an alarm, after IoT Central's time aggregation.
  - **3D scene linked to live data**: the existing three.js model can poll a small JSON endpoint (or a file written by the Python logger) and recolour each station mesh: green running, amber idle/starved, red alarm. This is the TwinMaker "tag" idea without AWS. three.js can also export glb if they ever do want TwinMaker.
  - **Replay mode**: log Arduino serial data to CSV, and add a "replay" toggle that streams the CSV into the dashboard, as the synthetic connector does. This is useful for viva demos.
- Open-source equivalents, if they want a "real platform" feel:
  - Node-RED or a plain Python serial reader;
  - an MQTT broker (Mosquitto);
  - InfluxDB/SQLite for time series;
  - Grafana for dashboards and alert rules;
  - Eclipse Ditto as the "digital twin registry".
  
  I did not research these in this session; they are background knowledge for the report writer to verify.
- Is it worth using TwinMaker? Probably only as a stretch demo, and only if a mentor supplies an AWS account. Running the Cookie Factory sample once (then destroying it) would let the student see a real industrial digital twin and screenshot it for the report. Porting OptiProductio onto it would mean writing a Lambda connector, uploading data to AWS, and learning IAM, CDK and Cognito, which is a large overhead for a first-year EL project. The learning outcomes the course likely rewards (OEE, CONWIP, Little's Law) live in the Python logic, not in the platform.
- For the report, cite these platforms as "industry analogues": the student's line is a miniature version of what Cookie Factory models (stations → equipment entities, conveyors → flowTo, alarms → alarm_status).

### Gaps
- No cost estimate for running the full Cookie Factory v2 stack for a day; it depends on Timestream, KVS and Lambda pricing, which were not looked up.
- I did not evaluate whether iot-app-kit components can be used without TwinMaker or SiteWise backends.
