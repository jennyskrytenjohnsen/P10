import vitaldb  
import requests
import pandas as pd
import io
import matplotlib.pyplot as plt
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Calculate duration in hours
df_clinical['duration_hours'] = (df_clinical['opend'] - df_clinical['opstart']) / 3600

# Prepare the new DataFrame
data_urineoutput = pd.DataFrame()
data_urineoutput['caseid'] = df_clinical['caseid']
data_urineoutput['uoraw'] = df_clinical['intraop_uo']  # do NOT fillna yet

# Handle duration and weight safely (avoid divide by zero)
safe_duration = df_clinical['duration_hours'].replace(0, pd.NA)
safe_weight = df_clinical['weight'].replace(0, pd.NA)

# uotime: urine volume / duration
data_urineoutput['uotime'] = (data_urineoutput['uoraw'] / safe_duration).round(0)

# oukgtime: urine volume / (weight * duration)
data_urineoutput['oukgtime'] = (data_urineoutput['uoraw'] / (safe_weight * safe_duration)).round(2)

# Ensure output directory exists
output_dir = os.path.join('Preprocessing', 'Data')
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
output_path = os.path.join(output_dir, 'Data_urineoutput.csv')
data_urineoutput.to_csv(output_path, index=False)

print(f"CSV file saved to {output_path}")
