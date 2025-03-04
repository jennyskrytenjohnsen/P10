import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # For better heatmap visualizations

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"  # Replace with correct URL for your clinical data
df_clinical = pd.read_csv(clinical_data_url)

# Display an overview of the dataset
print("Dataset Overview:")
print(df_clinical.info())  # Shows column names, data types, and missing values

# Specify the five features you want to analyze (adjust names as needed)
features = ["age", "height", "icu_days", "weight", "bmi"]  # Replace with actual column names

# Drop rows with missing values for selected features
df_features = df_clinical[features].dropna()

# Compute the correlation matrix
correlation_matrix = df_features.corr()

# --- Heatmap of the Correlation Matrix ---
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, annot_kws={"size": 10})
plt.title("Correlation Matrix of Selected Features")
plt.show()
