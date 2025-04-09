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

# Loop through each row in the clinical dataset
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # seconds
    opend_time = row['opend']      # seconds

    # Filter bilirubin lab data for the current caseid
    df_case_bili = df_bili[df_bili['caseid'] == caseid]

    # --- Preoperative bilirubin: latest before opstart ---
    df_pre = df_case_bili[df_case_bili['dt'] < opstart_time]
    if not df_pre.empty:
        prebil = df_pre.loc[df_pre['dt'].idxmax(), 'result']
    else:
        prebil = None

    # --- Perioperative bilirubin: closest during surgery to opend ---
    df_peri = df_case_bili[(df_case_bili['dt'] >= opstart_time) & (df_case_bili['dt'] <= opend_time)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend_time).abs()
        peribil = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        peribil = None

    # Save result for this case
    final_data.append({'caseid': caseid, 'prebil': prebil, 'peribil': peribil})

# Convert results to DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_bilirubin.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_bilirubin.csv' with prebil and peribil has been saved at {save_path}.")
