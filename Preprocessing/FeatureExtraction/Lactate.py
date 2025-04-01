import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'lac'
df_lac = df_lab[df_lab["name"] == "lac"]

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_lac = df_lac[(df_lac['caseid'] == caseid)]
    
    # Extract prelac and perilac values (Lactate before and after surgery)
    prelac = None
    perilac = None
    closest_perilac = None
    
    # Loop through lac data to find prelac and perilac
    for _, lac_row in df_case_lac.iterrows():
        lac_dt = lac_row['dt']  # dt is in seconds
        lac_value = lac_row['result']
        
        # If lac time is before opstart, record as prelac
        if lac_dt < opstart_time:
            prelac = lac_value
        
        # If lac time is after opstart and before opend, record as perilac
        elif opstart_time <= lac_dt < opend_time:
            if closest_perilac is None or abs(lac_dt - opend_time) < abs(closest_perilac['dt'] - opend_time):
                closest_perilac = lac_row  # Update closest perilac
    
    # Append prelac and closest perilac to the final data
    final_row = {'caseid': caseid, 'prelac': prelac}
    if closest_perilac is not None:
        final_row['perilac'] = closest_perilac['result']
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_lac.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_lac.csv' has been saved successfully at {save_path}.")
