import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Variables", page_icon="📊")

st.markdown("# Variables Affecting the Prediction")
st.write("This page offers an overview of the variables affecting the prediction of ICU admission. The importance of each variable is determined by the underlying machine learning algorithm, and therefore it might not match the physiological importance.")

# Define 5 columns and 2 rows
columns = ["Respiratory", "Circulatory", "Renal", "Demographic", "Others"]
rows = ["Preoperative", "Perioperative"]

# Each category has one variable per row → 2 variables per category
data_dict = {
    "Respiratory": [("PaO2", 85), ("FiO2", 75)],
    "Circulatory": [("MAP", 70), ("HR", 65)],
    "Renal": [("Creatinine", 80), ("BUN", 60)],
    "Demographic": [("Age", 50), ("Sex", 30)],
    "Others": [("Comorbidities", 70), ("Surgical type", 85)]
}

# Build variable names and values
variables = [v[0] for cat in columns for v in data_dict[cat]]
values = [v[1] for cat in columns for v in data_dict[cat]]

# Reshape into 2x5 table
data = pd.DataFrame(np.array(variables).reshape(2, 5), index=rows, columns=columns)
values_df = pd.DataFrame(np.array(values).reshape(2, 5), index=rows, columns=columns)

# Function to apply color based on value
def colorize(val):
    for row in data.index:
        for col in data.columns:
            if data.loc[row, col] == val:
                score = values_df.loc[row, col] / 100
                color = sns.color_palette("coolwarm", as_cmap=True)(score)
                return f'background-color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, 0.7)'
    return ''

# Style the table
styled_table = data.style.applymap(colorize)
st.write(styled_table)

# Add a color bar legend
st.markdown("Importance Scale")
fig, ax = plt.subplots(figsize=(8, 0.1))
cmap = sns.color_palette("coolwarm", as_cmap=True)
norm = plt.Normalize(0, 100)
cb1 = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
# cb1.set_label('Importance Score')
st.pyplot(fig)
