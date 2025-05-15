import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Variables", page_icon="📊")

# Map patient names to case IDs
patient_case_map = {
    "Åse Sørensen 020865-1448": 5,
    "Børge Holm 241279-1337": 16,
    "Ida Jensen 040499-1688": 706,
}

# Load SHAP values
shap_df = pd.read_csv("Machine/shap_values.csv")

# Load values from CSV (source of variable values to display)
values_df = pd.read_csv(r"TestTrainingSet\test_ids_pre&peri.csv")

# Get current case ID
case_id = patient_case_map.get(st.session_state.patient_option)

if case_id is not None and case_id in shap_df["caseid"].values:
    row_shap = shap_df[shap_df["caseid"] == case_id].iloc[0]
    patient_shap = row_shap.drop(labels="caseid").to_dict()
else:
    st.error("Patient not found or invalid case ID.")
    st.stop()

# Find the row with this case_id in values_df
if case_id not in values_df["caseid"].values:
    st.error("Case ID not found in values CSV.")
    st.stop()
row_values = values_df[values_df["caseid"] == case_id].iloc[0]

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
    "HR_total": "HR",
    "HR_w15minMV": "HR last 15 min MV",
    "value_eph": "Ephedrine use",
    "value_phe": "Phenylephrine use",
    "value_vaso": "vasopressin use",
    "value_ino": "Inotropes use",
    "has_aline": "Aline",
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
    "preop_dm": "Diabetis diagnosis",
    "preop_htn": "Hypertension",
    "asa": "ASA score",
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

# Format values nicely based on variable type
def format_value(var, val):
    if pd.isna(val):
        return "N/A"
    if var == "age":
        return f"{int(val)} years"
    elif var in ["height", "weight"]:
        return f"{val:.1f}"
    elif var in ["anesthesia_duration", "op_duration_min"]:
        return f"{int(val)} min"
    elif var.startswith("RR") or var.startswith("HR") or var.startswith("SpO2"):
        return f"{val:.1f}"
    elif var in ["prept", "preaptt", "prehb", "preplt", "prek", "prena", "preca"]:
        return f"{val:.2f}"
    elif var in ["value_eph", "value_phe", "value_vaso", "value_ino"]:
        return f"{val:.1f}"
    else:
        return str(val)

# Page title
st.markdown("# Variables Affecting the Prediction")
st.markdown(f"### Selected: {st.session_state.patient_option}")

st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Importance colorbar legend
st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.05))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(-1, 1)
plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# Background color function based on SHAP importance
def colorize(val):
    # val looks like "Age: 40 years" so we split to get name
    name = val.split(":")[0].strip()
    original_name = [k for k, v in feature_name_map.items() if v == name]
    score = patient_shap.get(original_name[0], 0) if original_name else 0
    norm_score = (score + 1) / 2
    color = sns.color_palette("coolwarm", as_cmap=True)(norm_score)
    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

# Combine feature name and formatted value from CSV row
def name_and_value(var):
    name = feature_name_map.get(var, var)
    if var in row_values.index:
        val_raw = row_values[var]
        val_str = format_value(var, val_raw)
    else:
        val_str = "N/A"
    return f"{name}: {val_str}"

# ----------------- MOST IMPORTANT VARIABLES -----------------
st.markdown("#### Summary of Most Important Variables for Prediction")

top_vars = sorted(patient_shap.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
imp_vars = [name_and_value(var) for var, _ in top_vars]

df_imp = pd.DataFrame({"Important Variables": imp_vars})
styled_imp = df_imp.style.applymap(colorize).hide(axis="index")
st.write(styled_imp)

# Two columns for grouping variables
col1, col2 = st.columns([1, 1])

# ----------------- DEMOGRAPHIC VARIABLES -----------------
with col1:
    st.markdown("#### Demographic Variables")
    demo_vars = ["age", "sex", "height", "weight", "BMI"]
    demo_vals = [name_and_value(v) for v in demo_vars]
    df_demo = pd.DataFrame({"Demographic": demo_vals})
    styled_demo = df_demo.style.applymap(colorize).hide(axis="index")
    st.write(styled_demo)

    # ----------------- PERIOPERATIVE VARIABLES -----------------
    st.markdown("#### Perioperative Variables")
    resp_vars = ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "RR_w15min", "SpO2_total", "SpO2_w15min", "SpO2_n90", "SpO2_w15minMV", "data_vent"]
    circ_vars = ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso", "value_ino", "has_aline", "FFP", "RBC", "under36", "over38", "differencebetween15min"]
    data_peri = pd.DataFrame({
        "Respiratory": [name_and_value(v) if v else "" for v in resp_vars],
        "Circulatory": [name_and_value(v) if v else "" for v in circ_vars]
    })
    styled_table_peri = data_peri.style.applymap(colorize).hide(axis="index")
    st.write(styled_table_peri)

# ----------------- PREOPERATIVE VARIABLES -----------------
with col2:
    st.markdown("#### Preoperative Variables")
    circ_pre = ["prept", "preaptt", "prehb", "preplt"]
    renal_pre = ["prek", "prena", "preca", ""]
    data_pre = pd.DataFrame({
        "Circulatory": [name_and_value(v) if v else "" for v in circ_pre],
        "Renal": [name_and_value(v) if v else "" for v in renal_pre]
    })
    styled_table_pre = data_pre.style.applymap(colorize).hide(axis="index")
    st.write(styled_table_pre)

    # ----------------- OTHER VARIABLES -----------------
    st.markdown("#### Other Variables")
    other_vars = ["preop_dm", "preop_htn", "asa", "cancer", "", "", "", "", ""]
    surg_vars = ["General surgery", "Thoracic surgery", "Urology", "Gynecology", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"]
    df_others = pd.DataFrame({
        "Others": [name_and_value(v) if v else "" for v in other_vars],
        "Surgical": [name_and_value(v) if v else "" for v in surg_vars]
    })
    styled_others = df_others.style.applymap(colorize).hide(axis="index")
    st.write(styled_others)
