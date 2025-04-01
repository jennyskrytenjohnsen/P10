import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns

st.set_page_config(page_title="Colored Table Demo", page_icon="📊")

st.markdown("# Colored Table Demo")
st.write("This table contains letters as both columns and rows, with numeric values and unique background colors.")

# Generate a dataframe with letters as row and column labels
letters = list("ABCDEFG")  # Adjust the range for more/less rows and columns
data = pd.DataFrame(np.random.randint(1, 100, size=(len(letters), len(letters))), index=letters, columns=letters)

# Apply background gradient using seaborn colormap
def colorize(val):
    color = sns.color_palette("coolwarm", as_cmap=True)(val / 100)  # Normalize between 0-1
    return f'background-color: rgba({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)}, 0.7)'

styled_table = data.style.applymap(colorize)

st.write(styled_table)