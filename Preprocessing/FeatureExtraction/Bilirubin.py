import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'tbil' (total bilirubin)
df_bili = df_lab[df_lab["name"] == "tbil"]

# Prepare list to collect final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_bili = df_bili[(df_bili['caseid'] == caseid) & (df_bili['dt'] >= opstart_time) & (df_bili['dt'] <= opend_time)]
    
    # If there are any matching lab data for this caseid, select the closest to opend
    if not df_case_bili.empty:
        df_case_bili['time_diff'] = (df_case_bili['dt'] - opend_time).abs()  # Calculate time difference to opend
        closest_bili_row = df_case_bili.loc[df_case_bili['time_diff'].idxmin()]  # Get the row with the closest time
        peribil = closest_bili_row['result']
    else:
        peribil = None  # If no matching lab data, set peribil to None
    
    # Append the row with caseid and peribil to the final_data list
    final_data.append({'caseid': caseid, 'peribil': peribil})

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing/Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_bilirubin.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_bilirubin.csv' has been saved successfully at {save_path}.")
