import vitaldb  
import requests
import pandas as pd
import io
import matplotlib.pyplot as plt
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Create a new column 'cancer' based on whether 'cancer' appears in the 'dx' column (case-insensitive)
df_clinical['cancer'] = df_clinical['dx'].str.contains('cancer', case=False, na=False).astype(int)

# Select only the caseid and cancer columns
df_cancer = df_clinical[['caseid', 'cancer']]

# Define the save path
save_path = r"C:\Users\mariah\Documents\GitHub\P10\Preprocessing\Data\Data_cancer.csv"

# Save the result to the specified CSV file path
df_cancer.to_csv(save_path, index=False)

# Print confirmation
print(f"CSV file has been saved to: {save_path}")
