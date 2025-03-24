import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # For better heatmap visualizations

### DEMOGRAPHIC VARIABLES ###

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"  # Replace with correct URL for your clinical data
df_clinical = pd.read_csv(clinical_data_url)

# Load laboratory dataset from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Display an overview of both datasets
print("Clinical Dataset Overview:")
print(df_clinical.info())

print("Laboratory Dataset Overview:")
print(df_lab.info())

# Extract relevant demographic variables for each patient
df_age = df_clinical[['caseid', 'age']].dropna()
df_height = df_clinical[['caseid', 'height']].dropna()
df_weight = df_clinical[['caseid', 'weight']].dropna()
df_bmi = df_clinical[['caseid', 'bmi']].dropna()
df_sex = df_clinical[['caseid', 'sex']].dropna()  # Using sex instead of gfr

# Encode sex as 0 for 'M' and 1 for 'F'
df_sex['sex'] = df_sex['sex'].map({'M': 0, 'F': 1})

# Merge all clinical data
df_clinical_merged = df_age.merge(df_height, on='caseid')\
                            .merge(df_weight, on='caseid')\
                            .merge(df_bmi, on='caseid')\
                            .merge(df_sex, on='caseid')

# Compute the correlation matrix using Spearman's correlation
correlation_matrix = df_clinical_merged[['age', 'height', 'weight', 'bmi', 'sex']].corr(method='spearman')

# Plot the correlation matrix
plt.figure(figsize=(6, 4))
sns.heatmap(correlation_matrix, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation of Demographic Variables")
plt.show()

print(correlation_matrix)
