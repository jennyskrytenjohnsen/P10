import pandas as pd
import os

# Load clinical and pao2 time-series data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

df_final = df_clinical[['caseid', 'opstart', 'preop_pao2']].copy()

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_pao2.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final[['caseid', 'preop_pao2']].to_csv(save_path, index=False)

print(f"CSV file 'Data_pao2.csv' with preop_pao2 saved successfully at {save_path}.")
