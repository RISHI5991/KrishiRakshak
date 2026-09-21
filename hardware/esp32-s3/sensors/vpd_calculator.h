#ifndef VPD_CALCULATOR_H
#define VPD_CALCULATOR_H

#include <math.h>

float calculateVPD(float tempC, float humidityPercent) {
    if (isnan(tempC) || isnan(humidityPercent)) return 0.0f;
    
    // Magnus formula for Saturated Vapor Pressure (SVP) in kPa
    float svp = 0.6108f * exp((17.27f * tempC) / (tempC + 237.3f));
    
    // Vapor Pressure Deficit (VPD)
    float vpd = svp * (1.0f - (humidityPercent / 100.0f));
    
    return vpd;
}

#endif
