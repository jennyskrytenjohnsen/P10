import os
import pandas as pd

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Create a new DataFrame with 'caseid' and the corresponding columns for each type of anesthesia
df_ane_types = pd.DataFrame()

# Set 'caseid' as the index
df_ane_types['caseid'] = df_clinical['caseid']

# Set 1 if 'ane_type' is 'General', otherwise 0
df_ane_types['general'] = df_clinical['ane_type'].apply(lambda x: 1 if x == 'General' else 0)

# Set 1 if 'ane_type' is 'Spinal', otherwise 0
df_ane_types['spinal'] = df_clinical['ane_type'].apply(lambda x: 1 if x == 'Spinal' else 0)

# Set 1 if 'ane_type' is 'Sedationalgesia', otherwise 0
df_ane_types['sedationalgesia'] = df_clinical['ane_type'].apply(lambda x: 1 if x == 'Sedationalgesia' else 0)

# Define the directory path where the CSV will be saved
output_directory = "Preprocessing/Data"
os.makedirs(output_directory, exist_ok=True)

# Define the output CSV file path
output_csv_path = os.path.join(output_directory, "Data_Anetype.csv")

# Save the DataFrame as a CSV file
df_ane_types.to_csv(output_csv_path, index=False)

# Confirm the file is saved
print(f"CSV file saved to: {output_csv_path}")
