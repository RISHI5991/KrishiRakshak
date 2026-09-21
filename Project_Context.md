This is the Project structure that we are aiming at for this project folder:

&nbsp;

Dhurandhar/

│

├── README.md

├── LICENSE

├── CONTRIBUTING.md

├── .gitignore

├── .gitattributes

│

├── docs/

│   ├── architecture/

│   │   ├── system-architecture.md

│   │   ├── ml-architecture.md

│   │   ├── hardware-architecture.md

│   │   ├── software-architecture.md

│   │   └── data-flow.md

│   │

│   ├── api/

│   │   └── api-reference.md

│   │

│   ├── hardware/

│   │   ├── wiring.md

│   │   ├── pinout.md

│   │   └── communication-protocol.md

│   │

│   └── research/

│       ├── experiments.md

│       └── benchmarks.md

│

├── apps/

│   │

│   ├── android/

│   │   └── farm-assistant/

│   │

│   └── web/

│       ├── frontend/

│       └── README.md

│

├── services/

│   │

│   └── flask-api/

│       ├── app.py

│       ├── config.py

│       ├── requirements.txt

│       │

│       ├── inference/

│       │   ├── crop\_handler.py

│       │   ├── disease\_handler.py

│       │   ├── pest\_handler.py

│       │   ├── irrigation\_handler.py

│       │   └── nutrient\_handler.py

│       │

│       ├── routes/

│       │   ├── health.py

│       │   ├── analyze.py

│       │   ├── plant.py

│       │   ├── pest.py

│       │   └── irrigation.py

│       │

│       ├── schemas/

│       │   └── responses.json

│       │

│       ├── templates/

│       ├── static/

│       └── tests/

│

├── ml/

│   │

│   ├── crop/

│   │   ├── training/

│   │   ├── evaluation/

│   │   ├── inference/

│   │   └── README.md

│   │

│   ├── disease/

│   │   ├── training/

│   │   ├── evaluation/

│   │   ├── inference/

│   │   └── README.md

│   │

│   ├── pest/

│   │   ├── src/

│   │   ├── training/

│   │   ├── evaluation/

│   │   ├── export/

│   │   └── README.md

│   │

│   ├── irrigation/

│   │   ├── training/

│   │   ├── evaluation/

│   │   ├── inference/

│   │   ├── embedded/

│   │   └── README.md

│   │

│   └── nutrient/

│       ├── training/

│       ├── evaluation/

│       ├── inference/

│       └── README.md

│

├── hardware/

│   │

│   ├── esp32-cam/

│   │   ├── firmware/

│   │   ├── camera/

│   │   ├── networking/

│   │   └── README.md

│   │

│   ├── esp32-s3/

│   │   ├── firmware/

│   │   ├── sensors/

│   │   ├── control/

│   │   └── README.md

│   │

│   ├── esp32-wroom/

│   │   ├── firmware/

│   │   ├── motor-control/

│   │   ├── pump-control/

│   │   └── README.md

│   │

│   └── schematics/

│       ├── wiring/

│       ├── pinouts/

│       └── diagrams/

│

├── shared/

│   ├── api-contracts/

│   ├── json-schemas/

│   ├── uart-protocol/

│   └── constants/

│

├── datasets/

│   └── README.md

│

├── models/

│   └── README.md

│

├── scripts/

│   ├── setup.sh

│   ├── run-server.sh

│   ├── test-all.sh

│   └── export-models.sh

│

└── .github/

&nbsp;&nbsp;&nbsp;&nbsp;├── workflows/

&nbsp;&nbsp;&nbsp;&nbsp;│   ├── android.yml

&nbsp;&nbsp;&nbsp;&nbsp;│   ├── flask.yml

&nbsp;&nbsp;&nbsp;&nbsp;│   └── tests.yml

&nbsp;&nbsp;&nbsp;&nbsp;│

&nbsp;&nbsp;&nbsp;&nbsp;├── ISSUE\_TEMPLATE/

&nbsp;&nbsp;&nbsp;&nbsp;└── pull\_request\_template.md

&nbsp;

&nbsp;

And this is for github push

&nbsp;

This was OUR solution to the problem

&nbsp;

We were making a hardware \+ software solution that had a hardware bot and 5 edge ml models

&nbsp;

Now about the hardware bot:

It had 1 ESP 32 S3 N16R8, 1 ESP 32 WROOM, 1 ESP 32 CAM Module, 1 L298N Motor Driver, 4 BO Motors connected to 4 wheels and 1 Capacitive Soil Moisture v2.0 sensor, 1 LDR Sensor, 1 DHT22 Sensor, 1 Rain sensor.

&nbsp;

And about the software part:

&nbsp;

We have 5 ML Models

M1: Crop Detection Model

M2: Crop Disease Detection Model

M3: Pest detection model

M4: Nutrient Model

M5: Irrigation Model

&nbsp;

And we have the working as such:

&nbsp;

\#\# Dhurandhar — Complete Working Flow

&nbsp;

1\. \*\*Robot enters the field\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* Dhurandhar moves through the agricultural field using its motorized chassis.

&nbsp;&nbsp;&nbsp;\* The \*\*ESP32-S3\*\* coordinates the overall embedded system.

&nbsp;&nbsp;&nbsp;\* The \*\*ESP32-WROOM\*\* handles low-level hardware actuation.

&nbsp;

2\. \*\*Primary field vision\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The \*\*ESP32-CAM is the primary autonomous vision interface\*\*.

&nbsp;&nbsp;&nbsp;\* It captures images of crops, leaves, pests and other relevant field observations.

&nbsp;&nbsp;&nbsp;\* This allows the robot to operate without requiring a human with a phone.

&nbsp;

3\. \*\*Environmental and soil sensing\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The robot simultaneously collects physical measurements such as:

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Soil moisture

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Temperature

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Humidity

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Rain

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Light

&nbsp;&nbsp;&nbsp;\* These measurements provide environmental context for agricultural decisions.&nbsp;

&nbsp;

4\. \*\*Data enters the AI pipeline\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* Visual data from the ESP32-CAM and relevant sensor data enter the agricultural intelligence pipeline.

&nbsp;&nbsp;&nbsp;\* The models are designed as \*\*lightweight, edge-oriented models\*\*, so the intelligence is intended to be deployable close to the robot.

&nbsp;

5\. \*\*Crop identification\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The crop model analyses the plant image.

&nbsp;&nbsp;&nbsp;\* It determines what crop/plant is being observed.

&nbsp;

6\. \*\*Disease analysis\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The disease model analyses the same plant image.

&nbsp;&nbsp;&nbsp;\* It determines whether the plant shows a disease and identifies the corresponding condition.

&nbsp;

7\. \*\*Pest detection\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The pest model analyses the image as an object-detection problem.

&nbsp;&nbsp;&nbsp;\* It identifies pests along with their confidence and location/bounding boxes.

&nbsp;&nbsp;&nbsp;\* Your current pest architecture uses the lightweight MobileNetV4/PAN-FPN/YOLO26-inspired pipeline.

&nbsp;

8\. \*\*Irrigation intelligence\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The irrigation model receives environmental and soil information.

&nbsp;&nbsp;&nbsp;\* Its current feature set includes previous/current soil moisture, moisture trend, temperature, humidity, recent rain and VPD.

&nbsp;&nbsp;&nbsp;\* It produces an irrigation decision such as \*\*WAIT\*\* or \*\*IRRIGATE\*\*.&nbsp;

&nbsp;

9\. \*\*Nutrient intelligence\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;\* The nutrient model analyses the agricultural/plant information for \*\*crop-specific nutrient analysis and recommendation\*\*.

&nbsp;&nbsp;&nbsp;\* This adds nutritional assessment as a separate intelligence layer rather than treating it as disease detection.&nbsp;

&nbsp;

10\. \*\*Agricultural state is formed\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The outputs of the five intelligence modules are combined into a broader understanding of the plant/field:

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* What crop is present

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Whether disease is present

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Whether pests are present

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Whether irrigation is required

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* What nutrient-related recommendation is appropriate

&nbsp;

11\. \*\*Flask acts as the common AI service layer\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* In the connected development/application configuration, the Flask API provides a common interface to the models.

&nbsp;&nbsp;&nbsp;&nbsp;\* It receives the image or relevant data, preprocesses it, invokes the appropriate model, post-processes the result and returns structured output.

&nbsp;&nbsp;&nbsp;&nbsp;\* This allows the robot, Android application and web interface to access the same AI pipeline.

&nbsp;

12\. \*\*Decision is generated\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* Some AI outputs are primarily informational, such as disease or nutrient recommendations.

&nbsp;&nbsp;&nbsp;&nbsp;\* Other outputs can lead to physical robot actions, such as irrigation or movement.

&nbsp;

13\. \*\*ESP32-S3 coordinates the action\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The S3 receives the decision and acts as the high-level embedded coordinator.

&nbsp;&nbsp;&nbsp;&nbsp;\* It does not directly handle every low-level actuator operation.

&nbsp;

14\. \*\*ESP32-S3 communicates with ESP32-WROOM\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The two controllers communicate through \*\*UART TX/RX/GND\*\*.

&nbsp;&nbsp;&nbsp;&nbsp;\* The S3 sends commands such as movement or pump-control instructions.&nbsp;

&nbsp;

15\. \*\*ESP32-WROOM performs the physical action\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The WROOM interfaces with the motor driver and pump-control circuitry.

&nbsp;&nbsp;&nbsp;&nbsp;\* It executes the command at the hardware level:

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Motors → robot movement

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Pump → irrigation

&nbsp;

16\. \*\*Result is shown to the user\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The Android application and web interface can receive the AI results.

&nbsp;&nbsp;&nbsp;&nbsp;\* The user can see crop identification, disease/pest information, irrigation status and nutrient recommendations.

&nbsp;

17\. \*\*Android provides a secondary vision path\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* The Android application does \*\*not replace the ESP32-CAM\*\*.

&nbsp;&nbsp;&nbsp;&nbsp;\* When manual analysis is required, the user can:

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Take a photo with the phone camera, or

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Select an image from the gallery.

&nbsp;&nbsp;&nbsp;&nbsp;\* That image goes through the same Flask/AI pipeline.

&nbsp;

18\. \*\*The robot continues operating\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\* After an action, the robot continues sensing.

&nbsp;&nbsp;&nbsp;&nbsp;\* For example, after irrigation:

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Soil moisture changes

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Sensor measures the new condition

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\* Irrigation model evaluates it again

&nbsp;&nbsp;&nbsp;&nbsp;\* Similarly, the ESP32-CAM continues capturing new observations as the robot moves.

&nbsp;

19\. \*\*This creates a closed loop\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\*\*Move → Sense → Capture → Analyze → Understand → Decide → Act → Measure again → Repeat\*\*

&nbsp;

20\. \*\*In one sentence:\*\*

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;\> \*\*Dhurandhar is an edge-AI agricultural robotics system that uses an onboard ESP32-CAM for autonomous vision, ESP32-based sensing and control for the robot, five agricultural intelligence models for crop, disease, pest, irrigation and nutrient analysis, Flask as the common connected AI interface, and Android/web applications for human interaction, forming a continuous sense–analyze–decide–act loop.\*\*

&nbsp;