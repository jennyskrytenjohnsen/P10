import vitaldb  
import requests
import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Create a new DataFrame with 'caseid' and surgery department columns
departments = ['General surgery', 'Thoracic surgery', 'Urology', 'Gynecology']
df_surgery = pd.DataFrame()

# Initialize the 'caseid' column
df_surgery['caseid'] = df_clinical['caseid']

# For each department, create a column with 1 or 0 based on whether the patient received surgery in that department
for department in departments:
    df_surgery[department] = df_clinical['department'].apply(lambda x: 1 if x == department else 0)

# Save the DataFrame to a CSV file in the desired location
output_path = os.path.join("Preprocessing", "Data", "Data_surgerydepartment.csv")
df_surgery.to_csv(output_path, index=False)

print(f"CSV file saved at {output_path}")
