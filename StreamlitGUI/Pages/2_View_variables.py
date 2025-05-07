import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Variables", page_icon="📊")

# Top part spanning the full width
st.markdown("# Variables Affecting the Prediction")
    
# Display the selected patient's name
st.markdown(f"### Selected: {st.session_state.patient_option}")

st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Add color bar legend
st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.05))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(0, 100)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# Create two columns: left for content, right for patient name
col1, col2 = st.columns([1, 1])  # Adjust width ratio as needed

# Put all other content inside col1
with col1:
    # ----------------- DEMOGRAPHIC VARIABLES -----------------
    st.markdown("#### Demographic Variables")
    demo_vars = ["age", "sex", "height", "weight", "BMI"]
    demo_importance = [80, 65, 50, 70, 90]
    df_demo = pd.DataFrame({"Demographic": demo_vars})
    importance_demo = pd.Series(demo_importance, index=df_demo.index)

    def colorize_demo(val):
        idx = df_demo[df_demo["Demographic"] == val].index[0]
        score = importance_demo[idx] / 100
        color = sns.color_palette("coolwarm", as_cmap=True)(score)
        return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'

    styled_demo = df_demo.style.applymap(colorize_demo).hide(axis="index")
    st.write(styled_demo)

    
    # ----------------- PERIOPERATIVE VARIABLES -----------------
    st.markdown("#### Perioperative Variables")
    data_dict_var_peri = {
        "Respiratory": ["RR_total", "RR_n12", "RR_n20", "RR_w15minMV", "RR_w15min", "SpO2_total", "SpO2_w15min", "SpO2_n90", "SpO2_w15minMV", "data_vent", "", "", "", "", ""],
        "Circulatory": ["HR_n30", "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "value_eph", "value_phe", "value_vaso", "value_ino", "has_aline", "FFP", "RBC", "under36", "over38", "differencebetween15min"],
    }
    data_dict_numbers_peri = {
        "Respiratory": [85, 60, 45, 4, 5, 6, 7, 8, 9, 80, 50, 50, 50, 50, 50],
        "Circulatory": [70, 55, 50, 85, 60, 45, 4, 5, 6, 7, 8, 9, 80, 5, 50],
    }
    data_peri = pd.DataFrame.from_dict(data_dict_var_peri)
    values_df_peri = pd.DataFrame.from_dict(data_dict_numbers_peri)
    data_peri.reset_index(drop=True, inplace=True)
    values_df_peri.reset_index(drop=True, inplace=True)

    def colorize_peri(val):
        for i in range(data_peri.shape[0]):
            for col in data_peri.columns:
                if data_peri.loc[i, col] == val:
                    score = values_df_peri.loc[i, col] / 100
                    color = sns.color_palette("coolwarm", as_cmap=True)(score)
                    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
        return ''

    styled_table_peri = data_peri.style.applymap(colorize_peri).hide(axis="index")
    st.write(styled_table_peri)

    
with col2:
    # ----------------- PREOPERATIVE VARIABLES -----------------
    st.markdown("#### Preoperative Variables")
    data_dict_var_pre = {
        "Circulatory": ["prept", "preaptt", "prehb", "preplt"],
        "Renal": ["prek", "prena", "preca", ""]
    }
    data_dict_numbers_pre = {
        "Circulatory": [70, 55, 50, 8],
        "Renal": [75, 40, 30, 50]
    }
    data_pre = pd.DataFrame.from_dict(data_dict_var_pre)
    values_df_pre = pd.DataFrame.from_dict(data_dict_numbers_pre)
    data_pre.reset_index(drop=True, inplace=True)
    values_df_pre.reset_index(drop=True, inplace=True)

    def colorize_pre(val):
        for i in range(data_pre.shape[0]):
            for col in data_pre.columns:
                if data_pre.loc[i, col] == val:
                    score = values_df_pre.loc[i, col] / 100
                    color = sns.color_palette("coolwarm", as_cmap=True)(score)
                    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
        return ''

    styled_table_pre = data_pre.style.applymap(colorize_pre).hide(axis="index")
    st.write(styled_table_pre)

    # ----------------- OTHER VARIABLES -----------------
    st.markdown("#### Other Variables")
    data_dict_var_others = {
        "Others": ["preop_dm", "preop_htn", "asa", "cancer", ""],
        "Anesthesia": ["generalAnesthesia", "spinalAnesthesia", "sedationalgesia", "anesthesia_duration", "op_duration_min"],
        "Surgical category": ["General surgery", "Thoracic surgery", "Urology", "Gynecology", ""]
    }
    data_dict_importance_others = {
        "Others": [60, 65, 50, 70, 50],
        "Anesthesia": [70, 75, 80, 10, 20],
        "Surgical category": [0, 0, 0, 5, 50]
    }
    df_others = pd.DataFrame.from_dict(data_dict_var_others)
    importance_df_others = pd.DataFrame.from_dict(data_dict_importance_others)
    df_others.reset_index(drop=True, inplace=True)
    importance_df_others.reset_index(drop=True, inplace=True)

    def colorize_others(val):
        for i in range(df_others.shape[0]):
            for col in df_others.columns:
                if df_others.loc[i, col] == val:
                    score = importance_df_others.loc[i, col] / 100
                    color = sns.color_palette("coolwarm", as_cmap=True)(score)
                    return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
        return ''

    styled_others = df_others.style.applymap(colorize_others).hide(axis="index")
    st.write(styled_others)
