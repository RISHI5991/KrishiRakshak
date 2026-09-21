#include <stdio.h>

#include "m3_model_float.h"

int main(void)
{
    FILE *fp = fopen(
        "v2/firmware/float_parity_test.csv",
        "r"
    );

    if (!fp) {
        perror("Could not open float_parity_test.csv");
        return 1;
    }

    char line[1024];

    if (!fgets(line, sizeof(line), fp)) {
        fprintf(stderr, "Empty CSV\n");
        fclose(fp);
        return 1;
    }

    int total = 0;
    int matching = 0;
    int mismatching = 0;

    while (fgets(line, sizeof(line), fp)) {

        float features[7];
        int python_prediction;

        int parsed = sscanf(
            line,
            "%f,%f,%f,%f,%f,%f,%f,%d",
            &features[0],
            &features[1],
            &features[2],
            &features[3],
            &features[4],
            &features[5],
            &features[6],
            &python_prediction
        );

        if (parsed != 8) {
            continue;
        }

        int c_prediction = m3_model_float_predict(
            features,
            7
        );

        total++;

        if (c_prediction == python_prediction) {
            matching++;
        } else {
            mismatching++;

            if (mismatching <= 10) {
                printf(
                    "Mismatch %d: Python=%d C=%d "
                    "(sm_prev=%.4f sm=%.4f trend=%.4f "
                    "temp=%.4f hum=%.4f rain=%.4f vpd=%.4f)\n",
                    mismatching,
                    python_prediction,
                    c_prediction,
                    features[0],
                    features[1],
                    features[2],
                    features[3],
                    features[4],
                    features[5],
                    features[6]
                );
            }
        }
    }

    fclose(fp);

    printf("\n");
    printf("======================================================================\n");
    printf("PYTHON <-> C FLOAT MODEL PARITY\n");
    printf("======================================================================\n");
    printf("Samples tested : %d\n", total);
    printf("Matching       : %d\n", matching);
    printf("Mismatching    : %d\n", mismatching);

    if (total > 0) {
        printf(
            "Agreement      : %.3f%%\n",
            100.0 * (double) matching / total
        );
    }

    printf("======================================================================\n");

    return mismatching == 0 ? 0 : 2;
}
