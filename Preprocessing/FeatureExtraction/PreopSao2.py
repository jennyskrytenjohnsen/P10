import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract preop_sao2 directly from the clinical dataset
df_clinical['preop_sao2'] = df_clinical['preop_sao2']

# Keep only relevant columns
df_final = df_clinical[['caseid', 'preop_sao2']]

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_sao2.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_sao2.csv' has been saved successfully at {save_path}.")
