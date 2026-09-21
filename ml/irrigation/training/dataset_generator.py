import pandas as pd # Import pandas for data manipulation and creating the DataFrame
import numpy as np # Import numpy for numerical operations and random number generation

print("="*80) # Print a separator line
print("ENHANCED FEATURE ENGINEERING FOR 90%+ ACCURACY") # Print the script's title and goal
print("Strategy: 12-feature dataset with advanced interactions") # Describe the dataset strategy
print("="*80) # Print a separator line

np.random.seed(42) # Set the random seed for reproducibility of the generated data
n_samples = 20000 # Define the total number of data points to generate

print(f"\nGenerating {n_samples} samples with enhanced features...") # Inform the user about the process

data = [] # Initialize an empty list to hold the generated data rows

for i in range(n_samples): # Loop to generate each individual sample
    # Base sensor readings
    sm = np.random.randint(0, 101) # Generate random Soil Moisture (SM) from 0 to 100
    temp = np.random.uniform(22, 33) # Generate random Temperature (Temp) between 22 and 33
    hum = np.random.uniform(60, 80) # Generate random Humidity (Hum) between 60 and 80
    wl = np.random.randint(0, 101) # Generate random Water Level (WL) from 0 to 100
    
    # ENHANCED IRRIGATION LOGIC
    irrigation_score = 0 # Initialize the score that determines the need for irrigation
    
    # Factor 1: Soil moisture (primary driver) - Score contribution based on dryness
    if sm < 20: # Very dry soil
        irrigation_score += 4.0
    elif sm < 30: # Dry soil
        irrigation_score += 3.5
    elif sm < 40: # Moderately dry
        irrigation_score += 2.5
    elif sm < 50: # Slightly dry
        irrigation_score += 1.5
    elif sm < 60: # Acceptable, minor score
        irrigation_score += 0.8
    elif sm < 70: # Moist
        irrigation_score += 0.3
    elif sm >= 80: # High moisture - strongly discourage irrigation (negative score)
        irrigation_score -= 3.0 
    
    # Factor 2: Temperature stress - Score contribution based on heat stress
    if temp > 31:
        irrigation_score += 1.8
    elif temp > 29:
        irrigation_score += 1.2
    elif temp > 27:
        irrigation_score += 0.6
    elif temp < 23: # Low temperature - slightly discourages irrigation
        irrigation_score -= 0.3
    
    # Factor 3: Humidity (inverse relationship) - Low humidity increases water loss/need
    if hum < 62:
        irrigation_score += 1.2
    elif hum < 65:
        irrigation_score += 0.6
    elif hum > 77: # High humidity - slightly discourages irrigation
        irrigation_score -= 0.4
    
    # Factor 4: Combined temperature-humidity stress (VPD approximation)
    vpd = temp - (hum / 5.0) # Calculate a simple proxy for Vapor Pressure Deficit (VPD)
    if vpd > 15: # High VPD (high stress)
        irrigation_score += 1.5
    elif vpd > 12: # Moderate VPD
        irrigation_score += 0.8
    
    # Factor 5: Extreme conditions multiplier - Amplifies the need under severe combined stress
    if sm < 25 and temp > 30: # Very dry AND very hot
        irrigation_score *= 1.3 # Increase the final score by 30%
    
    if sm < 30 and temp > 29 and hum < 63: # Dry, hot, AND low humidity
        irrigation_score *= 1.2 # Increase the final score by 20%
    
    # Factor 6: Water availability constraint - Prevents irrigation if source is low
    if wl < 10: # Water source critically low
        irrigation_score = 0 # Force score to zero, regardless of plant need
    elif wl < 20:
        irrigation_score *= 0.6 # Reduce irrigation score (potential action) by 40%
    elif wl < 30:
        irrigation_score *= 0.8 # Reduce irrigation score (potential action) by 20%
    
    # Decision with adaptive threshold
    threshold = 2.3 + np.random.normal(0, 0.25) # Set an adaptive threshold with slight random noise
    needs_irrigation = 1 if irrigation_score > threshold else 0 # Final decision: 1 if score exceeds threshold, 0 otherwise
    
    # Reduce noise to 3%
    if np.random.random() < 0.03: # Introduce 3% random mislabeling (noise)
        needs_irrigation = 1 - needs_irrigation # Flip the target label (0 to 1 or 1 to 0)
    
    # ENGINEERED FEATURES (Features derived from the base sensors)
    
    # 1. Evapotranspiration proxy (Estimates water loss rate)
    et_rate = (temp * (100 - hum)) / 1000
    
    # 2. Soil-temperature interaction (Quantifies combined soil dryness and heat)
    soil_temp_stress = (100 - sm) * temp / 100
    
    # 3. Moisture deficit (Quantifies how far the soil moisture is from an ideal dry level, 50)
    moisture_deficit = max(0, 50 - sm)
    
    # 4. Combined stress index (A complex ratio reflecting heat/dryness vs. damping humidity)
    stress_index = ((100 - sm) * temp) / (hum + 1)
    
    # 5. Vapor Pressure Deficit (simplified) (Estimates atmospheric drying power)
    vpd_index = temp - (hum / 5)
    
    # 6. Temperature-humidity ratio (A simple proxy for evaporative demand)
    temp_hum_ratio = temp / (hum + 1)
    
    # 7. Critical threshold flag (Binary feature: 1 if soil is critically dry (<30))
    critical_dry = 1 if sm < 30 else 0
    
    # 8. Optimal moisture flag (Binary feature: 1 if soil is in the optimal range (60-80))
    optimal_moisture = 1 if 60 <= sm <= 80 else 0
    
    data.append({ # Append the generated features and target to the data list
        # Original features
        'soil_moisture': sm,
        'temperature': round(temp, 2), # Round to 2 decimal places
        'humidity': round(hum, 2),
        'water_level': wl,
        
        # Engineered features
        'et_rate': round(et_rate, 4), # Round to 4 decimal places
        'soil_temp_stress': round(soil_temp_stress, 2),
        'moisture_deficit': round(moisture_deficit, 1),
        'stress_index': round(stress_index, 2),
        'vpd_index': round(vpd_index, 2),
        'temp_hum_ratio': round(temp_hum_ratio, 4),
        'critical_dry': critical_dry,
        'optimal_moisture': optimal_moisture,
        
        # Target
        'irrigation_needed': needs_irrigation
    })

df = pd.DataFrame(data) # Convert the list of dictionaries into a pandas DataFrame

print("Dataset generated with 12 features!") # Confirm dataset generation

print("\n" + "="*80) # Print a separator
print("FEATURE ANALYSIS") # Inform about the analysis section
print("="*80) # Print a separator

print(f"\nDataset Shape: {df.shape}") # Print the final shape (rows, columns)
print(f"   Samples: {len(df)}") # Print the number of rows
print(f"   Features: {df.shape[1] - 1}") # Calculate number of features (columns - target)
print(f"   - Base Sensors: 4")
print(f"   - Engineered: 8")

print(f"\nTarget Distribution:") # Print the distribution of the target variable
target_counts = df['irrigation_needed'].value_counts().sort_index() # Count instances of 0 and 1
for cls, count in target_counts.items(): # Loop through target classes and print counts/percentages
    label = "No Irrigation" if cls == 0 else "Irrigation Needed"
    print(f"   {label}: {count} ({count/len(df)*100:.1f}%)")

print(f"\nFeature Correlations with Target:") # Print feature correlation section
correlation = df.corr()['irrigation_needed'].sort_values(ascending=False) # Calculate correlations with the target and sort
print("\n   Top 10 Predictive Features:")
for i, (feature, corr) in enumerate(list(correlation.items())[1:11], 1): # Loop through the top 10 (skipping the target itself)
    bar = '█' * int(abs(corr) * 40) # Create a text bar proportional to the absolute correlation value
    sign = '+' if corr > 0 else '-' # Determine the sign of the correlation
    print(f"   {i:2}. {feature:<25} {sign}{abs(corr):.3f} {bar}") # Print the rank, feature name, correlation value, and bar

print("\n" + "="*80) # Print a separator
print("SAVING DATASET") # Inform about saving
print("="*80) # Print a separator

df.to_csv('irrigation_enhanced_dataset.csv', index=False) # Save the DataFrame to a CSV file without the index
print("✓ Saved: irrigation_enhanced_dataset.csv") # Confirm save
print(f"   - {len(df)} samples")
print(f"   - 12 features + 1 target")
print(f"   - Ready for training")

print("\n" + "="*80) # Print a separator
print("NEXT STEP: Run train_enhanced_model.py") # Guide the user to the next script
print("="*80) # Print a separator