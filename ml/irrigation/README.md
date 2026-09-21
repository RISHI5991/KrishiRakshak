# M5 Irrigation Model

- Random Forest (scikit-learn)
- 7 features: soil_moisture_previous, soil_moisture, soil_moisture_trend, temperature, humidity, rain_recent, vpd
- Binary decision: IRRIGATE / WAIT
- Edge deployment: exported to C via emlearn (m3_model_float.h)
- Model artifact: m3_embedded_rf.joblib
