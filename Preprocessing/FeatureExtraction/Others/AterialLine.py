import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Create binary feature: 1 if aline1 or aline2 is not null, else 0
df_clinical['has_aline'] = df_clinical[['aline1', 'aline2']].notna().any(axis=1).astype(int)

# Extract relevant columns
df_aline = df_clinical[['caseid', 'has_aline']]

# Show first few rows
print(df_aline.head())

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_aline.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_aline.to_csv(save_path, index=False)

print(f"CSV file 'Data_aline.csv' has been saved successfully at {save_path}.")