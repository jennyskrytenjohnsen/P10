import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract preop_ph (preph) from the clinical dataset
df_clinical['preph'] = df_clinical['preop_ph']

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'ph'
df_ph = df_lab[df_lab["name"] == "ph"]

# Convert the `dt`, `opend`, and `opstart` columns to datetime format
df_ph['dt'] = pd.to_datetime(df_ph['dt'])
df_clinical['opend'] = pd.to_datetime(df_clinical['opend'])
df_clinical['opstart'] = pd.to_datetime(df_clinical['opstart'])

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    preph = row['preph']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_ph = df_ph[(df_ph['caseid'] == caseid) & (df_ph['dt'] >= opstart_time) & (df_ph['dt'] <= opend_time)]
    
    # If there are any matching lab data for this caseid, select the closest to opend
    if not df_case_ph.empty:
        df_case_ph['time_diff'] = (df_case_ph['dt'] - opend_time).abs()  # Calculate the time difference to opend
        closest_ph_row = df_case_ph.loc[df_case_ph['time_diff'].idxmin()]  # Get the row with the closest time
        periph = closest_ph_row['result']
    else:
        periph = None  # If no matching lab data, set periph to None
    
    # Append the row with caseid, preph, and periph to the final_data list
    final_data.append({'caseid': caseid, 'preph': preph, 'periph': periph})

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_ph.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_ph.csv' has been saved successfully at {save_path}.")
