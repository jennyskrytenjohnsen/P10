import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Variables", page_icon="📊")

st.markdown("# Variables Affecting the Prediction")
st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Add color bar legend
st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.05))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(0, 100)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# ----------------- DEMOGRAPHIC VARIABLES -----------------
st.markdown("#### Demographic Variables")

# Demographic data with importance values
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

# ----------------- PREOPERATIVE VARIABLES -----------------
st.markdown("#### Preoperative Variables")

data_dict_var_pre = {
    "Respiratory": ["PaO2", "Hej1", "Bla1"],
    "Circulatory": ["MAP", "Hej2", "Bla2"],
    "Renal": ["CR", "Hej3", "Bla3"]
}
data_dict_numbers_pre = {
    "Respiratory": [85, 60, 45],
    "Circulatory": [70, 55, 50],
    "Renal": [75, 40, 30]
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

# ----------------- PERIOPERATIVE VARIABLES -----------------
st.markdown("#### Perioperative Variables")

data_dict_var_peri = {
    "Respiratory": ["uhu", "skjd", "ski"],
    "Circulatory": ["MAP", "Hej2", "laj"],
    "Renal": ["CR", "Hej3", "Bla3"]
}
data_dict_numbers_peri = {
    "Respiratory": [85, 60, 45],
    "Circulatory": [70, 55, 50],
    "Renal": [75, 40, 30]
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

# ----------------- OTHER VARIABLES -----------------
st.markdown("#### Other Variables")

# Define the variable names and importance scores in transposed format
data_dict_var_others = {
    "Surgery details": ["Surgery duration", "Ane duration", "number3"],
    "Laboratory values": ["hej", "hy", "ju"],
    "Others": ["", "", ""]
}

data_dict_importance_others = {
    "Surgery details": [60, 65, 50],
    "Laboratory values": [70, 75, 80],
    "Others": [0, 0, 0]
}

# Create DataFrames
df_others = pd.DataFrame.from_dict(data_dict_var_others)
importance_df_others = pd.DataFrame.from_dict(data_dict_importance_others)

# Reset index to align rows properly
df_others.reset_index(drop=True, inplace=True)
importance_df_others.reset_index(drop=True, inplace=True)

# Coloring function for each value based on importance
def colorize_others(val):
    for i in range(df_others.shape[0]):
        for col in df_others.columns:
            if df_others.loc[i, col] == val:
                score = importance_df_others.loc[i, col] / 100
                color = sns.color_palette("coolwarm", as_cmap=True)(score)
                return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    return ''

# Apply the styling
styled_others = df_others.style.applymap(colorize_others).hide(axis="index")
st.write(styled_others)
