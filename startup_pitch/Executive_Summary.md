# Dhurandhar: Executive Summary
**Democratizing Precision Agriculture through Edge-AI Robotics**

## 1. The Problem
Globally, small and medium-scale farmers lose up to **40% of their crop yield** to pests, diseases, and nutrient deficiencies, while simultaneously over-consuming fresh water through inefficient irrigation. Current agricultural robotics and AI systems cost upwards of $10,000+, relying on expensive cloud computing and constant internet connectivity, putting them completely out of reach for the average farmer, especially in developing economies.

## 2. The Solution: Dhurandhar
Dhurandhar is an ultra-low-cost, autonomous agricultural robot that operates entirely on **Edge AI**. It creates a continuous "Sense ➔ Analyze ➔ Decide ➔ Act" loop directly in the field, without needing internet access. 
* **Navigates** the field autonomously.
* **Senses** micro-climate data (temp, humidity, soil moisture, light, rain).
* **Captures** high-res crop images.
* **Analyzes** data locally to identify crops, detect diseases, spot pests, and assess nutrient deficiencies.
* **Acts** by triggering precision irrigation and delivering actionable alerts to the farmer’s smartphone.

## 3. Technical Magic (How it Works)
Instead of an expensive onboard computer, Dhurandhar uses a distributed architecture of three $5 microcontrollers (ESP32 series) and heavily optimized machine learning models:
* **The Hardware:** A 3-tier ESP32 system. ESP32-CAM (Vision), ESP32-S3 (Central Brain & Sensor Hub), and ESP32-WROOM (Motor & Pump Actuation).
* **The AI (5 Edge Models):** We compressed state-of-the-art AI into micro-models.
  1. **Crop ID & Disease Detection:** Dual-head MobileNetV4 identifying 15 crops and 38 diseases.
  2. **Pest Detection:** Custom YOLO-inspired detector for 24 pest classes.
  3. **Nutrient Analysis:** N-P-K deficiency vision model.
  4. **Irrigation AI:** Random Forest model exported to native C code for instant microsecond decisions based on Vapor Pressure Deficit (VPD) and soil trends.

## 4. Market Opportunity
* **TAM (Total Addressable Market):** The global precision agriculture market is projected to reach $24.09 Billion by 2030.
* **SAM (Serviceable Addressable Market):** India alone has ~150 million farmers. Small/medium farms (1-10 hectares) represent a massive, entirely untapped market for affordable automation.

## 5. Financials & Unit Economics
Our unfair advantage is our Bill of Materials (BOM). By replacing expensive Raspberry Pis and Jetson Nanos with edge-optimized ESP32s, we shattered the price floor.

* **Hardware BOM (Prototype):** ~$40 - $60 USD (₹3,500 - ₹5,000 INR).
* **Retail Price:** ~$150 USD (₹12,500 INR) — representing a healthy **60% hardware gross margin**, while remaining cheaper than a mid-range smartphone for the farmer.
* **Recurring Revenue (SaaS):** A premium tier at $3/month (₹250/month) offering historical data analytics, multi-robot fleet management, and cloud backup via our Android/Web dashboard.

## 6. Traction & The Ask
Born out of the **Smart India Hackathon (SIH)** where it secured a **Top 15** spot at our institution, Dhurandhar is now transitioning from a proven prototype to a market-ready product. 

**The Ask:** We are seeking seed funding/incubation support to:
1. Transition from prototype chassis to weather-proof, mass-manufacturable PCB and hardware designs.
2. Conduct large-scale pilot testing across 50 local farms.
3. Obtain necessary agricultural and electronic certifications.
