import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # For better heatmap visualizations

### PREOPERATIVE RENAL VARIABLES ###

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

# Filter lab data to get only 'bun' results
df_bun = df_lab[df_lab['name'].str.contains("bun", case=False, na=False)]

# Average 'bun' results if multiple records exist for the same patient
df_bun_avg = df_bun.groupby("caseid", as_index=False)["result"].mean()
df_bun_avg.rename(columns={"result": "bun_avg"}, inplace=True)

# Filter lab data to get only 'k' results
df_k = df_lab[df_lab['name'].str.contains("k", case=False, na=False)]

# Average 'k' results if multiple records exist for the same patient
df_k_avg = df_k.groupby("caseid", as_index=False)["result"].mean()
df_k_avg.rename(columns={"result": "k_avg"}, inplace=True)

# Extract 'preop_cr' value for each patient
df_preop_cr = df_clinical[['caseid', 'preop_cr']].dropna()

# Merge datasets on 'caseid'
df_merged = df_preop_cr.merge(df_bun_avg, on='caseid').merge(df_k_avg, on='caseid')

# Compute the correlation matrix using Spearman's correlation
correlation_matrix = df_merged[['preop_cr', 'bun_avg', 'k_avg']].corr(method='spearman')

# Plot the correlation matrix
plt.figure(figsize=(6, 4))
sns.heatmap(correlation_matrix, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Spearman's Correlation Matrix")
plt.show()

print(correlation_matrix)
