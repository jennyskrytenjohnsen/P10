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

# Extract relevant clinical variables for each patient
df_preop_cr = df_clinical[['caseid', 'preop_cr']].dropna()
df_preop_alb = df_clinical[['caseid', 'preop_alb']].dropna()
df_preop_k = df_clinical[['caseid', 'preop_k']].dropna()
df_preop_na = df_clinical[['caseid', 'preop_na']].dropna()
df_preop_bun = df_clinical[['caseid', 'preop_bun']].dropna()

# Filter lab data for 'gfr' where 'dt' column is negative
df_gfr = df_lab[df_lab['name'].str.contains("gfr", case=False, na=False)]
df_gfr_negative_dt = df_gfr[df_gfr['dt'] < 0]

# Average 'gfr' results for each patient if multiple records exist
df_gfr_avg = df_gfr_negative_dt.groupby("caseid", as_index=False)["result"].mean()
df_gfr_avg.rename(columns={"result": "gfr_avg"}, inplace=True)

# Merge all clinical data
df_clinical_merged = df_preop_cr.merge(df_preop_alb, on='caseid')\
                                 .merge(df_preop_k, on='caseid')\
                                 .merge(df_preop_na, on='caseid')\
                                 .merge(df_preop_bun, on='caseid')\
                                 .merge(df_gfr_avg, on='caseid')

# Compute the correlation matrix using Spearman's correlation
correlation_matrix = df_clinical_merged[['preop_cr', 'preop_alb', 'preop_k', 'preop_na', 'preop_bun', 'gfr_avg']].corr(method='spearman')

# Plot the correlation matrix
plt.figure(figsize=(6, 4))
sns.heatmap(correlation_matrix, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Spearman's Correlation Matrix")
plt.show()

print(correlation_matrix)
