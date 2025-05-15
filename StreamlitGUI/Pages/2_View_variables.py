import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Variables", page_icon="📊")

# Map patient names to case IDs
patient_case_map = {
    "Åge Sørensen 020865-1448": 5,
    "Børge Holm 241279-1337": 16,
    "Ida Jensen 040499-1688": 706,
}

# Load SHAP values
shap_df = pd.read_csv("Machine/shap_values.csv")

# Get current case ID
case_id = patient_case_map.get(st.session_state.patient_option)

if case_id is not None and case_id in shap_df["caseid"].values:
    row = shap_df[shap_df["caseid"] == case_id].iloc[0]
    patient_shap = row.drop(labels="caseid").to_dict()
else:
    st.error("Patient not found or invalid case ID.")
    st.stop()

# Feature name mapping
feature_name_map = {
    "age": "Age",
    "sex": "Sex",
    "height": "Height",
    "weight": "Weight",
    "BMI": "BMI",
    "RR_total": "RR total",
    "RR_n12": "RR below 12 bpm",
    "RR_n20": "RR above 20 bpm",
    "RR_w15minMV": "RR last 15 min",
    "SpO2_total": "SpO2 total",
    "SpO2_n90": "SpO2 below 90%",
    "SpO2_w15minMV": "SpO2 last 15 min",
    "data_vent": "Ventilator use",
    "HR_n30": "HR below 30 bpm",
    "HR_n60": "HR below 60 bpm",
    "HR_n100": "HR above 100 bpm",
    "HR_total": "HR",
    "HR_w15minMV": "HR last 15 min",
    "value_eph": "Ephedrine use",
    "value_phe": "Phenylephrine use",
    "value_vaso": "Vasopressin use",
    "value_ino": "Inotropes use",
    "has_aline": "Arterial line",
    "FFP": "FFP",
    "RBC": "RBC",
    "under36": "Temp below 36",
    "over38": "Temp above 38",
    "differencebetween15min": "Temp difference start/end operation",
    "prept": "PT",
    "preaptt": "APTT",
    "prehb": "Hemoglobin",
    "preplt": "Platelet count",
    "prek": "Potassium",
    "prena": "Sodium",
    "preca": "Calcium",
    "preop_dm": "Diabetis mellitus",
    "preop_htn": "Hypertension",
    "asa": "ASA PS score",
    "cancer": "Cancer diagnosis",
    "General surgery": "General surgery",
    "Thoracic surgery": "Thoracic surgery",
    "Urology": "Urology",
    "Gynecology": "Gynecology",
    "generalAnesthesia": "General anesthesia",
    "spinalAnesthesia": "Spinal anesthesia",
    "sedationalgesia": "Sedation algesia",
    "anesthesia_duration": "Anesthesia duration",
    "op_duration_min": "Operation duration"
}

# Remove excluded variables
excluded_vars = ["RR_w15min", "SpO2_w15min", "HR_w15min"]
patient_shap = {k: v for k, v in patient_shap.items() if k not in excluded_vars}

# Headline
st.markdown("# Variables Affecting the Prediction")

# Selected patient and timestamp
st.markdown(f"### Selected patient: {st.session_state.patient_option}")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Timestamp for prediction:** {current_time}")

# Introductory explanation
st.write("This page offers an overview of the variables affecting the prediction of ICU need certainty. The importance of each variable is determined by the underlying machine learning algorithm.")
st.write("If a variable has an importance score close to 1, and is colored red, it indicates a high certainty of ICU need. If the score is closer to -1, it is blue, indicating high certainty of no ICU need. Scores close to 0 are grey, indicating minimal importance.")

# Color function
cmap = sns.color_palette("coolwarm", as_cmap=True)
def colorize(val):
    original_name = [k for k, v in feature_name_map.items() if v == val]
    score = patient_shap.get(original_name[0], 0) if original_name else 0
    norm_score = (score + 1) / 2
    color = cmap(norm_score)
    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

# Color bar legend
st.markdown("**Variable importance scale**")
fig, ax = plt.subplots(figsize=(8, 0.1))
norm = plt.Normalize(-1, 1)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# Top 5 important variables
st.markdown("#### Summary of most important variables for prediction")
top_vars = sorted(patient_shap.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
imp_vars = [feature_name_map.get(var, var) for var, _ in top_vars]
df_imp = pd.DataFrame({"Important Variables": imp_vars})
st.write(df_imp.style.applymap(colorize).hide(axis="index"))

# Demographic Variables
st.markdown("#### Demographic Variables")
demo_vars = ["age", "sex", "height", "weight", "BMI"]
demo_labels = [feature_name_map[v] for v in demo_vars]
st.write(pd.DataFrame({"Demographic": demo_labels}).style.applymap(colorize).hide(axis="index"))

# Preoperative Variables
st.markdown("#### Preoperative Variables")
circ_pre = ["prept", "preaptt", "prehb", "preplt"]
renal_pre = ["prek", "prena", "preca", ""]
data_pre = pd.DataFrame({
    "Circulatory": [feature_name_map.get(v, v) if v else "" for v in circ_pre],
    "Renal": [feature_name_map.get(v, v) if v else "" for v in renal_pre]
})
st.write(data_pre.style.applymap(colorize).hide(axis="index"))

# Perioperative Variables
st.markdown("#### Perioperative Variables")
resp_vars = ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "SpO2_total", "SpO2_n90", "SpO2_w15minMV", "data_vent"]
circ_vars = ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso"]
max_len = max(len(resp_vars), len(circ_vars))
resp_vars += [""] * (max_len - len(resp_vars))
circ_vars += [""] * (max_len - len(circ_vars))
data_peri = pd.DataFrame({
    "Respiratory": [feature_name_map.get(v, v) if v else "" for v in resp_vars],
    "Circulatory": [feature_name_map.get(v, v) if v else "" for v in circ_vars]
})
st.write(data_peri.style.applymap(colorize).hide(axis="index"))

# Other Variables
st.markdown("#### Other Variables")
other_vars = ["preop_dm", "preop_htn", "asa", "cancer"]
surg_vars = ["General surgery", "Thoracic surgery", "Urology", "Gynecology", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"]
max_len = max(len(other_vars), len(surg_vars))
other_vars += [""] * (max_len - len(other_vars))
surg_vars += [""] * (max_len - len(surg_vars))
df_others = pd.DataFrame({
    "Others": [feature_name_map.get(v, v) if v else "" for v in other_vars],
    "Surgical": [feature_name_map.get(v, v) if v else "" for v in surg_vars]
})
st.write(df_others.style.applymap(colorize).hide(axis="index"))
