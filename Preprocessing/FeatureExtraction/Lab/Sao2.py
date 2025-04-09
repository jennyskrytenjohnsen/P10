import pandas as pd
import os

# Load clinical and lab data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for sao2
df_sao2 = df_lab[df_lab["name"] == "sao2"]

# Collect results
final_data = []

for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    presao2 = row.get('preop_sao2')  # from clinical table
    opstart = row['opstart']
    opend = row['opend']

    df_case_sao2 = df_sao2[
        (df_sao2['caseid'] == caseid) &
        (df_sao2['dt'] >= opstart) &
        (df_sao2['dt'] <= opend)
    ]

    # Find perisao2: closest to opend
    if not df_case_sao2.empty:
        df_case_sao2 = df_case_sao2.copy()
        df_case_sao2['time_diff'] = (df_case_sao2['dt'] - opend).abs()
        perisao2 = df_case_sao2.loc[df_case_sao2['time_diff'].idxmin(), 'result']
    else:
        perisao2 = None

    final_data.append({
        'caseid': caseid,
        'presao2': presao2,
        'perisao2': perisao2
    })

# Create DataFrame
df_final = pd.DataFrame(final_data)

# Save output
save_path = os.path.join('Preprocessing', 'Data', 'Data_sao2.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_sao2.csv' with presao2 and perisao2 saved successfully at {save_path}.")