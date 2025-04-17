import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Variables", page_icon="📊")

st.markdown("# Variables Affecting the Prediction")
st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Color bar legend
st.markdown("**Importance Scale**")
fig, ax = plt.subplots(figsize=(8, 0.05))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(0, 100)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
st.pyplot(fig)

# ----------------- DEMOGRAPHIC VARIABLES -----------------
st.markdown("#### Demographic Variables")

demo_vars = ["age", "sex", "height", "weight", "BMI"]
demo_importance = [80, 65, 50, 70, 90]
demo_units = ["years", "male", "cm", "kg", "kg/m²"]

# Combine name, value, and unit
combined_demo = [
    f"{name} ({score} {unit})" if unit else f"{name} ({score})"
    for name, score, unit in zip(demo_vars, demo_importance, demo_units)
]

df_demo = pd.DataFrame({"Demographic": combined_demo})

def colorize_demo(val):
    try:
        score_part = val.split("(")[-1].split()[0]  # Get the number before unit
        score = int(score_part)
        color = sns.color_palette("coolwarm", as_cmap=True)(score / 100)
        return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    except:
        return ''

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

# Merge into strings like "PaO2 (85)"
data_pre = pd.DataFrame({
    col: [f"{v} ({s})" for v, s in zip(data_dict_var_pre[col], data_dict_numbers_pre[col])]
    for col in data_dict_var_pre
})

def colorize_pre(val):
    try:
        score = int(val.split("(")[-1].rstrip(")"))
        color = sns.color_palette("coolwarm", as_cmap=True)(score / 100)
        return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    except:
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

data_peri = pd.DataFrame({
    col: [f"{v} ({s})" for v, s in zip(data_dict_var_peri[col], data_dict_numbers_peri[col])]
    for col in data_dict_var_peri
})

def colorize_peri(val):
    try:
        score = int(val.split("(")[-1].rstrip(")"))
        color = sns.color_palette("coolwarm", as_cmap=True)(score / 100)
        return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    except:
        return ''

styled_table_peri = data_peri.style.applymap(colorize_peri).hide(axis="index")
st.write(styled_table_peri)

# ----------------- OTHER VARIABLES -----------------
st.markdown("#### Other Variables")
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

df_others = pd.DataFrame({
    col: [f"{v} ({s})" if v else "" for v, s in zip(data_dict_var_others[col], data_dict_importance_others[col])]
    for col in data_dict_var_others
})

def colorize_others(val):
    try:
        if not val.strip(): return ''
        score = int(val.split("(")[-1].rstrip(")"))
        color = sns.color_palette("coolwarm", as_cmap=True)(score / 100)
        return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    except:
        return ''

styled_others = df_others.style.applymap(colorize_others).hide(axis="index")
st.write(styled_others)
