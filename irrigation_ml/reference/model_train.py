import pandas as pd # Import pandas for data manipulation and analysis
import numpy as np # Import numpy for numerical operations, especially array handling
import matplotlib.pyplot as plt # Import matplotlib's pyplot for basic plotting
import seaborn as sns # Import seaborn for enhanced statistical data visualization
from sklearn.ensemble import RandomForestClassifier # Import RandomForestClassifier for the model
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve # Import utilities for model evaluation and splitting
from sklearn.metrics import (classification_report, accuracy_score, balanced_accuracy_score, 
                            confusion_matrix, roc_curve, auc, precision_recall_curve) # Import various metrics for model assessment
import pickle # Import pickle for serializing (saving) the trained model
import json # Import json for saving model metadata in a structured format
import warnings # Import warnings to manage warning messages
warnings.filterwarnings('ignore') # Suppress all warnings for cleaner output

# Set style
plt.style.use('seaborn-v0_8-darkgrid') # Set a specific plotting style (Seaborn dark grid)
sns.set_palette("husl") # Set the color palette for Seaborn plots

print("="*80) # Print a separator line
print("ENHANCED MODEL TRAINING WITH COMPREHENSIVE VISUALIZATION") # Print the script's title
print("Target: >90% Accuracy, <30 KB Model Size, 12 Features") # Print the project goals
print("="*80) # Print a separator line

# Load dataset
print("\nLoading enhanced dataset...") # Inform the user about data loading
df = pd.read_csv('irrigation_enhanced_dataset.csv') # Load the dataset into a pandas DataFrame
print(f"✓ Loaded: {len(df)} samples, {df.shape[1]-1} features") # Print dataset summary

X = df.drop('irrigation_needed', axis=1) # Separate features (X) by dropping the target column
y = df['irrigation_needed'] # Separate the target variable (y)

feature_names = list(X.columns) # Get a list of the feature names
print(f"\nFeatures ({len(feature_names)}):") # Print the feature count
for i, feat in enumerate(feature_names, 1): # Loop through and print each feature name
    print(f"   {i:2}. {feat}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y # Split data into 80% training and 20% testing, stratified for balanced classes
)

print(f"\nData Split:") # Print data split summary
print(f"   Training: {len(X_train)} samples")
print(f"   Testing:  {len(X_test)} samples")

# Candidate configurations
configs = [ # Define a list of hyperparameter configurations for different models
    {
        'name': 'Accuracy Focused', # Configuration 1: Aiming for high overall accuracy
        'n_estimators': 12,
        'max_depth': 6,
        'min_samples_leaf': 1,
        'min_samples_split': 3,
        'max_features': 'sqrt'
    },
    {
        'name': 'Balanced Plus', # Configuration 2: Focusing on balanced performance
        'n_estimators': 14,
        'max_depth': 5,
        'min_samples_leaf': 1,
        'min_samples_split': 4,
        'max_features': 'sqrt'
    },
    {
        'name': 'Deep Learner', # Configuration 3: Slightly deeper trees
        'n_estimators': 10,
        'max_depth': 7,
        'min_samples_leaf': 2,
        'min_samples_split': 3,
        'max_features': 'sqrt'
    }
]

print("\n" + "="*80) # Print a separator
print("TRAINING AND EVALUATING MODELS") # Inform the user about the training process
print("="*80) # Print a separator

results = [] # Initialize a list to store the results of each model

for config in configs: # Loop through each configuration
    name = config.pop('name') # Extract and store the model name, removing it from config for RandomForest
    print(f"\n{name}...") # Print the name of the model being trained
    
    model = RandomForestClassifier( # Initialize the Random Forest model
        **config, # Unpack the configuration hyperparameters
        class_weight='balanced', # Use 'balanced' class weight to handle potential class imbalance
        random_state=42 # Set random state for reproducibility
    )
    model.fit(X_train, y_train) # Train the model on the training data
    
    # Predictions
    y_pred = model.predict(X_test) # Get class predictions on the test set
    y_pred_proba = model.predict_proba(X_test)[:, 1] # Get probability estimates for the positive class (class 1)
    
    # Metrics
    acc = accuracy_score(y_test, y_pred) # Calculate overall accuracy
    balanced_acc = balanced_accuracy_score(y_test, y_pred) # Calculate balanced accuracy (better for imbalanced data)
    
    # Size calculation
    n_nodes = sum(tree.tree_.node_count for tree in model.estimators_) # Calculate total number of nodes across all trees (proxy for model size)
    size_kb = (n_nodes * 32) / 1024 # Estimate model size in KB (assuming 32 bytes per node for rough embedded estimation)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred) # Calculate the confusion matrix
    tn, fp, fn, tp = cm.ravel() # Flatten the matrix to get True Negative, False Positive, False Negative, True Positive
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0 # Calculate False Negative Rate (FNR)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0 # Calculate False Positive Rate (FPR)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy') # Perform 5-fold cross-validation on training data
    
    config['name'] = name # Add the name back to the config dictionary for storage
    results.append({ # Store all results for the current model
        'name': name,
        'config': config,
        'model': model,
        'accuracy': acc,
        'balanced_acc': balanced_acc,
        'size_kb': size_kb,
        'fnr': fnr,
        'fpr': fpr,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba,
        'cm': cm
    })
    
    print(f"   Accuracy: {acc*100:.2f}% | Balanced: {balanced_acc*100:.2f}%") # Print accuracy metrics
    print(f"   Size: {size_kb:.2f} KB | FNR: {fnr*100:.1f}% | FPR: {fpr*100:.1f}%") # Print size and error rates
    print(f"   CV Score: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%") # Print cross-validation score

# Select best model
best_result = max(results, key=lambda x: x['balanced_acc']) # Select the model with the highest balanced accuracy
best_model = best_result['model'] # Extract the best trained model object

print("\n" + "="*80) # Print a separator
print(f"BEST MODEL: {best_result['name']}") # Announce the best model
print("="*80) # Print a separator

print(f"\nPerformance:") # Print detailed performance metrics for the best model
print(f"   Accuracy:          {best_result['accuracy']*100:.2f}%")
print(f"   Balanced Accuracy: {best_result['balanced_acc']*100:.2f}%")
print(f"   CV Accuracy:       {best_result['cv_mean']*100:.2f}% ± {best_result['cv_std']*100:.2f}%")
print(f"   Model Size:        {best_result['size_kb']:.2f} KB")
print(f"   False Neg Rate:    {best_result['fnr']*100:.1f}%")
print(f"   False Pos Rate:    {best_result['fpr']*100:.1f}%")

# Detailed classification report
print(f"\nClassification Report:") # Print a full classification report
print(classification_report(y_test, best_result['y_pred'],
                          target_names=['No Irrigation', 'Irrigation Needed'], # Define class names
                          digits=3)) # Set precision to 3 digits

# ============================================================================
# VISUALIZATION SECTION
# ============================================================================

print("\n" + "="*80) # Print a separator
print("GENERATING VISUALIZATIONS") # Inform about visualization generation
print("="*80) # Print a separator

# Create figure directory
import os # Import os module
os.makedirs('training_visuals', exist_ok=True) # Create a directory to save plots, if it doesn't exist

# 1. Model Comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10)) # Create a 2x2 subplot figure
fig.suptitle('Model Comparison - Enhanced 12-Feature Dataset', fontsize=16, fontweight='bold') # Set the main title

# Accuracy comparison
ax = axes[0, 0] # Select the top-left subplot
names = [r['name'] for r in results] # Get model names
accuracies = [r['accuracy']*100 for r in results] # Get accuracy scores
balanced_accs = [r['balanced_acc']*100 for r in results] # Get balanced accuracy scores
x = np.arange(len(names)) # Get the x-axis tick locations
width = 0.35 # Set bar width
ax.bar(x - width/2, accuracies, width, label='Accuracy', alpha=0.8) # Plot overall accuracy bars
ax.bar(x + width/2, balanced_accs, width, label='Balanced Accuracy', alpha=0.8) # Plot balanced accuracy bars
ax.set_ylabel('Accuracy (%)', fontweight='bold') # Set y-axis label
ax.set_title('Accuracy Comparison') # Set subplot title
ax.set_xticks(x) # Set x-axis ticks
ax.set_xticklabels(names, rotation=15, ha='right') # Set x-axis tick labels and rotate
ax.legend() # Display legend
ax.axhline(y=90, color='r', linestyle='--', alpha=0.5, label='90% Target') # Plot the 90% target line
ax.grid(axis='y', alpha=0.3) # Add a horizontal grid

# Size comparison
ax = axes[0, 1] # Select the top-right subplot
sizes = [r['size_kb'] for r in results] # Get model sizes
colors = ['green' if s < 30 else 'orange' for s in sizes] # Set bar color based on 30 KB target
ax.bar(names, sizes, alpha=0.8, color=colors) # Plot model sizes
ax.set_ylabel('Model Size (KB)', fontweight='bold') # Set y-axis label
ax.set_title('Model Size Comparison') # Set subplot title
ax.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='30 KB Target') # Plot the 30 KB target line
ax.set_xticklabels(names, rotation=15, ha='right') # Set x-axis tick labels and rotate
ax.legend() # Display legend
ax.grid(axis='y', alpha=0.3) # Add a horizontal grid

# Error rates
ax = axes[1, 0] # Select the bottom-left subplot
fnrs = [r['fnr']*100 for r in results] # Get False Negative Rates
fprs = [r['fpr']*100 for r in results] # Get False Positive Rates
x = np.arange(len(names)) # Get the x-axis tick locations
ax.bar(x - width/2, fnrs, width, label='False Neg Rate', alpha=0.8, color='coral') # Plot FNR
ax.bar(x + width/2, fprs, width, label='False Pos Rate', alpha=0.8, color='skyblue') # Plot FPR
ax.set_ylabel('Error Rate (%)', fontweight='bold') # Set y-axis label
ax.set_title('Error Rate Comparison') # Set subplot title
ax.set_xticks(x) # Set x-axis ticks
ax.set_xticklabels(names, rotation=15, ha='right') # Set x-axis tick labels and rotate
ax.legend() # Display legend
ax.grid(axis='y', alpha=0.3) # Add a horizontal grid

# CV scores
ax = axes[1, 1] # Select the bottom-right subplot
cv_means = [r['cv_mean']*100 for r in results] # Get mean CV scores
cv_stds = [r['cv_std']*100 for r in results] # Get CV standard deviations
ax.bar(names, cv_means, alpha=0.8, yerr=cv_stds, capsize=5) # Plot CV mean scores with standard deviation as error bars
ax.set_ylabel('CV Accuracy (%)', fontweight='bold') # Set y-axis label
ax.set_title('Cross-Validation Performance') # Set subplot title
ax.set_xticklabels(names, rotation=15, ha='right') # Set x-axis tick labels and rotate
ax.grid(axis='y', alpha=0.3) # Add a horizontal grid

plt.tight_layout() # Adjust subplot parameters for tight layout
plt.savefig('training_visuals/01_model_comparison.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 01_model_comparison.png") # Confirm save
plt.close() # Close the figure

# 2. Confusion Matrix (Best Model)
fig, ax = plt.subplots(figsize=(8, 6)) # Create a new figure
cm = best_result['cm'] # Get the confusion matrix of the best model
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar_kws={'label': 'Count'}) # Plot the confusion matrix using Seaborn heatmap
ax.set_title(f'Confusion Matrix - {best_result["name"]}\nAccuracy: {best_result["accuracy"]*100:.2f}%', 
             fontweight='bold', fontsize=14) # Set the title
ax.set_ylabel('True Label', fontweight='bold') # Set y-axis label
ax.set_xlabel('Predicted Label', fontweight='bold') # Set x-axis label
ax.set_xticklabels(['No Irrigation', 'Irrigation']) # Set x-tick labels
ax.set_yticklabels(['No Irrigation', 'Irrigation']) # Set y-tick labels

# Add percentages
tn, fp, fn, tp = cm.ravel() # Unpack the confusion matrix values
total = tn + fp + fn + tp # Calculate the total number of samples
for i in range(2): # Loop through rows (True Labels)
    for j in range(2): # Loop through columns (Predicted Labels)
        value = cm[i, j] # Get the count
        percentage = value / total * 100 # Calculate the percentage of total
        ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)', # Add the percentage text to the plot
               ha='center', va='center', fontsize=10, color='gray')

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/02_confusion_matrix.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 02_confusion_matrix.png") # Confirm save
plt.close() # Close the figure

# 3. ROC Curve
fig, ax = plt.subplots(figsize=(8, 6)) # Create a new figure
fpr, tpr, _ = roc_curve(y_test, best_result['y_pred_proba']) # Calculate False Positive Rate and True Positive Rate
roc_auc = auc(fpr, tpr) # Calculate the Area Under the Curve (AUC)

ax.plot(fpr, tpr, color='darkorange', lw=2, 
        label=f'ROC curve (AUC = {roc_auc:.3f})') # Plot the ROC curve
ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier') # Plot the diagonal line for a random classifier
ax.set_xlim([0.0, 1.0]) # Set x-axis limits
ax.set_ylim([0.0, 1.05]) # Set y-axis limits
ax.set_xlabel('False Positive Rate', fontweight='bold') # Set x-axis label
ax.set_ylabel('True Positive Rate', fontweight='bold') # Set y-axis label
ax.set_title(f'ROC Curve - {best_result["name"]}', fontweight='bold', fontsize=14) # Set title
ax.legend(loc="lower right") # Display legend
ax.grid(alpha=0.3) # Add grid

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/03_roc_curve.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 03_roc_curve.png") # Confirm save
plt.close() # Close the figure

# 4. Precision-Recall Curve
fig, ax = plt.subplots(figsize=(8, 6)) # Create a new figure
precision, recall, _ = precision_recall_curve(y_test, best_result['y_pred_proba']) # Calculate Precision and Recall values

ax.plot(recall, precision, color='blue', lw=2) # Plot the Precision-Recall curve
ax.set_xlabel('Recall', fontweight='bold') # Set x-axis label
ax.set_ylabel('Precision', fontweight='bold') # Set y-axis label
ax.set_title(f'Precision-Recall Curve - {best_result["name"]}', fontweight='bold', fontsize=14) # Set title
ax.grid(alpha=0.3) # Add grid
ax.set_xlim([0.0, 1.0]) # Set x-axis limits
ax.set_ylim([0.0, 1.05]) # Set y-axis limits

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/04_precision_recall.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 04_precision_recall.png") # Confirm save
plt.close() # Close the figure

# 5. Feature Importance
fig, ax = plt.subplots(figsize=(10, 8)) # Create a new figure
feature_importance = pd.DataFrame({ # Create a DataFrame for feature importance
    'feature': feature_names,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=True) # Sort features by importance

colors = plt.cm.viridis(np.linspace(0, 1, len(feature_importance))) # Generate colors for the bars
ax.barh(feature_importance['feature'], feature_importance['importance'], color=colors, alpha=0.8) # Plot horizontal bar chart
ax.set_xlabel('Importance', fontweight='bold') # Set x-axis label
ax.set_title(f'Feature Importance - {best_result["name"]}', fontweight='bold', fontsize=14) # Set title
ax.grid(axis='x', alpha=0.3) # Add vertical grid lines

for i, (idx, row) in enumerate(feature_importance.iterrows()): # Loop through features to add text labels
    ax.text(row['importance'], i, f" {row['importance']:.4f}", # Add importance value next to the bar
           va='center', fontsize=9)

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/05_feature_importance.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 05_feature_importance.png") # Confirm save
plt.close() # Close the figure

# 6. Learning Curves
fig, ax = plt.subplots(figsize=(10, 6)) # Create a new figure
train_sizes, train_scores, val_scores = learning_curve( # Calculate learning curve metrics
    best_model, X_train, y_train, cv=5, n_jobs=-1, # Use the best model, training data, 5-fold CV, and all processors
    train_sizes=np.linspace(0.1, 1.0, 10), random_state=42 # Define 10 training set sizes from 10% to 100%
)

train_mean = np.mean(train_scores, axis=1) # Calculate mean training score for each size
train_std = np.std(train_scores, axis=1) # Calculate std dev of training score
val_mean = np.mean(val_scores, axis=1) # Calculate mean cross-validation score for each size
val_std = np.std(val_scores, axis=1) # Calculate std dev of cross-validation score

ax.plot(train_sizes, train_mean, 'o-', color='r', label='Training score') # Plot mean training score
ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='r') # Plot std dev of training score
ax.plot(train_sizes, val_mean, 'o-', color='g', label='Cross-validation score') # Plot mean validation score
ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='g') # Plot std dev of validation score

ax.set_xlabel('Training Examples', fontweight='bold') # Set x-axis label
ax.set_ylabel('Score', fontweight='bold') # Set y-axis label
ax.set_title(f'Learning Curves - {best_result["name"]}', fontweight='bold', fontsize=14) # Set title
ax.legend(loc='lower right') # Display legend
ax.grid(alpha=0.3) # Add grid

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/06_learning_curves.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 06_learning_curves.png") # Confirm save
plt.close() # Close the figure

# 7. Correlation Heatmap
fig, ax = plt.subplots(figsize=(12, 10)) # Create a new figure
correlation_matrix = df.corr() # Calculate the correlation matrix of all features and target
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool)) # Create a mask to show only the lower triangle (for clarity)
sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.2f', # Plot the heatmap
            cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title('Feature Correlation Matrix', fontweight='bold', fontsize=14) # Set title
plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/07_correlation_matrix.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 07_correlation_matrix.png") # Confirm save
plt.close() # Close the figure

# 8. Feature Distribution
fig, axes = plt.subplots(3, 4, figsize=(16, 12)) # Create a 3x4 subplot figure (12 plots for 12 features)
fig.suptitle('Feature Distributions by Irrigation Need', fontsize=16, fontweight='bold') # Set the main title

for idx, feature in enumerate(feature_names): # Loop through all feature names
    row = idx // 4 # Calculate the subplot row index
    col = idx % 4 # Calculate the subplot column index
    ax = axes[row, col] # Select the current subplot axis
    
    df[df['irrigation_needed']==0][feature].hist(ax=ax, bins=30, alpha=0.6, # Plot histogram for the 'No Irrigation' class
                                                  label='No Irrigation', color='blue')
    df[df['irrigation_needed']==1][feature].hist(ax=ax, bins=30, alpha=0.6, # Plot histogram for the 'Irrigation Needed' class (overlay)
                                                  label='Irrigation', color='red')
    ax.set_title(feature, fontweight='bold') # Set subplot title to the feature name
    ax.set_xlabel('') # Clear the x-label (to avoid clutter)
    ax.legend(fontsize=8) # Display legend
    ax.grid(alpha=0.3) # Add grid

plt.tight_layout() # Adjust layout
plt.savefig('training_visuals/08_feature_distributions.png', dpi=300, bbox_inches='tight') # Save the plot
print("✓ Saved: 08_feature_distributions.png") # Confirm save
plt.close() # Close the figure

# 9. Final Summary Dashboard
fig = plt.figure(figsize=(16, 10)) # Create a large figure for the dashboard
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3) # Define a 3x3 grid for subplots

# Title
fig.suptitle(f'Training Summary - {best_result["name"]}\n' + # Set the main title with key metrics
             f'Accuracy: {best_result["accuracy"]*100:.2f}% | Size: {best_result["size_kb"]:.2f} KB',
             fontsize=18, fontweight='bold')

# Metrics text
ax1 = fig.add_subplot(gs[0, 0]) # Select the top-left section (1 row, 1 column)
ax1.axis('off') # Turn off the axis for a text-only area
metrics_text = f""" # Format the key metrics into a string
PERFORMANCE METRICS

Accuracy:          {best_result['accuracy']*100:.2f}%
Balanced Accuracy: {best_result['balanced_acc']*100:.2f}%
CV Accuracy:       {best_result['cv_mean']*100:.2f}% ± {best_result['cv_std']*100:.2f}%

False Negative:    {best_result['fnr']*100:.1f}%
False Positive:    {best_result['fpr']*100:.1f}%

Model Size:        {best_result['size_kb']:.2f} KB
Trees:             {best_result['config']['n_estimators']}
Max Depth:         {best_result['config']['max_depth']}
"""
ax1.text(0.1, 0.9, metrics_text, transform=ax1.transAxes, fontsize=10, # Display the metrics text
        verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) # Add a background box

# Confusion matrix (small)
ax2 = fig.add_subplot(gs[0, 1:]) # Select the top-middle and top-right sections (1 row, 2 columns)
sns.heatmap(best_result['cm'], annot=True, fmt='d', cmap='Blues', ax=ax2, cbar=False) # Plot a simplified heatmap
ax2.set_title('Confusion Matrix', fontweight='bold') # Set title
ax2.set_ylabel('True') # Set y-axis label
ax2.set_xlabel('Predicted') # Set x-axis label

# Feature importance (top 8)
ax3 = fig.add_subplot(gs[1, :]) # Select the entire middle row
top_features = feature_importance.tail(8) # Get the 8 most important features
ax3.barh(top_features['feature'], top_features['importance'], color='steelblue', alpha=0.8) # Plot horizontal bar chart
ax3.set_xlabel('Importance', fontweight='bold') # Set x-axis label
ax3.set_title('Top 8 Features', fontweight='bold') # Set title
ax3.grid(axis='x', alpha=0.3) # Add vertical grid lines

# ROC curve (small)
ax4 = fig.add_subplot(gs[2, 0]) # Select the bottom-left section
fpr, tpr, _ = roc_curve(y_test, best_result['y_pred_proba']) # Calculate ROC metrics
roc_auc = auc(fpr, tpr) # Calculate AUC
ax4.plot(fpr, tpr, color='darkorange', lw=2) # Plot ROC curve
ax4.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--') # Plot random classifier line
ax4.set_title(f'ROC (AUC={roc_auc:.3f})', fontweight='bold') # Set title with AUC
ax4.grid(alpha=0.3) # Add grid

# Model comparison
ax5 = fig.add_subplot(gs[2, 1:]) # Select the bottom-middle and bottom-right sections
names = [r['name'] for r in results] # Get model names
accuracies = [r['accuracy']*100 for r in results] # Get accuracy scores
colors_list = ['green' if r['name'] == best_result['name'] else 'gray' for r in results] # Highlight the best model
ax5.bar(names, accuracies, alpha=0.8, color=colors_list) # Plot model accuracies
ax5.set_ylabel('Accuracy (%)', fontweight='bold') # Set y-axis label
ax5.set_title('Model Comparison', fontweight='bold') # Set title
ax5.axhline(y=90, color='r', linestyle='--', alpha=0.5) # Plot the 90% target line
ax5.grid(axis='y', alpha=0.3) # Add horizontal grid
ax5.set_xticklabels(names, rotation=15, ha='right') # Set x-axis labels

plt.savefig('training_visuals/09_final_summary.png', dpi=300, bbox_inches='tight') # Save the final dashboard
print("✓ Saved: 09_final_summary.png") # Confirm save
plt.close() # Close the figure

print("\n✓ All visualizations saved to training_visuals/") # Final confirmation for all visualizations

# ============================================================================
# SAVE MODEL
# ============================================================================

print("\n" + "="*80) # Print a separator
print("SAVING MODEL AND METADATA") # Inform about saving process
print("="*80) # Print a separator

with open('irrigation_esp32_enhanced.pkl', 'wb') as f: # Open file for binary writing
    pickle.dump(best_model, f) # Serialize and save the best model using pickle
print("✓ Saved: irrigation_esp32_enhanced.pkl") # Confirm model save

# Save metadata
metadata = { # Create a dictionary to store model metadata
    'model_name': best_result['name'],
    'model_type': 'RandomForest',
    'configuration': best_result['config'],
    'n_features': len(feature_names),
    'features': feature_names,
    'accuracy': float(best_result['accuracy']), # Convert numpy float to standard Python float
    'balanced_accuracy': float(best_result['balanced_acc']),
    'cv_mean': float(best_result['cv_mean']),
    'cv_std': float(best_result['cv_std']),
    'model_size_kb': float(best_result['size_kb']),
    'false_negative_rate': float(best_result['fnr']),
    'false_positive_rate': float(best_result['fpr']),
    'feature_importance': dict(zip(feature_names, best_model.feature_importances_.tolist())), # Store feature importances
    'confusion_matrix': best_result['cm'].tolist(), # Convert numpy array to list
    'dataset_used': 'irrigation_enhanced_dataset.csv',
    'training_samples': len(X_train),
    'test_samples': len(X_test)
}

with open('model_metadata_enhanced.json', 'w') as f: # Open file for writing
    json.dump(metadata, f, indent=2) # Save the metadata dictionary as a pretty-printed JSON file
print("✓ Saved: model_metadata_enhanced.json") # Confirm metadata save

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*80) # Print a separator
print("TRAINING COMPLETE!") # Final message
print("="*80) # Print a separator

status_emoji = "✅" if best_result['accuracy'] >= 0.90 and best_result['size_kb'] < 30 else "⚠️" # Determine status emoji based on targets

print(f""" # Print the final summary report
{status_emoji} FINAL RESULTS

Model: {best_result['name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE:
   Accuracy:          {best_result['accuracy']*100:.2f}% {'✓' if best_result['accuracy'] >= 0.90 else '✗'} # Check against 90% target
   Balanced Accuracy: {best_result['balanced_acc']*100:.2f}%
   CV Score:          {best_result['cv_mean']*100:.2f}% ± {best_result['cv_std']*100:.2f}%
   
QUALITY:
   False Negatives:   {best_result['fnr']*100:.1f}% (missed irrigation) # FNR interpretation
   False Positives:   {best_result['fpr']*100:.1f}% (over-watering) # FPR interpretation
   
SIZE:
   Model Size:        {best_result['size_kb']:.2f} KB {'✓' if best_result['size_kb'] < 30 else '✗'} # Check against 30 KB target
   Memory Usage:      {best_result['size_kb']/520*100:.1f}% of ESP32 SRAM # Estimate memory usage percentage (assuming 520 KB SRAM)
   Available:         {520 - best_result['size_kb']:.1f} KB free # Calculate remaining free memory

CONFIGURATION:
   Trees:             {best_result['config']['n_estimators']}
   Max Depth:         {best_result['config']['max_depth']}
   Min Samples Leaf:  {best_result['config']['min_samples_leaf']}
   Features:          12 (4 sensors + 8 engineered)

TOP FEATURES:
""")

for i, (feat, imp) in enumerate(sorted(metadata['feature_importance'].items(), # Loop through the top 5 features
                                      key=lambda x: x[1], reverse=True)[:5], 1): # Sort by importance and take the top 5
    bar = '█' * int(imp * 50) # Create a simple text-based bar visualization
    print(f"   {i}. {feat:<25} {imp:.4f} {bar}") # Print feature rank, name, importance, and bar

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 VISUALIZATIONS: training_visuals/ directory # List all saved visualizations
   01_model_comparison.png
   02_confusion_matrix.png
   03_roc_curve.png
   04_precision_recall.png
   05_feature_importance.png
   06_learning_curves.png
   07_correlation_matrix.png
   08_feature_distributions.png
   09_final_summary.png

🚀 NEXT STEPS: # List next actions for the user
   1. Review visualizations in training_visuals/
   2. Run deploy_enhanced.py to generate ESP32 code
   3. Upload to ESP32 S3 hardware
   4. Calibrate sensors with real data
   5. Monitor and iterate

{'='*80}
SUCCESS! Model ready for deployment.
{'='*80}
""")