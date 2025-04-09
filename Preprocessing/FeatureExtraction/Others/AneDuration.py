import os
import pandas as pd

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Convert anestart and aneend to numeric (if they are not already)
df_clinical['anestart'] = pd.to_numeric(df_clinical['anestart'], errors='coerce')
df_clinical['aneend'] = pd.to_numeric(df_clinical['aneend'], errors='coerce')

# Calculate duration in seconds (aneend - anestart) and round to nearest whole second
df_clinical['anesthesia_duration'] = (df_clinical['aneend'] - df_clinical['anestart']).round()

# Create the DataFrame with only caseid and the rounded duration in seconds
df_duration = df_clinical[['caseid', 'anesthesia_duration']]

# Define the directory path
output_directory = "Preprocessing/Data"

# Ensure the directory exists
os.makedirs(output_directory, exist_ok=True)

# Save the DataFrame as a CSV file
output_file_path = os.path.join(output_directory, "Data_aneduration.csv")
df_duration.to_csv(output_file_path, index=False)

print(f"CSV file saved at: {output_file_path}")
