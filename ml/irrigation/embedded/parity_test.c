#include <stdio.h>
#include <stdint.h>

#include "m3_model.h"

int main(void)
{
    int16_t features[7] = {
        50,   // soil_moisture_previous
        42,   // soil_moisture
        -8,   // soil_moisture_trend
        31,   // temperature
        55,   // humidity
        0,    // rain_recent
        2     // vpd, quantized to int16
    };

    float probabilities[2] = {0.0f, 0.0f};

    int prediction = m3_model_predict(
        features,
        7
    );

    int status = m3_model_predict_proba(
        features,
        7,
        probabilities,
        2
    );

    printf("============================================================\n");
    printf("M3 EMBEDDED C MODEL TEST\n");
    printf("============================================================\n");

    printf("Prediction        : %d (%s)\n",
           prediction,
           prediction == 1 ? "IRRIGATE" : "WAIT");

    printf("predict_proba rc  : %d\n", status);
    printf("WAIT probability  : %.6f\n", probabilities[0]);
    printf("IRRIGATE probability: %.6f\n", probabilities[1]);

    printf("============================================================\n");

    return 0;
}
