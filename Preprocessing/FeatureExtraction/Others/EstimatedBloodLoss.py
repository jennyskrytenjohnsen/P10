import pandas as pd
import os

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Convert opstart and opend to datetime
df_clinical['opstart'] = pd.to_datetime(df_clinical['opstart'])
df_clinical['opend'] = pd.to_datetime(df_clinical['opend'])

# Calculate duration in minutes
df_clinical['op_duration_min'] = (df_clinical['opend'] - df_clinical['opstart']) / 60


# Calculate EBL per minute
df_clinical['ebl_per_min'] = df_clinical['intraop_ebl'] / df_clinical['op_duration_min']

# Keep relevant columns
df_ebl = df_clinical[['caseid', 'intraop_ebl', 'op_duration_min', 'ebl_per_min']]


# Round all values to 2 decimals
df_ebl = df_ebl.round(2)

# Show first 50 rows
print(df_ebl.head(50))

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_ebl.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_ebl.to_csv(save_path, index=False)

print(f"CSV file 'Data_ebl.csv' with EBL per minute has been saved at {save_path}.")
