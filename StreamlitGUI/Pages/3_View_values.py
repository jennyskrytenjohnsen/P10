import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# MARIA fix age og asa decimaler
# RR below 12 bpm: 181 % FIX
# Temp below 36: 9383 %

st.set_page_config(page_title="Variables", page_icon="📊")

# Map patient names to case IDs
patient_case_map = {
    "Åse Sørensen 020865-1448": 5,
    "Børge Holm 241279-1337": 16,
    "Ida Jensen 040499-1688": 706,
}

# Load SHAP values
shap_df = pd.read_csv("Machine/shap_values.csv")
values_df = pd.read_csv(r"TestTrainingSet/test_ids_pre&peri.csv")

case_id = patient_case_map.get(st.session_state.patient_option)

if case_id is not None and case_id in shap_df["caseid"].values:
    row_shap = shap_df[shap_df["caseid"] == case_id].iloc[0]
    patient_shap = row_shap.drop(labels="caseid").to_dict()
else:
    st.error("Patient not found or invalid case ID.")
    st.stop()

if case_id not in values_df["caseid"].values:
    st.error("Case ID not found in values CSV.")
    st.stop()
row_values = values_df[values_df["caseid"] == case_id].iloc[0]

feature_name_map = {
    "age": "Age",
    "sex": "Sex",
    "height": "Height",
    "weight": "Weight",
    "BMI": "BMI",
    "RR_total": "RR total",
    "RR_n12": "RR below 12 bpm",
    "RR_n20": "RR above 20 bpm",
    "RR_w15minMV": "RR last 15 min MV",
    "RR_w15min": "RR last 15 min",
    "SpO2_total": "SpO2 total",
    "SpO2_w15min": "SpO2 last 15 min",
    "SpO2_n90": "SpO2 below 90%",
    "SpO2_w15minMV": "SpO2 last 15 min MV",
    "data_vent": "Ventilator use",
    "HR_n30": "HR below 30 bpm",
    "HR_n60": "HR below 60 bpm",
    "HR_n100": "HR above 100 bpm",
    "HR_total": "HR total",
    "HR_w15minMV": "HR last 15 min MV",
    "value_eph": "Ephedrine use",
    "value_phe": "Phenylephrine use",
    "value_vaso": "Vasopressin use",
    "value_ino": "Inotropes use",
    "has_aline": "Arterial line",
    "FFP": "FFP",
    "RBC": "RBC",
    "under36": "Temp below 36",
    "over38": "Temp above 38",
    "differencebetween15min": "Temp difference start/end",
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

for placeholder in [""] * 10:
    patient_shap[placeholder] = 0

def format_value(var, val):
    if pd.isna(val):
        return "N/A"

    binary_mappings = {
        "sex": {0: "female", 1: "male"},
        "data_vent": {0: "no", 1: "yes"},
        "value_eph": {0: "no", 1: "yes"},
        "value_phe": {0: "no", 1: "yes"},
        "value_vaso": {0: "no", 1: "yes"},
        "value_ino": {0: "no", 1: "yes"},
        "has_aline": {0: "no", 1: "yes"},
        "General surgery": {0.0: "no", 1.0: "yes"},
        "Thoracic surgery": {0.0: "no", 1.0: "yes"},
        "Urology": {0.0: "no", 1.0: "yes"},
        "Gynecology": {0.0: "no", 1.0: "yes"},
        "generalAnesthesia": {0.0: "no", 1.0: "yes"},
        "spinalAnesthesia": {0.0: "no", 1.0: "yes"},
        "sedationalgesia": {0.0: "no", 1.0: "yes"},
        "preop_dm": {0: "no", 1: "yes"},
        "preop_htn": {0: "no", 1: "yes"},
        "cancer": {0: "no", 1: "yes"},
    }

    if var in binary_mappings:
        return binary_mappings[var].get(val, "N/A")

    units = {
        "age": "years",
        "height": "cm",
        "weight": "kg",
        "BMI": "kg/m²",
        "prept": "%",
        "preaptt": "s",
        "prehb": "g/dL",
        "preplt": "×10³/µL",
        "prek": "mmol/L",
        "prena": "mmol/L",
        "preca": "mmol/L",
        "FFP": "units",
        "RBC": "units",
    }

    percent_vars = [
        "RR_n12", "RR_n20",
        "SpO2_n90",
        "HR_n30", "HR_n60", "HR_n100",
        "under36", "over38"
    ]

    if var in percent_vars:
        return f"{val * 100:.0f} %"
    elif var == "differencebetween15min":
        return f"{val:.2f} °C"
    elif var.startswith("RR") or var.startswith("HR"):
        return f"{val:.1f} bpm"
    elif var.startswith("SpO2"):
        return f"{val:.1f} %"
    elif var in units:
        return f"{val:.2f} {units[var]}" if isinstance(val, float) else f"{val} {units[var]}"
    elif var in ["anesthesia_duration"]:
        hours = val / 3600
        return f"{hours:.1f} hours"
    elif var in ["op_duration_min"]:
        hours = val / 60
        return f"{hours:.1f} hours"
    else:
        return str(val)

st.markdown("# Variable values affecting the prediction")
st.markdown(f"### Selected patient: {st.session_state.patient_option}")
st.write("This page offers an overview of the variables affecting the prediction of ICU need certainty. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")
st.write("If a variable has an importance score close to 1, and is colored red, the variable indicates a high certainty of ICU need. On the contrary, if the importance score is closer to -1, and the variable is colored blue, the variable indicates a high certainty of no ICU need. Lastly, if the variable has an importance score close to 0, the variable is colored grey, and has minimal importance for the certainty of ICU need.")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Timestamp for prediction:** {current_time}")

st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.1))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(-1, 1)
plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

def colorize(val):
    if val == "":
        return ""
    name = val.split(":")[0].strip()
    original_name = [k for k, v in feature_name_map.items() if v == name]
    score = patient_shap.get(original_name[0], 0) if original_name else 0
    norm_score = (score + 1) / 2
    color = sns.color_palette("coolwarm", as_cmap=True)(norm_score)
    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

def name_and_value(var):
    if var == "":
        return ""
    name = feature_name_map.get(var, var)
    val_raw = row_values.get(var, np.nan)
    val_str = format_value(var, val_raw)
    return f"{name}: {val_str}"

# Top 5 variables
st.markdown("#### Summary of Most Important Variables for Prediction")
top_vars = sorted(patient_shap.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
imp_vars = [name_and_value(var) for var, _ in top_vars]
while len(imp_vars) < 5:
    imp_vars.append("")

df_imp = pd.DataFrame({"Important Variables": imp_vars})
styled_imp = df_imp.style.applymap(colorize).hide(axis="index")
st.write(styled_imp)

# Demographic
col1, col2 = st.columns([1, 1])

st.markdown("#### Demographic Variables")
demo_vars = ["age", "sex", "height", "weight", "BMI"]
demo_vals = [name_and_value(v) for v in demo_vars]
df_demo = pd.DataFrame({"Demographic": demo_vals})
styled_demo = df_demo.style.applymap(colorize).hide(axis="index")
st.write(styled_demo)

st.markdown("#### Perioperative Variables")
resp_vars = ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "RR_w15min", "SpO2_total", "SpO2_w15min", "SpO2_n90", "SpO2_w15minMV", "data_vent"]
circ_vars = ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso", "value_ino", "has_aline", "FFP", "RBC", "under36", "over38", "differencebetween15min"]
max_len = max(len(resp_vars), len(circ_vars))
resp_vars += [""] * (max_len - len(resp_vars))
circ_vars += [""] * (max_len - len(circ_vars))
data_peri = pd.DataFrame({
    "Respiratory": [name_and_value(v) for v in resp_vars],
    "Circulatory": [name_and_value(v) for v in circ_vars]
})
styled_table_peri = data_peri.style.applymap(colorize).hide(axis="index")
st.write(styled_table_peri)


st.markdown("#### Preoperative Variables")
circ_pre = ["prept", "preaptt", "prehb", "preplt"]
renal_pre = ["prek", "prena", "preca"]
max_len = max(len(circ_pre), len(renal_pre))
circ_pre += [""] * (max_len - len(circ_pre))
renal_pre += [""] * (max_len - len(renal_pre))
data_pre = pd.DataFrame({
    "Circulatory": [name_and_value(v) for v in circ_pre],
    "Renal": [name_and_value(v) for v in renal_pre]
})
styled_table_pre = data_pre.style.applymap(colorize).hide(axis="index")
st.write(styled_table_pre)

st.markdown("#### Other Variables")
other_vars = ["preop_dm", "preop_htn", "asa", "cancer"]
surg_vars = ["General surgery", "Thoracic surgery", "Urology", "Gynecology", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"]
max_len = max(len(other_vars), len(surg_vars))
other_vars += [""] * (max_len - len(other_vars))
surg_vars += [""] * (max_len - len(surg_vars))
df_others = pd.DataFrame({
    "Others": [name_and_value(v) for v in other_vars],
    "Surgical": [name_and_value(v) for v in surg_vars]
})
styled_others = df_others.style.applymap(colorize).hide(axis="index")
st.write(styled_others)
