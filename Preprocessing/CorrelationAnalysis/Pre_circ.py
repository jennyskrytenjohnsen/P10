import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # For better heatmap visualizations

### PREOPERATIVE CIRCULATORY VARIABLES ###

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

# Filter lab data to get only 'aptt' results
df_aptt = df_lab[df_lab['name'].str.contains("aptt", case=False, na=False)]

# Average 'aptt' results if multiple records exist for the same patient
df_aptt_avg = df_aptt.groupby("caseid", as_index=False)["result"].mean()
df_aptt_avg.rename(columns={"result": "aptt_avg"}, inplace=True)

# Filter lab data to get only 'ptsec' results
df_ptsec = df_lab[df_lab['name'].str.contains("ptsec", case=False, na=False)]

# Average 'ptsec' results if multiple records exist for the same patient
df_ptsec_avg = df_ptsec.groupby("caseid", as_index=False)["result"].mean()
df_ptsec_avg.rename(columns={"result": "ptsec_avg"}, inplace=True)

# Extract 'preop_htn' value for each patient
df_preop_htn = df_clinical[['caseid', 'preop_htn']].dropna()

# Merge datasets on 'caseid'
df_merged = df_preop_htn.merge(df_aptt_avg, on='caseid').merge(df_ptsec_avg, on='caseid')

# Compute the correlation matrix using Spearman's correlation
correlation_matrix = df_merged[['preop_htn', 'aptt_avg', 'ptsec_avg']].corr(method='spearman')

# Plot the correlation matrix
plt.figure(figsize=(6, 4))
sns.heatmap(correlation_matrix, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Matrix - Pre Circulatory Values")
plt.show()

print(correlation_matrix)
