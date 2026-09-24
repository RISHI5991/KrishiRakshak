/*
 * ESP32 S3 Enhanced Irrigation Model - Auto-Generated
 * 
 * Model: Accuracy Focused
 * Accuracy: 93.03%
 * Balanced Accuracy: 93.04%
 * Model Size: 43.38 KB
 * False Negative Rate: 6.5%
 * Cross-Validation: 92.85% ± 0.71%
 * 
 * Features: 12 total
 *   Base Sensors (4): soil_moisture, temperature, humidity, water_level
 *   Engineered (8): et_rate, soil_temp_stress, moisture_deficit, stress_index,
 *                   vpd_index, temp_hum_ratio, critical_dry, optimal_moisture
 * 
 * Memory: 43.38 KB / 520 KB (8.3%)
 * Available: 476.6 KB for application
 */

#ifndef IRRIGATION_MODEL_ENHANCED_H
#define IRRIGATION_MODEL_ENHANCED_H
#define max(a,b) ((a)>(b)?(a):(b))

#define N_FEATURES 12
#define N_TREES 12
#define MODEL_VERSION "Enhanced-12F-v1.0"

// Feature indices
#define FEAT_SOIL_MOISTURE 0
#define FEAT_TEMPERATURE 1
#define FEAT_HUMIDITY 2
#define FEAT_WATER_LEVEL 3
#define FEAT_ET_RATE 4
#define FEAT_SOIL_TEMP_STRESS 5
#define FEAT_MOISTURE_DEFICIT 6
#define FEAT_STRESS_INDEX 7
#define FEAT_VPD_INDEX 8
#define FEAT_TEMP_HUM_RATIO 9
#define FEAT_CRITICAL_DRY 10
#define FEAT_OPTIMAL_MOISTURE 11

// Decision tree functions

// Tree 0
float tree_0(float features[N_FEATURES]) {
    if (features[8] <= 13.745000f) {
        if (features[5] <= 15.235000f) {
            if (features[2] <= 63.010000f) {
                if (features[6] <= 0.500000f) {
                    if (features[5] <= 12.155000f) {
                        if (features[4] <= 0.976950f) {
                            return 0.032790f;
                        } else {
                            return 0.277715f;
                        }
                    } else {
                        if (features[4] <= 0.963350f) {
                            return 0.349073f;
                        } else {
                            return 0.927904f;
                        }
                    }
                } else {
                    if (features[4] <= 0.893150f) {
                        if (features[5] <= 14.030000f) {
                            return 0.118218f;
                        } else {
                            return 0.682043f;
                        }
                    } else {
                        if (features[3] <= 19.000000f) {
                            return 0.159149f;
                        } else {
                            return 0.939973f;
                        }
                    }
                }
            } else {
                if (features[6] <= 10.500000f) {
                    if (features[5] <= 13.370000f) {
                        if (features[1] <= 27.685000f) {
                            return 0.025930f;
                        } else {
                            return 0.067832f;
                        }
                    } else {
                        if (features[8] <= 12.080000f) {
                            return 0.045238f;
                        } else {
                            return 0.527036f;
                        }
                    }
                } else {
                    if (features[3] <= 34.000000f) {
                        if (features[5] <= 14.425000f) {
                            return 0.300218f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[9] <= 0.329400f) {
                            return 0.430876f;
                        } else {
                            return 0.779706f;
                        }
                    }
                }
            }
        } else {
            if (features[7] <= 24.190001f) {
                if (features[6] <= 20.500000f) {
                    if (features[0] <= 33.500000f) {
                        if (features[2] <= 77.059998f) {
                            return 0.505309f;
                        } else {
                            return 0.079023f;
                        }
                    } else {
                        if (features[2] <= 67.260002f) {
                            return 0.961042f;
                        } else {
                            return 0.541241f;
                        }
                    }
                } else {
                    if (features[6] <= 28.500000f) {
                        if (features[1] <= 22.285000f) {
                            return 1.000000f;
                        } else {
                            return 0.789646f;
                        }
                    } else {
                        if (features[8] <= 6.615000f) {
                            return 1.000000f;
                        } else {
                            return 0.501373f;
                        }
                    }
                }
            } else {
                if (features[3] <= 9.500000f) {
                    if (features[8] <= 9.960000f) {
                        if (features[7] <= 32.259999f) {
                            return 0.052560f;
                        } else {
                            return 0.391551f;
                        }
                    } else {
                        if (features[7] <= 33.164999f) {
                            return 0.023449f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[1] <= 23.224999f) {
                        if (features[5] <= 21.850000f) {
                            return 0.905515f;
                        } else {
                            return 0.758810f;
                        }
                    } else {
                        if (features[3] <= 19.500000f) {
                            return 0.724262f;
                        } else {
                            return 0.975925f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[0] <= 79.500000f) {
            if (features[6] <= 0.500000f) {
                if (features[3] <= 19.500000f) {
                    if (features[8] <= 17.345000f) {
                        if (features[4] <= 1.120850f) {
                            return 0.041269f;
                        } else {
                            return 0.349073f;
                        }
                    } else {
                        if (features[2] <= 64.994999f) {
                            return 0.562755f;
                        } else {
                            return 0.125113f;
                        }
                    }
                } else {
                    if (features[1] <= 29.015000f) {
                        if (features[4] <= 1.011350f) {
                            return 0.255702f;
                        } else {
                            return 0.906128f;
                        }
                    } else {
                        if (features[1] <= 30.884999f) {
                            return 0.805862f;
                        } else {
                            return 0.972523f;
                        }
                    }
                }
            } else {
                if (features[5] <= 32.415001f) {
                    if (features[0] <= 38.500000f) {
                        if (features[5] <= 20.505000f) {
                            return 0.940610f;
                        } else {
                            return 0.880154f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.010612f;
                        } else {
                            return 0.953430f;
                        }
                    }
                } else {
                    if (features[9] <= 0.466100f) {
                        if (features[4] <= 0.791900f) {
                            return 0.263359f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        return 1.000000f;
                    }
                }
            }
        } else {
            if (features[1] <= 32.995001f) {
                if (features[3] <= 0.500000f) {
                    if (features[5] <= 5.655000f) {
                        return 0.000000f;
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[4] <= 1.132550f) {
                        if (features[3] <= 11.500000f) {
                            return 0.054643f;
                        } else {
                            return 0.014843f;
                        }
                    } else {
                        if (features[4] <= 1.132850f) {
                            return 1.000000f;
                        } else {
                            return 0.047167f;
                        }
                    }
                }
            } else {
                if (features[7] <= 7.660000f) {
                    return 0.000000f;
                } else {
                    return 1.000000f;
                }
            }
        }
    }
}

// Tree 1
float tree_1(float features[N_FEATURES]) {
    if (features[5] <= 14.535000f) {
        if (features[8] <= 15.005000f) {
            if (features[7] <= 18.445001f) {
                if (features[5] <= 10.635000f) {
                    if (features[2] <= 60.504999f) {
                        if (features[0] <= 69.500000f) {
                            return 0.562755f;
                        } else {
                            return 0.082045f;
                        }
                    } else {
                        if (features[11] <= 0.500000f) {
                            return 0.021932f;
                        } else {
                            return 0.036949f;
                        }
                    }
                } else {
                    if (features[2] <= 62.049999f) {
                        if (features[8] <= 11.680000f) {
                            return 0.096865f;
                        } else {
                            return 0.810970f;
                        }
                    } else {
                        if (features[1] <= 29.000000f) {
                            return 0.077347f;
                        } else {
                            return 0.529670f;
                        }
                    }
                }
            } else {
                if (features[4] <= 0.879850f) {
                    if (features[3] <= 93.500000f) {
                        if (features[3] <= 30.500000f) {
                            return 0.085687f;
                        } else {
                            return 0.302527f;
                        }
                    } else {
                        if (features[0] <= 42.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.616683f;
                        }
                    }
                } else {
                    if (features[3] <= 19.500000f) {
                        if (features[2] <= 64.875000f) {
                            return 0.000000f;
                        } else {
                            return 0.263359f;
                        }
                    } else {
                        if (features[1] <= 27.690000f) {
                            return 0.715079f;
                        } else {
                            return 0.243434f;
                        }
                    }
                }
            }
        } else {
            if (features[11] <= 0.500000f) {
                if (features[1] <= 31.340000f) {
                    if (features[3] <= 10.500000f) {
                        if (features[5] <= 5.175000f) {
                            return 0.000000f;
                        } else {
                            return 0.050897f;
                        }
                    } else {
                        if (features[0] <= 70.000000f) {
                            return 0.901691f;
                        } else {
                            return 0.028270f;
                        }
                    }
                } else {
                    if (features[4] <= 1.254450f) {
                        if (features[2] <= 65.135002f) {
                            return 0.192469f;
                        } else {
                            return 0.131025f;
                        }
                    } else {
                        if (features[0] <= 70.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            } else {
                if (features[3] <= 19.500000f) {
                    if (features[5] <= 10.675000f) {
                        if (features[8] <= 19.650000f) {
                            return 0.077593f;
                        } else {
                            return 0.445800f;
                        }
                    } else {
                        if (features[9] <= 0.460250f) {
                            return 0.149303f;
                        } else {
                            return 0.774375f;
                        }
                    }
                } else {
                    if (features[4] <= 1.011650f) {
                        if (features[4] <= 1.009650f) {
                            return 0.828194f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[7] <= 10.185000f) {
                            return 0.369094f;
                        } else {
                            return 0.958707f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[9] <= 0.372750f) {
            if (features[7] <= 21.110001f) {
                if (features[8] <= 12.615000f) {
                    if (features[3] <= 36.500000f) {
                        return 0.000000f;
                    } else {
                        if (features[0] <= 30.500000f) {
                            return 0.933079f;
                        } else {
                            return 0.293727f;
                        }
                    }
                } else {
                    if (features[3] <= 21.000000f) {
                        return 0.000000f;
                    } else {
                        if (features[0] <= 49.000000f) {
                            return 0.959343f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            } else {
                if (features[10] <= 0.500000f) {
                    if (features[1] <= 22.710000f) {
                        if (features[4] <= 0.666000f) {
                            return 1.000000f;
                        } else {
                            return 0.211440f;
                        }
                    } else {
                        if (features[2] <= 64.995003f) {
                            return 0.887200f;
                        } else {
                            return 0.598840f;
                        }
                    }
                } else {
                    if (features[9] <= 0.371800f) {
                        if (features[3] <= 9.500000f) {
                            return 0.075449f;
                        } else {
                            return 0.933689f;
                        }
                    } else {
                        if (features[5] <= 22.035001f) {
                            return 0.286836f;
                        } else {
                            return 0.810970f;
                        }
                    }
                }
            }
        } else {
            if (features[5] <= 16.785001f) {
                if (features[1] <= 27.320000f) {
                    if (features[9] <= 0.389950f) {
                        if (features[0] <= 38.500000f) {
                            return 0.714497f;
                        } else {
                            return 0.194968f;
                        }
                    } else {
                        if (features[3] <= 19.000000f) {
                            return 0.000000f;
                        } else {
                            return 0.925433f;
                        }
                    }
                } else {
                    if (features[3] <= 9.500000f) {
                        if (features[0] <= 51.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.066731f;
                        }
                    } else {
                        if (features[7] <= 23.320000f) {
                            return 0.925646f;
                        } else {
                            return 0.988262f;
                        }
                    }
                }
            } else {
                if (features[1] <= 23.000000f) {
                    return 0.000000f;
                } else {
                    if (features[5] <= 29.085000f) {
                        if (features[3] <= 9.500000f) {
                            return 0.025955f;
                        } else {
                            return 0.965194f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.130552f;
                        } else {
                            return 0.966975f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 2
float tree_2(float features[N_FEATURES]) {
    if (features[5] <= 13.705000f) {
        if (features[8] <= 15.005000f) {
            if (features[4] <= 0.961850f) {
                if (features[7] <= 20.060000f) {
                    if (features[1] <= 27.685000f) {
                        if (features[4] <= 0.717100f) {
                            return 0.016037f;
                        } else {
                            return 0.042251f;
                        }
                    } else {
                        if (features[3] <= 22.500000f) {
                            return 0.009402f;
                        } else {
                            return 0.134738f;
                        }
                    }
                } else {
                    if (features[3] <= 21.500000f) {
                        return 0.000000f;
                    } else {
                        if (features[9] <= 0.376350f) {
                            return 0.096865f;
                        } else {
                            return 0.973309f;
                        }
                    }
                }
            } else {
                if (features[2] <= 62.035000f) {
                    if (features[0] <= 70.500000f) {
                        if (features[3] <= 24.500000f) {
                            return 0.118218f;
                        } else {
                            return 0.821320f;
                        }
                    } else {
                        if (features[8] <= 14.750000f) {
                            return 0.011049f;
                        } else {
                            return 0.234561f;
                        }
                    }
                } else {
                    if (features[5] <= 11.085000f) {
                        if (features[7] <= 12.230000f) {
                            return 0.011649f;
                        } else {
                            return 0.176621f;
                        }
                    } else {
                        if (features[8] <= 13.345000f) {
                            return 0.000000f;
                        } else {
                            return 0.772540f;
                        }
                    }
                }
            }
        } else {
            if (features[7] <= 9.170000f) {
                if (features[3] <= 45.500000f) {
                    if (features[8] <= 18.285000f) {
                        if (features[3] <= 1.500000f) {
                            return 0.127594f;
                        } else {
                            return 0.009722f;
                        }
                    } else {
                        if (features[9] <= 0.462850f) {
                            return 0.211440f;
                        } else {
                            return 0.026989f;
                        }
                    }
                } else {
                    if (features[0] <= 79.500000f) {
                        if (features[1] <= 30.750000f) {
                            return 0.714497f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[8] <= 18.015000f) {
                            return 0.013650f;
                        } else {
                            return 0.035429f;
                        }
                    }
                }
            } else {
                if (features[8] <= 17.045000f) {
                    if (features[7] <= 15.465000f) {
                        if (features[7] <= 15.305000f) {
                            return 0.675534f;
                        } else {
                            return 0.118218f;
                        }
                    } else {
                        if (features[3] <= 15.500000f) {
                            return 0.130552f;
                        } else {
                            return 0.961925f;
                        }
                    }
                } else {
                    if (features[5] <= 7.010000f) {
                        if (features[0] <= 79.500000f) {
                            return 0.621865f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[7] <= 11.455000f) {
                            return 0.643343f;
                        } else {
                            return 0.853542f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[5] <= 16.335000f) {
            if (features[1] <= 27.020000f) {
                if (features[2] <= 66.875000f) {
                    if (features[3] <= 19.000000f) {
                        return 0.000000f;
                    } else {
                        if (features[8] <= 11.055000f) {
                            return 0.722587f;
                        } else {
                            return 0.922939f;
                        }
                    }
                } else {
                    if (features[6] <= 19.500000f) {
                        if (features[3] <= 68.500000f) {
                            return 0.107191f;
                        } else {
                            return 0.409680f;
                        }
                    } else {
                        if (features[9] <= 0.324000f) {
                            return 0.909176f;
                        } else {
                            return 0.263359f;
                        }
                    }
                }
            } else {
                if (features[3] <= 19.500000f) {
                    if (features[3] <= 9.500000f) {
                        if (features[1] <= 31.120000f) {
                            return 0.000000f;
                        } else {
                            return 0.036892f;
                        }
                    } else {
                        if (features[4] <= 0.827000f) {
                            return 0.132863f;
                        } else {
                            return 0.676232f;
                        }
                    }
                } else {
                    if (features[9] <= 0.351400f) {
                        if (features[0] <= 40.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[9] <= 0.394050f) {
                            return 0.791781f;
                        } else {
                            return 0.939651f;
                        }
                    }
                }
            }
        } else {
            if (features[9] <= 0.354650f) {
                if (features[3] <= 19.500000f) {
                    if (features[7] <= 27.275001f) {
                        if (features[3] <= 11.500000f) {
                            return 0.056982f;
                        } else {
                            return 0.254434f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.013564f;
                        } else {
                            return 0.622230f;
                        }
                    }
                } else {
                    if (features[7] <= 23.370000f) {
                        if (features[7] <= 21.110001f) {
                            return 0.198403f;
                        } else {
                            return 0.696813f;
                        }
                    } else {
                        if (features[10] <= 0.500000f) {
                            return 0.818336f;
                        } else {
                            return 0.969887f;
                        }
                    }
                }
            } else {
                if (features[3] <= 9.500000f) {
                    if (features[1] <= 24.870000f) {
                        if (features[2] <= 63.989998f) {
                            return 0.000000f;
                        } else {
                            return 0.263359f;
                        }
                    } else {
                        if (features[5] <= 26.595000f) {
                            return 0.037105f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[9] <= 0.534550f) {
                        if (features[3] <= 18.500000f) {
                            return 0.914342f;
                        } else {
                            return 0.974846f;
                        }
                    } else {
                        if (features[3] <= 71.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 3
float tree_3(float features[N_FEATURES]) {
    if (features[5] <= 13.695000f) {
        if (features[7] <= 9.135000f) {
            if (features[5] <= 7.245000f) {
                if (features[3] <= 0.500000f) {
                    if (features[8] <= 10.975000f) {
                        return 0.000000f;
                    } else {
                        if (features[8] <= 11.290000f) {
                            return 1.000000f;
                        } else {
                            return 0.151648f;
                        }
                    }
                } else {
                    if (features[11] <= 0.500000f) {
                        if (features[1] <= 32.924999f) {
                            return 0.025014f;
                        } else {
                            return 0.122727f;
                        }
                    } else {
                        if (features[1] <= 28.995000f) {
                            return 0.024550f;
                        } else {
                            return 0.285382f;
                        }
                    }
                }
            } else {
                return 1.000000f;
            }
        } else {
            if (features[9] <= 0.402850f) {
                if (features[4] <= 0.883300f) {
                    if (features[1] <= 29.105000f) {
                        if (features[8] <= 12.505000f) {
                            return 0.026222f;
                        } else {
                            return 0.115896f;
                        }
                    } else {
                        if (features[8] <= 14.930000f) {
                            return 0.261414f;
                        } else {
                            return 0.776042f;
                        }
                    }
                } else {
                    if (features[5] <= 11.875000f) {
                        if (features[3] <= 99.500000f) {
                            return 0.083754f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[0] <= 49.500000f) {
                            return 0.688296f;
                        } else {
                            return 0.254434f;
                        }
                    }
                }
            } else {
                if (features[5] <= 10.180000f) {
                    if (features[5] <= 6.475000f) {
                        if (features[9] <= 0.472850f) {
                            return 0.378021f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[3] <= 19.500000f) {
                            return 0.073182f;
                        } else {
                            return 0.777265f;
                        }
                    }
                } else {
                    if (features[1] <= 28.405000f) {
                        if (features[4] <= 0.980800f) {
                            return 0.331795f;
                        } else {
                            return 0.746802f;
                        }
                    } else {
                        if (features[4] <= 1.042050f) {
                            return 0.786759f;
                        } else {
                            return 0.901152f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[8] <= 12.725000f) {
            if (features[0] <= 29.500000f) {
                if (features[4] <= 0.520400f) {
                    if (features[3] <= 27.500000f) {
                        if (features[1] <= 22.565000f) {
                            return 0.349073f;
                        } else {
                            return 0.026765f;
                        }
                    } else {
                        if (features[7] <= 21.040000f) {
                            return 0.349073f;
                        } else {
                            return 0.989022f;
                        }
                    }
                } else {
                    if (features[1] <= 22.634999f) {
                        if (features[0] <= 3.500000f) {
                            return 0.533591f;
                        } else {
                            return 0.807975f;
                        }
                    } else {
                        if (features[8] <= 8.480000f) {
                            return 0.782278f;
                        } else {
                            return 0.875638f;
                        }
                    }
                }
            } else {
                if (features[7] <= 21.855000f) {
                    if (features[7] <= 21.040000f) {
                        if (features[7] <= 18.190000f) {
                            return 0.000000f;
                        } else {
                            return 0.237849f;
                        }
                    } else {
                        if (features[9] <= 0.352050f) {
                            return 0.571446f;
                        } else {
                            return 0.078064f;
                        }
                    }
                } else {
                    if (features[3] <= 29.500000f) {
                        if (features[8] <= 11.055000f) {
                            return 0.000000f;
                        } else {
                            return 0.195986f;
                        }
                    } else {
                        if (features[2] <= 78.764999f) {
                            return 0.884803f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            }
        } else {
            if (features[5] <= 16.554999f) {
                if (features[9] <= 0.368050f) {
                    if (features[9] <= 0.366450f) {
                        if (features[6] <= 7.000000f) {
                            return 0.595917f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        return 0.000000f;
                    }
                } else {
                    if (features[5] <= 16.505000f) {
                        if (features[3] <= 9.500000f) {
                            return 0.015091f;
                        } else {
                            return 0.877953f;
                        }
                    } else {
                        if (features[4] <= 0.802150f) {
                            return 1.000000f;
                        } else {
                            return 0.211440f;
                        }
                    }
                }
            } else {
                if (features[7] <= 38.085001f) {
                    if (features[5] <= 18.065000f) {
                        if (features[5] <= 17.855000f) {
                            return 0.893229f;
                        } else {
                            return 0.675903f;
                        }
                    } else {
                        if (features[5] <= 22.435000f) {
                            return 0.927321f;
                        } else {
                            return 0.885061f;
                        }
                    }
                } else {
                    if (features[5] <= 31.515000f) {
                        if (features[3] <= 9.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.973209f;
                        }
                    } else {
                        if (features[6] <= 48.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.925997f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 4
float tree_4(float features[N_FEATURES]) {
    if (features[6] <= 0.500000f) {
        if (features[8] <= 14.925000f) {
            if (features[7] <= 17.210000f) {
                if (features[5] <= 12.480000f) {
                    if (features[11] <= 0.500000f) {
                        if (features[8] <= 7.310000f) {
                            return 0.103402f;
                        } else {
                            return 0.025660f;
                        }
                    } else {
                        if (features[8] <= 14.195000f) {
                            return 0.028333f;
                        } else {
                            return 0.165088f;
                        }
                    }
                } else {
                    if (features[5] <= 12.530000f) {
                        if (features[8] <= 12.135000f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[0] <= 53.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.410777f;
                        }
                    }
                }
            } else {
                if (features[1] <= 28.945001f) {
                    if (features[0] <= 56.500000f) {
                        if (features[4] <= 0.980800f) {
                            return 0.214023f;
                        } else {
                            return 0.641264f;
                        }
                    } else {
                        if (features[1] <= 25.580000f) {
                            return 0.000000f;
                        } else {
                            return 0.882460f;
                        }
                    }
                } else {
                    if (features[3] <= 17.500000f) {
                        return 0.000000f;
                    } else {
                        if (features[9] <= 0.368050f) {
                            return 0.263359f;
                        } else {
                            return 0.919617f;
                        }
                    }
                }
            }
        } else {
            if (features[5] <= 6.315000f) {
                if (features[7] <= 9.215000f) {
                    if (features[9] <= 0.385700f) {
                        return 1.000000f;
                    } else {
                        if (features[5] <= 6.295000f) {
                            return 0.033754f;
                        } else {
                            return 0.349073f;
                        }
                    }
                } else {
                    if (features[1] <= 29.665000f) {
                        if (features[5] <= 6.215000f) {
                            return 0.882460f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[11] <= 0.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            } else {
                if (features[5] <= 7.125000f) {
                    if (features[2] <= 61.719999f) {
                        if (features[9] <= 0.507300f) {
                            return 0.939584f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[3] <= 26.500000f) {
                            return 0.050897f;
                        } else {
                            return 0.620399f;
                        }
                    }
                } else {
                    if (features[4] <= 1.214200f) {
                        if (features[9] <= 0.406450f) {
                            return 0.846180f;
                        } else {
                            return 0.737931f;
                        }
                    } else {
                        if (features[7] <= 11.820000f) {
                            return 0.000000f;
                        } else {
                            return 0.944278f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[3] <= 9.500000f) {
            if (features[5] <= 31.125000f) {
                if (features[9] <= 0.524950f) {
                    if (features[4] <= 0.670400f) {
                        if (features[5] <= 14.395000f) {
                            return 0.044554f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[7] <= 19.540000f) {
                            return 0.176621f;
                        } else {
                            return 0.033942f;
                        }
                    }
                } else {
                    if (features[8] <= 20.424999f) {
                        return 1.000000f;
                    } else {
                        return 0.000000f;
                    }
                }
            } else {
                if (features[5] <= 31.915000f) {
                    if (features[8] <= 17.634999f) {
                        return 0.000000f;
                    } else {
                        return 1.000000f;
                    }
                } else {
                    return 0.000000f;
                }
            }
        } else {
            if (features[6] <= 10.500000f) {
                if (features[8] <= 11.995000f) {
                    if (features[2] <= 61.995001f) {
                        if (features[4] <= 0.906450f) {
                            return 0.391551f;
                        } else {
                            return 0.865505f;
                        }
                    } else {
                        if (features[6] <= 9.500000f) {
                            return 0.028171f;
                        } else {
                            return 0.116086f;
                        }
                    }
                } else {
                    if (features[3] <= 28.500000f) {
                        if (features[9] <= 0.393450f) {
                            return 0.134717f;
                        } else {
                            return 0.844029f;
                        }
                    } else {
                        if (features[5] <= 14.200000f) {
                            return 0.656412f;
                        } else {
                            return 0.936596f;
                        }
                    }
                }
            } else {
                if (features[3] <= 18.500000f) {
                    if (features[8] <= 12.005000f) {
                        if (features[7] <= 25.230000f) {
                            return 0.069619f;
                        } else {
                            return 0.513800f;
                        }
                    } else {
                        if (features[10] <= 0.500000f) {
                            return 0.772540f;
                        } else {
                            return 0.960893f;
                        }
                    }
                } else {
                    if (features[6] <= 19.500000f) {
                        if (features[5] <= 16.175000f) {
                            return 0.531664f;
                        } else {
                            return 0.928257f;
                        }
                    } else {
                        if (features[5] <= 15.550000f) {
                            return 0.000000f;
                        } else {
                            return 0.966410f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 5
float tree_5(float features[N_FEATURES]) {
    if (features[7] <= 19.554999f) {
        if (features[5] <= 6.475000f) {
            if (features[11] <= 0.500000f) {
                if (features[2] <= 74.884998f) {
                    if (features[4] <= 0.566400f) {
                        if (features[3] <= 15.000000f) {
                            return 1.000000f;
                        } else {
                            return 0.263359f;
                        }
                    } else {
                        if (features[8] <= 13.985000f) {
                            return 0.020292f;
                        } else {
                            return 0.049900f;
                        }
                    }
                } else {
                    if (features[1] <= 22.460000f) {
                        if (features[1] <= 22.445001f) {
                            return 0.068874f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[5] <= 0.770000f) {
                            return 0.059899f;
                        } else {
                            return 0.004888f;
                        }
                    }
                }
            } else {
                if (features[2] <= 62.355000f) {
                    if (features[2] <= 62.335001f) {
                        if (features[5] <= 5.925000f) {
                            return 0.022311f;
                        } else {
                            return 0.326315f;
                        }
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[5] <= 6.265000f) {
                        if (features[9] <= 0.389550f) {
                            return 0.036127f;
                        } else {
                            return 0.108884f;
                        }
                    } else {
                        if (features[8] <= 6.680000f) {
                            return 1.000000f;
                        } else {
                            return 0.117045f;
                        }
                    }
                }
            }
        } else {
            if (features[9] <= 0.402550f) {
                if (features[9] <= 0.381850f) {
                    if (features[1] <= 27.315000f) {
                        if (features[5] <= 13.370000f) {
                            return 0.025462f;
                        } else {
                            return 0.118669f;
                        }
                    } else {
                        if (features[11] <= 0.500000f) {
                            return 0.379991f;
                        } else {
                            return 0.044350f;
                        }
                    }
                } else {
                    if (features[4] <= 0.771550f) {
                        if (features[3] <= 19.500000f) {
                            return 0.198403f;
                        } else {
                            return 0.768926f;
                        }
                    } else {
                        if (features[4] <= 0.960700f) {
                            return 0.111736f;
                        } else {
                            return 0.842834f;
                        }
                    }
                }
            } else {
                if (features[3] <= 19.500000f) {
                    if (features[4] <= 1.119150f) {
                        if (features[9] <= 0.403350f) {
                            return 0.682043f;
                        } else {
                            return 0.050034f;
                        }
                    } else {
                        if (features[5] <= 10.750000f) {
                            return 0.300218f;
                        } else {
                            return 0.720209f;
                        }
                    }
                } else {
                    if (features[5] <= 6.740000f) {
                        if (features[7] <= 9.340000f) {
                            return 0.921862f;
                        } else {
                            return 0.403093f;
                        }
                    } else {
                        if (features[9] <= 0.421250f) {
                            return 0.667375f;
                        } else {
                            return 0.931760f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[7] <= 23.345000f) {
            if (features[8] <= 13.345000f) {
                if (features[0] <= 29.500000f) {
                    if (features[2] <= 78.209999f) {
                        if (features[2] <= 70.825001f) {
                            return 0.300218f;
                        } else {
                            return 0.872842f;
                        }
                    } else {
                        if (features[4] <= 0.536400f) {
                            return 0.517500f;
                        } else {
                            return 1.000000f;
                        }
                    }
                } else {
                    if (features[6] <= 10.500000f) {
                        if (features[4] <= 0.883050f) {
                            return 0.214899f;
                        } else {
                            return 0.616683f;
                        }
                    } else {
                        if (features[3] <= 31.000000f) {
                            return 0.106481f;
                        } else {
                            return 0.675374f;
                        }
                    }
                }
            } else {
                if (features[8] <= 15.160000f) {
                    if (features[2] <= 71.980000f) {
                        if (features[5] <= 13.650000f) {
                            return 0.433780f;
                        } else {
                            return 0.712822f;
                        }
                    } else {
                        if (features[3] <= 19.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.987557f;
                        }
                    }
                } else {
                    if (features[4] <= 1.279400f) {
                        if (features[9] <= 0.392950f) {
                            return 0.517500f;
                        } else {
                            return 0.875063f;
                        }
                    } else {
                        if (features[9] <= 0.529800f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    }
                }
            }
        } else {
            if (features[1] <= 27.105000f) {
                if (features[10] <= 0.500000f) {
                    if (features[5] <= 18.670000f) {
                        if (features[5] <= 15.045000f) {
                            return 1.000000f;
                        } else {
                            return 0.691893f;
                        }
                    } else {
                        if (features[4] <= 0.639250f) {
                            return 0.000000f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[5] <= 20.165000f) {
                        if (features[5] <= 20.005000f) {
                            return 0.832699f;
                        } else {
                            return 0.603825f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.050897f;
                        } else {
                            return 0.939190f;
                        }
                    }
                }
            } else {
                if (features[5] <= 17.150000f) {
                    if (features[3] <= 9.000000f) {
                        return 0.000000f;
                    } else {
                        if (features[9] <= 0.516400f) {
                            return 0.986207f;
                        } else {
                            return 0.762899f;
                        }
                    }
                } else {
                    if (features[3] <= 9.500000f) {
                        if (features[7] <= 44.690001f) {
                            return 0.017419f;
                        } else {
                            return 0.263359f;
                        }
                    } else {
                        if (features[4] <= 0.614250f) {
                            return 0.916993f;
                        } else {
                            return 0.976963f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 6
float tree_6(float features[N_FEATURES]) {
    if (features[7] <= 19.155000f) {
        if (features[1] <= 28.945001f) {
            if (features[8] <= 15.025000f) {
                if (features[5] <= 8.125000f) {
                    if (features[1] <= 22.515000f) {
                        if (features[0] <= 89.500000f) {
                            return 0.033616f;
                        } else {
                            return 0.092237f;
                        }
                    } else {
                        if (features[5] <= 1.935000f) {
                            return 0.033873f;
                        } else {
                            return 0.016201f;
                        }
                    }
                } else {
                    if (features[9] <= 0.415250f) {
                        if (features[8] <= 12.055000f) {
                            return 0.031321f;
                        } else {
                            return 0.130552f;
                        }
                    } else {
                        if (features[1] <= 27.775000f) {
                            return 0.593917f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            } else {
                if (features[7] <= 9.185000f) {
                    if (features[0] <= 80.500000f) {
                        if (features[3] <= 82.000000f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[9] <= 0.438700f) {
                            return 0.069619f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[3] <= 19.500000f) {
                        if (features[9] <= 0.459550f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[0] <= 71.500000f) {
                            return 0.895619f;
                        } else {
                            return 0.700091f;
                        }
                    }
                }
            }
        } else {
            if (features[8] <= 15.015000f) {
                if (features[7] <= 15.135000f) {
                    if (features[0] <= 67.500000f) {
                        if (features[9] <= 0.390750f) {
                            return 0.116386f;
                        } else {
                            return 0.572773f;
                        }
                    } else {
                        if (features[5] <= 9.455000f) {
                            return 0.029851f;
                        } else {
                            return 0.263359f;
                        }
                    }
                } else {
                    if (features[0] <= 57.500000f) {
                        if (features[1] <= 30.050000f) {
                            return 0.842834f;
                        } else {
                            return 0.546815f;
                        }
                    } else {
                        if (features[9] <= 0.381800f) {
                            return 0.906128f;
                        } else {
                            return 0.096865f;
                        }
                    }
                }
            } else {
                if (features[8] <= 15.645000f) {
                    if (features[0] <= 77.500000f) {
                        if (features[3] <= 21.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.968050f;
                        }
                    } else {
                        if (features[2] <= 74.849998f) {
                            return 0.142984f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[5] <= 6.330000f) {
                        if (features[3] <= 36.500000f) {
                            return 0.065145f;
                        } else {
                            return 0.021313f;
                        }
                    } else {
                        if (features[5] <= 6.765000f) {
                            return 0.510259f;
                        } else {
                            return 0.771173f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[7] <= 23.165000f) {
            if (features[3] <= 28.500000f) {
                if (features[8] <= 15.885000f) {
                    if (features[0] <= 44.500000f) {
                        if (features[7] <= 22.215000f) {
                            return 0.012682f;
                        } else {
                            return 0.215921f;
                        }
                    } else {
                        if (features[7] <= 20.185000f) {
                            return 0.453187f;
                        } else {
                            return 0.154069f;
                        }
                    }
                } else {
                    if (features[9] <= 0.413850f) {
                        return 1.000000f;
                    } else {
                        if (features[4] <= 1.110350f) {
                            return 0.525179f;
                        } else {
                            return 0.846530f;
                        }
                    }
                }
            } else {
                if (features[8] <= 12.905000f) {
                    if (features[5] <= 16.315000f) {
                        if (features[9] <= 0.381350f) {
                            return 0.403658f;
                        } else {
                            return 0.885351f;
                        }
                    } else {
                        if (features[8] <= 7.975000f) {
                            return 1.000000f;
                        } else {
                            return 0.737011f;
                        }
                    }
                } else {
                    if (features[8] <= 14.945000f) {
                        if (features[2] <= 70.575001f) {
                            return 0.787162f;
                        } else {
                            return 0.988891f;
                        }
                    } else {
                        if (features[7] <= 21.085000f) {
                            return 0.987332f;
                        } else {
                            return 0.954368f;
                        }
                    }
                }
            }
        } else {
            if (features[3] <= 9.500000f) {
                if (features[4] <= 1.276300f) {
                    if (features[7] <= 45.100000f) {
                        if (features[0] <= 24.500000f) {
                            return 0.025771f;
                        } else {
                            return 0.063975f;
                        }
                    } else {
                        if (features[0] <= 2.000000f) {
                            return 0.000000f;
                        } else {
                            return 0.445800f;
                        }
                    }
                } else {
                    return 0.682043f;
                }
            } else {
                if (features[7] <= 25.705000f) {
                    if (features[3] <= 18.500000f) {
                        if (features[1] <= 27.485000f) {
                            return 0.202566f;
                        } else {
                            return 0.903705f;
                        }
                    } else {
                        if (features[3] <= 44.500000f) {
                            return 0.915679f;
                        } else {
                            return 0.972573f;
                        }
                    }
                } else {
                    if (features[9] <= 0.350950f) {
                        if (features[1] <= 27.639999f) {
                            return 0.930955f;
                        } else {
                            return 0.720209f;
                        }
                    } else {
                        if (features[4] <= 1.298800f) {
                            return 0.971625f;
                        } else {
                            return 0.517500f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 7
float tree_7(float features[N_FEATURES]) {
    if (features[0] <= 49.500000f) {
        if (features[10] <= 0.500000f) {
            if (features[5] <= 15.205000f) {
                if (features[9] <= 0.383850f) {
                    if (features[7] <= 21.885000f) {
                        if (features[7] <= 18.134999f) {
                            return 0.027152f;
                        } else {
                            return 0.175879f;
                        }
                    } else {
                        if (features[3] <= 34.000000f) {
                            return 0.192469f;
                        } else {
                            return 0.947022f;
                        }
                    }
                } else {
                    if (features[8] <= 13.570000f) {
                        if (features[2] <= 65.805000f) {
                            return 0.728360f;
                        } else {
                            return 0.484130f;
                        }
                    } else {
                        if (features[7] <= 19.950000f) {
                            return 0.000000f;
                        } else {
                            return 0.901152f;
                        }
                    }
                }
            } else {
                if (features[9] <= 0.373500f) {
                    if (features[8] <= 12.170000f) {
                        if (features[5] <= 18.670000f) {
                            return 0.470836f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[4] <= 0.749950f) {
                            return 0.699143f;
                        } else {
                            return 0.906128f;
                        }
                    }
                } else {
                    if (features[7] <= 22.090000f) {
                        if (features[2] <= 74.455002f) {
                            return 0.546815f;
                        } else {
                            return 0.931856f;
                        }
                    } else {
                        if (features[1] <= 32.145000f) {
                            return 0.859977f;
                        } else {
                            return 0.963339f;
                        }
                    }
                }
            }
        } else {
            if (features[3] <= 9.500000f) {
                if (features[7] <= 44.810001f) {
                    if (features[5] <= 18.575000f) {
                        if (features[1] <= 24.495000f) {
                            return 0.080005f;
                        } else {
                            return 0.588486f;
                        }
                    } else {
                        if (features[3] <= 4.500000f) {
                            return 0.012509f;
                        } else {
                            return 0.047727f;
                        }
                    }
                } else {
                    if (features[7] <= 45.280001f) {
                        if (features[5] <= 27.599999f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[8] <= 18.575001f) {
                            return 0.517500f;
                        } else {
                            return 0.000000f;
                        }
                    }
                }
            } else {
                if (features[3] <= 19.500000f) {
                    if (features[8] <= 11.665000f) {
                        if (features[2] <= 67.450001f) {
                            return 0.830596f;
                        } else {
                            return 0.339855f;
                        }
                    } else {
                        if (features[9] <= 0.493350f) {
                            return 0.966819f;
                        } else {
                            return 0.707021f;
                        }
                    }
                } else {
                    if (features[2] <= 75.875000f) {
                        if (features[8] <= 10.855000f) {
                            return 0.953374f;
                        } else {
                            return 0.973117f;
                        }
                    } else {
                        if (features[3] <= 21.500000f) {
                            return 0.789646f;
                        } else {
                            return 0.991786f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[4] <= 0.961900f) {
            if (features[1] <= 29.065000f) {
                if (features[4] <= 0.926150f) {
                    if (features[5] <= 12.985000f) {
                        if (features[0] <= 59.500000f) {
                            return 0.068200f;
                        } else {
                            return 0.018145f;
                        }
                    } else {
                        if (features[1] <= 28.940001f) {
                            return 0.250542f;
                        } else {
                            return 0.865505f;
                        }
                    }
                } else {
                    if (features[5] <= 11.875000f) {
                        if (features[3] <= 14.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.094726f;
                        }
                    } else {
                        if (features[9] <= 0.417050f) {
                            return 0.371028f;
                        } else {
                            return 0.797269f;
                        }
                    }
                }
            } else {
                if (features[7] <= 8.855000f) {
                    if (features[7] <= 8.240000f) {
                        if (features[2] <= 74.735001f) {
                            return 0.038782f;
                        } else {
                            return 0.013108f;
                        }
                    } else {
                        if (features[8] <= 14.745000f) {
                            return 0.000000f;
                        } else {
                            return 0.318021f;
                        }
                    }
                } else {
                    if (features[3] <= 20.500000f) {
                        if (features[11] <= 0.500000f) {
                            return 0.189633f;
                        } else {
                            return 0.091364f;
                        }
                    } else {
                        if (features[8] <= 15.005000f) {
                            return 0.438211f;
                        } else {
                            return 0.937873f;
                        }
                    }
                }
            }
        } else {
            if (features[0] <= 79.500000f) {
                if (features[0] <= 74.500000f) {
                    if (features[5] <= 10.845000f) {
                        if (features[9] <= 0.428500f) {
                            return 0.254003f;
                        } else {
                            return 0.750979f;
                        }
                    } else {
                        if (features[3] <= 10.500000f) {
                            return 0.069997f;
                        } else {
                            return 0.881447f;
                        }
                    }
                } else {
                    if (features[2] <= 60.190001f) {
                        if (features[7] <= 9.185000f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[3] <= 29.500000f) {
                            return 0.095428f;
                        } else {
                            return 0.720662f;
                        }
                    }
                }
            } else {
                if (features[7] <= 5.860000f) {
                    if (features[9] <= 0.480150f) {
                        if (features[4] <= 1.137500f) {
                            return 0.006269f;
                        } else {
                            return 0.046486f;
                        }
                    } else {
                        if (features[8] <= 18.080000f) {
                            return 0.433780f;
                        } else {
                            return 0.019475f;
                        }
                    }
                } else {
                    if (features[4] <= 1.015400f) {
                        if (features[3] <= 11.500000f) {
                            return 0.616683f;
                        } else {
                            return 0.069319f;
                        }
                    } else {
                        if (features[3] <= 99.500000f) {
                            return 0.022311f;
                        } else {
                            return 0.682043f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 8
float tree_8(float features[N_FEATURES]) {
    if (features[7] <= 19.525001f) {
        if (features[0] <= 79.500000f) {
            if (features[8] <= 14.925000f) {
                if (features[1] <= 28.945001f) {
                    if (features[9] <= 0.412700f) {
                        if (features[5] <= 13.080000f) {
                            return 0.045884f;
                        } else {
                            return 0.170118f;
                        }
                    } else {
                        if (features[5] <= 10.600000f) {
                            return 0.222904f;
                        } else {
                            return 0.692528f;
                        }
                    }
                } else {
                    if (features[5] <= 11.865000f) {
                        if (features[4] <= 0.691450f) {
                            return 0.039135f;
                        } else {
                            return 0.211440f;
                        }
                    } else {
                        if (features[3] <= 25.500000f) {
                            return 0.082045f;
                        } else {
                            return 0.840388f;
                        }
                    }
                }
            } else {
                if (features[0] <= 77.500000f) {
                    if (features[8] <= 16.575000f) {
                        if (features[4] <= 0.844500f) {
                            return 0.778835f;
                        } else {
                            return 0.638271f;
                        }
                    } else {
                        if (features[5] <= 6.720000f) {
                            return 0.000000f;
                        } else {
                            return 0.803847f;
                        }
                    }
                } else {
                    if (features[2] <= 70.510002f) {
                        if (features[1] <= 32.484999f) {
                            return 0.555811f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[3] <= 25.000000f) {
                            return 0.125113f;
                        } else {
                            return 0.874553f;
                        }
                    }
                }
            }
        } else {
            if (features[9] <= 0.392200f) {
                if (features[0] <= 96.500000f) {
                    if (features[1] <= 22.335000f) {
                        if (features[1] <= 22.205000f) {
                            return 0.000000f;
                        } else {
                            return 0.151648f;
                        }
                    } else {
                        if (features[2] <= 74.264999f) {
                            return 0.012757f;
                        } else {
                            return 0.001918f;
                        }
                    }
                } else {
                    if (features[5] <= 0.725000f) {
                        if (features[7] <= 0.335000f) {
                            return 0.052134f;
                        } else {
                            return 0.006537f;
                        }
                    } else {
                        if (features[4] <= 0.782150f) {
                            return 0.084192f;
                        } else {
                            return 0.562755f;
                        }
                    }
                }
            } else {
                if (features[7] <= 5.780000f) {
                    if (features[8] <= 18.010000f) {
                        if (features[1] <= 32.195000f) {
                            return 0.018742f;
                        } else {
                            return 0.079023f;
                        }
                    } else {
                        if (features[8] <= 18.040000f) {
                            return 0.391551f;
                        } else {
                            return 0.068276f;
                        }
                    }
                } else {
                    if (features[7] <= 5.800000f) {
                        return 0.682043f;
                    } else {
                        if (features[3] <= 1.500000f) {
                            return 0.263359f;
                        } else {
                            return 0.059666f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[3] <= 9.500000f) {
            if (features[1] <= 32.875000f) {
                if (features[10] <= 0.500000f) {
                    if (features[0] <= 60.000000f) {
                        if (features[2] <= 79.799999f) {
                            return 0.011649f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[7] <= 24.634999f) {
                        if (features[3] <= 2.500000f) {
                            return 0.728360f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[5] <= 18.580000f) {
                            return 0.220119f;
                        } else {
                            return 0.039877f;
                        }
                    }
                }
            } else {
                if (features[0] <= 5.000000f) {
                    return 0.865505f;
                } else {
                    if (features[4] <= 0.770250f) {
                        return 0.000000f;
                    } else {
                        return 0.000000f;
                    }
                }
            }
        } else {
            if (features[3] <= 19.500000f) {
                if (features[7] <= 25.365001f) {
                    if (features[9] <= 0.399950f) {
                        if (features[5] <= 17.330000f) {
                            return 0.039986f;
                        } else {
                            return 0.432485f;
                        }
                    } else {
                        if (features[1] <= 27.990000f) {
                            return 0.000000f;
                        } else {
                            return 0.865505f;
                        }
                    }
                } else {
                    if (features[1] <= 27.380000f) {
                        if (features[1] <= 22.265000f) {
                            return 0.000000f;
                        } else {
                            return 0.759226f;
                        }
                    } else {
                        if (features[3] <= 12.500000f) {
                            return 1.000000f;
                        } else {
                            return 0.951813f;
                        }
                    }
                }
            } else {
                if (features[9] <= 0.381850f) {
                    if (features[6] <= 19.500000f) {
                        if (features[5] <= 15.095000f) {
                            return 0.399185f;
                        } else {
                            return 0.739621f;
                        }
                    } else {
                        if (features[6] <= 20.500000f) {
                            return 0.838956f;
                        } else {
                            return 0.968676f;
                        }
                    }
                } else {
                    if (features[5] <= 14.485000f) {
                        if (features[4] <= 0.883050f) {
                            return 0.600249f;
                        } else {
                            return 0.907459f;
                        }
                    } else {
                        if (features[9] <= 0.534450f) {
                            return 0.970402f;
                        } else {
                            return 0.641264f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 9
float tree_9(float features[N_FEATURES]) {
    if (features[10] <= 0.500000f) {
        if (features[9] <= 0.379150f) {
            if (features[9] <= 0.359450f) {
                if (features[3] <= 30.500000f) {
                    if (features[3] <= 18.500000f) {
                        if (features[9] <= 0.335350f) {
                            return 0.000000f;
                        } else {
                            return 0.017974f;
                        }
                    } else {
                        if (features[1] <= 27.635000f) {
                            return 0.049463f;
                        } else {
                            return 0.263359f;
                        }
                    }
                } else {
                    if (features[6] <= 10.500000f) {
                        if (features[5] <= 16.090000f) {
                            return 0.024935f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[4] <= 0.540800f) {
                            return 0.156062f;
                        } else {
                            return 0.688369f;
                        }
                    }
                }
            } else {
                if (features[6] <= 0.500000f) {
                    if (features[5] <= 12.505000f) {
                        if (features[7] <= 13.925000f) {
                            return 0.020883f;
                        } else {
                            return 0.120529f;
                        }
                    } else {
                        if (features[3] <= 26.000000f) {
                            return 0.000000f;
                        } else {
                            return 0.590802f;
                        }
                    }
                } else {
                    if (features[0] <= 39.500000f) {
                        if (features[9] <= 0.378500f) {
                            return 0.787361f;
                        } else {
                            return 0.349073f;
                        }
                    } else {
                        if (features[3] <= 30.500000f) {
                            return 0.070380f;
                        } else {
                            return 0.718719f;
                        }
                    }
                }
            }
        } else {
            if (features[0] <= 79.500000f) {
                if (features[8] <= 14.925000f) {
                    if (features[6] <= 0.500000f) {
                        if (features[5] <= 11.105000f) {
                            return 0.110306f;
                        } else {
                            return 0.361274f;
                        }
                    } else {
                        if (features[0] <= 40.500000f) {
                            return 0.877305f;
                        } else {
                            return 0.679559f;
                        }
                    }
                } else {
                    if (features[5] <= 11.360000f) {
                        if (features[1] <= 29.765000f) {
                            return 0.578804f;
                        } else {
                            return 0.739270f;
                        }
                    } else {
                        if (features[5] <= 18.804999f) {
                            return 0.848180f;
                        } else {
                            return 0.909350f;
                        }
                    }
                }
            } else {
                if (features[2] <= 60.164999f) {
                    if (features[4] <= 1.118650f) {
                        return 0.000000f;
                    } else {
                        if (features[5] <= 3.560000f) {
                            return 0.000000f;
                        } else {
                            return 0.810970f;
                        }
                    }
                } else {
                    if (features[1] <= 31.045000f) {
                        if (features[0] <= 85.500000f) {
                            return 0.045054f;
                        } else {
                            return 0.013642f;
                        }
                    } else {
                        if (features[8] <= 19.185000f) {
                            return 0.051643f;
                        } else {
                            return 0.008859f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[8] <= 9.405000f) {
            if (features[1] <= 25.115001f) {
                if (features[0] <= 19.500000f) {
                    if (features[9] <= 0.328900f) {
                        if (features[1] <= 22.335000f) {
                            return 0.687373f;
                        } else {
                            return 0.889270f;
                        }
                    } else {
                        if (features[0] <= 1.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.722587f;
                        }
                    }
                } else {
                    if (features[7] <= 24.500000f) {
                        if (features[2] <= 79.670002f) {
                            return 0.791216f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[1] <= 22.474999f) {
                            return 0.198403f;
                        } else {
                            return 0.603085f;
                        }
                    }
                }
            } else {
                if (features[2] <= 79.780003f) {
                    return 0.000000f;
                } else {
                    return 1.000000f;
                }
            }
        } else {
            if (features[2] <= 67.910000f) {
                if (features[2] <= 60.025000f) {
                    if (features[9] <= 0.462200f) {
                        return 1.000000f;
                    } else {
                        return 0.416918f;
                    }
                } else {
                    if (features[1] <= 32.715000f) {
                        if (features[0] <= 25.500000f) {
                            return 0.896505f;
                        } else {
                            return 0.955842f;
                        }
                    } else {
                        if (features[0] <= 8.000000f) {
                            return 1.000000f;
                        } else {
                            return 0.641264f;
                        }
                    }
                }
            } else {
                if (features[1] <= 23.945001f) {
                    if (features[6] <= 34.000000f) {
                        if (features[3] <= 25.000000f) {
                            return 0.000000f;
                        } else {
                            return 0.855051f;
                        }
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[4] <= 0.863950f) {
                        if (features[5] <= 23.845000f) {
                            return 0.841808f;
                        } else {
                            return 0.891159f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.032430f;
                        } else {
                            return 0.957122f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 10
float tree_10(float features[N_FEATURES]) {
    if (features[6] <= 0.500000f) {
        if (features[7] <= 16.355000f) {
            if (features[5] <= 6.615000f) {
                if (features[8] <= 12.945000f) {
                    if (features[8] <= 6.810000f) {
                        if (features[8] <= 6.795000f) {
                            return 0.066731f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[8] <= 7.880000f) {
                            return 0.052560f;
                        } else {
                            return 0.011524f;
                        }
                    }
                } else {
                    if (features[7] <= 10.535000f) {
                        if (features[11] <= 0.500000f) {
                            return 0.031603f;
                        } else {
                            return 0.110709f;
                        }
                    } else {
                        return 1.000000f;
                    }
                }
            } else {
                if (features[9] <= 0.392950f) {
                    if (features[8] <= 13.925000f) {
                        if (features[11] <= 0.500000f) {
                            return 0.053335f;
                        } else {
                            return 0.021836f;
                        }
                    } else {
                        if (features[4] <= 0.640500f) {
                            return 0.665760f;
                        } else {
                            return 0.235591f;
                        }
                    }
                } else {
                    if (features[0] <= 64.500000f) {
                        if (features[2] <= 72.864998f) {
                            return 0.312933f;
                        } else {
                            return 0.762899f;
                        }
                    } else {
                        if (features[8] <= 15.005000f) {
                            return 0.132863f;
                        } else {
                            return 0.741529f;
                        }
                    }
                }
            }
        } else {
            if (features[9] <= 0.401350f) {
                if (features[7] <= 18.389999f) {
                    if (features[8] <= 12.300000f) {
                        if (features[4] <= 0.890700f) {
                            return 0.000000f;
                        } else {
                            return 0.198403f;
                        }
                    } else {
                        if (features[4] <= 0.752700f) {
                            return 0.549037f;
                        } else {
                            return 0.230953f;
                        }
                    }
                } else {
                    if (features[1] <= 28.980000f) {
                        if (features[3] <= 66.500000f) {
                            return 0.026765f;
                        } else {
                            return 0.424418f;
                        }
                    } else {
                        if (features[9] <= 0.381300f) {
                            return 1.000000f;
                        } else {
                            return 0.722587f;
                        }
                    }
                }
            } else {
                if (features[5] <= 14.525000f) {
                    if (features[0] <= 53.500000f) {
                        if (features[1] <= 27.350000f) {
                            return 0.439392f;
                        } else {
                            return 0.673803f;
                        }
                    } else {
                        if (features[3] <= 10.500000f) {
                            return 0.000000f;
                        } else {
                            return 0.871440f;
                        }
                    }
                } else {
                    if (features[5] <= 16.330000f) {
                        if (features[7] <= 20.935000f) {
                            return 0.988188f;
                        } else {
                            return 0.873046f;
                        }
                    } else {
                        return 0.517500f;
                    }
                }
            }
        }
    } else {
        if (features[5] <= 15.185000f) {
            if (features[1] <= 27.005000f) {
                if (features[7] <= 20.455000f) {
                    if (features[2] <= 62.175001f) {
                        if (features[3] <= 27.000000f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[0] <= 39.500000f) {
                            return 0.248812f;
                        } else {
                            return 0.041303f;
                        }
                    }
                } else {
                    if (features[4] <= 0.896450f) {
                        if (features[1] <= 24.075000f) {
                            return 0.552459f;
                        } else {
                            return 0.151648f;
                        }
                    } else {
                        if (features[8] <= 11.825000f) {
                            return 1.000000f;
                        } else {
                            return 0.805718f;
                        }
                    }
                }
            } else {
                if (features[7] <= 18.820001f) {
                    if (features[2] <= 76.455002f) {
                        return 1.000000f;
                    } else {
                        return 0.000000f;
                    }
                } else {
                    if (features[2] <= 77.075001f) {
                        if (features[5] <= 15.165000f) {
                            return 0.877717f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        return 0.000000f;
                    }
                }
            }
        } else {
            if (features[3] <= 9.500000f) {
                if (features[7] <= 44.810001f) {
                    if (features[0] <= 9.500000f) {
                        return 0.000000f;
                    } else {
                        if (features[6] <= 38.500000f) {
                            return 0.033165f;
                        } else {
                            return 0.128872f;
                        }
                    }
                } else {
                    if (features[8] <= 19.849999f) {
                        if (features[5] <= 30.349999f) {
                            return 0.000000f;
                        } else {
                            return 0.433780f;
                        }
                    } else {
                        return 1.000000f;
                    }
                }
            } else {
                if (features[7] <= 22.995000f) {
                    if (features[10] <= 0.500000f) {
                        if (features[7] <= 20.345000f) {
                            return 0.416918f;
                        } else {
                            return 0.685223f;
                        }
                    } else {
                        if (features[8] <= 8.205000f) {
                            return 0.983623f;
                        } else {
                            return 0.753961f;
                        }
                    }
                } else {
                    if (features[4] <= 0.605050f) {
                        if (features[0] <= 19.500000f) {
                            return 0.932178f;
                        } else {
                            return 0.802384f;
                        }
                    } else {
                        if (features[7] <= 26.515000f) {
                            return 0.926192f;
                        } else {
                            return 0.972132f;
                        }
                    }
                }
            }
        }
    }
}

// Tree 11
float tree_11(float features[N_FEATURES]) {
    if (features[5] <= 14.425000f) {
        if (features[1] <= 29.015000f) {
            if (features[8] <= 14.945000f) {
                if (features[8] <= 11.995000f) {
                    if (features[0] <= 47.500000f) {
                        if (features[7] <= 20.555000f) {
                            return 0.070439f;
                        } else {
                            return 0.493680f;
                        }
                    } else {
                        if (features[8] <= 7.880000f) {
                            return 0.051385f;
                        } else {
                            return 0.015925f;
                        }
                    }
                } else {
                    if (features[7] <= 17.235000f) {
                        if (features[2] <= 60.924999f) {
                            return 0.211440f;
                        } else {
                            return 0.046018f;
                        }
                    } else {
                        if (features[3] <= 29.500000f) {
                            return 0.058804f;
                        } else {
                            return 0.595519f;
                        }
                    }
                }
            } else {
                if (features[4] <= 1.005300f) {
                    if (features[5] <= 9.315000f) {
                        if (features[4] <= 0.978150f) {
                            return 0.109192f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[1] <= 28.195001f) {
                            return 0.416918f;
                        } else {
                            return 0.789646f;
                        }
                    }
                } else {
                    if (features[7] <= 9.030000f) {
                        if (features[8] <= 15.210000f) {
                            return 0.132863f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[7] <= 21.355000f) {
                            return 0.805493f;
                        } else {
                            return 0.349073f;
                        }
                    }
                }
            }
        } else {
            if (features[5] <= 6.315000f) {
                if (features[2] <= 74.165001f) {
                    if (features[11] <= 0.500000f) {
                        if (features[2] <= 74.140003f) {
                            return 0.025525f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[9] <= 0.426100f) {
                            return 0.401318f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[1] <= 32.655001f) {
                        if (features[7] <= 5.760000f) {
                            return 0.000000f;
                        } else {
                            return 0.008715f;
                        }
                    } else {
                        if (features[7] <= 6.660000f) {
                            return 0.038206f;
                        } else {
                            return 0.234561f;
                        }
                    }
                }
            } else {
                if (features[7] <= 15.725000f) {
                    if (features[9] <= 0.391300f) {
                        if (features[5] <= 11.175000f) {
                            return 0.158659f;
                        } else {
                            return 0.616683f;
                        }
                    } else {
                        if (features[0] <= 79.500000f) {
                            return 0.722532f;
                        } else {
                            return 0.000000f;
                        }
                    }
                } else {
                    if (features[3] <= 10.500000f) {
                        if (features[4] <= 1.216950f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    } else {
                        if (features[4] <= 0.716750f) {
                            return 0.658769f;
                        } else {
                            return 0.943749f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[9] <= 0.368150f) {
            if (features[6] <= 20.500000f) {
                if (features[3] <= 29.500000f) {
                    if (features[2] <= 79.945000f) {
                        if (features[5] <= 16.650000f) {
                            return 0.000000f;
                        } else {
                            return 0.224061f;
                        }
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[0] <= 39.500000f) {
                        if (features[7] <= 20.345000f) {
                            return 0.343483f;
                        } else {
                            return 0.752555f;
                        }
                    } else {
                        if (features[8] <= 11.995000f) {
                            return 0.015306f;
                        } else {
                            return 0.855051f;
                        }
                    }
                }
            } else {
                if (features[4] <= 0.475350f) {
                    if (features[3] <= 25.500000f) {
                        return 0.000000f;
                    } else {
                        return 1.000000f;
                    }
                } else {
                    if (features[1] <= 22.095000f) {
                        return 1.000000f;
                    } else {
                        if (features[9] <= 0.367650f) {
                            return 0.848991f;
                        } else {
                            return 0.600249f;
                        }
                    }
                }
            }
        } else {
            if (features[7] <= 23.155000f) {
                if (features[3] <= 15.000000f) {
                    if (features[1] <= 31.809999f) {
                        if (features[7] <= 20.445000f) {
                            return 0.118218f;
                        } else {
                            return 0.000000f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.000000f;
                        } else {
                            return 1.000000f;
                        }
                    }
                } else {
                    if (features[8] <= 13.425000f) {
                        if (features[6] <= 7.500000f) {
                            return 0.805331f;
                        } else {
                            return 0.476894f;
                        }
                    } else {
                        if (features[3] <= 30.000000f) {
                            return 0.788052f;
                        } else {
                            return 0.968105f;
                        }
                    }
                }
            } else {
                if (features[1] <= 32.315001f) {
                    if (features[5] <= 23.685000f) {
                        if (features[6] <= 28.500000f) {
                            return 0.888669f;
                        } else {
                            return 0.940189f;
                        }
                    } else {
                        if (features[3] <= 9.500000f) {
                            return 0.045823f;
                        } else {
                            return 0.975862f;
                        }
                    }
                } else {
                    if (features[3] <= 7.500000f) {
                        if (features[9] <= 0.520050f) {
                            return 0.000000f;
                        } else {
                            return 0.349073f;
                        }
                    } else {
                        if (features[3] <= 9.000000f) {
                            return 0.682043f;
                        } else {
                            return 0.981573f;
                        }
                    }
                }
            }
        }
    }
}


/*
 * Feature Engineering Functions
 * Compute engineered features from raw sensor readings
 */

void compute_features(float soil_moisture, float temperature, float humidity, 
                     float water_level, float features[N_FEATURES]) {
    
    // Base sensor readings
    features[FEAT_SOIL_MOISTURE] = soil_moisture;
    features[FEAT_TEMPERATURE] = temperature;
    features[FEAT_HUMIDITY] = humidity;
    features[FEAT_WATER_LEVEL] = water_level;
    
    // Engineered Feature 1: Evapotranspiration rate
    // Represents water loss through evaporation and plant transpiration
    features[FEAT_ET_RATE] = (temperature * (100.0f - humidity)) / 1000.0f;
    
    // Engineered Feature 2: Soil-temperature stress
    // Combines dry soil with heat stress
    features[FEAT_SOIL_TEMP_STRESS] = ((100.0f - soil_moisture) * temperature) / 100.0f;
    
    // Engineered Feature 3: Moisture deficit
    // How far soil moisture is below optimal (50%)
    features[FEAT_MOISTURE_DEFICIT] = max(0.0f, 50.0f - soil_moisture);
    
    // Engineered Feature 4: Combined stress index
    // Multi-factor plant stress indicator
    features[FEAT_STRESS_INDEX] = ((100.0f - soil_moisture) * temperature) / (humidity + 1.0f);
    
    // Engineered Feature 5: Vapor Pressure Deficit index
    // Simplified VPD - measures "thirstiness" of air
    features[FEAT_VPD_INDEX] = temperature - (humidity / 5.0f);
    
    // Engineered Feature 6: Temperature-humidity ratio
    // Air dryness indicator
    features[FEAT_TEMP_HUM_RATIO] = temperature / (humidity + 1.0f);
    
    // Engineered Feature 7: Critical dry threshold
    // Binary flag for very dry soil (<30%)
    features[FEAT_CRITICAL_DRY] = (soil_moisture < 30.0f) ? 1.0f : 0.0f;
    
    // Engineered Feature 8: Optimal moisture flag
    // Binary flag for ideal moisture range (60-80%)
    features[FEAT_OPTIMAL_MOISTURE] = (soil_moisture >= 60.0f && soil_moisture <= 80.0f) ? 1.0f : 0.0f;
}

/*
 * Main Prediction Function
 * Returns: 1 = irrigation needed, 0 = no action
 */
int predict_irrigation(float soil_moisture, float temperature, float humidity, float water_level) {
    float features[N_FEATURES];
    
    // Compute all features from sensor readings
    compute_features(soil_moisture, temperature, humidity, water_level, features);
    
    // Accumulate predictions from all trees
    float sum = 0.0f;
    sum += tree_0(features);
    sum += tree_1(features);
    sum += tree_2(features);
    sum += tree_3(features);
    sum += tree_4(features);
    sum += tree_5(features);
    sum += tree_6(features);
    sum += tree_7(features);
    sum += tree_8(features);
    sum += tree_9(features);
    sum += tree_10(features);
    sum += tree_11(features);
    
    // Average and apply threshold
    float avg = sum / N_TREES;
    return (avg > 0.5f) ? 1 : 0;
}

/*
 * Get Prediction Probability
 * Returns: probability of needing irrigation (0.0 to 1.0)
 */
float predict_irrigation_probability(float soil_moisture, float temperature, 
                                    float humidity, float water_level) {
    float features[N_FEATURES];
    compute_features(soil_moisture, temperature, humidity, water_level, features);
    
    float sum = 0.0f;
    sum += tree_0(features);
    sum += tree_1(features);
    sum += tree_2(features);
    sum += tree_3(features);
    sum += tree_4(features);
    sum += tree_5(features);
    sum += tree_6(features);
    sum += tree_7(features);
    sum += tree_8(features);
    sum += tree_9(features);
    sum += tree_10(features);
    sum += tree_11(features);
    
    return sum / N_TREES;
}

/*
 * Get Feature Values (for debugging)
 * Fills the provided array with computed feature values
 */
void get_feature_values(float soil_moisture, float temperature, float humidity, 
                       float water_level, float features[N_FEATURES]) {
    compute_features(soil_moisture, temperature, humidity, water_level, features);
}

/*
 * Model Information
 */
void print_model_info() {
    Serial.println("========================================");
    Serial.println("Enhanced Irrigation Model");
    Serial.println("========================================");
    Serial.print("Version: ");
    Serial.println(MODEL_VERSION);
    Serial.print("Accuracy: ");
    Serial.print(93.03);
    Serial.println("%");
    Serial.print("Model Size: ");
    Serial.print(43.38);
    Serial.println(" KB");
    Serial.print("Trees: ");
    Serial.println(N_TREES);
    Serial.print("Features: ");
    Serial.println(N_FEATURES);
    Serial.println("========================================");
}

#endif // IRRIGATION_MODEL_ENHANCED_H
