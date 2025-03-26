import vitaldb  
import requests
import pandas as pd
import io
import matplotlib.pyplot as plt

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Access intraop_rbc, intraop_ffp, and icu_days columns
intraop_rbc = df_clinical['intraop_rbc']
intraop_ffp = df_clinical['intraop_ffp']
icu_days = df_clinical['icu_days']

# Create a new column to categorize whether the patient went to ICU (ICU or No ICU)
df_clinical['icu_status'] = icu_days.apply(lambda x: 'ICU' if x != 0 else 'No ICU')

# Group the data by ICU status
grouped = df_clinical.groupby('icu_status')

# Calculate total transfusion per group
total_transfusion = grouped[['intraop_rbc', 'intraop_ffp']].sum()

# Count number of patients in each group
patient_counts = grouped.size()

# Normalize transfusion by number of patients
normalized_transfusion = total_transfusion.div(patient_counts, axis=0)

# Reorder rows so that 'No ICU' is first
normalized_transfusion = normalized_transfusion.loc[['No ICU', 'ICU']]

# Plot the normalized results
plt.figure(figsize=(10, 6))
normalized_transfusion.plot(kind='bar', ax=plt.gca(), color=['blue', 'red'], alpha=0.7)

# Add labels and title
plt.xlabel('ICU Status')
plt.ylabel('Average Blood Transfusion Units per Patient')
plt.title('Average Blood Transfusion (RBC & FFP) per Patient for ICU and No ICU Groups')
plt.xticks(rotation=0)
plt.legend(title="Blood Product", labels=['RBC', 'FFP'])

# Display the plot
plt.show()

# -------- Save FFP and RBC data to CSV --------
# Create new DataFrame with caseid, FFP and RBC
df_transfusion = df_clinical[['caseid', 'intraop_ffp', 'intraop_rbc']].copy()

# Rename columns to match requested format
df_transfusion.rename(columns={'intraop_ffp': 'FFP', 'intraop_rbc': 'RBC'}, inplace=True)

# Replace missing values with 0
df_transfusion.fillna(0, inplace=True)

# Save to CSV in the specified path
output_path = 'C:/Users/mariah/Documents/GitHub/P10/Preprocessing/Data/Data_FFPandRBC.csv'
df_transfusion.to_csv(output_path, index=False)
