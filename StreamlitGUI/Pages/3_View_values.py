
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Variables", page_icon="📊")

# Map patient names to case IDs
patient_case_map = {
    "Åge Sørensen 020859-1447": 5,
    "Børge Holm 241268-1337": 16,
    "Ida Jensen 040464-1688": 706,
    "Mona Due Bak 161055-9446": 729,
    "Hanne Holmegård 091288-8446": 328,
    "Ib Bentsen 081168-6757": 5870,
}

# Load SHAP values
shap_df = pd.read_csv("Machine/shap_values_preperi.csv")
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
    "age": "Age", "sex": "Sex", "height": "Height", "weight": "Weight", "BMI": "BMI",
    "RR_total": "RR total", "RR_n12": "RR below 12 bpm", "RR_n20": "RR above 20 bpm", "RR_w15minMV": "RR last 15 min",
    "SpO2_total": "SpO2 total", "SpO2_n90": "SpO2 below 90%", "SpO2_w15minMV": "SpO2 last 15 min",
    "data_vent": "Ventilator use", "HR_n30": "HR below 30 bpm", "HR_n60": "HR below 60 bpm",
    "HR_n100": "HR above 100 bpm", "HR_total": "HR total", "HR_w15minMV": "HR last 15 min",
    "value_eph": "Ephedrine use", "value_phe": "Phenylephrine use", "value_vaso": "Vasopressin use",
    "value_ino": "Inotropes use", "has_aline": "Arterial line", "FFP": "FFP", "RBC": "RBC",
    "under36": "Temp below 36", "over38": "Temp above 38", "differencebetween15min": "Temp difference start/end",
    "prept": "PT", "preaptt": "APTT", "prehb": "Hemoglobin", "preplt": "Platelet count",
    "prek": "Potassium", "prena": "Sodium", "preca": "Calcium", "preop_dm": "Diabetis mellitus",
    "preop_htn": "Hypertension", "asa": "ASA PS score", "cancer": "Cancer diagnosis",
    "General surgery": "General surgery", "Thoracic surgery": "Thoracic surgery",
    "Urology": "Urology", "Gynecology": "Gynecology",
    "generalAnesthesia": "General anesthesia", "spinalAnesthesia": "Spinal anesthesia",
    "sedationalgesia": "Sedation algesia", "anesthesia_duration": "Anesthesia duration",
    "op_duration_min": "Operation duration"
}

for placeholder in [""] * 10:
    patient_shap[placeholder] = 0

def format_value(var, val):
    if pd.isna(val): return "N/A"
    int_vars = ["age", "preca", "asa", "FFP", "RBC", "prept", "preaptt", "prena", "preplt"]
    one_decimal_vars = ["height", "weight", "prek"]

    binary_mappings = {
        "sex": {0: "female", 1: "male"}, "data_vent": {0: "no", 1: "yes"},
        "value_eph": {0: "no", 1: "yes"}, "value_phe": {0: "no", 1: "yes"},
        "value_vaso": {0: "no", 1: "yes"}, "value_ino": {0: "no", 1: "yes"},
        "has_aline": {0: "no", 1: "yes"}, "General surgery": {0.0: "no", 1.0: "yes"},
        "Thoracic surgery": {0.0: "no", 1.0: "yes"}, "Urology": {0.0: "no", 1.0: "yes"},
        "Gynecology": {0.0: "no", 1.0: "yes"}, "generalAnesthesia": {0.0: "no", 1.0: "yes"},
        "spinalAnesthesia": {0.0: "no", 1.0: "yes"}, "sedationalgesia": {0.0: "no", 1.0: "yes"},
        "preop_dm": {0: "no", 1: "yes"}, "preop_htn": {0: "no", 1: "yes"}, "cancer": {0: "no", 1: "yes"}
    }
    if var in binary_mappings:
        return binary_mappings[var].get(val, "N/A")
    if var in int_vars:
        return f"{int(round(val))}"
    if var in one_decimal_vars:
        return f"{val:.1f}"
    if var in ["differencebetween15min"]:
        return f"{val:.2f} °C"
    if var.startswith("RR") or var.startswith("HR"):
        return f"{val:.1f} bpm"
    if var.startswith("SpO2"):
        return f"{val:.1f} %"
    if var in ["anesthesia_duration"]:
        return f"{val / 3600:.1f} hours"
    if var in ["op_duration_min"]:
        return f"{val / 60:.1f} hours"
    return str(val)

def name_and_value(var):
    if var == "":
        return ""
    name = feature_name_map.get(var, var)
    val_raw = row_values.get(var, np.nan)
    val_str = format_value(var, val_raw)
    return f"{name}: {val_str}"

def colorize(val):
    if val == "":
        return ""
    name = val.split(":")[0].strip()
    original_name = [k for k, v in feature_name_map.items() if v == name]
    score = patient_shap.get(original_name[0], 0) if original_name else 0
    norm_score = (score + 1) / 2
    color = sns.color_palette("coolwarm", as_cmap=True)(norm_score)
    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

def make_sorted_table(var_list, title):
    sorted_vars = sorted(var_list, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)
    data = [name_and_value(v) for v in sorted_vars]
    df = pd.DataFrame({title: data})
    styled = df.style.applymap(colorize).hide(axis="index")
    return styled

st.markdown("# Variable values affecting the prediction")
st.markdown(f"### Selected patient: {st.session_state.patient_option}")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Timestamp for prediction:** {current_time}")

st.markdown("#### Summary of Most Important Variables for Prediction")
top_vars = sorted(patient_shap.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
top_display = [name_and_value(var) for var, _ in top_vars]
df_top = pd.DataFrame({"Important Variables": top_display})
styled_top = df_top.style.applymap(colorize).hide(axis="index")
st.write(styled_top)

# Section tables
st.markdown("#### Demographic Variables")
st.write(make_sorted_table(["age", "sex", "height", "weight", "BMI"], "Demographic"))

st.markdown("#### Perioperative Variables")
resp = ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "SpO2_total", "SpO2_n90", "SpO2_w15minMV", "data_vent"]
circ = ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso", "value_ino", "has_aline", "FFP", "RBC", "under36", "over38", "differencebetween15min"]
max_len = max(len(resp), len(circ))
resp += [""] * (max_len - len(resp))
circ += [""] * (max_len - len(circ))
df_peri = pd.DataFrame({
    "Respiratory": [name_and_value(v) for v in sorted(resp, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)],
    "Circulatory": [name_and_value(v) for v in sorted(circ, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)]
})
st.write(df_peri.style.applymap(colorize).hide(axis="index"))

st.markdown("#### Preoperative Variables")
circ_pre = ["prept", "preaptt", "prehb", "preplt"]
renal_pre = ["prek", "prena", "preca"]
max_len = max(len(circ_pre), len(renal_pre))
circ_pre += [""] * (max_len - len(circ_pre))
renal_pre += [""] * (max_len - len(renal_pre))
df_pre = pd.DataFrame({
    "Circulatory": [name_and_value(v) for v in sorted(circ_pre, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)],
    "Renal": [name_and_value(v) for v in sorted(renal_pre, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)]
})
st.write(df_pre.style.applymap(colorize).hide(axis="index"))

st.markdown("#### Other Variables")
other_vars = ["preop_dm", "preop_htn", "asa", "cancer"]
surg_vars = ["General surgery", "Thoracic surgery", "Urology", "Gynecology", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"]
max_len = max(len(other_vars), len(surg_vars))
other_vars += [""] * (max_len - len(other_vars))
surg_vars += [""] * (max_len - len(surg_vars))
df_other = pd.DataFrame({
    "Others": [name_and_value(v) for v in sorted(other_vars, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)],
    "Surgical": [name_and_value(v) for v in sorted(surg_vars, key=lambda x: abs(patient_shap.get(x, 0)), reverse=True)]
})
st.write(df_other.style.applymap(colorize).hide(axis="index"))
