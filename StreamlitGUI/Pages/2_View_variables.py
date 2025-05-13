import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Variables", page_icon="📊")

# Map patient names to case IDs
patient_case_map = {
    "Åse Sørensen 020865-1448": 20,
    "Børge Holm 241279-1337": 76,
    "Ida Jensen 040499-1688": 87,
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

# Page title
st.markdown("# Variables Affecting the Prediction")

# Display selected patient
st.markdown(f"### Selected: {st.session_state.patient_option}")

st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Add color bar legend
st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.05))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(-1, 1)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# Function to generate background color
def colorize(val):
    score = patient_shap.get(val, 0)
    norm_score = (score + 1) / 2
    color = sns.color_palette("coolwarm", as_cmap=True)(norm_score)
    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

# ----------------- MOST IMPORTANT VARIABLES -----------------
st.markdown("#### Summary of Most Important Variables for Prediction")
imp_vars = ["age", "sex", "height", "weight", "BMI"]
df_imp = pd.DataFrame({"Important Variables": imp_vars})
styled_imp = df_imp.style.applymap(colorize).hide(axis="index")
st.write(styled_imp)

# Create two columns: left for content, right for patient name
col1, col2 = st.columns([1, 1])

# ----------------- DEMOGRAPHIC VARIABLES -----------------
with col1:
    st.markdown("#### Demographic Variables")
    demo_vars = ["age", "sex", "height", "weight", "BMI"]
    df_demo = pd.DataFrame({"Demographic": demo_vars})
    styled_demo = df_demo.style.applymap(colorize).hide(axis="index")
    st.write(styled_demo)

    # ----------------- PERIOPERATIVE VARIABLES -----------------
    st.markdown("#### Perioperative Variables")
    data_dict_var_peri = {
        "Respiratory": ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "RR_w15min", "SpO2_total", "SpO2_w15min", "SpO2_n90", "SpO2_w15minMV", "data_vent", "", "", "", "", ""],
        "Circulatory": ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso", "value_ino", "has_aline", "FFP", "RBC", "under36", "over38", "differencebetween15min"],
    }
    data_peri = pd.DataFrame.from_dict(data_dict_var_peri)
    data_peri.reset_index(drop=True, inplace=True)
    styled_table_peri = data_peri.style.applymap(colorize).hide(axis="index")
    st.write(styled_table_peri)

# ----------------- PREOPERATIVE VARIABLES -----------------
with col2:
    st.markdown("#### Preoperative Variables")
    data_dict_var_pre = {
        "Circulatory": ["prept", "preaptt", "prehb", "preplt"],
        "Renal": ["prek", "prena", "preca", ""]
    }
    data_pre = pd.DataFrame.from_dict(data_dict_var_pre)
    data_pre.reset_index(drop=True, inplace=True)
    styled_table_pre = data_pre.style.applymap(colorize).hide(axis="index")
    st.write(styled_table_pre)

    # ----------------- OTHER VARIABLES -----------------
    st.markdown("#### Other Variables")
    data_dict_var_others = {
        "Others": ["preop_dm", "preop_htn", "asa", "cancer", "", "", "", "", ""],
        "Surgical": ["General surgery", "Thoracic surgery", "Urology", "Gynecology", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"]
    }
    df_others = pd.DataFrame.from_dict(data_dict_var_others)
    df_others.reset_index(drop=True, inplace=True)
    styled_others = df_others.style.applymap(colorize).hide(axis="index")
    st.write(styled_others)
