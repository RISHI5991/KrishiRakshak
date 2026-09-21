# Dhurandhar: Comprehensive Business & Technical Plan
**An Edge-AI Autonomous Agricultural Robotics Ecosystem**

---

## 1. Executive Overview
Dhurandhar is an accessible, closed-loop precision agriculture system designed for small to medium-scale farmers. It combines an autonomous ground vehicle, a suite of environmental sensors, and five edge-deployed Machine Learning models to monitor crop health, detect pests/diseases, and automate irrigation. By leveraging heavily optimized microcontrollers instead of expensive computing hardware, Dhurandhar reduces the entry cost of ag-robotics by over 95%.

---

## 2. Problem Statement
The agricultural sector faces a trilemma:
1. **Resource Scarcity:** Freshwater scarcity and fertilizer shortages require highly precise application.
2. **Crop Loss:** Pests and diseases routinely wipe out 20-40% of yields because manual scouting is slow and reactive.
3. **Technological Exclusivity:** Existing ag-tech solutions (drones, large autonomous tractors) cost thousands of dollars, making them exclusive to massive corporate farms. The average farmer in developing nations relies purely on intuition.

---

## 3. Product & Technical Architecture
Dhurandhar solves this through a deeply integrated Hardware + Software + AI ecosystem.

### 3.1 Hardware Architecture (The 3-ESP32 Topology)
Our hardware strategy drastically cuts costs by decentralizing processing across three cheap, highly efficient microcontrollers:
* **ESP32-CAM (The Eyes):** Dedicated exclusively to capturing crop images via an OV2640 camera and streaming JPEGs over local WiFi.
* **ESP32-S3 N16R8 (The Brain):** The central coordinator. It polls a suite of analog/digital sensors (DHT22 for temp/humidity, Soil Moisture, Light, Rain), calculates complex metrics like Vapor Pressure Deficit (VPD), communicates with the AI server, and coordinates actions.
* **ESP32-WROOM (The Muscle):** Dedicated to actuation. It receives JSON commands via UART from the S3 to drive the 4-wheel chassis (via L298N drivers) and toggle the irrigation water pump relay.

### 3.2 AI & Machine Learning Pipeline
Dhurandhar runs **5 specialized AI models** locally (Edge AI), meaning it works perfectly in deep rural areas with zero internet connectivity.
1. **M1 (Crop Identification):** MobileNetV4-ConvSmall architecture classifying 15 different crops.
2. **M2 (Disease Detection):** Shares a backbone with M1 to save memory, branching into a 38-class disease detection head.
3. **M3 (Pest Detection):** A custom YOLO-inspired object detection model trained on the Pest24 dataset, capable of drawing bounding boxes around 24 specific insect threats.
4. **M4 (Nutrient Deficiency):** Analyzes foliage to detect N-P-K (Nitrogen, Phosphorus, Potassium) deficiencies, providing visual GradCAM heatmaps to show the farmer exactly where the plant is ailing.
5. **M5 (Irrigation AI):** A scikit-learn Random Forest model exported natively to C code (via emlearn). It takes 7 sensor features and outputs an immediate `IRRIGATE` or `WAIT` decision, preventing water waste.

### 3.3 Software Infrastructure
* **Flask AI Gateway:** A lightweight local server that hosts the ML models, exposing a clean REST API.
* **Android Application:** Built with modern Kotlin and Jetpack Compose, allowing the farmer to view real-time field summaries, disease alerts, and manually override robot controls.
* **Web Dashboard:** A cross-platform UI for deep analytics and fleet management.

---

## 4. Financial Plan & Unit Economics

### 4.1 Cost of Goods Sold (COGS) - Prototype Scale
* Microcontrollers (S3, CAM, WROOM): $15
* Sensors (DHT22, Soil, LDR, Rain): $8
* Actuation (Motors, Wheels, L298N, Relay, Pump): $17
* Chassis, Wiring, Battery & Power Regulation: $20
* **Total Estimated BOM:** ~$60 USD (₹5,000 INR)

### 4.2 Revenue Model
We utilize a **Hardware-enabled SaaS (Software as a Service)** model.

1. **Hardware Sales (Upfront Revenue):** 
   * **Target Retail Price:** $150 USD (₹12,500 INR). 
   * **Gross Margin:** 60%. This is highly affordable for a farmer (costing less than a smartphone) while leaving room for distributor margins.
2. **Software Subscription (Recurring Revenue):**
   * **Basic Tier:** Free. Includes all local edge-AI inference, direct Android app control, and real-time irrigation.
   * **Pro Tier:** $3-$5/month (₹250-₹400/month). Unlocks cloud-sync, historical yield/health analytics over the season, predictive pest outbreak alerts based on regional data, and multi-robot fleet management.

### 4.3 Target Market & Go-To-Market Strategy
* **Phase 1: Local Co-ops (Months 1-6):** Partner with local agricultural cooperatives and Farmer Producer Organizations (FPOs) to deploy 50 pilot units. Offer the hardware at cost in exchange for field data and testimonials.
* **Phase 2: B2B2C Retail (Months 6-18):** Distribute through established agri-input retailers (seed/fertilizer shops) where farmers already go for crop health advice.
* **Phase 3: Government Subsidy Integration:** Apply for agricultural tech subsidies (e.g., under Indian schemes like SMAM), which could effectively reduce the farmer's out-of-pocket cost to zero, driving massive volume.

---

## 5. Competitive Advantage
| Feature | Traditional Ag-Robots | Dhurandhar |
|---------|-----------------------|------------|
| **Price** | $5,000 - $20,000+ | **$150** |
| **Compute** | Heavy (Jetson, Cloud) | **Edge Microcontrollers** |
| **Connectivity** | Requires 4G/5G/WiFi | **Zero Internet Required (Local Edge)** |
| **Maintenance** | Requires technicians | **Modular, plug-and-play parts** |

---

## 6. Funding Ask & Roadmap
Originating as a Top 15 project at the Smart India Hackathon (SIH), the core R&D and software pipeline are already built and proven.

**We are raising a seed/incubation round to achieve the following milestones:**
1. **Hardware Refinement (Q1):** Transition from breadboards/jumpers to a unified, weather-proof (IP67) custom PCB.
2. **Pilot Manufacturing (Q2):** Produce the first 100 beta units for real-world stress testing across different crop types (e.g., Rice, Wheat, Cotton).
3. **ML Iteration (Q3):** Expand the dataset via our pilot units to improve the NPK nutrient and pest detection accuracy in diverse lighting conditions.
4. **Commercial Launch (Q4):** Launch the consumer-ready product in 3 target states.

Dhurandhar isn't just a robot; it's the missing link to bringing data-driven, precision agriculture to the farmers who need it most.
