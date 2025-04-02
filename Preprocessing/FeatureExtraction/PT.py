import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract preop_pt
df_final = df_clinical[['caseid', 'preop_pt']]

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_preopPT.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_preop_pt.csv' has been saved successfully at {save_path}.")
